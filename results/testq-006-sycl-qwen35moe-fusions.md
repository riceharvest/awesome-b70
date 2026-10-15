---
title: "B70 test 006"
---
{% raw %}
_Lab notes from our B70 test queue, published as written (2026-10-15). Raw logs are not included. Back to the [performance guide](../performance.md)._

# 006 RESULT: PASS with notes (~6 GPU min)

| arm | tg128 tok/s |
|---|---|
| master | 93.39 ± 0.19 |
| master_recipe (lab runtime settings) | 93.48 ± 0.10 |
| branch, flags off | 93.36 ± 0.05 (= master, port changes nothing when off) |
| **branch, flags on** | **107.92 ± 1.47 (+15.5%)** |

Greedy 128 tokens, master vs branch flags on: code IDENTICAL, prose IDENTICAL.

Hit counts (fused_hits): moe_gate_up 10280, moe_gate_residual_rms 10280, residual_rms_norm 10280, concat_state 7710,
gdn_rms_gate 7710, qk_norm_rope 2570. **Zero hits: moe_shared_residual_rms, concat_state_direct, gdn_state_io** (those
3 matchers don't fit master's qwen35moe graph; the other 7 account for the +15.5%). Lab target 131.5 not reached; their
base is Ornith Q4_K_M, ours UD-Q4_K_M (Q8_0 attention/SSM).
Note: master here is 93.4, not the 97.7 in RUN.md (same binary/flags; difference is run-to-run/thermal, all arms back to back).

{% endraw %}
