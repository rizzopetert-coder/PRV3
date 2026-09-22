// tools/sleuth/crawler/crawl.mjs
//
// BFS crawler for sleuth (tools/sleuth/cli.py orchestrates this as a
// subprocess). Node + Playwright, not Python, because the project's only
// installed Playwright is the Node one already in web/node_modules
// (playwright ^1.62.1, Chromium binaries already downloaded) -- reusing
// it avoids a redundant ~300MB Python-side Chromium install for a tool
// whose actual browser-automation need is identical either way. Run
// this script with `cwd` set to web/ (cli.py does this) so Node's own
// module resolution finds web/node_modules/playwright and
// web/node_modules/axe-core without any new install step.
//
// Invocation (always via cli.py, not run directly in normal use):
//   node crawl.mjs <job-spec-path> <output-path>
// job-spec JSON shape: { baseUrl, theme, extraHeaders, userAgent,
//   concurrency, maxPages, perPageTimeoutMs }

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Node's ESM `import` resolves bare specifiers by walking up from THIS
// file's own directory (tools/sleuth/crawler/), never finding
// web/node_modules that way. `createRequire`, anchored explicitly at a
// path inside web/, resolves the same way `require()` would if this file
// lived there -- the standard pattern for borrowing a sibling project's
// already-installed node_modules without a new install or a symlink.
const WEB_DIR = path.resolve(__dirname, "..", "..", "..", "web");
const requireFromWeb = createRequire(path.join(WEB_DIR, "package.json"));
const { chromium } = requireFromWeb("playwright");

const [, , jobSpecPath, outputPath] = process.argv;
if (!jobSpecPath || !outputPath) {
  console.error("usage: node crawl.mjs <job-spec-path> <output-path>");
  process.exit(2);
}

const job = JSON.parse(fs.readFileSync(jobSpecPath, "utf-8"));
const {
  baseUrl,
  theme,
  extraHeaders = {},
  userAgent = "SleuthBot/1.0",
  concurrency = 3,
  maxPages = 400,
  perPageTimeoutMs = 20000,
} = job;

// axe-core's minified bundle, read once, injected fresh into every page.
// Resolved via the same web-anchored `require`, not a cwd-relative path --
// works regardless of what directory this script happens to be invoked
// from.
const AXE_SOURCE = fs.readFileSync(
  requireFromWeb.resolve("axe-core/axe.min.js"),
  "utf-8"
);

const origin = new URL(baseUrl).origin;

function normalizeUrl(href, base) {
  try {
    const u = new URL(href, base);
    if (u.origin !== origin) return null;
    u.hash = "";
    // Trailing slash normalization: keep root "/" as-is, strip trailing
    // slash elsewhere, matching Next.js's own route-manifest path shape
    // (no trailing slash) so orphan-diffing against prerender-manifest.json
    // compares like-for-like.
    if (u.pathname.length > 1 && u.pathname.endsWith("/")) {
      u.pathname = u.pathname.slice(0, -1);
    }
    return u.toString();
  } catch {
    return null;
  }
}

