# Awesome Arc Pro B70

Everything a new **Intel Arc Pro B70** (32 GB, Battlemage G31, `8086:e223`) owner needs to run local LLMs on Linux,
in one place: setup checks, which engine to pick, the known driver and engine bugs with their workarounds, benchmarks,
and models that are tested on the card. Most of it also applies to the B60, B50, B580 and B570.

Last reviewed **2026-10-15**. The status badges in the bug table are live. Corrections and additions are welcome, see
[Contributing](#contributing).

**Contents:** [Start here](#start-here) · [Pick an engine](#pick-an-engine) ·
[Known problems and workarounds](#known-problems-and-workarounds) · [Tools](#tools) · [Guides and recipes](#guides-and-recipes) ·
[Models tested on a B70](#models-tested-on-a-b70) · [Benchmarks](#benchmarks) · [Upstream trackers](#upstream-trackers)

## Start here

1. **Check the setup.** Run [b70-doctor](https://github.com/riceharvest/b70-doctor), a read-only script. It checks that
   the `xe` driver is bound, the firmware versions, the real PCIe slot link, Resizable BAR, render-node permissions,
   past GPU hangs in the kernel log, and the compute-runtime and Mesa versions. For each problem it prints the fix:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/riceharvest/b70-doctor/main/b70-doctor.sh | bash
   ```
   SergiioB's cookbook has its own [`doctor.py`](https://github.com/SergiioB/intel-arc-pro-b70-inference-cookbook/blob/master/scripts/doctor.py),
   which adds dual-card oneCCL hints for vLLM TP2.
2. **Turn on Resizable BAR** in the BIOS ("Above 4G Decoding" + "Re-Size BAR Support", CSM off). The doctor tells you if it's off.
3. **Pick an engine** from the table below. If you just want to chat, use Ollama or LM Studio. **If you want speed,
   use llama.cpp with SYCL:** on a B70 it decodes about 1.7× faster than the Vulkan path that Ollama and LM Studio use,
   and handles long prompts up to 8× faster ([measured below](#measured-sycl-vs-vulkan-on-a-b70)). To serve many users
   or long context, use vLLM.
4. **Skim the [known problems](#known-problems-and-workarounds)** before you lose an evening to one of them.

## Pick an engine

| engine | backend on a B70 | good for | notes |
|---|---|---|---|
| [Ollama](https://github.com/ollama/ollama) | Vulkan (on by default when the backend is installed) | easiest start | Needs Mesa's Intel Vulkan driver. The `ollama` user needs access to `/dev/dri/renderD*` (the render group; Ollama's docs mention this for AMD, and it's the same permission). `sudo setcap cap_perfmon+ep /usr/local/bin/ollama` lets it see free VRAM ([docs](https://github.com/ollama/ollama/blob/main/docs/gpu.mdx)). SYCL support is only a [proposal](https://github.com/ollama/ollama/issues/16930). |
| [LM Studio](https://lmstudio.ai) | Vulkan llama.cpp runtime | GUI, model browser | Same Vulkan caveats as llama.cpp Vulkan. |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) SYCL | Level Zero / oneAPI | best llama.cpp speed, long context | Build with `-DGGML_SYCL_F16=ON`: it is off by default and gives about 3.7× prefill ([tuning log](https://github.com/ggml-org/llama.cpp/discussions/27593)). Don't set `GGML_SYCL_ENABLE_OPT=0`; the same log measured it costing about 68% of generation speed. Docker: `ghcr.io/ggml-org/llama.cpp:server-intel`. |
| llama.cpp Vulkan | Mesa ANV | no oneAPI needed | Keep Mesa current: 26.0.8 → 26.1.7 doubled decode on a B580 ([discussion](https://github.com/ggml-org/llama.cpp/discussions/27777)). Today about 1.7× slower decode than SYCL on a B70, and much slower at long context ([measured](#measured-sycl-vs-vulkan-on-a-b70)); see also the bug table. |
| [vLLM](https://github.com/vllm-project/vllm) XPU | PyTorch XPU + vllm-xpu-kernels | many users, MTP, 262K context | Official image `vllm/vllm-openai-xpu`. [Qwen3.8-27B cookbook](https://github.com/riceharvest/b70-qwen38-cookbook) + prebuilt image `ghcr.io/riceharvest/b70-vllm`. |
| [Intel LLM Scaler](https://github.com/intel/llm-scaler) | Intel's vLLM / ComfyUI builds for B60/B70 | Intel-supported serving and image/video gen | `intel/llm-scaler-vllm` images. 0.26.0-b2 fixes prefix caching with MTP. `intel/llm-scaler-omni` for ComfyUI. |
| OpenVINO | OpenVINO GenAI | an alternative to vLLM | Measured on a B70 in [SergiioB's cookbook](https://github.com/SergiioB/intel-arc-pro-b70-inference-cookbook/blob/master/docs/qwen38-27b/OPENVINO-B70-TUNING.md). |

### Measured: SYCL vs Vulkan on a B70

llama.cpp master `a0e6dc738` (2026-10-14), both backends built from the same commit, one Arc Pro B70, Fedora 43,
kernel 7.1.8, Mesa 25.3.6, oneAPI 2025.3. `llama-bench -ngl 99 -sm none -fa 1 -p 512 -n 128 -r 3`, tokens/s.

| model | test | Vulkan (Ollama, LM Studio) | SYCL | SYCL is |
|---|---|---|---|---|
| Qwen3.8-27B UD-Q4_K_XL | decode | 13.2 | 21.9 | 1.7× faster |
| Qwen3.8-27B UD-Q4_K_XL | decode after 32K context | 11.1 | 16.3 | 1.5× faster |
| Qwen3.8-27B UD-Q4_K_XL | prompt (512 tokens) | 684 | 868 | 1.3× faster |
| Qwen3.8-27B UD-Q4_K_XL | prompt after 8K context | 336 | 809 | 2.4× faster |
| Qwen3.8-27B UD-Q4_K_XL | prompt after 32K context | 86 | 720 | 8.4× faster |
| a 1.7B dense model, Q8_0 | decode | 71.5 | 191 | 2.7× faster |
| a 1.7B dense model, Q8_0 | prompt (512 tokens) | 5291 | 12477 | 2.4× faster |

SYCL build: `-DGGML_SYCL=ON -DGGML_SYCL_F16=ON -DGGML_SYCL_DEVICE_ARCH=bmg-g31-a0` (AOT for the B70, which also turns on
the XMX path), oneDNN on. The Vulkan gaps come from known slow paths on Xe2 + Mesa: scalar flash attention (see the bug
table) and slow mat-vec for some quant types (Q8_0, Q6_K, Q3_K, Q5_0). These numbers are from Mesa 25.3.6 (the newest
in Fedora 43). Newer Mesa narrows the gap: [one report](https://jonathanmann.tech/blog/intel-arc-b70-llama-cpp-benchmarks/)
has Vulkan level with SYCL on Qwen3.6-35B-A3B with Mesa 26.1. One machine, so treat these as a guide and
[add your numbers](https://github.com/riceharvest/b70-bench).

**Experimental Vulkan fixes** (branches on a llama.cpp fork, not merged upstream, same machine and model):

| test (Qwen3.8-27B) | Vulkan master | with fixes | SYCL master | fix |
|---|---|---|---|---|
| decode | 13.2 | **22.7** | 21.9 | [mat-vec loads](https://github.com/riceharvest/llama.cpp/blob/vk-mmvq-u32-loads/B70_RESULTS.md) |
| decode after 32K context | 11.1 | **17.5**, **19.0** with the FA split | 16.3 | + [decode FA split](https://github.com/riceharvest/llama.cpp/tree/vk-xe-fa-decode-split) |
| prompt (512 tokens) | 684 | **711** | 868 | [matmul split-k](https://github.com/riceharvest/llama.cpp/tree/vk-xe2-matmul-splitk) |

On a 1.7B Q8_0 model the same fixes take decode from 71.5 to 154 tok/s and prompts from 5464 to 6091. Prompts at long
context are still far behind SYCL (Intel's prefill kernel in [#29357](https://github.com/ggml-org/llama.cpp/pull/29357)
doubles them on a B70: 128 → 259 tok/s after 32K). All branches together: [`vk-b70-stack`](https://github.com/riceharvest/llama.cpp/tree/vk-b70-stack).

For speed comparisons between backends on this card, see [Benchmarks](#benchmarks).

## Known problems and workarounds

Each row links the upstream issue, and the badge shows its live state. "Workaround" means what reporters found to help;
most of these are mitigations, not fixes.

### Setup

| symptom | cause / workaround | upstream |
|---|---|---|
| Card not used, `i915` bound, or no driver | Battlemage needs the `xe` driver and a kernel that knows the G31 IDs. 7.0 (Ubuntu 26.04) and 7.1 (Fedora 43) work. [b70-doctor](https://github.com/riceharvest/b70-doctor) shows which case you're in. | — |
| Slow model loads, odd memory errors | Resizable BAR off: enable "Above 4G Decoding" + "Re-Size BAR" in the BIOS. | — |
| `lspci` / sysfs shows the GPU at "2.5 GT/s x1" | Normal: those are the card's own internal PCIe switch ports. The real slot link is on the upstream port; b70-doctor reads that one. | — |
| llama.cpp SYCL aborts: `failed to get device memory size` | Fixed in llama.cpp [#28227](https://github.com/ggml-org/llama.cpp/pull/28227) (2026-09-13). Update, or install the Level Zero dev package. | [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/28515)](https://github.com/ggml-org/llama.cpp/issues/28515) |

### GPU hangs and resets

| symptom | cause / workaround | upstream |
|---|---|---|
| `xe ... Engine reset: engine_class=ccs`, then `UR_RESULT_ERROR_DEVICE_LOST` under sustained load (llama.cpp SYCL, vLLM) | Driver-level; it tracks the compute-runtime release line. Reported mitigations:<br>• Opting out of Level Zero v2: `SYCL_UR_USE_LEVEL_ZERO_V2=0` gave no resets in a 20-min soak on 26.27 ([#27595](https://github.com/ggml-org/llama.cpp/issues/27595)); `UR_LOADER_USE_LEVEL_ZERO_V2=0` stopped a launch crash ([#27198](https://github.com/ggml-org/llama.cpp/issues/27198)).<br>• Driver versions are mixed: 25.48.36300.8 lowered the reset rate for one llama.cpp reporter, but failed a plain 24 GB allocate-and-memset probe that 26.35 passed, and 26.35 still died under vLLM load (#944). Test before you pin a version.<br>• Intel's maintainer suggests setting PCIe to Gen4 in the BIOS and using a ≥1000 W PSU (the card draws up to 290 W). | [![](https://img.shields.io/github/issues/detail/state/intel/compute-runtime/944)](https://github.com/intel/compute-runtime/issues/944) [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/25692)](https://github.com/ggml-org/llama.cpp/issues/25692) [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/27595)](https://github.com/ggml-org/llama.cpp/issues/27595) |
| Device **wedged** (`Xe has declared device ... as wedged`); nothing runs until reboot | Seen when a job runs close to the 32 GB limit: the driver's own copy jobs time out. Leave a few GB of VRAM headroom. If the B70 also drives your display, the desktop goes down with it. | [drm/xe#7893](https://gitlab.freedesktop.org/drm/xe/kernel/-/issues/7893) |
| `Engine memory CAT error [18]: class=bcs` + copy-engine reset while loading weights (vLLM start never becomes ready) | Open; seen with vLLM and with plain PyTorch weight copies. Retry the start; report details upstream. | [![](https://img.shields.io/github/issues/detail/state/vllm-project/vllm/61300)](https://github.com/vllm-project/vllm/issues/61300) |
| You want more headroom before the driver kills a long kernel | `job_timeout_ms` (default 5000) can be raised to 10000 per engine in `/sys/class/drm/cardN/device/tile0/gt0/engines/ccs/`, as root, until reboot. It doesn't fix real hangs. | — |

### llama.cpp

| symptom | cause / workaround | upstream |
|---|---|---|
| Vulkan: decode collapses about 8× at 64K context; prompt processing gets quadratically slower; sometimes device loss | Flash attention falls back to a scalar shader on Xe2: the driver advertises only an 8×16×16 coopmat shape. Use SYCL for long context, or try `-fa off` (it doesn't work for every model). An Intel FA prefill kernel is in review ([#29357](https://github.com/ggml-org/llama.cpp/pull/29357)). | [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/28721)](https://github.com/ggml-org/llama.cpp/issues/28721) [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/27638)](https://github.com/ggml-org/llama.cpp/issues/27638) [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/30503)](https://github.com/ggml-org/llama.cpp/issues/30503) |
| SYCL dual B70 `--split-mode tensor`: crash in `dev2dev_memcpy` (DEVICE_LOST), slow, or hangs with quantized KV | `GGML_SYCL_DEV2DEV_MEMCPY=2` (host-staged copies, slower but stable). For the hang, `GGML_SYCL_ENABLE_VMM=0` also helps. Or use `--split-mode layer`. | [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/27198)](https://github.com/ggml-org/llama.cpp/issues/27198) [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/26409)](https://github.com/ggml-org/llama.cpp/issues/26409) |
| SYCL: empty or gibberish output on hybrid models (Qwen3.5/3.6/3.8, qwen3next) | Regression reported on B60/B70; [#28227](https://github.com/ggml-org/llama.cpp/pull/28227) fixed the related Qwen3.6-35B case for one maintainer. Update to current master; if it persists, add your data to the issue. | [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/24168)](https://github.com/ggml-org/llama.cpp/issues/24168) [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/28728)](https://github.com/ggml-org/llama.cpp/issues/28728) |
| SYCL: high CPU use with large models | Caused by the host-pinned memory path for large allocations. No workaround yet; a maintainer suggested host-pinned memory should be off when USM is used. | [![](https://img.shields.io/github/issues/detail/state/ggml-org/llama.cpp/27038)](https://github.com/ggml-org/llama.cpp/issues/27038) |

### vLLM XPU

| symptom | cause / workaround | upstream |
|---|---|---|
| EngineCore hangs in `torch.xpu.graphs.replay()` under concurrent load | Open. Disabling MTP makes it rarer but doesn't stop it. | [![](https://img.shields.io/github/issues/detail/state/vllm-project/vllm/54698)](https://github.com/vllm-project/vllm/issues/54698) |
| Corrupt output with prefix caching + MTP on Qwen3.5/3.8 (hybrid GDN) | Use `intel/llm-scaler-vllm:0.26.0-b2` or later (fixes it), or the [cookbook](https://github.com/riceharvest/b70-qwen38-cookbook)'s patches, or turn off prefix caching. | [![](https://img.shields.io/github/issues/detail/state/vllm-project/vllm/53912)](https://github.com/vllm-project/vllm/issues/53912) |
| `!!!!!!` output with FP8 MoE at TP 4 | Bug in the block-FP8 GEMM. Fixed in vllm-xpu-kernels 0.1.16 ([#611](https://github.com/vllm-project/vllm-xpu-kernels/pull/611)); until then use TP 2. | [![](https://img.shields.io/github/issues/detail/state/vllm-project/vllm/59415)](https://github.com/vllm-project/vllm/issues/59415) |
| `UR OUT_OF_DEVICE_MEMORY` in docker with host-offloaded weights | Pass `-e ZE_AFFINITY_MASK=0` (pick the card explicitly). | — |
| `Unsupported quantization config: bits=4, sym=False` | Stock vLLM rejects asymmetric GPTQ. The [cookbook](https://github.com/riceharvest/b70-qwen38-cookbook) has a loader patch; an upstream fix is being tested. | — |

## Tools

- [b70-doctor](https://github.com/riceharvest/b70-doctor): read-only setup check that prints fixes; `--report` gives a bug-report environment block.
- [b70-bench](https://github.com/riceharvest/b70-bench): one standard llama.cpp benchmark (SYCL vs Vulkan, 7B/27B/MoE, 32K-depth decode) with a shared [results table](https://github.com/riceharvest/b70-bench/blob/main/RESULTS.md).
- [b70-launcher](https://github.com/SergiioB/b70-launcher): desktop launcher for B70 inference recipes.
- [turboquant-xpu](https://github.com/bryanvine/turboquant-xpu): TurboQuant KV-cache quantization ported to XPU.
- [proxmox-intel-b70-sriov](https://github.com/CraftComputing/proxmox-intel-b70-sriov): SR-IOV on the B70 in Proxmox, to split the card between VMs.

## Guides and recipes

- [Intel Arc Pro B70 Inference Cookbook](https://github.com/SergiioB/intel-arc-pro-b70-inference-cookbook) (SergiioB): the largest
  collection of measured recipes. vLLM XPU, EXL3, llama.cpp SYCL, OpenVINO, dual B70, Windows.
- [b70-qwen38-cookbook](https://github.com/riceharvest/b70-qwen38-cookbook): Qwen3.8-27B on one B70 with vLLM, at 262K
  context with vision. Asymmetric GPTQ int4, B70 attention kernels, prebuilt image.
- [Squeezing every token/s from the B70](https://github.com/ggml-org/llama.cpp/discussions/27593): llama.cpp SYCL flags and env vars, measured one at a time.
- [Unofficial Intel XPU Optimization Lab](https://github.com/steveseguin/b70-optimization-lab) (steveseguin): setup notes, repros and patches across many model lanes.
- [intel-arc-pro-b70-qwen38-vllm](https://github.com/MikeCaldera/intel-arc-pro-b70-qwen38-vllm): reproducible Qwen3.8-27B GPTQ + MTP on vLLM XPU.
- [arc-pro-b70-ubuntu-gpu-speedup-bugfixes](https://github.com/Hal9000AIML/arc-pro-b70-ubuntu-gpu-speedup-bugfixes) and
  [arc-pro-b70-inference-setup-ubuntu-server](https://github.com/Hal9000AIML/arc-pro-b70-inference-setup-ubuntu-server):
  Ubuntu Server setup, llama.cpp cherry-picks, and a SYCL-vs-Vulkan selection guide.
- [b70-setup](https://github.com/jeffgrover/b70-setup): B70 as a USB4 eGPU, llama.cpp SYCL + llama-swap.
- [gemma4-intelb70-archsetup](https://github.com/ChrisTitusTech/gemma4-intelb70-archsetup): Arch Linux + Ollama build.
- [qwen38-flash-next-b70-offload](https://github.com/sybil-solutions/qwen38-flash-next-b70-offload) (archived): a 180B MoE on one B70 with experts on NVMe.

## Models tested on a B70

| model | format | what's measured on the card |
|---|---|---|
| [Qwen3.8-27B-GPTQ-Int4-asym](https://huggingface.co/darioooooo0o/Qwen3.8-27B-GPTQ-Int4-asym) | vLLM, GPTQ int4 asym | KL 0.039 vs BF16, 262K context + vision on 32 GB, 64–128 tok/s decode |
| [Qwen3.8-27B-Uncensored-GPTQ-Int4-asym](https://huggingface.co/darioooooo0o/Qwen3.8-27B-Uncensored-GPTQ-Int4-asym) | vLLM | same recipe on the OrcaRouter finetune |
| [JEV-27B-VL-GPTQ-Int4-asym](https://huggingface.co/darioooooo0o/JEV-27B-VL-GPTQ-Int4-asym) | vLLM + LoRA | an 80 GB-card model on one B70; PubMedQA matches BF16 |
| [Lightning-4step-Qwen-Image-2.1](https://huggingface.co/darioooooo0o/Lightning-4step-Qwen-Image-2.1-Diffusers) ([GGUF](https://huggingface.co/darioooooo0o/Lightning-4step-Qwen-Image-2.1-GGUF), [ComfyUI](https://huggingface.co/darioooooo0o/Lightning-4step-Qwen-Image-2.1-ComfyUI)) | image generation | VRAM measured on a B70 (about 21.7 GB peak at 1024²) |
| any GGUF | llama.cpp / Ollama / LM Studio | 32 GB fits a 27B dense model at Q4–Q6 with long context, or a 35B-A3B MoE at Q4. [b70-bench](https://github.com/riceharvest/b70-bench/blob/main/RESULTS.md) collects comparable speeds (first results pending). |

Intel's [llm-scaler](https://github.com/intel/llm-scaler) release notes list the models Intel validates on B60/B70.

## Benchmarks

- [b70-bench results](https://github.com/riceharvest/b70-bench/blob/main/RESULTS.md) (collecting first results): SYCL and Vulkan side by side, 27B and MoE, decode after 8K/32K context, with driver and firmware per row. Run it and add yours.
- [PMZFX/intel-arc-pro-b70-benchmarks](https://github.com/PMZFX/intel-arc-pro-b70-benchmarks): many llama.cpp SYCL measurements, dual-GPU scaling, video generation.
- llama.cpp scoreboards: [Vulkan](https://github.com/ggml-org/llama.cpp/discussions/10879) and [SYCL](https://github.com/ggml-org/llama.cpp/discussions/23313) (Llama-2-7B, compare across GPUs).

## Upstream trackers

- [intel/compute-runtime](https://github.com/intel/compute-runtime/issues): Level Zero / OpenCL driver ([releases](https://github.com/intel/compute-runtime/releases))
- [drm/xe kernel issues](https://gitlab.freedesktop.org/drm/xe/kernel/-/issues): kernel driver, hangs, wedges
- [llama.cpp SYCL issues](https://github.com/ggml-org/llama.cpp/issues?q=is%3Aissue+is%3Aopen+SYCL) and the [SYCL long-term tracker](https://github.com/ggml-org/llama.cpp/discussions/5277)
- [vllm-project/vllm-xpu-kernels](https://github.com/vllm-project/vllm-xpu-kernels): vLLM's XPU kernels
- [intel/llm-scaler](https://github.com/intel/llm-scaler/issues): Intel's B60/B70 serving stack

## Contributing

Send a PR or open an issue: a guide we missed, a workaround that helped you, or a row that's wrong or out of date.
Please link the source (issue, discussion, or your own measurement). Links are checked weekly.

Maintained by [@imdariotoo](https://x.com/imdariotoo) ([riceharvest](https://github.com/riceharvest) on GitHub,
[darioooooo0o](https://huggingface.co/darioooooo0o) on Hugging Face). Content is [CC0](LICENSE).
