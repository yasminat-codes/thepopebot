# Ollama Speed Optimization Research -- Qwen3.5 on macOS Apple Silicon

Date: 2026-03-13

## Recommendations Ranked by Expected Impact

### 1. CRITICAL: Docker Cannot Use Metal GPU (You May Be CPU-bound)
Docker on macOS has NO access to Metal GPU acceleration. This is an Apple/Docker limitation. Since you run Ollama on the host and access via `host.docker.internal`, you are fine -- the host Ollama process uses Metal. Verify this is actually working:
```bash
# Confirm Metal support
system_profiler SPDisplaysDataType | grep Metal

# Check Ollama logs for Metal initialization
# Look for "metal: initialized" in ollama serve output
```
No env vars needed -- Ollama auto-detects Apple Silicon Metal. But verify the logs.

### 2. HIGH IMPACT: Reduce Context Window (num_ctx)
Default is 4096 tokens. Reducing it is the single biggest speed lever on desktop hardware. VRAM scales linearly with context length. If your agent tasks don't need long context:
```
# In Modelfile
PARAMETER num_ctx 2048
```
Going from 4096 to 2048 roughly halves KV cache memory and noticeably speeds inference. Only reduce if your prompts + responses fit within the window.

### 3. HIGH IMPACT: Enable Flash Attention + KV Cache Quantization
As of Ollama v0.13.5 (2025), Flash Attention is enabled by default for models. Verify and also enable KV cache quantization:
```bash
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0    # Halves KV cache memory vs FP16
```
This reduces memory usage significantly, allowing more headroom for speed. Requires Flash Attention to be on.

### 4. HIGH IMPACT: Use Q4_K_M Quantization
If you're running the default (likely Q4_K_M already for smaller models, or Q8 for larger), switching to Q4_K_M gives 4-6x VRAM reduction with <1% perplexity degradation for coding tasks. Check what you're running:
```bash
ollama show qwen3.5 --modelfile
```
The 35B-A3B variant at Q4 hits 60-70+ tok/s on M4 Max via MLX, ~35 tok/s via Ollama. If you're using a larger variant, consider the 35B-A3B (Mixture of Experts, only 3B active params).

### 5. MEDIUM IMPACT: OLLAMA_KEEP_ALIVE (Eliminate Cold Starts)
Default: 5 minutes. After 5min idle, the model unloads from memory. Reloading takes seconds. Set to infinite:
```bash
export OLLAMA_KEEP_ALIVE=-1    # Never unload
```
This eliminates cold-start latency entirely. Essential if jobs arrive sporadically.

### 6. LOW-MEDIUM IMPACT: OLLAMA_NUM_PARALLEL
Default: 1. Controls max parallel requests per model. Since your Docker agent likely sends one request at a time, this is less relevant. Increasing it increases memory usage (scales by num_parallel * context_length). Leave at 1 unless you have concurrent requests.

### 7. LOW IMPACT: OLLAMA_MAX_LOADED_MODELS
Default: 3 (or 3 * num GPUs). Only relevant if running multiple different models simultaneously. If you only use qwen3.5, set to 1 to free memory:
```bash
export OLLAMA_MAX_LOADED_MODELS=1
```

### 8. Modelfile PARAMETER Tuning for Speed
```
PARAMETER num_predict 4096      # Cap max output tokens (prevents runaway generation)
PARAMETER temperature 0.1       # Lower temp = less sampling overhead (marginal)
PARAMETER top_k 40              # Restrict sampling vocabulary
PARAMETER top_p 0.9             # Nucleus sampling threshold
PARAMETER repeat_penalty 1.1    # Prevent loops that waste tokens
```
`num_predict` is useful to cap runaway outputs. The others have marginal speed impact but prevent pathological slow cases.

### 9. Alternative Models to Consider
- **qwen3.5:35b-a3b** -- MoE model, only 3B active parameters, 35B total. Very fast. 60-70 tok/s on M4 Max.
- **qwen3-coder** -- Coding-focused variant from Qwen team. Available on Ollama.
- **Qwen3-Coder-Next** -- 80B total / 3B active, optimized for agentic coding workflows. Check Ollama availability.
- **qwen3.5:9b** -- If 35B-A3B is too large, the 9B is a solid smaller option.

## Complete Recommended Setup

### Environment variables (set before `ollama serve` or in launchd plist on macOS):
```bash
export OLLAMA_KEEP_ALIVE=-1
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
```

### Modelfile for derived model:
```
FROM qwen3.5
SYSTEM "/no_think"
PARAMETER num_ctx 2048
PARAMETER num_predict 4096
```

### On macOS (launchd), set env vars via:
```bash
launchctl setenv OLLAMA_KEEP_ALIVE -1
launchctl setenv OLLAMA_FLASH_ATTENTION 1
launchctl setenv OLLAMA_KV_CACHE_TYPE q8_0
launchctl setenv OLLAMA_MAX_LOADED_MODELS 1
```
Then restart Ollama.

## Sources
- Ollama FAQ: https://docs.ollama.com/faq
- Ollama GPU docs: https://docs.ollama.com/gpu
- Ollama Performance Tuning (2026): https://dasroot.net/posts/2026/01/ollama-performance-tuning-gpu-acceleration-model-quantization/
- Apple Silicon + Docker limitation: https://chariotsolutions.com/blog/post/apple-silicon-gpus-docker-and-ollama-pick-two/
- Qwen3.5 local guide: https://insiderllm.com/guides/qwen-3-5-local-guide/
- Qwen3.5 MLX vs Ollama: https://insiderllm.com/guides/qwen35-mac-mlx-vs-ollama/
- Ollama env config source: https://github.com/ollama/ollama/blob/main/envconfig/config.go
- KV Cache Quantization: https://smcleod.net/2024/12/bringing-k/v-context-quantisation-to-ollama/
- VRAM tuning on Mac: https://blog.peddals.com/en/ollama-vram-fine-tune-with-kv-cache/
