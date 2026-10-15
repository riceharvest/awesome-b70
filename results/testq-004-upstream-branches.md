---
title: "B70 test 004"
---
{% raw %}
_Lab notes from our B70 test queue, published as written (2026-10-15). Raw logs are not included. Back to the [performance guide](../performance.md)._

# 004 result (2026-10-15): xk GEMV branch PASS (kernel), test bug to fix; vLLM online lm_head branch FAIL in serving

GPU used: ~28 min (over the 20 budget: two extra short runs to fix the pytest harness and get the failing assertion).
Setup: vLLM nightly image 3f1bcfd8 (vllm 0.32.0rc1.dev190, vllm-xpu-kernels 0.1.15.4). xk branch commit fad147a applied to
release/0.1.15.4 (applies cleanly), op built as an `_xpu_C` library fragment (no full xk rebuild); vLLM branch a7be137fb files
overlaid (nightly copies are byte-identical to its parent 7020600b1). Model palmfuture/Qwen3.6-35B-A3B-GPTQ-Int4, --language-model-only,
fp8 KV, XPU graphs, util 0.82 (<=25 GB).

## xk moe-int4-decode-gemv
- pytest test_grouped_gemm.py -k "moe_int4_gemv or int4": 46 passed, 6 failed — all 6 are test OOM (n=5120,k=8192,e=256 builds the
  random weights as int64 = ~40 GiB). Fix: `torch.randint(..., dtype=torch.uint8)` or e=16. Kernel itself passes every shape it can fit.
- pytest test_fused_moe.py -k int4: 40 passed.
- E2E no MTP, 4K ctx: GEMV=0 75.8/76.3 tok/s, GEMV=1 86.6/87.2 (+14%); gsm8k first 100: 97/100 both.
- GEMV + MTP4 (2K ctx): 157.3/118.7 tok/s, no xe faults.

## vLLM online-quant-lm-head
- pytest test_online.py -k "targets or lm_head": 9 passed.
- Serving with targets lm_head fp8_per_channel: NOT applied ("Quantizing 0 layers", no XPUW8A16FP8 kernel, memory unchanged,
  speed = GEMV-only). CPU resolve_quant_method on a stub ParallelLMHead does select the online method → serving path differs.
  FAIL; needs a fix in code (b70-code) and a re-test. MTP-with-fp8-head question still open.

PR drafts updated: ~/b70_prep/upstream/xk-moe-int4-gemv-PR.md (Test Result filled), vllm-online-lmhead-PR.md (blocker noted).

{% endraw %}
