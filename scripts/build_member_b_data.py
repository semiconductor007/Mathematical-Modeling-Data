"""Build Member B raw metadata and source-evidence tables.

This script encodes *verified, source-backed* data gathered from official
model/pricing pages and reputable launch coverage, retrieved on 2026-08-16
(DATA_CUTOFF_DATE = 2026-08-17). It writes:

  data/raw/model_metadata.csv      -- one row per candidate model
  data/sources/metadata_sources.csv -- per-field evidence (one row per field)

Every numeric value is either a real number or the literal "NA" (never
imputed). Each metadata field has a corresponding evidence row in
metadata_sources.csv. The script is the single source of truth so the CSVs
stay reproducible and auditable.

References (retrieved 2026-08-16):
  Kimi K3            https://www.kimi.com/blog/kimi-k3
  GPT-5.6 Sol        https://developers.openai.com/api/docs/models/compare/
                     https://platform.openai.com/docs/pricing/
  Claude Opus 4.8    https://platform.claude.com/docs/zh-CN/about-claude/models
  Gemini 3.1 Pro     https://ai.google.dev/gemini-api/docs/pricing
  DeepSeek V4 Pro    https://api-docs.deepseek.com/quick_start/pricing
  Qwen3.8-Max        https://qwen.ai/blog?id=qwen3.8
                     (overseas price via https://www.globaltimes.cn/page/202608/1367420.shtml)
  GLM-5.2            https://open.bigmodel.cn/pricing
  Grok 4.6           https://docs.x.ai/developers/pricing
                     https://x.ai/news/grok-4-6
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETRIEVAL = "2026-08-16"

# CNY -> USD conversion used only for Zhipu (official list price is in CNY).
CNY_USD = 7.10  # approx. spot rate on retrieval date; documented in notes.

# ---------------------------------------------------------------------------
# Raw metadata: one row per candidate model (Member B scope).
# All prices are USD / 1M tokens. NA = not disclosed / not verified.
# ---------------------------------------------------------------------------
METADATA = [
    {
        "model_id": "kimi-k3",
        "model_name": "Kimi K3",
        "provider": "Moonshot AI",
        "exact_version": "Kimi K3",
        "release_date": "2026-07-16",
        "context_window": 1048576,
        "max_output_tokens": 33000,
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 3.00,
        "output_price_usd_per_million": 15.00,
        "cached_input_price_usd_per_million": 0.30,
        "batch_input_price": "NA",
        "batch_output_price": "NA",
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-07-16",
        "source_url": "https://www.kimi.com/blog/kimi-k3",
        "retrieval_date": RETRIEVAL,
        "notes": "Required by problem statement. 2.8T MoE (104B active); native vision (text/image/video); always-on thinking (effort low/high/max, max default). Max output 33K from secondary aggregator (swfte.com); official blog did not state it. No batch discount found. 1M context at standard rate (no separate long-context tier found).",
    },
    {
        "model_id": "gpt-5.6-sol",
        "model_name": "GPT-5.6 Sol",
        "provider": "OpenAI",
        "exact_version": "GPT-5.6 Sol",
        "release_date": "NA",
        "context_window": 1050000,
        "max_output_tokens": 128000,
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 5.00,
        "output_price_usd_per_million": 30.00,
        "cached_input_price_usd_per_million": 0.50,
        "batch_input_price": 2.50,
        "batch_output_price": 15.00,
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": RETRIEVAL,
        "source_url": "https://developers.openai.com/api/docs/models/compare/",
        "retrieval_date": RETRIEVAL,
        "notes": "Flagship frontier model. Standard rates shown are for context <270K; OpenAI applies a separate long-context (>270K) tier whose exact values were not captured at retrieval (verify on pricing page) -> long_context_price NA. Batch = 50% off standard. Regional (data-residency) endpoints +10%. Release date not confirmed in retrieved sources.",
    },
    {
        "model_id": "claude-opus-4-8",
        "model_name": "Claude Opus 4.8",
        "provider": "Anthropic",
        "exact_version": "Claude Opus 4.8 (API ID claude-opus-4-8)",
        "release_date": "2026-05-28",
        "context_window": 1000000,
        "max_output_tokens": 128000,
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 5.00,
        "output_price_usd_per_million": 25.00,
        "cached_input_price_usd_per_million": 0.50,
        "batch_input_price": 2.50,
        "batch_output_price": 12.50,
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-05-28",
        "source_url": "https://platform.claude.com/docs/zh-CN/about-claude/models",
        "retrieval_date": RETRIEVAL,
        "notes": "Recommended default flagship. 1M context at standard pricing (no long-context surcharge). Cached input = prompt-cache read = 10% of input per Anthropic docs ($0.50). Batch API = 50% off. Adaptive thinking with effort controls. Release date 2026-05-28 (metacto/usagepricing).",
    },
    {
        "model_id": "gemini-3.1-pro",
        "model_name": "Gemini 3.1 Pro",
        "provider": "Google",
        "exact_version": "Gemini 3.1 Pro Preview (gemini-3.1-pro-preview)",
        "release_date": "NA",
        "context_window": 2000000,
        "max_output_tokens": "NA",
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 2.00,
        "output_price_usd_per_million": 12.00,
        "cached_input_price_usd_per_million": 0.20,
        "batch_input_price": 1.00,
        "batch_output_price": 6.00,
        "long_context_price": 4.00,
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": RETRIEVAL,
        "source_url": "https://ai.google.dev/gemini-api/docs/pricing",
        "retrieval_date": RETRIEVAL,
        "notes": "Tiered by prompt length: <=200K input $2.00 / output $12.00 / cached $0.20; >200K input $4.00 / output $18.00 / cached $0.40. long_context_price records the >200K input price; output is $18.00 (see notes). Batch = 50% off. Context window 2M per model card / secondary sources; official pricing doc lists >200K tier but does not print the window number. Max output not stated. Release date not confirmed.",
    },
    {
        "model_id": "deepseek-v4-pro",
        "model_name": "DeepSeek V4 Pro",
        "provider": "DeepSeek",
        "exact_version": "DeepSeek-V4-Pro-0813",
        "release_date": "2026-08-13",
        "context_window": 1000000,
        "max_output_tokens": 384000,
        "vision_support": "no",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 0.435,
        "output_price_usd_per_million": 0.87,
        "cached_input_price_usd_per_million": 0.003625,
        "batch_input_price": "NA",
        "batch_output_price": "NA",
        "long_context_price": "NA",
        "peak_price": 0.44,
        "off_peak_price": 0.22,
        "pricing_effective_date": "2026-08-16",
        "source_url": "https://api-docs.deepseek.com/quick_start/pricing",
        "retrieval_date": RETRIEVAL,
        "notes": "Thinking mode default. No multimodal (text-only). Prices are cache-miss (standard) rates; cached input (cache hit) = $0.003625. Peak/off-peak billing took effect 2026-08-16 16:00 UTC: PEAK input $0.44 / output $1.32; OFF-PEAK input $0.22 / output $0.66. peak_price/off_peak_price record the cache-miss INPUT prices; outputs noted here. No explicit batch discount found in retrieved docs. Release inferred from version stamp 0813.",
    },
    {
        "model_id": "qwen3.8-max",
        "model_name": "Qwen3.8-Max",
        "provider": "Alibaba (Qwen Team / QwenCloud / DashScope)",
        "exact_version": "Qwen3.8-Max",
        "release_date": "2026-08-03",
        "context_window": 1000000,
        "max_output_tokens": 65536,
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 2.00,
        "output_price_usd_per_million": 6.00,
        "cached_input_price_usd_per_million": 0.25,
        "batch_input_price": "NA",
        "batch_output_price": "NA",
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-08-03",
        "source_url": "https://qwen.ai/blog?id=qwen3.8",
        "retrieval_date": RETRIEVAL,
        "notes": "2.4T MoE (95B active); 1M context; vision (text/image) and thinking mode (reasoning_effort xhigh/medium/low). Overseas API price $2/$6, implicit cache-hit $0.25 (domestic CNY price differs: 12/36 yuan, cache-hit 1.5 yuan). Official blog does not list price; overseas price sourced from launch coverage (Global Times). No batch discount found. 1M context at standard rate.",
    },
    {
        "model_id": "glm-5.2",
        "model_name": "GLM-5.2",
        "provider": "Zhipu AI",
        "exact_version": "GLM-5.2",
        "release_date": "NA",
        "context_window": 1048576,
        "max_output_tokens": 128000,
        "vision_support": "NA",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 1.13,
        "output_price_usd_per_million": 3.94,
        "cached_input_price_usd_per_million": 0.28,
        "batch_input_price": "NA",
        "batch_output_price": "NA",
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-08-09",
        "source_url": "https://open.bigmodel.cn/pricing",
        "retrieval_date": RETRIEVAL,
        "notes": "Official list price is CNY: input Y8 / output Y28 / cache-hit Y2 per 1M. Converted to USD at 7.10 CNY/USD on 2026-08-16 -> $1.13 / $3.94 / $0.28 (conversion is reproducible; raw CNY kept in notes). Max output 128K from official pricing-page mirror (OpenRouter lists 262K - conflict noted in metadata_notes). Modality not explicitly confirmed (GLM-5.1 documented text-only) -> vision_support NA. Release date not confirmed. 1M context at standard rate.",
    },
    {
        "model_id": "grok-4.6",
        "model_name": "Grok 4.6",
        "provider": "xAI",
        "exact_version": "Grok 4.6 (grok-4.6)",
        "release_date": "2026-08-12",
        "context_window": 500000,
        "max_output_tokens": "NA",
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 2.00,
        "output_price_usd_per_million": 6.00,
        "cached_input_price_usd_per_million": 0.50,
        "batch_input_price": "NA",
        "batch_output_price": "NA",
        "long_context_price": 4.00,
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-08-12",
        "source_url": "https://docs.x.ai/developers/pricing",
        "retrieval_date": RETRIEVAL,
        "notes": "Short context (<200K input): input $2.00 / cached $0.50 / output $6.00. Long context (>=200K input): input $4.00 / cached $1.00 / output $12.00 -> long_context_price records the >=200K INPUT price; output $12.00 (notes). No published output cap. No Batch discount for 4.6 in retrieved docs. Instead of peak/off-peak, xAI offers Priority Processing at 2x standard (noted, peak/off-peak NA). Reasoning levels low/medium/high/xhigh. Vision: text + image input.",
    },
]

# ---------------------------------------------------------------------------
# Per-field evidence. Each entry: (model_id, field, value, source_name,
# source_url, publication_date, retrieval_date, notes)
# ---------------------------------------------------------------------------
S = RETRIEVAL
SOURCES = [
    # ---- kimi-k3 ----
    ("kimi-k3", "provider, exact_version, release_date", "Moonshot AI; Kimi K3; 2026-07-16",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "Launch date 2026-07-16; weights released 2026-07-27."),
    ("kimi-k3", "context_window", "1048576",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "1,048,576-token context window per Hugging Face model card cited in blog."),
    ("kimi-k3", "max_output_tokens", "33000",
     "Swfte AI Model Directory (secondary)", "https://www.swfte.com/zh/ai/models/moonshot-kimi-k3", "2026-08-16", S,
     "33K max output from secondary aggregator; official blog did not state it - single source, flagged."),
    ("kimi-k3", "vision_support", "yes",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "Native multimodal: text, image, video input."),
    ("kimi-k3", "reasoning_support", "yes",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "Always-on thinking; effort low/high/max (max default)."),
    ("kimi-k3", "api_available", "yes",
     "Kimi API Platform", "https://platform.kimi.ai/", "2026-07-16", S,
     "Available via Kimi API, OpenRouter, GitHub Copilot (Fireworks), Perplexity."),
    ("kimi-k3", "input/output/cached input price", "3.00 / 15.00 / 0.30 USD per 1M",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "Standard API: input $3, cached input $0.30, output $15 per 1M tokens."),
    ("kimi-k3", "batch / long-context / peak-offpeak price", "NA",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "No batch discount, no separate long-context tier, no peak/off-peak found at retrieval."),

    # ---- gpt-5.6-sol ----
    ("gpt-5.6-sol", "provider, exact_version, release_date", "OpenAI; GPT-5.6 Sol; NA",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "Release date not confirmed in retrieved sources."),
    ("gpt-5.6-sol", "context_window", "1050000",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "1,050,000-token context window."),
    ("gpt-5.6-sol", "max_output_tokens", "128000",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "128,000 max output tokens."),
    ("gpt-5.6-sol", "vision_support", "yes",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "Image input supported."),
    ("gpt-5.6-sol", "reasoning_support", "yes",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "Reasoning model."),
    ("gpt-5.6-sol", "api_available", "yes",
     "OpenAI API", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Generally available via OpenAI API."),
    ("gpt-5.6-sol", "input/output/cached input price", "5.00 / 30.00 / 0.50 USD per 1M",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Standard rates for context <270K: input $5, cached $0.50, output $30."),
    ("gpt-5.6-sol", "batch price", "input 2.50 / output 15.00 USD per 1M",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Batch API = 50% off standard."),
    ("gpt-5.6-sol", "long-context / peak-offpeak price", "NA",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Long-context (>270K) tier exists but exact values not captured at retrieval; no peak/off-peak. NA pending verification."),

    # ---- claude-opus-4-8 ----
    ("claude-opus-4-8", "provider, exact_version, release_date", "Anthropic; Claude Opus 4.8; 2026-05-28",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "API ID claude-opus-4-8; released 2026-05-28 per secondary launch coverage."),
    ("claude-opus-4-8", "context_window", "1000000",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "1,000,000-token context window."),
    ("claude-opus-4-8", "max_output_tokens", "128000",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "128K max output tokens."),
    ("claude-opus-4-8", "vision_support", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Vision capable."),
    ("claude-opus-4-8", "reasoning_support", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Adaptive thinking with effort controls."),
    ("claude-opus-4-8", "api_available", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "GA on Claude API, Bedrock, Vertex, Foundry."),
    ("claude-opus-4-8", "input/output/cached input price", "5.00 / 25.00 / 0.50 USD per 1M",
     "Anthropic models overview + pricing docs", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Input $5, output $25; prompt-cache read = 10% of input = $0.50."),
    ("claude-opus-4-8", "batch price", "input 2.50 / output 12.50 USD per 1M",
     "Anthropic pricing docs", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Batch API = 50% off."),
    ("claude-opus-4-8", "long-context / peak-offpeak price", "NA",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "1M context at standard rate (no surcharge); no peak/off-peak."),

    # ---- gemini-3.1-pro ----
    ("gemini-3.1-pro", "provider, exact_version, release_date", "Google; Gemini 3.1 Pro Preview; NA",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "gemini-3.1-pro-preview; release date not confirmed."),
    ("gemini-3.1-pro", "context_window", "2000000",
     "Gemini model card / secondary", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "2M context per model card and secondary sources; official pricing doc prints >200K tier but not the window number."),
    ("gemini-3.1-pro", "max_output_tokens", "NA",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Max output not stated in retrieved sources."),
    ("gemini-3.1-pro", "vision_support", "yes",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Multimodal (text/image/audio)."),
    ("gemini-3.1-pro", "reasoning_support", "yes",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Thinking/reasoning supported."),
    ("gemini-3.1-pro", "api_available", "yes",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Available via Gemini Developer API and Vertex AI."),
    ("gemini-3.1-pro", "input/output/cached input price (<=200K)", "2.00 / 12.00 / 0.20 USD per 1M",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Standard tier, prompt <=200K: input $2, output $12, cached $0.20."),
    ("gemini-3.1-pro", "batch price (<=200K)", "input 1.00 / output 6.00 USD per 1M",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Batch = 50% off standard."),
    ("gemini-3.1-pro", "long-context price (>200K)", "input 4.00 / output 18.00 / cached 0.40 USD per 1M",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Prompt >200K: input $4, output $18, cached $0.40. long_context_price records input $4.00."),
    ("gemini-3.1-pro", "peak-offpeak price", "NA",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "No peak/off-peak; service tiers Standard/Batch/Flex/Priority instead."),

    # ---- deepseek-v4-pro ----
    ("deepseek-v4-pro", "provider, exact_version, release_date", "DeepSeek; DeepSeek-V4-Pro-0813; 2026-08-13",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Version stamp 0813 -> 2026-08-13."),
    ("deepseek-v4-pro", "context_window", "1000000",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "1M context length."),
    ("deepseek-v4-pro", "max_output_tokens", "384000",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Max output 384K."),
    ("deepseek-v4-pro", "vision_support", "no",
     "DeepSeek API docs / secondary", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "DeepSeek V4 is text-only (no multimodal) per retrieved sources."),
    ("deepseek-v4-pro", "reasoning_support", "yes",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Thinking mode (default) + non-thinking."),
    ("deepseek-v4-pro", "api_available", "yes",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Available via api.deepseek.com (OpenAI/Anthropic compatible)."),
    ("deepseek-v4-pro", "input/output/cached input price", "0.435 / 0.87 / 0.003625 USD per 1M",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Cache-miss input $0.435, output $0.87, cache-hit input $0.003625."),
    ("deepseek-v4-pro", "batch / long-context price", "NA",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "No explicit batch discount found; 1M context at standard rate."),
    ("deepseek-v4-pro", "peak / off-peak price", "PEAK input 0.44 / output 1.32; OFF-PEAK input 0.22 / output 0.66 USD per 1M",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Peak/off-peak billing effective 2026-08-16 16:00 UTC. peak/off-peak columns record cache-miss INPUT prices; outputs in notes."),

    # ---- qwen3.8-max ----
    ("qwen3.8-max", "provider, exact_version, release_date", "Alibaba Qwen; Qwen3.8-Max; 2026-08-03",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "Released 2026-08-03."),
    ("qwen3.8-max", "context_window", "1000000",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "1,000,000-token context window (config context_window: 1000000)."),
    ("qwen3.8-max", "max_output_tokens", "65536",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "OpenClaw config maxTokens: 65536."),
    ("qwen3.8-max", "vision_support", "yes",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "input_modalities text, image; multimodal agents."),
    ("qwen3.8-max", "reasoning_support", "yes",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "enable_thinking True; reasoning_effort xhigh/medium/low."),
    ("qwen3.8-max", "api_available", "yes",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "QwenCloud API (OpenAI/Anthropic compatible), global nodes."),
    ("qwen3.8-max", "input/output/cached input price (overseas)", "2.00 / 6.00 / 0.25 USD per 1M",
     "Global Times launch coverage", "https://www.globaltimes.cn/page/202608/1367420.shtml", "2026-08-03", S,
     "Overseas price $2/$6, implicit cache-hit $0.25. Official blog omits price; domestic CNY 12/36, cache-hit 1.5."),
    ("qwen3.8-max", "batch / long-context / peak-offpeak price", "NA",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-03", S,
     "No batch discount, no separate long-context tier, no peak/off-peak found."),

    # ---- glm-5.2 ----
    ("glm-5.2", "provider, exact_version, release_date", "Zhipu AI; GLM-5.2; NA",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "Release date not confirmed in retrieved sources."),
    ("glm-5.2", "context_window", "1048576",
     "Zhipu official pricing / OpenRouter", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "1,048,576-token context window."),
    ("glm-5.2", "max_output_tokens", "128000",
     "Zhipu pricing mirror (llmcostcalc)", "https://llmcostcalc.com/cloud/zhipu", "2026-08-03", S,
     "128K max output per official pricing-page mirror; OpenRouter lists 262K (conflict noted in metadata_notes)."),
    ("glm-5.2", "vision_support", "NA",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "Modality not explicitly confirmed (GLM-5.1 documented text-only)."),
    ("glm-5.2", "reasoning_support", "yes",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "GLM supports thinking/reasoning mode."),
    ("glm-5.2", "api_available", "yes",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "Available via bigmodel.cn / Z.AI platform."),
    ("glm-5.2", "input/output/cached input price (CNY list, USD converted)", "CNY 8 / 28 / 2 -> USD 1.13 / 3.94 / 0.28 per 1M",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "Official list price CNY: input Y8, output Y28, cache-hit Y2. Converted at 7.10 CNY/USD on 2026-08-16."),
    ("glm-5.2", "batch / long-context / peak-offpeak price", "NA",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "No batch discount, no separate long-context tier, no peak/off-peak found in retrieved docs."),

    # ---- grok-4.6 ----
    ("grok-4.6", "provider, exact_version, release_date", "xAI; Grok 4.6; 2026-08-12",
     "xAI Grok 4.6 launch", "https://x.ai/news/grok-4-6", "2026-08-12", S,
     "Released 2026-08-12; API ID grok-4.6."),
    ("grok-4.6", "context_window", "500000",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "500,000-token context window."),
    ("grok-4.6", "max_output_tokens", "NA",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "No published output cap."),
    ("grok-4.6", "vision_support", "yes",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "Text + image input."),
    ("grok-4.6", "reasoning_support", "yes",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "Reasoning levels low/medium/high/xhigh."),
    ("grok-4.6", "api_available", "yes",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "xAI API, OpenRouter, Vercel, Cloudflare, Cursor."),
    ("grok-4.6", "input/output/cached input price (short <200K)", "2.00 / 6.00 / 0.50 USD per 1M",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "Short context (<200K input): input $2, cached $0.50, output $6."),
    ("grok-4.6", "batch price", "NA",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "Grok 4.6 not in Batch discount table at retrieval."),
    ("grok-4.6", "long-context price (>=200K)", "input 4.00 / output 12.00 / cached 1.00 USD per 1M",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "Prompt >=200K: input $4, cached $1, output $12. long_context_price records input $4.00."),
    ("grok-4.6", "peak-offpeak price", "NA (Priority Processing 2x)",
     "xAI API docs", "https://docs.x.ai/developers/pricing", "2026-08-12", S,
     "No peak/off-peak; Priority Processing at 2x standard rates."),
]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    meta_path = ROOT / "data/raw/model_metadata.csv"
    write_csv(meta_path, list(METADATA[0].keys()), METADATA)
    print(f"Wrote {len(METADATA)} metadata row(s) to {meta_path}")

    src_path = ROOT / "data/sources/metadata_sources.csv"
    src_fields = ["model_id", "field", "value", "source_name", "source_url",
                  "publication_date", "retrieval_date", "notes"]
    src_rows = [dict(zip(src_fields, rec)) for rec in SOURCES]
    write_csv(src_path, src_fields, src_rows)
    print(f"Wrote {len(src_rows)} source-evidence row(s) to {src_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
