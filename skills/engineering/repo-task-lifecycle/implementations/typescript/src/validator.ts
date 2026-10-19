import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";
import { createHash } from "node:crypto";

export const statuses = ["proposed", "ready", "in-progress", "blocked", "validation", "done", "superseded", "deferred"] as const;
const statusSet = new Set<string>(statuses);
const terminal = new Set(["done", "superseded", "deferred"]);
const authorities = new Set(["repository", "tracker", "manual"]);
const syncModes = new Set(["push", "pull", "bidirectional", "manual"]);
const trackerSystems = new Set(["github", "gitlab", "linear", "clickup"]);
const labelStrategies = new Set(["replace", "managed-subset", "read-only", "ignore"]);
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const linkGraphExcludedTypes = new Set(["tracker profile", "log"]);
const linkGraphExcludedTypeMarkers = ["runbook", "handoff", "session", "temporary", "scratch"];
const linkGraphExcludedDirectories = new Set([".git", ".venv", "build", "dist", "generated", "node_modules", "runbooks", "scratch", "temp", "temporary", "vendor"]);

type RecordValue = Record<string, unknown>;
type Parsed = { metadata: RecordValue; body: string };

function frontmatterStrings(value: unknown, field = "$"): Array<[string, string]> {
  if (typeof value === "string") return [[field, value]];
  if (Array.isArray(value)) return value.flatMap((child, index) => frontmatterStrings(child, `${field}[${index}]`));
  if (value && typeof value === "object") return Object.entries(value as RecordValue).flatMap(([key, child]) =>
    frontmatterStrings(child, field === "$" ? key : `${field}.${key}`));
  return [];
}

