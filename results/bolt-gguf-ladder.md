---
title: Nemotron 3.5 Bolt 74B-A9B GGUF ladder (from BF16) - quality and memory
---
# Nemotron-3.5-Bolt-74B-A9B GGUF ladder (3- to 8-bit, from the BF16 weights)

Files: [darioooooo0o/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-GGUF](https://huggingface.co/darioooooo0o/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-GGUF).
On the Hub now: **Q4_K_M** (45.0 GiB, 2 parts) and the vision projector (mmproj Q8_0 / BF16). Coming, each after its
quality check: IQ3_XXS, Q3_K_M, IQ4_XS, Q5_K_M, Q6_K, Q8_0.

Measured 2026-10-15. **B70 speed: pending** (only NVIDIA's 24 GB file has B70 numbers so far, in
[bolt-24gb-b70.md](bolt-24gb-b70.md)).

## Quality

`llama-perplexity` on wikitext-2 *test*, 16 windows of 2048 tokens (32,768 tokens). KL divergence and same top-1 token
are against our Q8_0, because the BF16 model (138 GiB) does not fit the test machine; Q8_0 is normally within noise of BF16.

| file | size GiB | PPL | KL vs Q8_0 (mean) | KL 99th pct | same top-1 token |
|---|---|---|---|---|---|
| Q8_0 (reference, upload coming) | 73.4 | 4.541 | reference | | |
| **Q4_K_M** (imatrix, on the Hub) | 45.0 | **4.563 ± 0.077** | **0.0150** | 0.117 | 94.1% |
| Q4_K_M without imatrix (not published) | 45.0 | 4.566 ± 0.077 | 0.0151 | 0.118 | 94.2% |
| [NVIDIA 24 GB](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF) (QAT IQ2) | 20.5 | 5.284 ± 0.096 | 0.169 | 1.59 | 84.2% |

Caveat: NVIDIA's file is quantized from its own QAT-retrained checkpoint, so its KL against our BF16-based Q8_0 includes
that retraining, not only rounding error. PPL compares both files on equal terms.

The imatrix and no-imatrix Q4_K_M are the same within noise; the published file uses the imatrix.

## Memory (computed, not measured)

Weights + 32K context + compute buffers, from the file sizes. The routed experts are ~89% of the weights, so a file
bigger than the card runs by keeping some experts in system RAM (`-ncmoe N`, or let llama.cpp's default `--fit on` pick).

| file | size GiB | status | 24 GB card | 32 GB card (B70) |
|---|---|---|---|---|
| NVIDIA 24 GB (QAT IQ2) | 20.5 | on the Hub (NVIDIA) | fits whole | fits whole (measured on the B70: 22.9 GiB with the LiLiCorr drafter at 32K) |
| IQ3_XXS | 29.8 | coming | ~21 GiB VRAM + ~10 GiB RAM | ~29 GiB VRAM + ~3 GiB RAM |
| Q3_K_M | 36.1 | coming | ~21 + ~17 | not computed yet |
| IQ4_XS | 39.1 | coming | ~21 + ~20 | not computed yet |
| **Q4_K_M** | 45.0 | **on the Hub** | ~21 + ~26 (`-ngl 99 -ncmoe 64`) | ~28 + ~18 (`-ngl 99 -ncmoe 46`) |
| Q5_K_M, Q6_K, Q8_0 | | coming | | |

Measured VRAM replaces these numbers after the B70 runs.

## Method

1. BF16 safetensors to GGUF with `convert_hf_to_gguf.py` plus the Bolt fix on
   [riceharvest/llama.cpp `bolt-convert`](https://github.com/riceharvest/llama.cpp/commit/56ce232d0eafba2c32441a90dbb6a2d63dde2789)
   (master's converter fails on this checkpoint, see [known problems](../#llamacpp)).
2. Importance matrix from a Q6_K made without one: 152 chunks of 512 tokens of bartowski's calibration_datav3 +
   wikitext-2 *train* + C++/Python source (the test split used above is not in it).
3. `llama-quantize` with per-tensor overrides: routed experts take the file's type; attention and the LatentMoE
   projections stay Q8_0, Mamba in/out and the shared expert Q6_K (for Q4_K_M). Full table and scripts are on the
   [model card](https://huggingface.co/darioooooo0o/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-GGUF#how-these-were-made).
4. `llama-perplexity --kl-divergence` against the Q8_0 logits, numbers as above.

## Runtimes

Needs **llama.cpp b11669+** ([#30520](https://github.com/ggml-org/llama.cpp/pull/30520)). Ollama stable 0.40.4 can't
load it; the pre-release [0.40.5-rc2](https://github.com/ollama/ollama/releases/tag/v0.40.5-rc2) bundles b11669 (not
tested by us). LM Studio: not verified. The [b70-llama-builds](https://github.com/riceharvest/b70-llama-builds) release
is not on b11669 yet (a Bolt update is waiting for a GPU test); build upstream for now (see
[bolt-24gb-b70.md](bolt-24gb-b70.md#build)).

```bash
hf download darioooooo0o/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-GGUF --include "Q4_K_M/*" --local-dir bolt
hf download darioooooo0o/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-GGUF mmproj-NVIDIA-Nemotron-3.5-Bolt-74B-A9B-Q8_0.gguf --local-dir bolt
./build/bin/llama-server -m bolt/Q4_K_M/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-Q4_K_M-00001-of-00002.gguf \
  --mmproj bolt/mmproj-NVIDIA-Nemotron-3.5-Bolt-74B-A9B-Q8_0.gguf --no-mmproj-offload \
  -ngl 99 -ncmoe 46 -fa on -c 32768 --jinja
```

`-ncmoe 46` is the computed split for a 32 GB card; use 64 on a 24 GB card, or drop `-ngl`/`-ncmoe` and let `--fit` choose.

[Back to the performance guide](../performance.md#nemotron-35-bolt-74b-a9b)
