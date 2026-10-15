---
title: "B70 test 001"
---
{% raw %}
_Lab notes from our B70 test queue, published as written (2026-10-15). Raw logs are not included. Back to the [performance guide](../performance.md)._

# 001 result: llama.cpp MTP on Qwen3.6-35B-A3B (UD-Q4_K_M), B70, 2026-10-15 — FAIL (SYCL correctness), Vulkan PASS

Raw: RESULT.txt. Server `-ngl 99 -sm none -fa on -c 8192 -np 1`, 3 prompts × 256 tok greedy, 2nd run reported. Peak VRAM 22.82 GB (<= 25 GB OK).

| backend | none | MTP n=1 | MTP n=2 | MTP n=3 |
|---|---|---|---|---|
| SYCL master a0e6dc738 (mean tok/s) | 86.7 | 69.0 | 77.0 | 80.9 |
| Vulkan vk-b70-stack 54b6e8485 (mean tok/s) | 70.7 | 91.3 | 100.8 | **108.5** |

Acceptance (n=3): SYCL code 83% / prose 58% / reason 89%; Vulkan 78% / 62% / 93%. Best single prompt: Vulkan n=3 reasoning 122.3.

Pass/fail:
- **Correctness: SYCL FAIL**: with greedy, every MTP config (n=1/2/3) on all 3 prompts produces text that DIFFERS from the
  no-spec output. Vulkan: all 9 MTP runs IDENTICAL to no-spec (PASS). So the SYCL MTP path changes results; it is also slower
  than no-spec (69–81 vs 86.7), i.e. the SYCL verify/draft path is broken or very inefficient. Worth a bug report after b70-code
  looks at where it diverges (byte offsets not captured by test.sh).
- **Speed target 132.9 tok/s: not reached.** Best is Vulkan + MTP n=3 at 108.5 mean (+53% over Vulkan no-spec), still 18% short.
  SYCL no-spec (86.7) is above Vulkan no-spec (70.7) but SYCL MTP is unusable as is.

{% endraw %}
