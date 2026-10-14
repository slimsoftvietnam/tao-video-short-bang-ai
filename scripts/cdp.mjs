// Own captures of PUBLIC pages, no page assets saved: drives chrome-headless-shell over raw CDP
// (node >= 22, zero dependencies — the same approach as motion-doctrine's seam-gate.mjs).
//
//   shot <url> <out.png> [--w 1920] [--h 1080] [--dpr 1] [--wait 3000] [--js "<expr>"] [--clip "<css selector>"] [--pad 0]
//   eval <url> <out.txt> --expr "<js expression returning a string>" [--wait 3000]
//
// `eval` writes a page value straight to disk (e.g. a logo's inline <svg> outerHTML), so nothing is
// ever transcribed by hand. The browser runs with its own default user agent: no bot-check evasion.
import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync, readdirSync, statSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { join } from "node:path";

// The headless Chrome HyperFrames downloads (~/.cache/hyperframes/chrome/...), or CHROME_PATH.
function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const want = process.platform === "win32" ? "chrome-headless-shell.exe" : "chrome-headless-shell";
  const walk = (dir, depth) => {
    let hits = [];
    let entries = [];
    try { entries = readdirSync(dir); } catch { return hits; }
    for (const e of entries) {
      const p = join(dir, e);
      let st;
      try { st = statSync(p); } catch { continue; }
      if (st.isFile() && e === want) hits.push({ p, t: st.mtimeMs });
      else if (st.isDirectory() && depth > 0) hits = hits.concat(walk(p, depth - 1));
    }
    return hits;
  };
  const hits = walk(join(homedir(), ".cache", "hyperframes", "chrome"), 5).sort((a, b) => b.t - a.t);
  if (!hits.length) throw new Error("no headless Chrome: run any `npx hyperframes snapshot` once, or set CHROME_PATH");
  return hits[0].p;
}
const CHROME = findChrome();
const [mode, url, out, ...rest] = process.argv.slice(2);
const flag = (n, d) => { const i = rest.indexOf("--" + n); return i >= 0 ? rest[i + 1] : d; };

const prof = mkdtempSync(join(tmpdir(), "cdp-"));
const child = spawn(CHROME, ["--remote-debugging-port=0", "--no-first-run", "--hide-scrollbars", "--mute-audio",
  "--user-data-dir=" + prof, "about:blank"], { stdio: ["ignore", "pipe", "pipe"] });
const wsUrl = await new Promise((res, rej) => {
  let buf = "";
  const t = setTimeout(() => rej(new Error("no DevTools endpoint")), 20000);
  child.stderr.on("data", (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) { clearTimeout(t); res(m[1]); } });
});
const ws = new WebSocket(wsUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error("ws")); });
let id = 0; const pend = new Map(); const evs = [];
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } else if (m.method) evs.forEach((f) => f(m)); };
const send = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
const once = (method, sid, ms = 60000) => new Promise((res, rej) => { const t = setTimeout(() => rej(new Error("timeout " + method)), ms); const f = (m) => { if (m.method === method && m.sessionId === sid) { clearTimeout(t); evs.splice(evs.indexOf(f), 1); res(m.params); } }; evs.push(f); });

try {
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId: s } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, s);
  await send("Runtime.enable", {}, s);
  const W = +flag("w", 1920), H = +flag("h", 1080), DPR = +flag("dpr", 1);
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DPR, mobile: false }, s);
  const loaded = once("Page.loadEventFired", s);
  await send("Page.navigate", { url }, s);
  await loaded.catch(() => {});
  await new Promise((r) => setTimeout(r, +flag("wait", 3000)));
  const ev = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, s);
    if (r.exceptionDetails) throw new Error("page: " + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
    return r.result.value;
  };
  if (flag("js")) { await ev(flag("js")); await new Promise((r) => setTimeout(r, 1200)); }
  if (mode === "eval") {
    const v = await ev(flag("expr"));
    writeFileSync(out, String(v), "utf8");
    console.log("wrote", out, String(v).length, "chars");
  } else {
    let clip;
    if (flag("clip")) {
      const pad = +flag("pad", 0);
      const r = await ev(`(() => { const e = document.querySelector(${JSON.stringify(flag("clip"))}); if (!e) return null; e.scrollIntoView({block:"center"}); const b = e.getBoundingClientRect(); return {x:b.left+scrollX, y:b.top+scrollY, w:b.width, h:b.height}; })()`);
      if (!r) throw new Error("clip selector not found");
      await new Promise((r2) => setTimeout(r2, 800));
      clip = { x: Math.max(0, r.x - pad), y: Math.max(0, r.y - pad), width: r.w + 2 * pad, height: r.h + 2 * pad, scale: 1 };
    }
    const { data } = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: !!clip, ...(clip ? { clip } : {}) }, s);
    writeFileSync(out, Buffer.from(data, "base64"));
    console.log("wrote", out);
  }
} catch (e) {
  console.error("ERROR", e.message);
  process.exitCode = 1;
} finally {
  ws.close();
  child.kill();
}
