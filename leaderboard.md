---
title: B70 leaderboard
---
{% raw %}
# Arc Pro B70 leaderboard

Fastest submitted runs on the Intel Arc Pro B70, from [localmaxxing.com](https://www.localmaxxing.com) (560 approved B70 runs, updated 2026-10-15 by a daily GitHub Action). Results are **submitted by users** and mostly not independently verified. Engines measure decode differently (llama-bench tg128, server inter-token medians, vLLM benchmarks), so compare within an engine. Best run per model, engine, quant and speculative-decoding setting.

[Back to the hub](./) · [Prebuilt llama.cpp for the B70](https://github.com/riceharvest/b70-llama-builds)

## How to reproduce the top runs

- **llama.cpp SYCL with fused kernels** (about 131 tok/s on a 35B-A3B MoE, one card, no speculative decoding): [steveseguin/b70-optimization-lab](https://github.com/steveseguin/b70-optimization-lab) publishes the exact patch, build, model hash and commands for each run ([Ornith 1.5 35B-A3B packet](https://github.com/steveseguin/b70-optimization-lab/tree/main/repro/ornith-15-35b-a3b-q4km-b70)). The patch is public domain, default off, and enabled with `GGML_SYCL_FUSED_*` environment flags.
- **vLLM on XPU with GPTQ int4 + MTP**: [SergiioB's B70 cookbook](https://github.com/SergiioB/intel-arc-pro-b70-inference-cookbook) (container, patches, launch flags).
- **Plain llama.cpp**: start from [b70-llama-builds](https://github.com/riceharvest/b70-llama-builds) (SYCL AOT for the B70, no oneAPI install) and copy the flags from the run details below.
- Check your setup first with [b70-doctor](https://github.com/riceharvest/b70-doctor): driver, Mesa, oneAPI and PCIe link problems cost more speed than any flag.

## Single stream, one B70

| # | decode tok/s | model | quant | engine | spec | ctx | prefill tok/s | date | links |
|---:|---:|---|---|---|---|---:|---:|---|---|
| 1 | **248.3** | [Qwen3.6-35B-A3B-GPTQ-Int4](https://huggingface.co/palmfuture/Qwen3.6-35B-A3B-GPTQ-Int4) | GPTQ-4bit | vllm vLLM 0.26.1.dev0 XPU, built from… | MTP (cmd) | 32768 | 12400 | 2026-08-08 | [run](https://www.localmaxxing.com/en/runs/cmsk153ne00q1qm01369d61m8) |
| 2 | **244.5** | [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-B…](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) | gptq-int4 | vllm 0.26.1 |  | 2048 | 4511 | 2026-09-30 | [run](https://www.localmaxxing.com/en/runs/cmuoi4wc90kcelq018zju1oj9) |
| 3 | **244.5** | [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-W…](https://huggingface.co/useful-quants/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-W4A16) | gptq-int4 | vllm 0.26.1 |  | 2048 |  | 2026-09-30 | [run](https://www.localmaxxing.com/en/runs/cmuogpumd0kc0lq01ygewetlg) |
| 4 | **204.6** | [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | GPTQ-Int4 | vllm 0.21.1.dev18+gec426505f XPU | MTP (cmd) | 16384 | 8715 | 2026-08-07 | [run](https://www.localmaxxing.com/en/runs/cmsiwwpzf00a4qm01z18izmad) |
| 5 | **191.7** | [Qwen3.5-4B-quantized.w4a16](https://huggingface.co/RedHatAI/Qwen3.5-4B-quantized.w4a16) | W4A16 | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-12 | [run](https://www.localmaxxing.com/en/runs/cmtyqbecv0aq9ps01ms6eum7z) |
| 6 | **186.6** | [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-B…](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) | GPTQ-INT4-G64-sym… | vllm v0.26.1rc1.dev668+g3ee2df303 (XP… | spec (cmd) | 16384 | 7160 | 2026-08-13 | [run](https://www.localmaxxing.com/en/runs/cmsr9po4w000ams01e4fc5qhj) |
| 7 | **132.4** | [LFM2.5-2.6B-GGUF](https://huggingface.co/LiquidAI/LFM2.5-2.6B-GGUF) | Q8_0 | llama.cpp 9fee29e9435f; oneAPI 2026.1… |  | 8192 |  | 2026-08-26 | [run](https://www.localmaxxing.com/en/runs/cmt9m8h6i00ymli018jvpod9i) · [repro](https://github.com/steveseguin/b70-optimization-lab/tree/main/repro/lfm25-26b-q8-b70) |
| 8 | **131.5** | [Ornith-1.5-35B-A3B-GGUF](https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF) | Q4_K_M | llama.cpp 9fee29e9435f + neural.downl… |  | 8192 |  | 2026-08-26 | [run](https://www.localmaxxing.com/en/runs/cmt9m8gvg00yeli01ylok5hfn) · [repro](https://github.com/steveseguin/b70-optimization-lab/tree/main/repro/ornith-15-35b-a3b-q4km-b70) |
| 9 | **125.0** | [gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) | Q8_K_XL | llama.cpp c926ad098 local B70 SYCL/AO… | MTP | 32768 |  | 2026-07-01 | [run](https://www.localmaxxing.com/en/runs/cmr1u77na01k2ld01kalwzs1e) |
| 10 | **124.1** | [Qwen3.5-9B-quantized.w4a16](https://huggingface.co/RedHatAI/Qwen3.5-9B-quantized.w4a16) | W4A16 | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-12 | [run](https://www.localmaxxing.com/en/runs/cmtyqbel70aqcps01zrvj4kjp) |
| 11 | **120.8** | [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | Q4_K_M | llama.cpp |  | 2048 | 3326 | 2026-08-16 | [run](https://www.localmaxxing.com/en/runs/cmswdukys08ofms014vye7nit) |
| 12 | **115.2** | [gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) | UD-Q8_K_XL | llama.cpp 9769 (c926ad098), IntelLLVM… | MTP | 32768 | 997 | 2026-07-03 | [run](https://www.localmaxxing.com/en/runs/cmr47ivql0045nv011pfdjlaa) · [repro](https://github.com/steveseguin/b70-optimization-lab/blob/8723f783fa904092dcc019272f7abff939879f39/data/gemma4-26b-prod-service-32k-smoke-20260703T002811Z.json) |
| 13 | **112.7** | [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | GPTQ-Int4+draft-I… | vllm 0.27.2rc1.dev77+gac7509e2b XPU | MTP (cmd) | 131072 | 1696 | 2026-08-19 | [run](https://www.localmaxxing.com/en/runs/cmszpqy000e8fms014ty6i5x3) |
| 14 | **108.4** | [Ornith-1.5-35B-A3B-GPTQ-Int4-sym-G128-M…](https://huggingface.co/SergiioB/Ornith-1.5-35B-A3B-GPTQ-Int4-sym-G128-MTP-BF16-MixedCal-v2) | GPTQ-Int4 | vllm |  | 2048 | 9073 | 2026-08-21 | [run](https://www.localmaxxing.com/en/runs/cmt2tdx5q0hy0mv01koh4xwpw) |
| 15 | **108.1** | [Qwen3-Coder-30B-A3B-Instruct-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF) | GGUF UD-Q4_K_XL | llama.cpp llama.cpp fdb1db877 / llama… |  | 4096 |  | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr6w2ekt00gimn01orbith22) |
| 16 | **107.5** | [Qwen3-30B-A3B-Instruct-2507-GGUF](https://huggingface.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF) | GGUF UD-Q4_K_XL | llama.cpp llama-server version 9763 (… |  | 4096 |  | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr6rr2kv008imn019frg0x3m) |
| 17 | **106.7** | [Qwen3.8-27B-GPTQ-Int4-sym-G128-MTP-BF16](https://huggingface.co/SergiioB/Qwen3.8-27B-GPTQ-Int4-sym-G128-MTP-BF16) | GPTQ-Int4 | vllm |  | 131072 | 1694 | 2026-08-19 | [run](https://www.localmaxxing.com/en/runs/cmt03mj040eh8ms01trjvhm75) |
| 18 | **106.5** | [Nex-N2-mini](https://huggingface.co/nex-agi/Nex-N2-mini) | Q4_K_M | llama.cpp |  | 2048 |  | 2026-06-20 | [run](https://www.localmaxxing.com/en/runs/cmqm49cui01fbnv01d7l6io6u) |
| 19 | **104.3** | [gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) | Q8_K_XL | llama.cpp c926ad098 local B70 SYCL/AO… | draft-mtp | 8192 |  | 2026-06-27 | [run](https://www.localmaxxing.com/en/runs/cmqw1tgzx0366qr01g4lkv7f1) |
| 20 | **100.5** | [Qwen3-30B-A3B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507) | Q4_K_XL | llama.cpp |  | 2048 | 1464 | 2026-08-16 | [run](https://www.localmaxxing.com/en/runs/cmswd9mgo08nims01vjv4cyta) |
| 21 | **98.1** | [Qwen3.5-9B-FP8-dynamic](https://huggingface.co/RedHatAI/Qwen3.5-9B-FP8-dynamic) | FP8 | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-07 | [run](https://www.localmaxxing.com/en/runs/cmtqyanxc00bjpa01nojy87wp) |
| 22 | **97.8** | [Qwen3.8-27B-Uncensored-int4-AutoRound](https://huggingface.co/johannrplaster/Qwen3.8-27B-Uncensored-int4-AutoRound) | GPTQ-Int4 | vllm 0.27.2rc1.dev78+g8e6d8e4f6 XPU (… | spec (cmd) | 2048 | 1782 | 2026-08-20 | [run](https://www.localmaxxing.com/en/runs/cmt0vrxjk0fvpms01n4i9cmns) |
| 23 | **96.5** | [microsoft_Phi-4-mini-instruct-GGUF](https://huggingface.co/bartowski/microsoft_Phi-4-mini-instruct-GGUF) | GGUF Q4_K_M | llama.cpp fdb1db877 |  | 4096 |  | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr6yazhe00hcmn01i5gz2xe0) |
| 24 | **95.1** | [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | exl3 | vllm 0.26.1 |  | 2048 |  | 2026-09-30 | [run](https://www.localmaxxing.com/en/runs/cmuogo72v0kbwlq01hchdyd6k) |
| 25 | **94.6** | [QUEST-30B-RL-B70-Turbo-GGUF](https://huggingface.co/Frosty40/QUEST-30B-RL-B70-Turbo-GGUF) | Q5_K_M | llama.cpp |  | 2048 | 1342 | 2026-08-17 | [run](https://www.localmaxxing.com/en/runs/cmsx5ihe00aoyms01gxlfewdt) |
| 26 | **93.0** | [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-B…](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) | GPTQ-INT4-G64-sym… | vllm v0.26.1rc1.dev668+g3ee2df303 (XP… |  | 16384 | 8368 | 2026-08-12 | [run](https://www.localmaxxing.com/en/runs/cmsql0duh00oimr01sgfq0ose) |
| 27 | **87.8** | [Laguna-XS-2.1](https://huggingface.co/poolside/Laguna-XS-2.1) | Q4_K_M | llama.cpp |  | 2048 | 1044 | 2026-08-16 | [run](https://www.localmaxxing.com/en/runs/cmswdumj608oqms01sbdm6vdo) |
| 28 | **87.4** | [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-G…](https://huggingface.co/bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF) | Q4_0 | llama.cpp b306 SYCL (f785fc9ea) + cus… | MTP (cmd) | 16384 | 766 | 2026-08-12 | [run](https://www.localmaxxing.com/en/runs/cmspqg83m0039mr01abjms5mw) |
| 29 | **87.4** | [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-B…](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) | Q4_0 | llama.cpp b306 SYCL (f785fc9ea) + cus… | MTP (cmd) | 16384 | 766 | 2026-08-11 | [run](https://www.localmaxxing.com/en/runs/cmsp78jxo00mhmp015lf9v28b) |
| 30 | **83.7** | [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | GPTQ-Int4 | vllm 0.27.2rc1.dev77+gac7509e2b XPU | MTP (cmd) | 131072 | 1774 | 2026-08-15 | [run](https://www.localmaxxing.com/en/runs/cmsur82fz06svms01ga1f0z83) |

## Single stream, multiple B70s

| # | decode tok/s | model | quant | engine | spec | ctx | prefill tok/s | date | links |
|---:|---:|---|---|---|---|---:|---:|---|---|
| 1 | **236.9** | [Qwen3.5-4B-quantized.w4a16](https://huggingface.co/RedHatAI/Qwen3.5-4B-quantized.w4a16) | W4A16 | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-08 | [run](https://www.localmaxxing.com/en/runs/cmtrycz0y002pps011142ifrk) |
| 2 | **172.3** | [Qwen3.5-9B-quantized.w4a16](https://huggingface.co/RedHatAI/Qwen3.5-9B-quantized.w4a16) | W4A16 | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-07 | [run](https://www.localmaxxing.com/en/runs/cmtrn9hoy001ops01qzd4axry) |
| 3 | **161.9** | [Muse-Glimmer-30B-GGUF](https://huggingface.co/unsloth/Muse-Glimmer-30B-GGUF) | UD-Q8_K_XL | llama.cpp 10433; 030ebb558 + Muse TP4… | draft-dflash | 32768 |  | 2026-08-14 | [run](https://www.localmaxxing.com/en/runs/cmss8515c00n0ms01n3begqgg) |
| 4 | **147.8** | [Qwen3.5-9B-FP8-dynamic](https://huggingface.co/RedHatAI/Qwen3.5-9B-FP8-dynamic) | FP8 | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-07 | [run](https://www.localmaxxing.com/en/runs/cmtqzhlvn00c0pa0109xxfb2f) |
| 5 | **125.5** | [Laguna-S-2.1-INT4](https://huggingface.co/poolside/Laguna-S-2.1-INT4) | INT4_W4A16 | vllm 0.1.dev1172+g4a6fd8747; local vL… | dflash | 8192 |  | 2026-08-01 | [run](https://www.localmaxxing.com/en/runs/cms9wuuf300cqpm01t5i285tq) |
| 6 | **120.8** | [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | BF16 (native) | vllm vllm-main d272418f4 (XPU graph +… |  | 65536 |  | 2026-06-25 | [run](https://www.localmaxxing.com/en/runs/cmqszbv1q012hqr01fsmv2wnu) |
| 7 | **117.5** | [Qwen3.8-27B-int4-AutoRound](https://huggingface.co/devan-carlin/Qwen3.8-27B-int4-AutoRound) | int4 AutoRound W4… | vllm vllm 0.27.2rc1.dev77+gac7509e2b … | MTP | 1024 |  | 2026-09-12 | [run](https://www.localmaxxing.com/en/runs/cmtyqbeu40aqgps011wl4mljo) |
| 8 | **110.7** | [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | FP8 (online) + FP… | vllm vllm-main d272418f4 (XPU graph +… |  | 65536 |  | 2026-06-25 | [run](https://www.localmaxxing.com/en/runs/cmqsyq9lt011rqr010otg1494) |
| 9 | **102.5** | [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | BF16 | vllm g6607a80da (custom) |  | 262144 |  | 2026-06-19 | [run](https://www.localmaxxing.com/en/runs/cmqkd78qq00ujnv01oqd8vgv0) |
| 10 | **101.9** | [Qwen3.8-27B-int4-AutoRound](https://huggingface.co/devan-carlin/Qwen3.8-27B-int4-AutoRound) | AutoRound INT4 W4… | vllm v0.20.2rc1.dev13+g9557d9108 loca… |  | 2048 |  | 2026-08-18 | [run](https://www.localmaxxing.com/en/runs/cmszbkxco0e11ms01l2rixxbt) |

## Batched / concurrent throughput (aggregate tok/s)

| # | decode tok/s | model | quant | engine | spec | ctx | prefill tok/s | date | links |
|---:|---:|---|---|---|---|---:|---:|---|---|
| 1 | **1139.8** | [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | GPTQ-Int4 | vllm 0.21.1.dev18+gec426505f XPU |  | 16384 | 8715 | 2026-08-07 | [run](https://www.localmaxxing.com/en/runs/cmsiwwqmt00a9qm010iekvi3u) |
| 2 | **796.2** | [gemma-4-12B-it-int4-AutoRound](https://huggingface.co/Intel/gemma-4-12B-it-int4-AutoRound) | INT4 AutoRound W4… | vllm 0.20.2rc1.dev2+gc51df4300.d20260… |  | 32768 |  | 2026-06-07 | [run](https://www.localmaxxing.com/en/runs/cmq3jm75g000tlj01bx4frdf0) |
| 3 | **438.5** | [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) | sym_int4 | vllm |  | 2048 | 10 | 2026-08-16 | [run](https://www.localmaxxing.com/en/runs/cmswf261n08qfms01xshb57ny) |
| 4 | **335.5** | [QUEST-30B-RL-B70-Turbo-GGUF](https://huggingface.co/Frosty40/QUEST-30B-RL-B70-Turbo-GGUF) | Q5_K_M GGUF | llama.cpp SYCL moe-ready build used b… |  | 131072 | 76 | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr5upo2o00heq901sll801vc) |
| 5 | **283.1** | [Laguna-XS-2.1-GGUF](https://huggingface.co/poolside/Laguna-XS-2.1-GGUF) | Q5_K_M GGUF | llama.cpp SYCL moe-ready build used b… |  | 131072 | 66 | 2026-07-05 | [run](https://www.localmaxxing.com/en/runs/cmr89jid800a9qr01lkojydrn) |
| 6 | **224.9** | [Ornith-1.0-35B-B70-Turbo](https://huggingface.co/Frosty40/Ornith-1.0-35B-B70-Turbo) | Q5_K_M GGUF | llama.cpp SYCL moe-ready build used b… |  | 131072 | 33 | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr5x1qce00khq901hg2qfi09) |
| 7 | **224.3** | [Nex-N2-mini-B70-Turbo-GGUF](https://huggingface.co/Frosty40/Nex-N2-mini-B70-Turbo-GGUF) | Q5_K_M GGUF | llama.cpp SYCL moe-ready build used b… |  | 131072 | 33 | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr5x1rol00kzq9013wn55zvr) |
| 8 | **224.2** | [Qwen3.8-27B-GPTQ-Int4-sym-G128-MTP-BF16](https://huggingface.co/SergiioB/Qwen3.8-27B-GPTQ-Int4-sym-G128-MTP-BF16) | GPTQ-Int4 | vllm |  | 2048 | 5 | 2026-08-19 | [run](https://www.localmaxxing.com/en/runs/cmt00i0eb0eflms012anb0yau) |
| 9 | **223.7** | [SIQ-1-35B-B70-Turbo-GGUF](https://huggingface.co/Frosty40/SIQ-1-35B-B70-Turbo-GGUF) | Q5_K_M GGUF | llama.cpp SYCL moe-ready build used b… |  | 131072 | 33 | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr5v06n400jhq901amkqmbw6) |
| 10 | **209.0** | [Qwen-AgentWorld-35B-A3B-B70-Turbo-GGUF](https://huggingface.co/Frosty40/Qwen-AgentWorld-35B-A3B-B70-Turbo-GGUF) | Q5_K_M GGUF | llama.cpp SYCL moe-ready build used b… |  | 30720 | 1925 | 2026-07-04 | [run](https://www.localmaxxing.com/en/runs/cmr5zf8x400phq901tg5jxhuc) |

## Top single-card runs in detail

### 1. 248.3 tok/s: palmfuture/Qwen3.6-35B-A3B-GPTQ-Int4 on vllm vLLM 0.26.1.dev0 XPU, built from…

```bash
vllm serve /models/Qwen3.6-35B-A3B-GPTQ-Int4 \
  --dtype float16 --max-model-len 32768 --max-num-seqs 16 \
  --kv-cache-dtype fp8 --max-num-batched-tokens 16384 --block-size 64 \
  --language-model-only --trust-remote-code \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --speculative-config '{"method":"mtp","num_speculative_tokens":4}'
```

### 2. 244.5 tok/s: nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 on vllm 0.26.1

```bash
# No command snippet available
```

> MoE vs Dense matched single-card comparison. p512/g128 greedy benchmark on Intel Arc Pro B70 at 200W cap. Yields 244.5 tok/s.

### 3. 244.5 tok/s: useful-quants/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-W4A16 on vllm 0.26.1

```bash
# No command snippet available
```

> MoE vs Dense matched single-card comparison. p512/g128 greedy benchmark on Intel Arc Pro B70 at 200W cap. Yields 244.5 tok/s.

### 4. 204.6 tok/s: Qwen/Qwen3.6-35B-A3B on vllm 0.21.1.dev18+gec426505f XPU

```bash
vllm serve /model --quantization gptq --dtype float16 --max-model-len 16384 --max-num-seqs 64 --max-num-batched-tokens 8192 --served-model-name Qwen3.6-35B-A3B-MTP-Preserved-GPTQ-Int4 --language-model-only --speculative-config {"method":"mtp","num_speculative_tokens":4}
```

> Single-stream MTP4 num_spec=4. vLLM 0.21 XPU int4moe + 2 patches: native int4 int8 store, BF16 MTP draft. Recurrent single-layer MTP emits 4 draft tokens/step. short/32 decode 204.6 t/s (grid, prefix-cache-off, warmup discarded). Prefill p4k 8715 t/s @230W. Decode @165W. --max-num-batched-tokens 8192. Model: Qwen3.6-35B-A3B-MTP-Preserved-GPTQ-Int4. 2026-08-07.

### 5. 191.7 tok/s: RedHatAI/Qwen3.5-4B-quantized.w4a16 on vllm vllm 0.27.2rc1.dev77+gac7509e2b …

```bash
MODEL_DIR=/path/to/Qwen3.5-4B-quantized.w4a16 VLLM_CACHE_DIR=/path/to/new-cache MTP_DEPTH=3 MAX_MODEL_LEN=1024 MAX_NUM_SEQS=1 repro/qwen35-4b-w4a16-b70/scripts/run-qwen35-4b-w4a16-server.sh  (ghcr.io/steveseguin/vllm-openai-xpu-qwen38-int4@sha256:78bd728d6109…)
```

---

Data: localmaxxing.com public API (`/api/speed-tests?gpuName=Intel Arc Pro B70`), user-submitted, provided as is. Generator: [`scripts/leaderboard.py`](scripts/leaderboard.py).
{% endraw %}
