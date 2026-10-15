---
title: B70 performance guide
---
# Arc Pro B70 performance guide

What we measured on one **Intel Arc Pro B70** (32 GB) and what to use as a result. Every number links to where it was
measured. Setup unless a row says otherwise: Fedora 43, kernel 7.1.8, oneAPI 2025.3, **Mesa 25.3.6**, one request at a
time. Measured 2026-10-14/15.

[Back to the hub](./) · [Leaderboard (user submissions)](leaderboard.md) · [Prebuilt llama.cpp](https://github.com/riceharvest/b70-llama-builds)

## Quick picks

| you want | use | measured |
|---|---|---|
| Qwen3.6-35B-A3B, one user, fastest | vLLM + [cookbook image](https://github.com/riceharvest/b70-qwen38-cookbook#qwen36-35b-a3b-moe-on-the-same-stack) `ghcr.io/riceharvest/b70-vllm`, MTP k=4 | **243.7** code / 164.4 prose tok/s ([cookbook](https://github.com/riceharvest/b70-qwen38-cookbook#qwen36-35b-a3b-moe-on-the-same-stack)) |
| Qwen3.6-35B-A3B in llama.cpp | Vulkan [b70 build](https://github.com/riceharvest/b70-llama-builds) + MTP n=3 | **108.5** tok/s, output identical to no MTP ([test 001](results/testq-001-llama-mtp-35b.md)) |
| Qwen3.6-35B-A3B, 64 users | vLLM + `--mamba-ssm-cache-dtype float16` | **1420-1511** generation, 2581-2769 total tok/s ([below](#vllm-64-concurrent-users)) |
| Qwen3.8-27B, one user | vLLM + [cookbook](https://github.com/riceharvest/b70-qwen38-cookbook#numbers) | code 113 / prose 66 tok/s, short prompt; 72 at 32K ([cookbook](https://github.com/riceharvest/b70-qwen38-cookbook#numbers)) |
| Qwen3.8-27B in llama.cpp | Vulkan b70 build on **Mesa 26.2.5** | **25.3** tok/s (SYCL 21.9) ([test 002](results/testq-002-mesa26-vulkan.md)) |
| long prompts in llama.cpp | SYCL | prompt after 32K context: 720 vs 86 tok/s on Vulkan (27B, Mesa 25) ([hub table](./#measured-sycl-vs-vulkan-on-a-b70)) |
| NVIDIA Nemotron 3.5 Bolt 74B-A9B (vision) | llama.cpp master Vulkan on **Mesa 26.2**, NVIDIA's 24 GB GGUF + LiLiCorr drafter | **43.2** tok/s decode, **54.4** on code with the drafter, 81.6 total with 4 users ([below](#nemotron-35-bolt-74b-a9b)) |
| no oneAPI on the machine | Vulkan, with **Mesa 26** | Mesa 26 more than doubles MoE decode vs 25 ([below](#mesa-25-vs-26)) |

Rule of thumb: on Mesa 25.x use llama.cpp SYCL for speed; on Mesa 26 Vulkan is as fast or faster on decode. For MTP in
llama.cpp, Vulkan is the safe choice today (exact output); SYCL MTP on master is slower than no MTP.

## Mesa 25 vs 26

llama.cpp Vulkan, same binaries, only the Mesa driver changed. `llama-bench -fa 1 -r 3`, tok/s ([test 002](results/testq-002-mesa26-vulkan.md)).

| model / test | master, Mesa 25.3.6 | master, Mesa 26.2.5 | b70 build, Mesa 25.3.6 | b70 build, Mesa 26.2.5 | SYCL |
|---|---|---|---|---|---|
| Qwen3.6-35B-A3B UD-Q4_K_M decode | 39.0 | 86.1 | 64.3 | **87.3** | 97.7 |
| Qwen3.6-35B-A3B UD-Q4_K_M prompt (512) | 1854 | 1637 | 1931 | 1737 | 1301 |
| Qwen3.8-27B decode | 13.2 | 22.9 | 22.7 | **25.3** | 21.9 |

Mesa 26 costs ~10% on short prompts. "b70 build" is the Vulkan tarball from
[b70-llama-builds](https://github.com/riceharvest/b70-llama-builds) (branch [`vk-b70-stack`](https://github.com/riceharvest/llama.cpp/blob/b70-docs/branches/vk-b70-stack.md)).

## llama.cpp: SYCL vs Vulkan at depth

Qwen3.6-35B-A3B UD-Q4_K_M, Mesa 25.3.6, tok/s ([branch doc](https://github.com/riceharvest/llama.cpp/blob/b70-docs/branches/vk-b70-stack.md)):

| test | Vulkan master | Vulkan b70 build | SYCL master |
|---|---|---|---|
| decode | 39.0 | 64.3 | **97.7** |
| decode after 32K | 32.7 | 52.5 | **74.5** |
| prompt (512) | 1854 | **1931** | 1301 |
| prompt after 32K | 312 | 630 | **1083** |

Dense 27B and a 1.7B model: [hub table](./#measured-sycl-vs-vulkan-on-a-b70).

## llama.cpp MTP (speculative decoding with the model's own MTP head)

Qwen3.6-35B-A3B-MTP UD-Q4_K_M, `llama-server`, greedy, 3 prompts x 256 tokens, mean tok/s
([test 001](results/testq-001-llama-mtp-35b.md), [test 007](results/testq-007-sycl-mmid-mtp.md)):

| backend | no MTP | MTP n=1 | n=2 | n=3 | output vs no MTP |
|---|---|---|---|---|---|
| Vulkan b70 build | 70.7 | 91.3 | 100.8 | **108.5** | identical |
| SYCL master | 86.7 | 69.0 | 77.0 | 80.9 | differs |
| SYCL, fork branch [`sycl-mmid-small-batch`](https://github.com/riceharvest/llama.cpp/blob/b70-docs/branches/sycl-mmid-small-batch.md) (not upstream) | 83.9 | | | **131.8** | differs (being checked) |

Why SYCL master is slow with MTP: its MoE path for 2-8 token verify batches goes through a host-synced sort and grouped
GEMM; the fork branch keeps those batches on the single-token kernel.

## llama.cpp SYCL decode fusions

A port of the public-domain qwen35moe fusions from steveseguin's b70-optimization-lab onto llama.cpp master, each behind
an environment flag ([test 006](results/testq-006-sycl-qwen35moe-fusions.md),
[branch doc](https://github.com/riceharvest/llama.cpp/blob/b70-docs/branches/sycl-qwen35moe-fusions.md)):

| Qwen3.6-35B-A3B UD-Q4_K_M, tg128 | tok/s |
|---|---|
| SYCL master | 93.4 |
| fork branch, fusions on | **107.9** (+15.5%), greedy output identical |

Not upstream and not in the prebuilt builds yet.

## Nemotron 3.5 Bolt 74B-A9B

NVIDIA's Mamba-2/Transformer LatentMoE (74B, 9B active, vision), the
[24 GB GGUF](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF) (2-bit QAT), llama.cpp master
`620d2225c` (Bolt support: [#30520](https://github.com/ggml-org/llama.cpp/pull/30520)), Vulkan ([details](results/bolt-24gb-b70.md)):

| | Mesa 26.2.5 | Mesa 25.3.6 |
|---|---|---|
| decode (tg128) at 0 / 8K / 32K context | **43.2 / 41.7 / 39.0** | 25.0 / 24.9 / 23.3 |
| prompt (pp512) at 0 / 8K / 32K | 680 / 526 / 326 | 768 / 606 / 303 |
| llama-server, code / prose answers | 42.8 / 42.4 | 27.3 / 27.3 |
| + LiLiCorr drafter (`--spec-draft-n-max 6`) | **54.4** / 42.5 | 32.3 / 23.5 |
| 4 users at once, total | 81.6 | 54.5 |

Mesa 26 is worth ~70% here. Vision works with the mmproj on the CPU (~5 s per image). With the drafter at 32K context
the card uses 22.9 GiB. SYCL + drafter currently aborts (see [known problems](./#llamacpp)). 3- to 8-bit files made from
the BF16 weights (for cards with more system RAM) are in progress.

## vLLM: Qwen3.6-35B-A3B, one request

palmfuture/Qwen3.6-35B-A3B-GPTQ-Int4, 16K context, code / prose answers of 512 tokens, decode tok/s
([cookbook](https://github.com/riceharvest/b70-qwen38-cookbook#qwen36-35b-a3b-moe-on-the-same-stack)):

| setup | no MTP | MTP k=4 |
|---|---|---|
| stock vLLM XPU v0.31 image | 75.6 / 76.3 | 123.4 / 113.2 (fits only at 2K context) |
| + cookbook patches | 73.4 / 73.7 | 175.9 / 126.6 |
| + fp8 lm_head | 78.7 / 79.1 | 183.9 / 134.3 |
| + int4 MoE decode GEMV | 93.8 / 94.3 | 200.8 / 145.4 |
| **+ fp8 attention/GDN/shared expert (image default)** | **118.9 / 119.6** | **243.7 / 164.4** |

Two of these are proposed upstream, measured on vLLM nightly (4K context, [test 004](results/testq-004-upstream-branches.md),
[test 005](results/testq-005-lmhead-retest.md)):

| change | before | after |
|---|---|---|
| int4 MoE decode GEMV ([vllm-xpu-kernels #644](https://github.com/vllm-project/vllm-xpu-kernels/pull/644)), no MTP | 75.8 / 76.3 | 86.6 / 87.2 |
| + fp8 lm_head via online quantization ([vllm #61815](https://github.com/vllm-project/vllm/pull/61815)), no MTP | 86.6 / 87.2 | 89.4 / 90.2 |
| same two, MTP k=4 (2K context) | 157.3 / 118.7 | 183.7 / 131.9 |

gsm8k (first 100) stayed at 96-97/100 in every arm.

## vLLM: 64 concurrent users

Qwen3.6-35B-A3B, 64 requests in flight, 512-token prompts and answers, no speculative decoding
([details, quality check and the exact command](results/vllm-64-users.md)):

| setup | running at once | median time per token | generation (64 / TPOT) | total tok/s |
|---|---|---|---|---|
| vLLM default (fp32 GDN state) | 61 of 64 | 49.3 ms | 1298.7 | 2092 |
| **`--mamba-ssm-cache-dtype float16`** | 64 of 64 | **42.3-45.1 ms** | **1420-1511** | **2581-2769** |

The fp16 state halves the per-request linear-attention state (fp32 by default for Qwen3.5/3.6/3.8); decode quality stays at
the fp32 noise floor in our check (gsm8k 98/100 vs 94/100 for fp32). Two runs: 1511.5 and 1420 generation. Best 64-user entry on localmaxxing for this model on one B70: 1139.8.

## Tools

- [b70-doctor](https://github.com/riceharvest/b70-doctor): checks driver, firmware, PCIe link, Resizable BAR, Mesa and
  compute-runtime versions, and prints the fix, including the exact Mesa 26 update command for your distro and outdated
  B70 container images.
- [b70-bench](https://github.com/riceharvest/b70-bench): the standard benchmark. `--prebuilt` downloads the B70 builds,
  so one command benchmarks SYCL and Vulkan and offers to add your result to the shared table:
  `curl -fsSL https://raw.githubusercontent.com/riceharvest/b70-bench/main/b70-bench.sh | bash -s -- --prebuilt --tier quick`
- [b70-llama-builds](https://github.com/riceharvest/b70-llama-builds): prebuilt llama.cpp SYCL (AOT for the B70, oneAPI
  runtime bundled) and Vulkan with the B70 fixes.
  Also as a [Docker image](https://github.com/riceharvest/b70-llama-builds#docker-image) that brings its own Mesa 26.2.4
  and compute-runtime, so Vulkan gets the Mesa 26 speed on any host distro.
