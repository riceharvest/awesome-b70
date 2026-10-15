#!/usr/bin/env python3
"""Build leaderboard.md from localmaxxing.com Arc Pro B70 runs (public API, user-submitted data).

Usage: python3 scripts/leaderboard.py [out.md]
Stdlib only, so the scheduled GitHub Action needs no installs.
"""
import datetime
import html
import json
import re
import sys
import urllib.parse
import urllib.request

API = "https://www.localmaxxing.com/api/speed-tests"
GPU = "Intel Arc Pro B70"
SITE = "https://www.localmaxxing.com/en/runs/"
UA = "awesome-b70-leaderboard (+https://github.com/riceharvest/awesome-b70)"


def fetch_all():
    rows, offset = [], 0
    while True:
        q = urllib.parse.urlencode({"gpuName": GPU, "limit": 100, "offset": offset})
        req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            page = json.load(r)
        batch = page.get("speedTests", [])
        rows += batch
        offset += len(batch)
        if not batch or offset >= page.get("total", 0):
            return rows


def safe(s):
    # user-submitted text: no raw HTML, no Liquid on GitHub Pages
    s = html.escape(str(s or ""), quote=False)
    return re.sub(r"\{[{%]|[%}]\}|endraw", "", s, flags=re.I)


def cell(s, n=None):
    s = re.sub(r"\s+", " ", safe(s)).strip().replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
    return s if n is None or len(s) <= n else s[: n - 1] + "…"


def flags(r):
    return r.get("engineFlags") or {}


def single_stream(r):
    f = flags(r)
    return (r.get("batchSize") in (None, 1)) and (f.get("concurrency") in (None, 1)) and (f.get("numParallel") in (None, 1))


def spec(r):
    f = flags(r)
    if f.get("mtpEnabled"):
        return "MTP"
    if f.get("specDecoding"):
        return cell(f.get("specMethod") or "spec", 14)
    # metadata often says "off" while the command line turns it on
    cmd = f.get("commandSnippet") or ""
    if re.search(r'"method"\s*:\s*"mtp"|draft-mtp|--mtp\b', cmd, re.I):
        return "MTP (cmd)"
    if re.search(r"--speculative|--spec-type|--model-draft|-md\s|--draft", cmd):
        return "spec (cmd)"
    return ""


def repro_link(r):
    extra = flags(r).get("extraFlags")
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except ValueError:
            extra = {}
    if isinstance(extra, dict):
        for k in ("githubResultPacket", "repro", "reproUrl"):
            if isinstance(extra.get(k), str) and extra[k].startswith("http"):
                return extra[k]
    m = re.search(r"https?://[^\s)\]>,;\"']+", r.get("notes") or "")
    return m.group(0).rstrip(".") if m else ""


def engine(r):
    e = r.get("engine") or {}
    v = e.get("engineVersion") or ""
    return cell(f"{e.get('engineName') or '?'} {v}", 38)


def best_per_setup(rows):
    best = {}
    for r in rows:
        if not r.get("tokSOut"):
            continue
        e = r.get("engine") or {}
        key = ((r.get("model") or {}).get("hfId"), e.get("engineName"), e.get("quantization"), spec(r))
        if key not in best or r["tokSOut"] > best[key]["tokSOut"]:
            best[key] = r
    return sorted(best.values(), key=lambda r: -r["tokSOut"])


def table(rows, n):
    out = ["| # | decode tok/s | model | quant | engine | spec | ctx | prefill tok/s | date | run | repro |",
           "|---:|---:|---|---|---|---|---:|---:|---|---|---|"]
    for i, r in enumerate(rows[:n], 1):
        hf = (r.get("model") or {}).get("hfId") or "?"
        model = (f"[{cell(hf.split('/')[-1], 40)}](https://huggingface.co/{urllib.parse.quote(hf, safe='/')})"
                 if re.fullmatch(r"[\w.-]+/[\w.-]+", hf) else cell(hf, 40))
        pre = f"{r['tokSPrefill']:.0f}" if r.get("tokSPrefill") else ""
        rl = repro_link(r)
        out.append(
            f"| {i} | **{r['tokSOut']:.1f}** | {model} | {cell((r.get('engine') or {}).get('quantization'), 18)} "
            f"| {engine(r)} | {spec(r)} | {cell(r.get('contextLength'))} | {pre} | {cell((r.get('createdAt') or '')[:10])} "
            f"| [run]({SITE}{urllib.parse.quote(str(r['id']))}) | {f'[repro]({rl})' if rl else ''} |")
    return out


