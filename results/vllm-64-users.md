---
title: "B70: 64 concurrent users on Qwen3.6-35B-A3B"
---
{% raw %}
# 64 concurrent users on one Arc Pro B70: Qwen3.6-35B-A3B with vLLM

Measured 2026-10-15 on one Arc Pro B70 (32 GB), Fedora 43. Back to the [performance guide](../performance.md).

## Result

`vllm bench serve`, 128 requests, at most 64 in flight, 512-token prompts, 512-token answers (ignore_eos), greedy.

| setup | requests running at once | median time per token | generation (64 / median TPOT) | output tok/s (wall) | total tok/s (wall) |
|---|---|---|---|---|---|
| fp32 GDN state (vLLM default for this model) | 61 of 64 (KV cache full) | 49.3 ms | 1298.7 | 1046 | 2092 |
| **fp16 GDN state** | **64 of 64** | **42.3 ms** | **1511.5** | **1385** | **2769** |
| fp16 GDN state, rerun with the exact command below | 64 of 64 (0 waiting) | 45.1 ms (from 64 / gen) | 1420 | | 2581 |

Expect about **1420-1510 tok/s generation** with the command below (two runs). The first run was through our benchmark
script; the rerun used the command on this page as written.

"Requests running at once" is from the engine's own log. Generation as 64 / median TPOT only means something when all 64
actually run at once; in our MTP runs at 64 concurrency only 4 fit, which makes that formula overstate throughput many times
over, so MTP numbers are not shown here.

For reference, the best 64-user entry on [localmaxxing](https://www.localmaxxing.com) for this model on one B70 is generation
1139.8 tok/s (64 / median TPOT 56 ms), wall aggregate 1967.7 (vLLM 0.21, diverse 512-token prompts). Our prompts were random
tokens; without speculative decoding the prompt text does not change decode speed.

## Why fp16 state

Qwen3.5/3.6/3.8 keep their linear-attention (GDN) state per request: 32 heads x 128 x 128 per layer, 30 layers. The model
config asks for fp32 (`mamba_ssm_dtype`), and vLLM follows it unless `--mamba-ssm-cache-dtype` is set. That is 60 MiB per
request, read and written every decode step: at 64 requests about 7.7 GB of an estimated ~24 GB the GPU moves per step (computed from the model config), and it filled
the KV cache at 61 requests. In fp16 it is half. By that estimate the step already runs at ~500 GB/s, i.e. memory-bound, so
fewer bytes is faster: the estimate predicted ~40 ms per token with fp16, measured 42.3.

## Quality

Greedy 1024-token answers to 8 prompts, generated with each state type, then every generated token scored by the fp32 model in
one prefill pass. KL divergence of the decode-time distribution from that reference, and top-1 agreement:

| positions | fp32 state (floor) | fp16 state |
|---|---|---|
| 0-255 | 0.0049, 98.0% | 0.0027, 98.6% |
| 256-511 | 0.0023, 99.5% | 0.0034, 99.5% |
| 512+ | 0.0041, 99.5% | 0.0035, 99.5% |

fp16 sits at the fp32 floor, with no growth over 1024 tokens. gsm8k (100 questions): fp16 state 98/100, fp32 state 94/100,
i.e. no loss (the difference is within run-to-run noise at n=100). Greedy text still diverges early from the fp32 run, as it does
under any numeric change at near-ties. Not covered: answers much longer than ~1.5K tokens.

## Reproduce

Image `ghcr.io/riceharvest/b70-vllm:v0.31.0-b70.3` ([cookbook](https://github.com/riceharvest/b70-qwen38-cookbook)), model
`palmfuture/Qwen3.6-35B-A3B-GPTQ-Int4` in `~/models/qwen36-a3b-gptq-palm`:

```bash
docker run -d --name moe --device /dev/dri -v /dev/dri:/dev/dri:ro --shm-size 8g -p 8021:8021 -v ~/models:/w:ro \
  -e B70_TARGET_LMHEAD_FP8=1 -e B70_LINEAR_FP8_FREE=1 \
  -e B70_LINEAR_FP8_RE='(self_attn\.(qkv_proj|o_proj)|linear_attn\.(in_proj_qkvz|in_proj_qkv|in_proj_z|out_proj)|shared_expert\.(gate_up_proj|down_proj))$' \
  --entrypoint bash ghcr.io/riceharvest/b70-vllm:v0.31.0-b70.3 -lc "exec vllm serve /w/qwen36-a3b-gptq-palm --port 8021 \
  --served-model-name moe --distributed-executor-backend mp --quantization gptq --dtype float16 --kv-cache-dtype fp8 \
  --max-model-len 16384 --gpu-memory-utilization 0.82 --max-num-seqs 64 --max-num-batched-tokens 8192 --language-model-only \
  --cpu-offload-gb 4 --cpu-offload-params embed_tokens --no-enable-prefix-caching --mamba-ssm-cache-dtype float16 \
  --compilation-config '{\"cudagraph_capture_sizes\":[1,2,4,8,16,24,32,40,48,56,64]}'"
docker exec moe vllm bench serve --backend vllm --base-url http://localhost:8021 --model moe --tokenizer /w/qwen36-a3b-gptq-palm \
  --dataset-name random --random-input-len 512 --random-output-len 512 --ignore-eos --num-prompts 128 --max-concurrency 64 \
  --seed 0 --temperature 0 --percentile-metrics ttft,tpot,itl --metric-percentiles 50,99
```

Check the server log shows "Running: 64 reqs" during the run. `B70_LINEAR_FP8_FREE=1` frees the bf16 copies of the
fp8-converted layers (more KV cache); it is safe without speculative decoding only.
{% endraw %}
