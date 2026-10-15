---
title: Nemotron 3.5 Bolt 74B-A9B (NVIDIA 24 GB GGUF) on a B70
---
# Nemotron-3.5-Bolt-74B-A9B (nvidia 24GB GGUF, 2-bit QAT) on one Intel Arc Pro B70

Measured 2026-10-15, llama.cpp master 620d2225c (needs >= cd0a5b6a1 for Bolt, 843e7dcc1 for the LiLiCorr drafter),
Vulkan backend, **Mesa 26.2.5** (Mesa 25.3.6 decodes ~40% slower: 25 vs 43 tok/s).

| | Mesa 26.2.5 | Mesa 25.3.6 |
|---|---|---|
| tg128 d=0 / 8K / 32K | **43.2 / 41.7 / 39.0** | 25.0 / 24.9 / 23.3 |
| pp512 d=0 / 8K / 32K | 680 / 526 / 326 | 768 / 606 / 303 |
| llama-server, 1 user, 512-tok answers | 42.8 code / 42.4 prose | 27.3 / 27.3 |
| + LiLiCorr drafter (n-max 6) | **54.4 code** / 42.5 prose | 32.3 / 23.5 |
| 4 parallel slots, aggregate | 81.6 (21.9 per stream) | 54.5 |
| vision (mmproj on CPU) | correct, 4.6 s | correct, 5.3 s |

VRAM with the drafter at 32K context: 22.9 GiB (fits a 24 GB card only without the drafter / with a shorter context;
32 GB cards have room). Sanity prompts (arithmetic, fact, code) all correct.

## Build

```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release && cmake --build build -j --target llama-server llama-bench
```

Use Mesa >= 26.2 (Fedora 43 updates / a Mesa PPA / a local build with `VK_DRIVER_FILES=.../intel_icd.x86_64.json`).

## Serve

```bash
hf download nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF --local-dir bolt
hf download nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-LiLiCorr-GGUF --local-dir bolt
./build/bin/llama-server -m bolt/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB.gguf \
  --mmproj bolt/mmproj-NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB.gguf --no-mmproj-offload \
  -ngl 99 -fa on -c 32768 -np 1 --jinja \
  --spec-type draft-dflash --spec-draft-model bolt/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-LiLiCorr.gguf \
  --spec-draft-ngl 99 --spec-draft-n-max 6
```

- Drop the three `--spec-draft*` lines for prose-heavy use (no gain there) or to save ~1 GB.
- `--no-mmproj-offload` keeps the 1.7 GB vision encoder on the CPU (images take ~5 s); remove it if you have VRAM to spare.
- Several users: `-np 4 -c 32768` (8K per slot) gave 81.6 tok/s total.

Measured with llama-bench and llama-server on one Arc Pro B70 (Fedora 43, kernel 7.1.8), 2026-10-15. [Back to the performance guide](../performance.md)
