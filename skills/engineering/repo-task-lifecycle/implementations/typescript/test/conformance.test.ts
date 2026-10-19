import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { prepareExternalArtifact, statuses, validateBundle } from "../src/validator.js";

const repository = process.cwd();
const manifest = JSON.parse(fs.readFileSync(path.join(repository, "conformance", "manifest.json"), "utf8")) as { cases: Array<{ id: string; path: string; valid: boolean; error?: string }> };

for (const fixture of manifest.cases) {
  test(fixture.id, () => {
    const errors = validateBundle(path.join(repository, "conformance", fixture.path));
    if (fixture.valid) assert.deepEqual(errors, []);
    else {
      assert.ok(errors.length > 0, `${fixture.id} unexpectedly passed`);
      assert.ok(errors.some((error) => error.includes(fixture.error!)), `${fixture.id}: expected ${fixture.error}; got ${errors.join(" | ")}`);
    }
  });
}

test("transition manifest covers every status pair", () => {
  const matrix = JSON.parse(fs.readFileSync(path.join(repository, "conformance", "transitions.json"), "utf8")) as { statuses: string[]; allowed: Record<string, string[]> };
  assert.deepEqual(matrix.statuses, [...statuses]);
  for (const source of statuses) for (const target of statuses) assert.equal(typeof (source === target || matrix.allowed[source].includes(target)), "boolean");
});

const exportManifest = JSON.parse(fs.readFileSync(path.join(repository, "conformance", "export-manifest.json"), "utf8")) as { cases: Array<{ id: string; path: string; source: string; remote: string; provider?: string; ref: string; valid: boolean; contains?: string; excludes?: string; error?: string }> };

for (const fixture of exportManifest.cases) {
  test(fixture.id, () => {
    const root = path.join(repository, "conformance", fixture.path);
    if (fixture.valid) {
      const rendered = prepareExternalArtifact(root, fixture.source, fixture.remote, fixture.ref, fixture.provider);
      assert.ok(rendered.includes(fixture.contains!));
      if (fixture.excludes) assert.ok(!rendered.includes(fixture.excludes));
    } else {
      assert.throws(
        () => prepareExternalArtifact(root, fixture.source, fixture.remote, fixture.ref, fixture.provider),
        (error: unknown) => {
          const message = String((error as Error).message);
          assert.ok(message.includes(fixture.error!), `${fixture.id}: ${message}`);
          if (fixture.excludes) assert.ok(!message.includes(fixture.excludes));
          return true;
        },
      );
    }
  });
}