def details(rows, n):
    out = []
    for i, r in enumerate(rows[:n], 1):
        f = flags(r)
        hf = (r.get("model") or {}).get("hfId") or "?"
        out.append(f"### {i}. {r['tokSOut']:.1f} tok/s: {cell(hf, 60)} on {engine(r)}")
        out.append("")
        rl = repro_link(r)
        if rl:
            out.append(f"Repro: <{html.escape(rl)}>")
            out.append("")
        if f.get("commandSnippet"):
            snippet = re.sub(r"\{[{%]|[%}]\}|endraw", "", (f["commandSnippet"] or "").replace("`", "'"), flags=re.I)
            out += ["```bash", snippet.strip()[:1500], "```", ""]
        if r.get("notes"):
            out += [f"> {cell(r['notes'], 600)}", ""]
    return out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "leaderboard.md"
    rows = [r for r in fetch_all() if r.get("status") == "APPROVED"]
    one = best_per_setup([r for r in rows if single_stream(r) and (r.get("hardware") or {}).get("gpuCount") == 1])
    multi = best_per_setup([r for r in rows if single_stream(r) and (r.get("hardware") or {}).get("gpuCount", 1) > 1])
    batched = best_per_setup([r for r in rows if not single_stream(r)])
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    md = ["---", "title: B70 leaderboard", "---", "{% raw %}",
          "# Arc Pro B70 leaderboard", "",
          f"Fastest submitted runs on the Intel Arc Pro B70, from [localmaxxing.com](https://www.localmaxxing.com) "
          f"({len(rows)} approved B70 runs, updated {today} by a daily GitHub Action). Results are **submitted by "
          f"users** and mostly not independently verified. Engines measure decode differently (llama-bench tg128, "
          f"server inter-token medians, vLLM benchmarks), so compare within an engine. Best run per model, engine, "
          f"quant and speculative-decoding setting.", "",
          "[Back to the hub](./) · [Prebuilt llama.cpp for the B70](https://github.com/riceharvest/b70-llama-builds)", "",
          "## How to reproduce the top runs", "",
          "- **llama.cpp SYCL with fused kernels** (about 131 tok/s on a 35B-A3B MoE, one card, no speculative "
          "decoding): [steveseguin/b70-optimization-lab](https://github.com/steveseguin/b70-optimization-lab) "
          "publishes the exact patch, build, model hash and commands for each run "
          "([Ornith 1.5 35B-A3B packet](https://github.com/steveseguin/b70-optimization-lab/tree/main/repro/ornith-15-35b-a3b-q4km-b70)). "
          "The patch is public domain, default off, and enabled with `GGML_SYCL_FUSED_*` environment flags.",
          "- **vLLM on XPU with GPTQ int4 + MTP**: [SergiioB's B70 cookbook](https://github.com/SergiioB/intel-arc-pro-b70-inference-cookbook) "
          "(container, patches, launch flags).",
          "- **Plain llama.cpp**: start from [b70-llama-builds](https://github.com/riceharvest/b70-llama-builds) "
          "(SYCL AOT for the B70, no oneAPI install) and copy the flags from the run details below.",
          "- Check your setup first with [b70-doctor](https://github.com/riceharvest/b70-doctor): driver, Mesa, "
          "oneAPI and PCIe link problems cost more speed than any flag.", "",
          "## Single stream, one B70", ""]
    md += table(one, 30) + ["", "## Single stream, multiple B70s", ""]
    md += table(multi, 10) + ["", "## Batched / concurrent throughput (aggregate tok/s)", ""]
    md += table(batched, 10) + ["", "## Top single-card runs in detail", ""]
    md += details(one, 5)
    md += ["---", "", "Data: localmaxxing.com public API (`/api/speed-tests?gpuName=Intel Arc Pro B70`), user-submitted, "
           "provided as is. Generator: [`scripts/leaderboard.py`](scripts/leaderboard.py).", "{% endraw %}", ""]
    with open(out_path, "w") as fh:
        fh.write("\n".join(md))
    print(f"{out_path}: {len(rows)} runs, {len(one)} single-card setups, {len(multi)} multi-card, {len(batched)} batched")


if __name__ == "__main__":
    main()
