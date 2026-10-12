#!/usr/bin/env node
// Local release-build benchmark. Requires Playwright; never drives a user session.
const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const zlib = require("node:zlib");
const [buildDir, outputDir, repeats = "3"] = process.argv.slice(2);
if (!buildDir || !outputDir)
  throw new Error(
    "Usage: node tool/profile_mobile_scroll.cjs BUILD OUTPUT [REPEATS]",
  );
fs.mkdirSync(outputDir, { recursive: true });
const mime = {
  ".js": "text/javascript",
  ".wasm": "application/wasm",
  ".json": "application/json",
  ".html": "text/html",
  ".css": "text/css",
  ".woff2": "font/woff2",
};
const server = http.createServer((req, res) => {
  const requested = decodeURIComponent(
    new URL(req.url, "http://localhost").pathname,
  );
  const file = path.resolve(
    buildDir,
    "." + (requested.endsWith("/") ? requested + "index.html" : requested),
  );
  if (
    !file.startsWith(path.resolve(buildDir) + path.sep) ||
    !fs.existsSync(file)
  ) {
    res.writeHead(404);
    res.end();
    return;
  }
  res.setHeader(
    "Content-Type",
    mime[path.extname(file)] || "application/octet-stream",
  );
  fs.createReadStream(file).pipe(res);
});
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const percentile = (items, q) =>
  items.length
    ? [...items].sort((a, b) => a - b)[
        Math.min(items.length - 1, Math.floor(items.length * q))
      ]
    : 0;