function frontmatterPresentation(value: string): string | undefined {
  const checks: Array<[string, RegExp]> = [
    ["Markdown link or image", /!?\[[^\]\n]+\]\([^)\n]+\)/],
    ["Markdown reference link", /\[[^\]\n]+\]\[[^\]\n]*\]/],
    ["Markdown code", /`+[^`\n]+`+/],
    ["Markdown emphasis", /(?:\*\*[^*\n]+\*\*|__[^_\n]+__|~~[^~\n]+~~|(^|[^\w/])\*[^*\n]+\*($|[^\w/])|(^|[^\w/])_[^_\n]+_($|[^\w/]))/],
    ["Markdown block formatting", /^\s{0,3}(?:#{1,6}|>|[-+*]|\d+[.)])\s+/m],
    ["HTML tag", /<\/?[A-Za-z][^>\n]*>/],
  ];
  return checks.find(([, pattern]) => pattern.test(value))?.[0];
}

function validatePlaintextFrontmatter(file: string, metadata: RecordValue, errors: string[]): void {
  for (const [field, value] of frontmatterStrings(metadata)) {
    const presentation = frontmatterPresentation(value);
    if (presentation) errors.push(`${file}: frontmatter string values must be plaintext; ${field} contains ${presentation}`);
  }
}

const secretPatterns: Array<[string, RegExp]> = [
  ["private key", /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----/],
  ["GitHub token", /\bgh[pousr]_[A-Za-z0-9_]{20,}\b/],
  ["AWS access key", /\bAKIA[0-9A-Z]{16}\b/],
  ["assigned secret", /\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*["']?[A-Za-z0-9_./+=-]{12,}/i],
];
const machinePathPatterns: Array<[string, RegExp]> = [
  ["file URI", /\bfile:\/\//i],
  ["Windows absolute path", /(?:^|[^A-Za-z0-9])(?:[A-Za-z]:[\\/]|\\\\)[^\s<>'"]+/],
  ["POSIX machine path", /(?:^|[^A-Za-z0-9])\/(?:home|Users|tmp|var\/tmp|etc|opt|srv|root|mnt|Volumes)\/[^\s<>'"]+/],
  ["home-relative path", /(?:^|[^A-Za-z0-9])~[\\/][^\s<>'"]+/],
];

function markdownFiles(root: string): string[] {
  if (!fs.existsSync(root)) return [];
  return fs.readdirSync(root, { withFileTypes: true }).flatMap((entry) => {
    const candidate = path.join(root, entry.name);
    return entry.isDirectory() ? markdownFiles(candidate) : entry.isFile() && entry.name.endsWith(".md") ? [candidate] : [];
  }).sort();
}

function parseDocument(file: string): Parsed {
  const source = fs.readFileSync(file, "utf8");
  if (!source.startsWith("---\n") && !source.startsWith("---\r\n")) throw new Error(`Missing YAML frontmatter in ${file}`);
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) throw new Error(`Unclosed YAML frontmatter in ${file}`);
  let metadata: unknown;
  try { metadata = YAML.parse(match[1]); } catch (error) { throw new Error(`Invalid YAML frontmatter in ${file}: ${String(error)}`); }
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) throw new Error(`Frontmatter must be a mapping in ${file}`);
  return { metadata: metadata as RecordValue, body: source.slice(match[0].length).replace(/^\r?\n/, "") };
}

function linkGraphRoot(bundle: string): string {
  const resolved = path.resolve(bundle);
  return path.basename(resolved) === "tasks" && path.basename(path.dirname(resolved)) === "docs"
    ? path.dirname(path.dirname(resolved)) : path.dirname(resolved);
}

function isSnapshotResource(file: string, root: string): boolean {
  if (fs.lstatSync(file).isSymbolicLink() || fs.statSync(file).size > 2 * 1024 * 1024) return false;
  for (let folder = path.dirname(file); folder !== root; folder = path.dirname(folder)) {
    const distance = path.relative(root, folder);
    if (distance === ".." || distance.startsWith(`..${path.sep}`) || path.isAbsolute(distance)) break;
    const manifest = path.join(folder, "OKF_UPSTREAM.json");
    try {
      const stat = fs.lstatSync(manifest);
      if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 2 * 1024 * 1024) continue;
      const snapshot = JSON.parse(fs.readFileSync(manifest, "utf8")) as RecordValue;
      if (snapshot.schema !== 1 || snapshot.producer !== "OKF Tasks" || !/^[a-f0-9]{40}$/.test(String(snapshot.source_commit ?? ""))) continue;
      const entries = snapshot.resources;
      if (!entries || typeof entries !== "object" || Array.isArray(entries) || Object.keys(entries).length > 2000) continue;
      const identity = (entries as RecordValue)[path.relative(folder, file).split(path.sep).join("/")];
      if (!identity || typeof identity !== "object") continue;
      const digest = (identity as RecordValue).package_sha256;
      if (typeof digest === "string" && /^[a-f0-9]{64}$/.test(digest)) return createHash("sha256").update(fs.readFileSync(file)).digest("hex") === digest;
    } catch { /* Invalid manifests grant no graph exemption. */ }
  }
  return false;
}

function durableLinkGraphErrors(bundle: string): string[] {
  const root = linkGraphRoot(bundle);
  const concepts = new Map<string, Parsed>();
  for (const file of markdownFiles(root)) {
    if (["index.md", "log.md"].includes(path.basename(file))) continue;
    const relativeParts = path.relative(root, file).split(path.sep).slice(0, -1).map((part) => part.toLowerCase());
    if (relativeParts.some((part) => linkGraphExcludedDirectories.has(part))) continue;
    const bundleDistance = path.relative(path.resolve(bundle), path.resolve(file));
    const outsideBundle = bundleDistance === ".." || bundleDistance.startsWith(`..${path.sep}`) || path.isAbsolute(bundleDistance);
    if (outsideBundle && isSnapshotResource(file, root)) continue;
    try {
      const parsed = parseDocument(file); const type = String(parsed.metadata.type ?? "").trim().toLowerCase();
      if (type && !linkGraphExcludedTypes.has(type) && !linkGraphExcludedTypeMarkers.some((marker) => type.includes(marker))) concepts.set(path.resolve(file), parsed);
    } catch { /* structural parser reports malformed bundle documents separately */ }
  }
  if (concepts.size < 2) return [];
  const adjacency = new Map([...concepts.keys()].map((file) => [file, new Set<string>()]));
  const connect = (source: string, candidate: string): void => {
    const target = path.resolve(candidate);
    if (target !== source && concepts.has(target)) { adjacency.get(source)!.add(target); adjacency.get(target)!.add(source); }
  };
  for (const [source, parsed] of concepts) {
    for (const match of parsed.body.matchAll(/(!)?\[[^\]\n]*\]\(([^)\s]+)[^)]*\)/g)) {
      if (match[1]) continue;
      const target = match[2].replace(/^<|>$/g, "");
      if (target.startsWith("#") || /^[a-z][a-z0-9+.-]*:/i.test(target)) continue;
      const local = decodeURIComponent(target.split("#", 1)[0].split("?", 1)[0]).replaceAll("\\", "/");
      if (local) connect(source, local.startsWith("/") ? path.join(root, local.replace(/^\/+/, "")) : path.join(path.dirname(source), local));
    }
    const type = String(parsed.metadata.type ?? "");
    if (type === "Task") {
      const structured = [typeof parsed.metadata.parent === "string" ? parsed.metadata.parent : "",
        ...(Array.isArray(parsed.metadata.depends_on) ? parsed.metadata.depends_on.map(String) : [])];
      for (const target of structured) {
        const clean = target.split("#", 1)[0].trim().replace(/^\.\//, "");
        if (!clean || /^[a-z][a-z0-9+.-]*:/i.test(clean)) continue;
        const candidate = path.join(bundle, clean); connect(source, path.extname(candidate) ? candidate : `${candidate}.md`);
      }
    } else if (type === "Workstream" && parsed.metadata.task) connect(source, path.join(bundle, String(parsed.metadata.task), "task.md"));
  }
  const errors = [...adjacency].filter(([, links]) => links.size === 0)
    .map(([file]) => `${root}: durable link graph contains orphan concept ${path.relative(root, file).replaceAll(path.sep, "/")}`);
  const remaining = new Set(adjacency.keys()); const components: Set<string>[] = [];
  while (remaining.size) {
    const first = remaining.values().next().value as string; const pending = [first]; const component = new Set<string>();
    while (pending.length) { const current = pending.pop()!; if (component.has(current)) continue; component.add(current); pending.push(...adjacency.get(current)!); }
    component.forEach((file) => remaining.delete(file)); components.push(component);
  }
  if (components.length > 1) errors.push(`${root}: durable link graph has ${components.length} disconnected components`);
  return errors;
}

export function egressFindings(text: string, root: string): string[] {
  const findings: string[] = [];
  const roots = [path.resolve(root), path.resolve(root).replaceAll("\\", "/")].map((value) => value.toLowerCase());
  text.split(/\r?\n/).forEach((line, index) => {
    for (const [name, pattern] of secretPatterns) if (pattern.test(line)) findings.push(`line ${index + 1}: detected ${name}`);
    for (const [name, pattern] of machinePathPatterns) if (pattern.test(line)) findings.push(`line ${index + 1}: detected ${name}`);
    if (roots.some((value) => value && line.toLowerCase().includes(value))) findings.push(`line ${index + 1}: detected repository-local absolute path`);
  });
  return [...new Set(findings)];
}

function repositoryWebBase(remote: string, requestedProvider?: string): { provider: "github" | "gitlab"; base: string } {
  let host: string; let repositoryPath: string;
  const scp = !remote.includes("://") ? remote.trim().match(/^(?:[^@/]+@)?([^:]+):(.+)$/) : null;
  if (scp) { [, host, repositoryPath] = scp; }
  else {
    let parsed: URL; try { parsed = new URL(remote); } catch { throw new Error("Unsupported repository remote"); }
    if (!["http:", "https:", "ssh:", "git:"].includes(parsed.protocol) || !parsed.hostname) throw new Error("Unsupported repository remote");
    host = parsed.host; repositoryPath = parsed.pathname.replace(/^\//, "");
  }
  repositoryPath = repositoryPath.replace(/\.git$/, "").replace(/^\/+|\/+$/g, "");
  let provider = requestedProvider;
  const hostname = host.split(":", 1)[0].toLowerCase();
  if (!provider && (hostname === "github.com" || hostname.endsWith(".github.com"))) provider = "github";
  if (!provider && hostname.includes("gitlab")) provider = "gitlab";
  if (provider !== "github" && provider !== "gitlab") throw new Error("Repository provider is not identifiable");
  const encoded = repositoryPath.split("/").map((part) => encodeURIComponent(decodeURIComponent(part))).join("/");
  return { provider, base: `https://${host}/${encoded}` };
}

