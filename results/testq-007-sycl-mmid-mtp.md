---
title: "B70 test 007"
---
{% raw %}
_Lab notes from our B70 test queue, published as written (2026-10-15). Raw logs are not included. Back to the [performance guide](../performance.md)._

# 007 RESULT: speed PASS (MTP now +57%), correctness OPEN (~8 GPU min)

**Speed (mean of code/prose/reason, 256 tok greedy):** branch_none 83.9, **branch_mtp3 131.8 tok/s (+57%)**
(001: SYCL mtp3 80.9 < none 86.7). Per prompt mtp3: code 135.4 (accept 182/219), prose 110.8 (161/279), reason 149.3 (186/204).
noesimd: none 85.4, mtp3 121.7.

**Determinism / identity:**
- master_none_1 vs master_none_2: IDENTICAL on all 3 → SYCL is deterministic across processes; 001's FAIL was real.
- master_none_1 vs branch_none: **DIFFERS** on code (char 340) and prose (char 261), reason identical. Unexpected: the
  change should only touch 2-8 token batches. Likely the prompt's last ubatch or a 2-8 token tail goes through the new path.
- branch_none vs branch_mtp3: DIFFERS code (241) / prose (525), reason IDENTICAL. Same pattern with ESIMD off
  (code 241 / prose 261), so the dense ESIMD-vs-MMVQ split is not the (only) cause.

**test-backend-ops MUL_MAT_ID: ABORTED (core dump) after 34 cases.** The "FAIL=0" line in RESULT.txt is misleading. Crash:
oneDNN `found misaligned buffer` → ggml_sycl_error in `ggml_sycl_op_mul_mat<no_quantize_q8_1>` ← ggml_sycl_mul_mat ←
ggml_sycl_mul_mat_id, right after `MUL_MAT_ID(type_a=f32,type_b=f32,n_mats=4,n_used=2,...,m_v=64)` passed. That is the f32
(non-quantized, oneDNN) path, probably not the new MMVQ code, but master's test-backend-ops was never built
(/mnt/ssd/b70-code/llama.cpp-sycl-master has no test-backend-ops), so it is not proven pre-existing. Needs: master
test-backend-ops MUL_MAT_ID on the same box (queue it with a build target) before any PR.

{% endraw %}
