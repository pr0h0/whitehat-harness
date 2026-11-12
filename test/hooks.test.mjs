// node --test test/
import assert from "node:assert/strict";
import { test } from "node:test";
import { decide as scopeDecide, inScope, targetsOf } from "../plugins/whitehat/scripts/scope-guard.mjs";
import { decide as stopDecide } from "../plugins/whitehat/scripts/stop-gate.mjs";
import { context } from "../plugins/whitehat/scripts/session-start.mjs";

const scope = { engagement: "t", expires: "2999-01-01", hosts: ["localhost:3000"] };
const bash = (command) => ({ tool_name: "Bash", tool_input: { command } });

test("targets are read from URLs and bare loopback/IP hosts", () => {
  assert.deepEqual(targetsOf("Bash", { command: "curl -s http://localhost:3000/rest/products" }).targets, ["localhost:3000"]);
  assert.deepEqual(targetsOf("Bash", { command: "nmap 10.0.0.5" }).targets, ["10.0.0.5"]);
  assert.equal(targetsOf("Bash", { command: "ls -la" }).network, false);
  assert.deepEqual(targetsOf("WebFetch", { url: "https://example.com/x" }).targets, ["example.com"]);
});

test("loopback names are interchangeable, ports must match when the entry has one", () => {
  assert.ok(inScope("127.0.0.1:3000", ["localhost:3000"]));
  assert.ok(!inScope("localhost:8080", ["localhost:3000"]));
  assert.ok(inScope("localhost:8080", ["localhost"]));
});

test("scope guard: pass in scope, deny out of scope, ask when blind, silent without engagement", () => {
  assert.equal(scopeDecide(bash("curl http://localhost:3000/"), scope), null);
  assert.equal(scopeDecide(bash("curl https://evil.example/"), scope).permissionDecision, "deny");
  assert.equal(scopeDecide(bash("curl $TARGET"), scope).permissionDecision, "ask");
  assert.equal(scopeDecide(bash("curl https://evil.example/"), null), null);
  assert.equal(scopeDecide(bash("npm test"), scope), null);
});

test("scope guard: expired or broken scope denies every network action", () => {
  assert.equal(scopeDecide(bash("curl http://localhost:3000/"), { ...scope, expires: "2000-01-01" }).permissionDecision, "deny");
  assert.equal(scopeDecide(bash("curl http://localhost:3000/"), { invalid: "x" }).permissionDecision, "deny");
});

test("stop gate blocks once while findings are pending", () => {
  const pending = { pending: { "routes/a.ts": { count: 2, session: "s1" } } };
  assert.equal(stopDecide({ session_id: "s1" }, pending).decision, "block");
  assert.equal(stopDecide({ session_id: "s1", stop_hook_active: true }, pending), null);
  assert.equal(stopDecide({ session_id: "s2" }, pending), null);
  assert.equal(stopDecide({}, { pending: {} }), null);
});

test("session context names the scope and flags expiry", () => {
  assert.match(context(scope), /localhost:3000/);
  assert.match(context({ ...scope, expires: "2000-01-01" }), /EXPIRED/);
  assert.equal(context(null), null);
});