export function prepareExternalArtifact(
  rootValue: string,
  sourceValue: string,
  remote: string,
  ref: string,
  requestedProvider?: string,
  allowRemoteImages = false,
): string {
  const root = path.resolve(rootValue); const source = path.resolve(root, sourceValue);
  const relativeSource = path.relative(root, source);
  if (relativeSource.startsWith("..") || path.isAbsolute(relativeSource)) throw new Error("Source document must remain inside the repository root");
  const { body } = parseDocument(source);
  const findings = egressFindings(body, root);
  if (findings.length) throw new Error(findings.join("\n"));
  const { provider, base } = repositoryWebBase(remote, requestedProvider);
  const encodedRef = encodeURIComponent(ref);
  const rendered = body.replace(/(!)?(\[[^\]\n]*\])\(([^)\s]+)([^)]*)\)/g, (original, image: string | undefined, label: string, rawTarget: string, suffix: string) => {
    const target = rawTarget.replace(/^<|>$/g, "");
    if (target.startsWith("#")) return original;
    if (/^[A-Za-z][A-Za-z0-9+.-]*:/.test(target)) {
      if (!target.startsWith("https://")) throw new Error("External artifact contains a non-HTTPS or machine-local link");
      if (image && !allowRemoteImages) throw new Error("External artifact contains a remote image without an explicit allow policy");
      return original;
    }
    if (target.startsWith("//") || /^[A-Za-z]:[\\/]/.test(target)) throw new Error("External artifact contains a machine-local absolute link");
    const [withoutFragment, fragment = ""] = target.split("#", 2);
    if (withoutFragment.includes("?")) throw new Error("Repository-local links with query strings are not portable");
    const localPath = decodeURIComponent(withoutFragment).replaceAll("\\", "/");
    const candidate = path.resolve(localPath.startsWith("/") ? root : path.dirname(source), localPath.replace(/^\//, ""));
    const relative = path.relative(root, candidate);
    if (relative.startsWith("..") || path.isAbsolute(relative)) throw new Error("External artifact contains a repository link outside the declared root");
    if (!fs.existsSync(candidate)) throw new Error("External artifact contains an unresolved repository-local link");
    const view = fs.statSync(candidate).isDirectory() ? "tree" : "blob";
    const encodedPath = relative.split(path.sep).map((part) => encodeURIComponent(part)).join("/");
    const encodedFragment = fragment ? `#${encodeURIComponent(decodeURIComponent(fragment))}` : "";
    const providerPath = provider === "gitlab" ? `-/${view}` : view;
    return `${image ?? ""}${label}(${base}/${providerPath}/${encodedRef}/${encodedPath}${encodedFragment}${suffix})`;
  });
  const provenance = `<!-- OKF Tasks export: source=${relativeSource.replaceAll("\\", "/")}; revision=${ref} -->\n\n`;
  const output = provenance + rendered.replace(/\s+$/, "") + "\n";
  const finalFindings = egressFindings(output, root);
  if (finalFindings.length) throw new Error(finalFindings.join("\n"));
  return output;
}

