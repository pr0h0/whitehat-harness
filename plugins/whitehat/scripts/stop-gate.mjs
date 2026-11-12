// Stop: if the edit gate left unresolved findings, keep the turn open once so the agent
// fixes them or explains why they are false positives. stop_hook_active prevents a loop.
import { pathToFileURL } from "node:url";
import { emit, loadState, readInput } from "./lib.mjs";

export const decide = (input, state) => {
  if (process.env.WHITEHAT_STOP_GATE === "0" || input.stop_hook_active) return null;
  // only this session's findings: an old, accepted finding must not hold every future turn open
  const files = Object.entries(state.pending ?? {})
    .filter(([, v]) => v.session === input.session_id)
    .map(([f, v]) => [f, v.count, v.errors?.length ?? 0]);
  if (!files.length) return null;
  return {
    decision: "block",
    reason: `whitehat: unresolved security findings in ${files.map(([f, n, e]) => `${f} (${n} finding(s)${e ? `, ${e} failed check(s)` : ""})`).join(", ")}. Restore and rerun failed scanners. Fix findings, or for each one say why it is a false positive, then finish.`,
  };
};

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const input = readInput();
  const d = decide(input, loadState(input));
  if (d) emit(d);
}
