---
title: "B70 test 002"
---
{% raw %}
_Lab notes from our B70 test queue, published as written (2026-10-15). Raw logs are not included. Back to the [performance guide](../performance.md)._

# 002 result (TRIMMED per user: <=20 GPU min): Mesa 26.2.5 vs 25.3.6, llama.cpp Vulkan, B70, 2026-10-15 — PASS (stack), master tbo NOT RUN

Trim: Mesa 26 only (Mesa 25.3.6 numbers = RUN.md table, measured 2026-10-15 on the same builds), d=0 only, 35B-A3B pp512/tg128
and 27B tg128, r=3; test-backend-ops MUL_MAT + FLASH_ATTN_EXT. Raw: RESULT.txt, results/. Driver line confirms "Mesa 26.2.5".

| model / test | master Mesa 25 | master Mesa 26 | stack Mesa 25 | stack Mesa 26 | SYCL master |
|---|---|---|---|---|---|
| 35B-A3B tg128 d=0 | 39.0 | **86.14 ±0.94** (+121%) | 64.3 | **87.32 ±0.34** (+36%) | 97.7 |
| 35B-A3B pp512 d=0 | 1854 | 1637 ±60 (−12%) | 1931 | 1737 ±25 (−10%) | 1301 |
| 27B tg128 d=0 | 13.2 | **22.85** (+73%) | 22.7 | **25.26 ±0.14** (+11%) | 21.9 |

test-backend-ops on Mesa 26: **stack** MUL_MAT 2279/2279, FLASH_ATTN_EXT 5321/5321 (PASS). **master: not run** — its build dir
has no test-backend-ops binary (the "FAIL=0" lines for master are empty output, not a pass).

Reading:
- Mesa 26 fixes most of master's Vulkan decode problem by itself (35B 39 → 86, 27B 13 → 23). The hub/doctor "use SYCL" advice
  needs a "Mesa >= 26" qualifier: on Mesa 26, Vulkan master 35B-A3B decode is 88% of SYCL (86.1 vs 97.7) and beats SYCL on prefill.
- On top of Mesa 26 the stack still adds +1.4% (35B tg) and **+10.5% (27B tg)**, so the 32-bit-load change is not just a Mesa-25
  workaround for the dense model; on the MoE it mostly washes out.
- Mesa 26 costs ~10–12% pp512 on 35B-A3B for both arms (worth a look before recommending it for prefill-heavy use).
- No xe faults during the run.

{% endraw %}