function heading(body: string, name: string): boolean {
  return new RegExp(`^##\\s+${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*$`, "m").test(body);
}

function rfc3339(value: unknown): boolean {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value) && !Number.isNaN(Date.parse(value));
}

function nonNegativeInteger(value: unknown): boolean { return Number.isInteger(value) && Number(value) >= 0; }
function mapping(value: unknown): value is RecordValue { return !!value && typeof value === "object" && !Array.isArray(value); }

function validateEstimate(file: string, task: RecordValue, errors: string[]): void {
  if (task.estimate !== undefined) {
    if (!mapping(task.estimate)) errors.push(`${file}: estimate must be a mapping`);
    else {
      const estimate = task.estimate;
      if (!nonNegativeInteger(estimate.effort_minutes)) errors.push(`${file}: estimate.effort_minutes must be a non-negative integer`);
      if (!["agent", "manual", "historical"].includes(String(estimate.method))) errors.push(`${file}: estimate.method is invalid`);
      if (!["low", "medium", "high"].includes(String(estimate.confidence))) errors.push(`${file}: estimate.confidence is invalid`);
      if (!estimate.basis || !estimate.actor || !rfc3339(estimate.timestamp)) errors.push(`${file}: estimate missing required fields`);
    }
  }
  if (task.sprint_points !== undefined) {
    if (!mapping(task.sprint_points)) errors.push(`${file}: sprint_points must be a mapping`);
    else {
      const points = task.sprint_points;
      if (typeof points.value !== "number" || points.value < 0) errors.push(`${file}: sprint_points.value must be a non-negative number`);
      if (typeof points.scale !== "string" || !points.scale.trim()) errors.push(`${file}: sprint_points.scale is required`);
      if (!rfc3339(points.timestamp)) errors.push(`${file}: sprint_points.timestamp must be RFC 3339`);
    }
  }
}

function validateSync(file: string, task: RecordValue, errors: string[]): void {
  if (task.external !== undefined) {
    if (!Array.isArray(task.external)) errors.push(`${file}: external must be a list`);
    else task.external.forEach((item, index) => {
      const required = ["tracker", "system", "host", "kind", "scope", "id", "key", "url", "sync"];
      if (!mapping(item) || required.some((key) => item[key] === undefined || item[key] === "" || item[key] === null)) {
        errors.push(`${file}: external[${index}] requires tracker, system, host, kind, scope, id, key, url, and sync`); return;
      }
      if (!trackerSystems.has(String(item.system))) errors.push(`${file}: external[${index}].system is unsupported`);
      if (!mapping(item.scope) || !item.scope.id || !item.scope.key) errors.push(`${file}: external[${index}].scope requires id and key`);
      if (!mapping(item.sync)) errors.push(`${file}: external[${index}].sync must be a mapping`);
      else if (item.sync.base !== undefined && !mapping(item.sync.base)) errors.push(`${file}: external[${index}].sync.base must be a mapping`);
    });
  }
  if (task.sync !== undefined) errors.push(`${file}: task-level sync is not permitted; synchronization state belongs to each external binding`);
}

