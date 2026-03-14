# Qwen3.5 Model Variants Research

## Date: 2026-03-13

## 1. Available Qwen3.5 Sizes on Ollama

All are multimodal (Text + Image), 256K context, support thinking mode:

| Tag | Size on disk | Notes |
|-----|-------------|-------|
| qwen3.5:0.8b | 1.0 GB | Smallest. Non-thinking by default. Prone to thinking loops. |
| qwen3.5:2b | 2.7 GB | Small. |
| qwen3.5:4b | 3.4 GB | Sweet spot candidate. |
| qwen3.5:9b | 6.6 GB | Default (`latest`). |
| qwen3.5:27b | 17 GB | Large. |
| qwen3.5:35b | 24 GB | MoE candidate (see below). |
| qwen3.5:122b | 81 GB | MoE candidate (see below). |
| qwen3.5:cloud | - | Cloud-hosted. |

Quantization tags available per size (example for 4b):
- `qwen3.5:4b` = q4_K_M (default, 3.4 GB)
- `qwen3.5:4b-q8_0` = Q8 (5.3 GB)
- `qwen3.5:4b-bf16` = BF16 full precision (9.3 GB)

Same pattern for 0.8b, 2b, 9b, 27b, 35b.

## 2. MoE (Mixture of Experts) Variants

Qwen3.5 uses a hybrid architecture: "Gated Delta Networks combined with sparse Mixture-of-Experts."
The 35B and 122B models are the MoE variants (following Qwen3 pattern where 30B-A3B and 235B were MoE).

- **qwen3.5:35b** - Total 35B params, likely ~3-4B active per token. Disk: 24 GB.
- **qwen3.5:122b** - Total 122B params, likely ~22B active per token. Disk: 81 GB.

The smaller models (0.8B, 2B, 4B, 9B, 27B) are dense.

Note: Even the dense models use "Gated DeltaNet" (linear attention) layers mixed with standard attention,
which is itself a form of architectural efficiency new to Qwen3.5.

## 3. Thinking Mode Details

### Default behavior per size:
- **0.8B**: Non-thinking by default (must explicitly enable thinking)
- **2B and above**: Thinking by default (must explicitly disable)

### Disabling thinking via Ollama API:
```json
// /api/chat endpoint
{
  "model": "qwen3.5:4b",
  "think": false,
  "messages": [{"role": "user", "content": "Hello!"}]
}
```

The `think` parameter works on both `/api/generate` and `/api/chat`.

### Important: Qwen3.5 does NOT support /think and /nothink soft-switch tokens
Unlike Qwen3, Qwen3.5 does NOT support inline `/think` and `/nothink` user tokens.
Thinking must be controlled via API parameters (`enable_thinking` for vLLM/OpenAI-compat, `think` for Ollama native API).

### For OpenAI-compatible endpoint (/v1/chat/completions on Ollama):
Not confirmed in Ollama docs whether `think` maps through the OpenAI-compat layer.
The vLLM/SGLang approach uses `extra_body={"enable_thinking": True/False}`.
If using Ollama's OpenAI-compat endpoint, may need to test or use the native `/api/chat` endpoint instead.

## 4. No "qwen3.5-coder" Variant

There is no separate `qwen3.5-coder` model on Ollama. The base Qwen3.5 models include coding capability natively.

## 5. Benchmark Comparison: 0.8B vs 2B vs 4B (Language, Non-Thinking Mode)

| Benchmark | Qwen3.5-0.8B | Qwen3.5-2B | Qwen3.5-4B | Qwen3-4B (for ref) |
|-----------|-------------|------------|------------|-------------------|
| MMLU-Pro | 29.7 | 55.3 | 79.1 | 69.6 |
| MMLU-Redux | 48.5 | 69.2 | 88.8 | 84.2 |
| C-Eval | 46.4 | 65.2 | 85.1 | 80.2 |
| IFEval | 52.1 | 61.2 | 89.8 | 83.4 |
| SuperGPQA | 16.9 | 30.4 | 52.9 | 42.8 |

### Key observations:
- **Qwen3.5-0.8B is very weak** in non-thinking mode (MMLU-Pro 29.7, IFEval 52.1)
- **Qwen3.5-2B** is a massive jump (MMLU-Pro 55.3, IFEval 61.2)
- **Qwen3.5-4B** is exceptional - beats Qwen3-4B on most benchmarks despite being a different generation
- Qwen3.5-0.8B is also prone to "thinking loops" when thinking is enabled

## 6. Qwen3.5-0.8B vs Qwen2.5:1.5b for Telegram Chatbot

Qwen3.5-0.8B in non-thinking mode:
- MMLU-Pro: 29.7 (very low)
- IFEval: 52.1 (barely follows instructions half the time)
- Prone to thinking loops in thinking mode
- Advantage: multimodal (can process images), 256K context

Qwen2.5:1.5B (from known benchmarks):
- MMLU-Pro: ~30-35 range
- Generally more stable at its size class

**Verdict: Qwen3.5-0.8B is NOT a clear upgrade over qwen2.5:1.5b for a chatbot.**
It trades blows at best. The 0.8B is simply too small despite the newer architecture.

## 7. Recommendation: Fastest Qwen3.5 That Beats qwen2.5:1.5b

**qwen3.5:2b with thinking disabled** is the sweet spot:
- 2.7 GB on disk (Q4_K_M default)
- MMLU-Pro 55.3 vs ~30-35 for qwen2.5:1.5b (massive improvement)
- IFEval 61.2 (decent instruction following)
- Multimodal (vision support as a bonus)
- 256K context window
- Disable thinking via `"think": false` in Ollama `/api/chat` for speed

**If you can afford slightly more RAM, qwen3.5:4b is dramatically better:**
- 3.4 GB on disk
- MMLU-Pro 79.1, IFEval 89.8 (excellent)
- Still fast on modern hardware

### Disable thinking in Ollama API call:
```json
POST http://localhost:11434/api/chat
{
  "model": "qwen3.5:2b",
  "think": false,
  "messages": [{"role": "user", "content": "Hello!"}]
}
```