(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({
    headless: true,
    args: ["--enable-unsafe-swiftshader"],
  });
  const reports = [];
  const system = await (
    await browser.newBrowserCDPSession()
  ).send("SystemInfo.getInfo");
  try {
    for (const state of (
      process.env.SCROLL_STATES || "empty,filled,invalid,reverse"
    ).split(",")) {
      for (let round = 0; round < Number(repeats); round++) {
        const context = await browser.newContext({
          viewport: { width: 390, height: 844 },
          deviceScaleFactor: 1,
          isMobile: true,
          hasTouch: true,
          userAgent:
            process.env.SCROLL_PLATFORM === "ios"
              ? "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
              : "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36",
        });
        await context.route("https://cloud.umami.is/**", (route) =>
          route.abort(),
        );
        const page = await context.newPage();
        const pageErrors = [];
        page.on("pageerror", (error) => pageErrors.push(error.message));
        await page.addInitScript((standalone) => {
          if (standalone)
            Object.defineProperty(navigator, "standalone", { get: () => true });
          window.probeLifecycle = {
            subscriptions: 0,
            unsubscriptions: 0,
            events: [],
          };
          for (const [name, counter] of [
            ["infusionCalcPwaSubscribe", "subscriptions"],
            ["infusionCalcPwaUnsubscribe", "unsubscriptions"],
          ]) {
            let fn;
            Object.defineProperty(window, name, {
              configurable: true,
              get: () => fn,
              set: (value) => {
                fn = (...args) => {
                  window.probeLifecycle[counter]++;
                  window.probeLifecycle.events.push({
                    counter,
                    t: performance.now(),
                  });
                  return value(...args);
                };
              },
            });
          }
        }, process.env.SCROLL_STANDALONE === "1");
        console.log(`Starting ${state} ${round}`);
        await page.goto(origin);
        await page.waitForFunction(
          () =>
            window.infusionProbeRead &&
            JSON.parse(window.infusionProbeRead()).pixels !== null,
          null,
          { timeout: 30000 },
        );
        await page.waitForFunction(
          () => document.documentElement.dataset.offlineReady === "true",
          null,
          { timeout: 30000 },
        );
        await page.waitForTimeout(1200);
        async function edit(key, value) {
          for (let offset = 0; offset < 3500; offset += 250) {
            await page.evaluate(
              (offset) => window.infusionProbeJump(offset),
              offset,
            );
            await page.waitForTimeout(70);
            if (
              await page.evaluate(
                ([key, value]) => window.infusionProbeEdit(key, value),
                [key, value],
              )
            ) {
              await page.waitForTimeout(150);
              return;
            }
          }
          throw new Error(`Field not mounted: ${key}`);
        }
        if (state !== "empty") {
          for (const [key, value] of [
            ["bodyMass", "70"],
            ["drugAmount", "4"],
            ["solutionVolume", "50"],
            ["flowRate", "5"],
          ])
            await edit("value-" + key, value);
          if (state === "invalid") await edit("value-bodyMass", "bad");
          if (state === "reverse") await edit("value-concentration", "100");
        }
        await page.evaluate(() => {
          window.infusionProbeBlur();
          window.infusionProbeJump(0);
        });
        await page.waitForTimeout(500);
        const cdp = await context.newCDPSession(page);
        await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
        const trace = [];
        if (round === 0 && process.env.PROFILE_TRACE === "1") {
          cdp.on("Tracing.dataCollected", (e) => trace.push(...e.value));
          await cdp.send("Tracing.start", {
            categories:
              "devtools.timeline,blink.user_timing,v8,disabled-by-default-devtools.timeline,disabled-by-default-v8.cpu_profiler",
            transferMode: "ReportEvents",
          });
        }
        await page.evaluate(() => {
          window.probeRun = {
            samples: [],
            tasks: [],
            events: [],
            gestures: [],
            lifecycleStart: { ...window.probeLifecycle },
            active: true,
          };
          const run = window.probeRun;
          run.observer = new PerformanceObserver((list) =>
            run.tasks.push(
              ...list
                .getEntries()
                .map((e) => ({ start: e.startTime, duration: e.duration })),
            ),
          );
          run.observer.observe({ type: "longtask" });
          for (const type of [
            "pointerdown",
            "pointermove",
            "pointerup",
            "pointercancel",
            "resize",
          ])
            window.addEventListener(
              type,
              (e) => {
                if (run.active)
                  run.events.push({
                    type,
                    t: performance.now(),
                    stamp: e.timeStamp,
                    y: e.clientY,
                  });
              },
              { passive: true },
            );
          const tick = (t) => {
            if (!run.active) return;
            run.samples.push({ t, ...JSON.parse(window.infusionProbeRead()) });
            requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        });
        for (const direction of [1, 1, 1, -1, -1, -1]) {
          const start = direction === 1 ? 700 : 220;
          await page.evaluate(
            (direction) =>
              window.probeRun.gestures.push({
                direction,
                start: performance.now(),
              }),
            direction,
          );
          await cdp.send("Input.dispatchTouchEvent", {
            type: "touchStart",
            touchPoints: [{ x: 195, y: start, radiusX: 4, radiusY: 4 }],
          });
          for (let step = 1; step <= 30; step++) {
            await sleep(16);
            await cdp.send("Input.dispatchTouchEvent", {
              type: "touchMove",
              touchPoints: [
                {
                  x: 195,
                  y: start - direction * step * 16,
                  radiusX: 4,
                  radiusY: 4,
                },
              ],
            });
          }
          await sleep(100);
          await page.evaluate(
            () => (window.probeRun.gestures.at(-1).end = performance.now()),
          );
          await cdp.send("Input.dispatchTouchEvent", {
            type: "touchEnd",
            touchPoints: [],
          });
          await sleep(180);
        }
        const data = await page.evaluate(() => {
          const r = window.probeRun;
          r.active = false;
          r.observer.disconnect();
          const { observer, ...data } = r;
          return { ...data, lifecycleEnd: { ...window.probeLifecycle } };
        });
        if (round === 0 && process.env.PROFILE_TRACE === "1") {
          const done = new Promise((resolve) =>
            cdp.once("Tracing.tracingComplete", resolve),
          );
          await cdp.send("Tracing.end");
          await done;
          fs.writeFileSync(
            path.join(outputDir, `${state}-trace.json.gz`),
            zlib.gzipSync(JSON.stringify({ traceEvents: trace })),
          );
          await page.screenshot({ path: path.join(outputDir, `${state}.png`) });
        }
        const intervals = data.samples
          .slice(1)
          .map((s, i) => s.t - data.samples[i].t);
        if (
          intervals.length < 30 ||
          new Set(data.samples.map((sample) => sample.pixels)).size < 10 ||
          pageErrors.length
        ) {
          throw new Error(`Invalid benchmark run: ${JSON.stringify(pageErrors)}`);
        }
        let reverseSteps = 0,
          extentChanges = 0,
          maxStep = 0,
          unexplainedJumps = 0;
        const reaction = [];
        for (let i = 1; i < data.samples.length; i++) {
          const s = data.samples[i],
            p = data.samples[i - 1];
          if (Math.abs(s.max - p.max) > 1) extentChanges++;
          const g = data.gestures.find(
            (g) => s.t > g.start + 80 && s.t < g.end - 100,
          );
          if (g && s.pixels > 0 && s.pixels < s.max) {
            const d = (s.pixels - p.pixels) * g.direction;
            if (d < -2) reverseSteps++;
            maxStep = Math.max(maxStep, Math.abs(d));
            const moves = data.events.filter(
              (e) => e.type === "pointermove" && e.t <= s.t,
            );
            const previousMoves = data.events.filter(
              (e) => e.type === "pointermove" && e.t <= p.t,
            );
            const inputDelta = Math.abs(
              (moves.at(-1)?.y ?? 0) - (previousMoves.at(-1)?.y ?? 0),
            );
            if (Math.abs(d) > inputDelta + 40) unexplainedJumps++;
          }
        }
        for (const g of data.gestures) {
          const initial = data.samples.find((s) => s.t >= g.start);
          const changed = data.samples.find(
            (s) =>
              s.t > g.start &&
              s.t < g.end &&
              initial &&
              Math.abs(s.pixels - initial.pixels) > 1,
          );
          if (changed) reaction.push(changed.t - g.start);
        }
        const summary = {
          state,
          round,
          frames: intervals.length,
          frameP50: percentile(intervals, 0.5),
          frameP95: percentile(intervals, 0.95),
          frameP99: percentile(intervals, 0.99),
          frameMax: Math.max(...intervals),
          over25: intervals.filter((t) => t > 25).length,
          longTasks: data.tasks.length,
          longTaskTotal: data.tasks.reduce((s, x) => s + x.duration, 0),
          reverseSteps,
          extentChanges,
          unexplainedJumps,
          maxDragFrameStep: maxStep,
          reactionP50: percentile(reaction, 0.5),
          reactionP95: percentile(reaction, 0.95),
          bannerRemounts:
            data.lifecycleEnd.subscriptions - data.lifecycleStart.subscriptions,
        };
        reports.push(summary);
        fs.writeFileSync(
          path.join(outputDir, `${state}-${round}.json`),
          JSON.stringify({ summary, ...data }),
        );
        console.log(JSON.stringify(summary));
        await context.close();
      }
    }
    fs.writeFileSync(
      path.join(outputDir, "summary.json"),
      JSON.stringify(
        {
          browser: await browser.version(),
          gpu: system.gpu.auxAttributes?.glRenderer,
          platform: process.env.SCROLL_PLATFORM || "android",
          simulatedStandalone: process.env.SCROLL_STANDALONE === "1",
          viewport: "390x844",
          dpr: 1,
          cpuSlowdown: 4,
          host: "Linux headless Chromium; mobile emulation, not a physical device",
          reports,
        },
        null,
        2,
      ),
    );
  } finally {
    await browser.close();
    server.close();
  }
})().catch((error) => {
  console.error(error);
  server.close();
  process.exitCode = 1;
});