function validatePortableFields(file: string, task: RecordValue, errors: string[]): void {
  if (task.fields === undefined) return;
  if (!mapping(task.fields)) { errors.push(`${file}: fields must be a mapping`); return; }
  const supported = new Set(["text", "number", "date", "boolean", "single-select", "multi-select", "user", "url"]);
  Object.entries(task.fields).forEach(([name, field]) => {
    if (!mapping(field) || !supported.has(String(field.type)) || !("value" in field)) { errors.push(`${file}: fields.${name} requires a supported type and value`); return; }
    const type = String(field.type); const value = field.value;
    const valid = (["text", "date", "single-select", "user", "url"].includes(type) && typeof value === "string")
      || (type === "number" && typeof value === "number") || (type === "boolean" && typeof value === "boolean")
      || (type === "multi-select" && Array.isArray(value) && value.every((item) => typeof item === "string"));
    if (!valid) errors.push(`${file}: fields.${name}.value is incompatible with type ${type}`);
  });
}

function validateTrackerProfile(file: string, profile: RecordValue, errors: string[]): void {
  const required = ["type", "tracker", "system", "host", "resource", "scope", "sync", "status_map", "field_map", "discovery"];
  const missing = required.filter((key) => profile[key] === undefined || profile[key] === "" || profile[key] === null);
  if (missing.length) { errors.push(`${file}: Tracker Profile missing required fields: ${missing.join(", ")}`); return; }
  if (profile.type !== "Tracker Profile") errors.push(`${file}: type must be Tracker Profile`);
  if (profile.tracker !== path.basename(file, ".md") || !slugPattern.test(String(profile.tracker))) errors.push(`${file}: tracker slug must match its filename`);
  if (profile.default !== undefined && typeof profile.default !== "boolean") errors.push(`${file}: default must be a boolean`);
  if (!trackerSystems.has(String(profile.system))) errors.push(`${file}: unsupported tracker system`);
  try { const host = new URL(String(profile.host)); if (host.protocol !== "https:" || host.username || host.password || host.pathname !== "/" || host.search || host.hash) errors.push(`${file}: host must be an HTTPS origin without a path`); }
  catch { errors.push(`${file}: host must be an HTTPS origin without a path`); }
  if (!mapping(profile.scope) || !profile.scope.kind || !profile.scope.id || !profile.scope.key) errors.push(`${file}: scope requires kind, id, and key`);
  if (!mapping(profile.sync)) errors.push(`${file}: sync must be a mapping`);
  else {
    if (!syncModes.has(String(profile.sync.mode))) errors.push(`${file}: sync.mode must be push, pull, bidirectional, or manual`);
    if (!authorities.has(String(profile.sync.authority))) errors.push(`${file}: sync.authority must be repository, tracker, or manual`);
  }
  if (!mapping(profile.status_map)) errors.push(`${file}: status_map must be a mapping`);
  else {
    const statusMap = profile.status_map;
    statuses.forEach((status) => { if (!statusMap[status]) errors.push(`${file}: status_map requires ${status}`); });
    if (mapping(profile.sync) && profile.sync.mode === "bidirectional" && profile.sync.authority === "tracker") {
      const values = statuses.map((status) => String((profile.status_map as RecordValue)[status])).filter((value) => value !== "undefined");
      if (new Set(values).size !== values.length) errors.push(`${file}: tracker-authoritative bidirectional status_map must be round-trippable`);
    }
  }
  if (!mapping(profile.field_map)) errors.push(`${file}: field_map must be a mapping`);
  else Object.entries(profile.field_map).forEach(([field, value]) => {
    if (!mapping(value) || !value.remote) errors.push(`${file}: field_map.${field} requires remote`);
    else {
      if (field === "tags" && !labelStrategies.has(String(value.strategy))) errors.push(`${file}: field_map.tags.strategy is invalid`);
      if (field === "tags" && value.strategy === "managed-subset" && !value.managed_prefix && !value.managed_values) errors.push(`${file}: field_map.tags managed-subset requires managed_prefix or managed_values`);
      if (value.authority !== undefined && !authorities.has(String(value.authority))) errors.push(`${file}: field_map.${field}.authority is invalid`);
    }
  });
  if (!mapping(profile.discovery) || !rfc3339(profile.discovery.observed_at) || !profile.discovery.fingerprint) errors.push(`${file}: discovery requires observed_at and fingerprint`);
}

