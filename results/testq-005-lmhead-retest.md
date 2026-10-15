---
title: "B70 test 005"
---
{% raw %}
_Lab notes from our B70 test queue, published as written (2026-10-15). Raw logs are not included. Back to the [performance guide](../performance.md)._

# 005 RESULT: PASS (~9 GPU min)

All pass lines present in RESULT.txt: guard imports branch from site-packages, `Quantizing 1 layers ... lm_head`,
`Selected XPUW8A16FP8LinearKernel for Fp8PerChannelWeightOnlyOnlineLinearMethod`, probe shows lm_head
`torch.float8_e4m3fn (2048, 248320)`. No xe fault lines in the kernel log.

| arm | 004 | 005 | delta |
|---|---|---|---|
| B: GEMV, 4K, decode code/prose tok/s | 86.6 / 87.2 | **89.4 / 90.2** | +3.2% / +3.4% |
| B: gsm8k 100 | 97/100 | **96/100** | -1 (>= 95 bar, within noise) |
| B: model loading | 20.18 GiB | **19.71 GiB** | -0.47 GiB (bf16 head freed) |
| C: GEMV + MTP k=4, 2K, decode | 157.3 / 118.7 | **183.7 / 131.9** | +16.8% / +11.1% |
| C: model loading | – | 21.75 GiB | MTP drafter's own lm_head also quantized ("Quantizing 2 layers") |

Note: C gains more than the head alone suggests; the drafter runs the lm_head every draft step, so its fp8 head counts k+1 times per step.

{% endraw %}
