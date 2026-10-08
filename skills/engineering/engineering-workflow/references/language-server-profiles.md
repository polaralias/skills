# Trusted language-server profiles

Configure servers explicitly at host scope in `~/.config/rke/language-servers.json`. The host process may set `RKE_LANGUAGE_SERVER_PROFILES` to an absolute configuration file. This is a host deployment setting, not an operation argument. Configuration and resolved implementation inputs must be outside the target repository. Repository-local configuration and symlinks into it are refused.

```json
{
  "schemaVersion": 1,
  "profiles": {
    "typescript": {
      "command": "/absolute/path/to/node",
      "args": ["/absolute/path/to/typescript-language-server/lib/cli.mjs", "--stdio"],
      "language": "typescript",
      "implementationInputs": [
        "/absolute/path/to/typescript-language-server/lib/cli.mjs",
        "/absolute/path/to/typescript-language-server/package.json",
        "/absolute/path/to/typescript/lib/tsserver.js",
        "/absolute/path/to/typescript/package.json"
      ]
    }
  }
}
```

Use platform-correct absolute paths; for Windows JSON escape backslashes or use forward slashes. The example is a format illustration, not an installed default. An administrator chooses and reviews the executable, arguments and implementation inputs. Never configure an interpreter with repository-supplied scripts or commands. Include the launcher, server implementation and compiler/dependency version files that identify the selected installation; omitted dependencies and environment inputs are outside the receipt's guarantee. Language servers retain their own plugin/configuration execution behavior, so authorize the selected installation for the repository being opened.

`rke structure resolve src/service.ts --server-profile typescript` accepts only the configured ID. CLI and MCP cannot override executable, arguments, language or configuration location. No runtime operation writes profiles, downloads a server or runs a version command. Unknown or malformed profiles fail before launch.

Receipts bind profile ID, argv, language, resolved executable bytes and declared implementation-input bytes, alongside source/target and workspace digests. Missing, replaced or upgraded declared inputs withhold old evidence; rerun resolution. Old receipt schemas are discarded. Warm implementation hashes reuse process-local stat identities; configuration is read again on every assessment. These receipts are server-reported navigation evidence, not runtime truth.