function validateTime(taskFile: string, task: RecordValue, errors: string[]): void {
  if (task.time !== undefined && !Array.isArray(task.time)) { errors.push(`${taskFile}: time must be a list`); return; }
  const rawEntries = Array.isArray(task.time) ? task.time : [];
  const entries: RecordValue[] = [];
  const running = new Map<string, string>();
  const ids = new Set<string>();
  for (let index = 0; index < rawEntries.length; index += 1) {
    const value = rawEntries[index]; const indexed = `${taskFile}#time[${index}]`;
    if (!mapping(value)) { errors.push(`${indexed}: time entry must be a mapping`); continue; }
    const entry = value; entries.push(entry);
    const required = ["id", "status", "actor", "started", "method", "activity"];
    const missing = required.filter((key) => entry[key] === undefined || entry[key] === "");
    if (missing.length) { errors.push(`${indexed}: missing required fields: ${missing.join(", ")}`); continue; }
    const label = `${taskFile}#time:${String(entry.id)}`;
    if (!slugPattern.test(String(entry.id))) errors.push(`${label}: id must be lowercase kebab-case`);
    if (ids.has(String(entry.id))) errors.push(`${label}: duplicate time entry id`); else ids.add(String(entry.id));
    if (!["running", "closed"].includes(String(entry.status))) errors.push(`${label}: time status must be running or closed`);
    if (!["tracked", "tracked-adjusted", "manual", "estimated-commit-review"].includes(String(entry.method))) errors.push(`${label}: unknown time method`);
    if (!["implementation", "review", "validation", "knowledge-maintenance", "research", "planning", "coordination", "other"].includes(String(entry.activity))) errors.push(`${label}: unknown time activity`);
    if (!rfc3339(entry.started)) errors.push(`${label}: started must be an RFC 3339 datetime`);
    if (entry.status === "running") {
      if (entry.method !== "tracked") errors.push(`${label}: running entries must use method tracked`);
      ["finished", "elapsed_minutes", "effort_minutes"].forEach((field) => { if (field in entry) errors.push(`${label}: running entry must not contain ${field}`); });
      const key = `${entry.actor}\u0000${entry.workstream ?? ""}`;
      if (running.has(key)) errors.push(`${label}: duplicate running actor/workstream`); else running.set(key, label);
    } else {
      if (entry.finished === undefined) errors.push(`${label}: closed entry requires finished`);
      else if (!rfc3339(entry.finished)) errors.push(`${label}: finished must be an RFC 3339 datetime`);
      if (entry.effort_minutes === undefined) errors.push(`${label}: closed entry requires effort_minutes`);
      if (entry.effort_minutes !== undefined && !nonNegativeInteger(entry.effort_minutes)) errors.push(`${label}: effort_minutes must be a non-negative integer`);
      if (entry.elapsed_minutes !== undefined && !nonNegativeInteger(entry.elapsed_minutes)) errors.push(`${label}: elapsed_minutes must be a non-negative integer`);
      if (["tracked-adjusted", "manual", "estimated-commit-review"].includes(String(entry.method)) && (!entry.basis || !String(entry.basis).trim())) errors.push(`${label}: ${String(entry.method)} entry requires basis`);
      if (entry.method === "estimated-commit-review") {
        if (!["low", "medium", "high"].includes(String(entry.confidence))) errors.push(`${label}: commit-review estimate requires low, medium, or high confidence`);
        if (!Array.isArray(entry.source_commits) || !entry.source_commits.length) errors.push(`${label}: commit-review estimate requires source_commits`);
        if (!mapping(entry.estimation)) errors.push(`${label}: commit-review estimate requires estimation`);
      }
    }
  }
  if (!entries.length) {
    if (task.started) errors.push(`${taskFile}: started requires at least one time entry`);
    if (task.effort_minutes !== undefined && task.effort_minutes !== 0) errors.push(`${taskFile}: effort_minutes requires closed time entries`);
    if (task.status === "done" && !task.finished) errors.push(`${taskFile}: done task requires finished`);
    return;
  }
  const closedEffort = entries.filter((entry) => entry.status === "closed" && Number.isInteger(entry.effort_minutes)).reduce((sum, entry) => sum + Number(entry.effort_minutes), 0);
  const starts = entries.map((entry) => entry.started).filter((value) => rfc3339(value)).map((value) => new Date(String(value)).getTime());
  if (starts.length && (!rfc3339(task.started) || new Date(String(task.started)).getTime() !== Math.min(...starts))) errors.push(`${taskFile}: started must equal the first time-entry start`);
  if (task.effort_minutes !== closedEffort) errors.push(`${taskFile}: effort_minutes must equal the closed time-entry sum (${closedEffort})`);
  if (task.status === "done" && entries.some((entry) => entry.status === "running")) errors.push(`${taskFile}: done task has running time entries`);
}