function isCrawlableScheme(href) {
  return !/^(mailto:|tel:|javascript:|#)/i.test(href.trim());
}

const visited = new Map(); // normalizedUrl -> page result
const queue = [normalizeUrl(baseUrl, baseUrl)];
const queued = new Set(queue);
const linkGraph = []; // { from, to, text }

async function extractPage(context, url) {
  const page = await context.newPage();
  const redirectChain = [];
  let finalStatus = null;
  let navError = null;

  let response;
  try {
    response = await page.goto(url, {
      waitUntil: "networkidle",
      timeout: perPageTimeoutMs,
    });
  } catch (err) {
    navError = String(err && err.message ? err.message : err);
  }

  if (response) {
    finalStatus = response.status();
    // Walk the redirect chain Playwright tracked for this navigation.
    let req = response.request();
    const chain = [];
    while (req.redirectedFrom()) {
      req = req.redirectedFrom();
      chain.unshift(req.url());
    }
    redirectChain.push(...chain);
  }

  let textContent = "";
  let links = [];
  let computedStyles = [];
  let axeViolations = [];

  if (!navError) {
    try {
      textContent = await page.evaluate(() => document.body?.innerText || "");
    } catch {
      /* page may have navigated away or errored post-load; leave empty */
    }

    try {
      links = await page.evaluate(() => {
        return Array.from(document.querySelectorAll("a[href]")).map((a) => ({
          href: a.getAttribute("href") || "",
          text: (a.textContent || "").trim().slice(0, 200),
        }));
      });
    } catch {
      links = [];
    }

    try {
      // Sample real text-bearing elements only (not every DOM node) --
      // avoids false Geist-fallback hits on containers with no explicit
      // font-ui/font-display/font-mono class (see tools/sleuth/tokens.py's
      // docstring for why that fallback is expected and accepted).
      // Raw getComputedStyle() values (rgb()/rgba() strings) are returned
      // as-is; normalization against the locked-token allowlist happens
      // Python-side (tokens.py), keeping this evaluate() block dependency-
      // free and its output easy to eyeball directly in sleuth_raw.json.
      computedStyles = await page.evaluate(() => {
        const selector = "h1, h2, h3, h4, p, a, span, li, button, label";
        const seen = [];
        const nodes = Array.from(document.querySelectorAll(selector)).slice(0, 400);
        for (const el of nodes) {
          const text = (el.textContent || "").trim();
          if (!text) continue;
          const cs = getComputedStyle(el);
          const anchor = el.closest("a[href]");
          seen.push({
            tag: el.tagName.toLowerCase(),
            textSample: text.slice(0, 80),
            fontFamily: cs.fontFamily,
            color: cs.color,
            backgroundColor: cs.backgroundColor,
            className: el.className && typeof el.className === "string" ? el.className : "",
            enclosingHref: anchor ? anchor.getAttribute("href") : null,
          });
        }
        return seen;
      });
    } catch {
      computedStyles = [];
    }

    try {
      await page.addScriptTag({ content: AXE_SOURCE });
      axeViolations = await page.evaluate(async () => {
        const result = await window.axe.run(document, {
          runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "cat.color", "cat.aria"] },
        });
        return result.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          description: v.description,
          help: v.help,
          nodes: v.nodes.length,
          targets: v.nodes.slice(0, 5).map((n) => n.target),
        }));
      });
    } catch (err) {
      axeViolations = [{ id: "sleuth-axe-error", impact: "unknown", description: String(err), help: "", nodes: 0, targets: [] }];
    }
  }

  await page.close();

  return {
    url,
    theme,
    status: finalStatus,
    navError,
    redirectChain,
    textContent,
    links,
    computedStyles,
    axeViolations,
  };
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent,
    extraHTTPHeaders: extraHeaders,
  });

  // Force the requested theme on every page in this context. The site
  // persists theme choice in localStorage ("prv3-theme", see
  // web/components/ThemeSwitcher.tsx) and an inline head script reads it
  // before hydration to set `data-theme` on <html> without a flash of the
  // wrong theme -- addInitScript runs before that inline script on every
  // navigation in this context, so seeding localStorage here is the same
  // mechanism a real returning visitor's persisted preference would use,
  // not a synthetic override. Without this, every crawl would silently
  // render Warm (the default) regardless of --theme, and the brand-color
  // check would be validating the wrong theme's pages.
  await context.addInitScript((themeValue) => {
    try {
      window.localStorage.setItem("prv3-theme", themeValue);
    } catch {
      /* localStorage unavailable (e.g. blocked); page falls back to warm,
         same as a real visitor with storage disabled would. */
    }
  }, theme);

  let activeWorkers = 0;
  const results = [];

  async function worker() {
    while (queue.length > 0 && visited.size < maxPages) {
      const url = queue.shift();
      if (!url || visited.has(url)) continue;
      visited.set(url, null); // reserve slot to avoid double-processing across workers
      const pageResult = await extractPage(context, url);
      visited.set(url, pageResult);
      results.push(pageResult);

      if (!pageResult.navError) {
        for (const link of pageResult.links) {
          if (!isCrawlableScheme(link.href)) continue;
          const normalized = normalizeUrl(link.href, url);
          linkGraph.push({ from: url, to: link.href, normalizedTo: normalized, text: link.text });
          if (normalized && !visited.has(normalized) && !queued.has(normalized) && visited.size + queue.length < maxPages) {
            queued.add(normalized);
            queue.push(normalized);
          }
        }
      }
    }
  }

  const workers = Array.from({ length: concurrency }, () => worker());
  await Promise.all(workers);

  await browser.close();

  const output = {
    baseUrl,
    theme,
    startedAt: job._startedAt || null,
    finishedAt: new Date().toISOString(),
    pageCount: results.length,
    pages: results,
    linkGraph,
  };

  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), "utf-8");
  console.log(`[crawl.mjs] wrote ${results.length} pages to ${outputPath}`);
}

main().catch((err) => {
  console.error("[crawl.mjs] fatal error:", err);
  process.exit(1);
});