export function validateBundle(bundle: string): string[] {
  const errors: string[] = [];
  if (!fs.existsSync(bundle)) return [`${bundle}: bundle does not exist`];
  for (const file of markdownFiles(bundle)) {
    if (path.basename(file) === "log.md") continue;
    try {
      const metadata = parseDocument(file).metadata;
      validatePlaintextFrontmatter(file, metadata, errors);
      if (path.basename(file) === "index.md") continue;
      if (!metadata.type) errors.push(`${file}: non-reserved Markdown concept requires a non-empty type`);
      if (metadata.navigation !== undefined) {
        const navigation = metadata.navigation;
        if (!mapping(navigation) || !Object.keys(navigation).length) errors.push(`${file}: navigation must be a non-empty mapping`);
        else {
          if (navigation.role !== undefined && !["entry-point", "foundational", "supporting", "reference"].includes(String(navigation.role))) errors.push(`${file}: navigation.role must be entry-point, foundational, supporting, or reference`);
          if (navigation.order !== undefined && (!Number.isInteger(navigation.order) || Number(navigation.order) < 0)) errors.push(`${file}: navigation.order must be a non-negative integer`);
        }
      }
    }
    catch (error) { errors.push(String((error as Error).message)); }
  }
  const profiles = new Map<string, RecordValue>();
  const trackerDir = path.join(bundle, "trackers");
  if (fs.existsSync(trackerDir)) fs.readdirSync(trackerDir).filter((name) => name.endsWith(".md")).sort().forEach((name) => {
    const file = path.join(trackerDir, name); try { const parsed = parseDocument(file); validateTrackerProfile(file, parsed.metadata, errors); if (parsed.metadata.tracker) profiles.set(String(parsed.metadata.tracker), parsed.metadata); } catch { /* parse error recorded above */ }
  });
  const defaults = [...profiles.values()].filter((profile) => profile.default === true).map((profile) => String(profile.tracker));
  if (defaults.length > 1) errors.push(`${trackerDir}: only one default Tracker Profile is allowed; found ${defaults.join(", ")}`);
  const taskFiles = fs.readdirSync(bundle, { withFileTypes: true }).filter((entry) => entry.isDirectory() && fs.existsSync(path.join(bundle, entry.name, "task.md"))).map((entry) => path.join(bundle, entry.name, "task.md")).sort();
  const external = new Map<string, { file: string; relationship: string; tracker: string; scope: string }[]>();
  const branches = new Map<string, string>();
  for (const file of taskFiles) {
    let parsed: Parsed; try { parsed = parseDocument(file); } catch { continue; }
    const task = parsed.metadata;
    const required = ["type", "task", "title", "description", "status", "created", "timestamp"];
    const missing = required.filter((key) => task[key] === undefined || task[key] === "");
    if (missing.length) { errors.push(`${file}: missing required fields: ${missing.join(", ")}`); continue; }
    if (task.type !== "Task") errors.push(`${file}: type must be Task`);
    if (task.task !== path.basename(path.dirname(file)) || !slugPattern.test(String(task.task))) errors.push(`${file}: task slug must match its directory`);
    if (!statusSet.has(String(task.status))) errors.push(`${file}: unknown status`);
    ["created", "timestamp"].forEach((field) => { if (!rfc3339(task[field])) errors.push(`${file}: ${field} must be an RFC 3339 datetime`); });
    ["Outcome", "Scope", "Acceptance", "Evidence"].forEach((name) => { if (!heading(parsed.body, name)) errors.push(`${file}: missing required heading`); });
    if (task.completion_history !== undefined) {
      if (!Array.isArray(task.completion_history)) errors.push(`${file}: completion_history must be a list`);
      else task.completion_history.forEach((event, index) => { if (!mapping(event) || !rfc3339(event.finished) || !rfc3339(event.reopened)) errors.push(`${file}: completion_history[${index}] requires finished and reopened RFC 3339 datetimes`); });
    }
    validateEstimate(file, task, errors); validatePortableFields(file, task, errors); validateSync(file, task, errors); validateTime(file, task, errors);
    const localEdges = new Set<string>();
    let pullSources = 0;
    if (Array.isArray(task.external)) task.external.forEach((item) => {
      if (!mapping(item) || !item.system || !item.host || !item.kind || item.id === undefined) return;
      const key = JSON.stringify([String(item.system), String(item.host), String(item.kind), String(item.id)]);
      if (localEdges.has(key)) errors.push(`${file}: duplicate external relationship`);
      localEdges.add(key);
      const relationship = item.relationship === undefined ? "mirror" : item.relationship;
      if (typeof relationship !== "string" || !["mirror", "reference", "contribution"].includes(relationship)) errors.push(`${file}: unsupported external relationship`);
      if (mapping(item.sync) && item.sync.pull_source !== undefined) {
        if (typeof item.sync.pull_source !== "boolean" || relationship !== "mirror") errors.push(`${file}: pull_source requires a boolean on a mirror`);
        if (item.sync.pull_source === true) pullSources++;
      }
      const group = external.get(key) || [];
      const writers = group.filter((edge) => edge.relationship !== "reference");
      if (relationship !== "reference") {
        if (writers.length && (relationship === "mirror" || writers.some((edge) => edge.relationship === "mirror"))) errors.push(`${file}: competing mirror/contribution writers`);
        if (writers.some((edge) => edge.tracker !== String(item.tracker) || edge.scope !== String(mapping(item.scope) ? item.scope.id : ""))) errors.push(`${file}: inconsistent writer profile or scope`);
      }
      group.push({file, relationship: String(relationship), tracker: String(item.tracker), scope: String(mapping(item.scope) ? item.scope.id : "")});
      external.set(key, group);
      const profile = profiles.get(String(item.tracker));
      if (!profile) errors.push(`${file}: external tracker profile ${String(item.tracker)} does not exist`);
      else {
        if (item.system !== profile.system || item.host !== profile.host) errors.push(`${file}: external binding system and host must match its Tracker Profile`);
        if (mapping(item.scope) && mapping(profile.scope) && item.scope.id !== profile.scope.id) errors.push(`${file}: external binding scope must match its Tracker Profile`);
      }
    });
    if (pullSources > 1) errors.push(`${file}: only one mirror pull_source is permitted`);
    const workstreamDir = path.join(path.dirname(file), "workstreams");
    const workstreamFiles = fs.existsSync(workstreamDir) ? fs.readdirSync(workstreamDir).filter((name) => name.endsWith(".md")).map((name) => path.join(workstreamDir, name)).sort() : [];
    for (const workstreamFile of workstreamFiles) {
      let wsParsed: Parsed; try { wsParsed = parseDocument(workstreamFile); } catch { continue; }
      const ws = wsParsed.metadata;
      const wsRequired = ["type", "task", "workstream", "title", "description", "status", "created", "timestamp"];
      const wsMissing = wsRequired.filter((key) => ws[key] === undefined || ws[key] === "");
      if (wsMissing.length) { errors.push(`${workstreamFile}: missing required fields: ${wsMissing.join(", ")}`); continue; }
      if (ws.task !== task.task) errors.push(`${workstreamFile}: parent task mismatch`);
      if (ws.workstream !== path.basename(workstreamFile, ".md") || !slugPattern.test(String(ws.workstream))) errors.push(`${workstreamFile}: workstream slug must match`);
      if (!statusSet.has(String(ws.status))) errors.push(`${workstreamFile}: unknown status`);
      ["created", "timestamp"].forEach((field) => { if (!rfc3339(ws[field])) errors.push(`${workstreamFile}: ${field} must be RFC 3339`); });
      ["Assigned outcome", "Acceptance and validation", "Evidence", "Handoff"].forEach((name) => { if (!heading(wsParsed.body, name)) errors.push(`${workstreamFile}: missing required heading`); });
      if (ws.branch && !terminal.has(String(ws.status))) { const branch = String(ws.branch); if (branches.has(branch)) errors.push(`${workstreamFile}: active branch also used by ${branches.get(branch)}`); else branches.set(branch, workstreamFile); }
    }
    if (task.status === "done" && workstreamFiles.some((wsFile) => { try { return !terminal.has(String(parseDocument(wsFile).metadata.status)); } catch { return false; } })) errors.push(`${file}: done task has active workstreams`);
  }
  const index = path.join(bundle, "index.md");
  if (!fs.existsSync(index)) errors.push(`${index}: generated index is missing`);
  else if (!fs.readFileSync(index, "utf8").includes("<!-- Generated by okf-task-lifecycle. Do not edit by hand. -->")) errors.push(`${index}: generated index is stale`);
  errors.push(...durableLinkGraphErrors(bundle));
  return errors;
}
