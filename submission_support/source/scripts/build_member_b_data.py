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

ALIGNED WITH MEMBER A CANDIDATE POOL (9 models):
  The model_id, model_name, provider, exact_version and release_date in this
  table now match Member A's data-benchmark branch exactly, so that all three
  raw tables (benchmark_scores, model_metadata, cost_efficiency) can be merged
  by model_id without ID conflicts.

References (retrieved 2026-08-16):
  Kimi K3                  https://www.kimi.com/blog/kimi-k3
                           https://www.kimi.com/help/kimi-api/api-troubleshooting
  GPT-5.6 Sol              https://developers.openai.com/api/docs/models/compare/
                           https://developers.openai.com/api/docs/models/gpt-5.6-sol
  Claude Fable 5           https://platform.claude.com/docs/en/about-claude/pricing
  Claude Opus 4.8          https://platform.claude.com/docs/zh-CN/about-claude/models
  GPT-5.5                  https://developers.openai.com/api/docs/models/compare/
                           https://platform.openai.com/docs/pricing/
  GLM-5.2                  https://open.bigmodel.cn/pricing
                           https://docs.bigmodel.cn/cn/guide/models/text/glm-5.2
                           https://huggingface.co/zai-org/GLM-5.2
  Gemini 3.1 Pro Preview   https://ai.google.dev/gemini-api/docs/pricing
  DeepSeek V4 Pro 0813     https://api-docs.deepseek.com/quick_start/pricing
  Qwen3.8 2.4T A95B        https://qwen.ai/blog?id=qwen3.8
                           (overseas price via https://www.globaltimes.cn/page/202608/1367420.shtml)
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
# model_id / model_name / provider / exact_version / release_date are aligned
# with Member A's data-benchmark branch (9 candidates).
# ---------------------------------------------------------------------------
METADATA = [
    {
        "model_id": "kimi-k3",
        "model_name": "Kimi K3",
        "provider": "Moonshot AI",
        "exact_version": "kimi-k3",
        "release_date": "2026-07-16",
        "context_window": 1048576,
        "max_output_tokens": 1048576,
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
        "retrieval_date": "2026-08-17",
        "notes": "Required by problem statement. 2.8T MoE (104B active); native vision (text/image/video); always-on thinking (effort low/high/max, max default). Official Kimi API docs allow max_completion_tokens up to 1,048,576; actual output is bounded by 1,048,576 minus prompt_tokens, and the default is 131,072. No batch discount found. 1M context at standard rate (no separate long-context tier found).",
    },
    {
        "model_id": "gpt-5.6-sol",
        "model_name": "GPT-5.6 Sol",
        "provider": "OpenAI",
        "exact_version": "gpt-5.6-sol",
        "release_date": "2026-07-09",
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
        "long_context_price": 10.00,
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-07-09",
        "source_url": "https://developers.openai.com/api/docs/models/gpt-5.6-sol",
        "retrieval_date": "2026-08-17",
        "notes": "Flagship frontier model. Standard rates are input $5 / cached input $0.50 / output $30 per 1M. For prompts with more than 272K input tokens, OpenAI charges 2x input and 1.5x output for the full request, i.e. $10 input and $45 output; long_context_price records the input rate. Batch = 50% off standard. Regional (data-residency) endpoints +10%. Release date 2026-07-09 aligned with Member A.",
    },
    {
        "model_id": "claude-fable-5",
        "model_name": "Claude Fable 5",
        "provider": "Anthropic",
        "exact_version": "claude-fable-5",
        "release_date": "2026-06-09",
        "context_window": 1000000,
        "max_output_tokens": 128000,
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 10.00,
        "output_price_usd_per_million": 50.00,
        "cached_input_price_usd_per_million": 1.00,
        "batch_input_price": 5.00,
        "batch_output_price": 25.00,
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-06-09",
        "source_url": "https://platform.claude.com/docs/en/about-claude/pricing",
        "retrieval_date": "2026-08-17",
        "notes": "Highest Anthropic tier (above Opus 4.8). Adaptive thinking with effort controls. AA labels Opus 4.8 Fallback safeguards that affect some evaluations; C audit flags HOLD because fallback routing frequency is not disclosed and model identity may be mixed. 1M context at standard pricing (no surcharge). Official current rates are input $10 / cached input $1 / output $50 per 1M; Batch API rates are $5 / $25.",
    },
    {
        "model_id": "claude-opus-4.8",
        "model_name": "Claude Opus 4.8",
        "provider": "Anthropic",
        "exact_version": "claude-opus-4.8",
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
        "notes": "Recommended default flagship. 1M context at standard pricing (no long-context surcharge). Cached input = prompt-cache read = 10% of input per Anthropic docs ($0.50). Batch API = 50% off. Adaptive thinking with effort controls (Adaptive Reasoning, Max Effort per AA). Release date 2026-05-28.",
    },
    {
        "model_id": "gpt-5.5",
        "model_name": "GPT-5.5",
        "provider": "OpenAI",
        "exact_version": "gpt-5.5",
        "release_date": "2026-04-23",
        "context_window": 256000,
        "max_output_tokens": 128000,
        "vision_support": "yes",
        "reasoning_support": "yes",
        "api_available": "yes",
        "input_price_usd_per_million": 3.00,
        "output_price_usd_per_million": 15.00,
        "cached_input_price_usd_per_million": 0.30,
        "batch_input_price": 1.50,
        "batch_output_price": 7.50,
        "long_context_price": "NA",
        "peak_price": "NA",
        "off_peak_price": "NA",
        "pricing_effective_date": "2026-04-23",
        "source_url": "https://developers.openai.com/api/docs/models/compare/",
        "retrieval_date": RETRIEVAL,
        "notes": "Mature OpenAI baseline model; AA marks deprecated but data was publicly verifiable before cutoff (DATA_RULES: deprecated lifecycle does not invalidate pre-cutoff evidence). Reasoning model with xhigh effort (per AA). Standard rates for context <270K; no separate long-context tier documented for this tier. Batch = 50% off standard. Regional endpoints +10%.",
    },
    {
        "model_id": "glm-5.2",
        "model_name": "GLM-5.2",
        "provider": "Z.ai",
        "exact_version": "GLM-5.2",
        "release_date": "2026-06-16",
        "context_window": 1048576,
        "max_output_tokens": 131072,
        "vision_support": "no",
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
        "pricing_effective_date": "2026-06-16",
        "source_url": "https://open.bigmodel.cn/pricing",
        "retrieval_date": "2026-08-17",
        "notes": "Provider aligned to Z.ai per Member A candidate pool (official platform: bigmodel.cn / z.ai). Official China list price is CNY: input Y8 / output Y28 / cache-hit Y2 per 1M. Converted to USD at 7.10 CNY/USD on 2026-08-16 -> $1.13 / $3.94 / $0.28 (conversion reproducible; raw CNY in notes). Official GLM-5.2 docs specify 128K maximum output, stored exactly as 131,072 tokens; the third-party 262K claim is rejected. The official Z.ai model card classifies GLM-5.2 as text generation, so vision_support=no. Release date 2026-06-16 (aligned with Member A). 1M context at standard rate.",
    },
    {
        "model_id": "gemini-3.1-pro-preview",
        "model_name": "Gemini 3.1 Pro Preview",
        "provider": "Google",
        "exact_version": "gemini-3.1-pro-preview",
        "release_date": "2026-02-19",
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
        "pricing_effective_date": "2026-02-19",
        "source_url": "https://ai.google.dev/gemini-api/docs/pricing",
        "retrieval_date": RETRIEVAL,
        "notes": "Tiered by prompt length: <=200K input $2.00 / output $12.00 / cached $0.20; >200K input $4.00 / output $18.00 / cached $0.40. long_context_price records the >200K input price; output is $18.00 (see notes). Batch = 50% off. Context window 2M per model card / secondary sources; official pricing doc lists >200K tier but does not print the window number. Max output not stated. Release date 2026-02-19 (aligned with Member A). AA separately reports AI Studio and Vertex; C audit recommends freezing AI Studio as the provider.",
    },
    {
        "model_id": "deepseek-v4-pro-0813",
        "model_name": "DeepSeek V4 Pro 0813",
        "provider": "DeepSeek",
        "exact_version": "DeepSeek V4 Pro 0813",
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
        "pricing_effective_date": "2026-08-13",
        "source_url": "https://api-docs.deepseek.com/quick_start/pricing",
        "retrieval_date": RETRIEVAL,
        "notes": "Thinking mode default. No multimodal (text-only). Prices are cache-miss (standard) rates; cached input (cache hit) = $0.003625. Peak/off-peak billing took effect 2026-08-16 16:00 UTC: PEAK input $0.44 / output $1.32; OFF-PEAK input $0.22 / output $0.66. peak_price/off_peak_price record the cache-miss INPUT prices; outputs noted here. No explicit batch discount found in retrieved docs. Release inferred from version stamp 0813 -> 2026-08-13 (aligned with Member A).",
    },
    {
        "model_id": "qwen3.8-2.4t-a95b",
        "model_name": "Qwen3.8 2.4T A95B",
        "provider": "Alibaba",
        "exact_version": "Qwen3.8 2.4T A95B",
        "release_date": "2026-08-12",
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
        "pricing_effective_date": "2026-08-12",
        "source_url": "https://qwen.ai/blog?id=qwen3.8",
        "retrieval_date": RETRIEVAL,
        "notes": "2.4T MoE (95B active); 1M context; vision (text/image) and thinking mode (reasoning_effort xhigh/medium/low). Overseas API price $2/$6, implicit cache-hit $0.25 (domestic CNY price differs: 12/36 yuan, cache-hit 1.5 yuan). Official blog does not list price; overseas price sourced from launch coverage (Global Times). No batch discount found. 1M context at standard rate. Release date 2026-08-12 (aligned with Member A).",
    },
]

# ---------------------------------------------------------------------------
# Per-field evidence. Each entry: (model_id, field, value, source_name,
# source_url, publication_date, retrieval_date, notes)
# ---------------------------------------------------------------------------
S = RETRIEVAL
SOURCES = [
    # ---- kimi-k3 ----
    ("kimi-k3", "provider, exact_version, release_date", "Moonshot AI; kimi-k3; 2026-07-16",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "Launch date 2026-07-16; weights released 2026-07-27. exact_version slug kimi-k3 aligned with Member A."),
    ("kimi-k3", "context_window", "1048576",
     "Kimi K3 official blog", "https://www.kimi.com/blog/kimi-k3", "2026-07-16", S,
     "1,048,576-token context window per Hugging Face model card cited in blog."),
    ("kimi-k3", "max_output_tokens", "1048576 (context-bound; default 131072)",
     "Kimi API troubleshooting", "https://www.kimi.com/help/kimi-api/api-troubleshooting", "2026-08-17", "2026-08-17",
     "Official docs: max_completion_tokens defaults to 131072 and can be set up to 1048576; actual output maximum equals 1048576 minus prompt_tokens."),
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
    ("gpt-5.6-sol", "provider, exact_version, release_date", "OpenAI; gpt-5.6-sol; 2026-07-09",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-07-09", S,
     "exact_version slug gpt-5.6-sol and release date 2026-07-09 aligned with Member A."),
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
     "Reasoning model; AA labels max effort."),
    ("gpt-5.6-sol", "api_available", "yes",
     "OpenAI API", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Generally available via OpenAI API."),
    ("gpt-5.6-sol", "input/output/cached input price", "5.00 / 30.00 / 0.50 USD per 1M",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Standard rates up to 272K input tokens: input $5, cached $0.50, output $30."),
    ("gpt-5.6-sol", "batch price", "input 2.50 / output 15.00 USD per 1M",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Batch API = 50% off standard."),
    ("gpt-5.6-sol", "long-context / peak-offpeak price", "input 10.00 / output 45.00 USD per 1M; peak/offpeak NA",
     "OpenAI GPT-5.6 Sol model page", "https://developers.openai.com/api/docs/models/gpt-5.6-sol", "2026-08-17", "2026-08-17",
     "Prompts with >272K input tokens are billed at 2x input and 1.5x output for the full request; no peak/off-peak price. long_context_price stores the $10 input rate."),

    # ---- claude-fable-5 ----
    ("claude-fable-5", "provider, exact_version, release_date", "Anthropic; claude-fable-5; 2026-06-09",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-06-09", S,
     "Highest Anthropic tier; released 2026-06-09. exact_version slug claude-fable-5 aligned with Member A."),
    ("claude-fable-5", "context_window", "1000000",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "1,000,000-token context window (same as Opus 4.8, Anthropic frontier standard)."),
    ("claude-fable-5", "max_output_tokens", "128000",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "128K max output tokens."),
    ("claude-fable-5", "vision_support", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Vision capable."),
    ("claude-fable-5", "reasoning_support", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Adaptive thinking with effort controls; AA labels Adaptive Reasoning, Max Effort."),
    ("claude-fable-5", "api_available", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "GA on Claude API, Bedrock, Vertex, Foundry."),
    ("claude-fable-5", "input/output/cached input price", "10.00 / 50.00 / 1.00 USD per 1M",
     "Anthropic pricing docs", "https://platform.claude.com/docs/en/about-claude/pricing", "2026-08-17", "2026-08-17",
     "Official current pricing: input $10, output $50, cache hits and refreshes $1 per 1M."),
    ("claude-fable-5", "batch price", "input 5.00 / output 25.00 USD per 1M",
     "Anthropic pricing docs", "https://platform.claude.com/docs/en/about-claude/pricing", "2026-08-17", "2026-08-17",
     "Batch API = 50% off standard."),
    ("claude-fable-5", "long-context / peak-offpeak price", "NA",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "1M context at standard rate (no surcharge); no peak/off-peak. Note: AA labels Opus 4.8 Fallback; C audit HOLD."),

    # ---- claude-opus-4.8 ----
    ("claude-opus-4.8", "provider, exact_version, release_date", "Anthropic; claude-opus-4.8; 2026-05-28",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "API ID claude-opus-4-8; exact_version slug claude-opus-4.8 aligned with Member A; released 2026-05-28."),
    ("claude-opus-4.8", "context_window", "1000000",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "1,000,000-token context window."),
    ("claude-opus-4.8", "max_output_tokens", "128000",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "128K max output tokens."),
    ("claude-opus-4.8", "vision_support", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Vision capable."),
    ("claude-opus-4.8", "reasoning_support", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Adaptive thinking with effort controls; AA labels Adaptive Reasoning, Max Effort."),
    ("claude-opus-4.8", "api_available", "yes",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "GA on Claude API, Bedrock, Vertex, Foundry."),
    ("claude-opus-4.8", "input/output/cached input price", "5.00 / 25.00 / 0.50 USD per 1M",
     "Anthropic models overview + pricing docs", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Input $5, output $25; prompt-cache read = 10% of input = $0.50."),
    ("claude-opus-4.8", "batch price", "input 2.50 / output 12.50 USD per 1M",
     "Anthropic pricing docs", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "Batch API = 50% off."),
    ("claude-opus-4.8", "long-context / peak-offpeak price", "NA",
     "Anthropic models overview", "https://platform.claude.com/docs/zh-CN/about-claude/models", "2026-08-16", S,
     "1M context at standard rate (no surcharge); no peak/off-peak."),

    # ---- gpt-5.5 ----
    ("gpt-5.5", "provider, exact_version, release_date", "OpenAI; gpt-5.5; 2026-04-23",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-04-23", S,
     "exact_version slug gpt-5.5 and release date 2026-04-23 aligned with Member A."),
    ("gpt-5.5", "context_window", "256000",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "256,000-token context window (mature tier, smaller than GPT-5.6 Sol's 1.05M)."),
    ("gpt-5.5", "max_output_tokens", "128000",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "128,000 max output tokens."),
    ("gpt-5.5", "vision_support", "yes",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "Image input supported."),
    ("gpt-5.5", "reasoning_support", "yes",
     "OpenAI model compare", "https://developers.openai.com/api/docs/models/compare/", "2026-08-16", S,
     "Reasoning model; AA labels xhigh effort. AA marks deprecated but evidence publicly verifiable before cutoff."),
    ("gpt-5.5", "api_available", "yes",
     "OpenAI API", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Available via OpenAI API (deprecated lifecycle but accessible before cutoff)."),
    ("gpt-5.5", "input/output/cached input price", "3.00 / 15.00 / 0.30 USD per 1M",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Standard rates: input $3, cached $0.30, output $15. Mature baseline pricing, below GPT-5.6 Sol ($5/$30)."),
    ("gpt-5.5", "batch price", "input 1.50 / output 7.50 USD per 1M",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "Batch API = 50% off standard."),
    ("gpt-5.5", "long-context / peak-offpeak price", "NA",
     "OpenAI API pricing", "https://platform.openai.com/docs/pricing/", "2026-08-16", S,
     "No separate long-context tier documented for this tier; no peak/off-peak."),

    # ---- glm-5.2 ----
    ("glm-5.2", "provider, exact_version, release_date", "Z.ai; GLM-5.2; 2026-06-16",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-06-16", S,
     "Provider aligned to Z.ai per Member A; official platform bigmodel.cn / z.ai. Release date 2026-06-16 aligned with Member A."),
    ("glm-5.2", "context_window", "1048576",
     "Zhipu official pricing / OpenRouter", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "1,048,576-token context window."),
    ("glm-5.2", "max_output_tokens", "131072",
     "Zhipu GLM-5.2 official model docs", "https://docs.bigmodel.cn/cn/guide/models/text/glm-5.2", "2026-06-16", "2026-08-17",
     "Official model page specifies 128K maximum output; stored as 128*1024=131072 tokens. Third-party 262K value is rejected."),
    ("glm-5.2", "vision_support", "no",
     "Z.ai official model card", "https://huggingface.co/zai-org/GLM-5.2", "2026-08-17", "2026-08-17",
     "Official Z.ai repository is classified as Text Generation and documents a text-generation pipeline; no image-input modality is listed."),
    ("glm-5.2", "reasoning_support", "yes",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "GLM supports thinking/reasoning mode."),
    ("glm-5.2", "api_available", "yes",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "Available via bigmodel.cn / Z.ai platform."),
    ("glm-5.2", "input/output/cached input price (CNY list, USD converted)", "CNY 8 / 28 / 2 -> USD 1.13 / 3.94 / 0.28 per 1M",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "Official list price CNY: input Y8, output Y28, cache-hit Y2. Converted at 7.10 CNY/USD on 2026-08-16."),
    ("glm-5.2", "batch / long-context / peak-offpeak price", "NA",
     "Zhipu official pricing", "https://open.bigmodel.cn/pricing", "2026-08-09", S,
     "No batch discount, no separate long-context tier, no peak/off-peak found in retrieved docs."),

    # ---- gemini-3.1-pro-preview ----
    ("gemini-3.1-pro-preview", "provider, exact_version, release_date", "Google; gemini-3.1-pro-preview; 2026-02-19",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-02-19", S,
     "exact_version slug gemini-3.1-pro-preview and release date 2026-02-19 aligned with Member A."),
    ("gemini-3.1-pro-preview", "context_window", "2000000",
     "Gemini model card / secondary", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "2M context per model card and secondary sources; official pricing doc prints >200K tier but not the window number."),
    ("gemini-3.1-pro-preview", "max_output_tokens", "NA",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Max output not stated in retrieved sources."),
    ("gemini-3.1-pro-preview", "vision_support", "yes",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Multimodal (text/image/audio)."),
    ("gemini-3.1-pro-preview", "reasoning_support", "yes",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Thinking/reasoning supported."),
    ("gemini-3.1-pro-preview", "api_available", "yes",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Available via Gemini Developer API (AI Studio) and Vertex AI. AA separately reports both; C audit recommends freezing AI Studio."),
    ("gemini-3.1-pro-preview", "input/output/cached input price (<=200K)", "2.00 / 12.00 / 0.20 USD per 1M",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Standard tier, prompt <=200K: input $2, output $12, cached $0.20."),
    ("gemini-3.1-pro-preview", "batch price (<=200K)", "input 1.00 / output 6.00 USD per 1M",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Batch = 50% off standard."),
    ("gemini-3.1-pro-preview", "long-context price (>200K)", "input 4.00 / output 18.00 / cached 0.40 USD per 1M",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "Prompt >200K: input $4, output $18, cached $0.40. long_context_price records input $4.00."),
    ("gemini-3.1-pro-preview", "peak-offpeak price", "NA",
     "Gemini API pricing", "https://ai.google.dev/gemini-api/docs/pricing", "2026-08-16", S,
     "No peak/off-peak; service tiers Standard/Batch/Flex/Priority instead."),

    # ---- deepseek-v4-pro-0813 ----
    ("deepseek-v4-pro-0813", "provider, exact_version, release_date", "DeepSeek; DeepSeek V4 Pro 0813; 2026-08-13",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "exact_version 'DeepSeek V4 Pro 0813' and model_id deepseek-v4-pro-0813 aligned with Member A. Version stamp 0813 -> 2026-08-13."),
    ("deepseek-v4-pro-0813", "context_window", "1000000",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "1M context length."),
    ("deepseek-v4-pro-0813", "max_output_tokens", "384000",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Max output 384K."),
    ("deepseek-v4-pro-0813", "vision_support", "no",
     "DeepSeek API docs / secondary", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "DeepSeek V4 is text-only (no multimodal) per retrieved sources."),
    ("deepseek-v4-pro-0813", "reasoning_support", "yes",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Thinking mode (default) + non-thinking. AA labels Reasoning, Max Effort."),
    ("deepseek-v4-pro-0813", "api_available", "yes",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Available via api.deepseek.com (OpenAI/Anthropic compatible)."),
    ("deepseek-v4-pro-0813", "input/output/cached input price", "0.435 / 0.87 / 0.003625 USD per 1M",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Cache-miss input $0.435, output $0.87, cache-hit input $0.003625."),
    ("deepseek-v4-pro-0813", "batch / long-context price", "NA",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "No explicit batch discount found; 1M context at standard rate."),
    ("deepseek-v4-pro-0813", "peak / off-peak price", "PEAK input 0.44 / output 1.32; OFF-PEAK input 0.22 / output 0.66 USD per 1M",
     "DeepSeek API docs", "https://api-docs.deepseek.com/quick_start/pricing", "2026-08-13", S,
     "Peak/off-peak billing effective 2026-08-16 16:00 UTC. peak/off-peak columns record cache-miss INPUT prices; outputs in notes."),

    # ---- qwen3.8-2.4t-a95b ----
    ("qwen3.8-2.4t-a95b", "provider, exact_version, release_date", "Alibaba; Qwen3.8 2.4T A95B; 2026-08-12",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "exact_version 'Qwen3.8 2.4T A95B' and model_id qwen3.8-2.4t-a95b aligned with Member A. Release date 2026-08-12."),
    ("qwen3.8-2.4t-a95b", "context_window", "1000000",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "1,000,000-token context window (config context_window: 1000000)."),
    ("qwen3.8-2.4t-a95b", "max_output_tokens", "65536",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "OpenClaw config maxTokens: 65536."),
    ("qwen3.8-2.4t-a95b", "vision_support", "yes",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "input_modalities text, image; multimodal agents."),
    ("qwen3.8-2.4t-a95b", "reasoning_support", "yes",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "enable_thinking True; reasoning_effort xhigh/medium/low. AA does not expose a named reasoning-effort level (CONDITIONAL per C audit)."),
    ("qwen3.8-2.4t-a95b", "api_available", "yes",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "QwenCloud API (OpenAI/Anthropic compatible), global nodes. Alibaba Cloud first-party per AA."),
    ("qwen3.8-2.4t-a95b", "input/output/cached input price (overseas)", "2.00 / 6.00 / 0.25 USD per 1M",
     "Global Times launch coverage", "https://www.globaltimes.cn/page/202608/1367420.shtml", "2026-08-12", S,
     "Overseas price $2/$6, implicit cache-hit $0.25. Official blog omits price; domestic CNY 12/36, cache-hit 1.5."),
    ("qwen3.8-2.4t-a95b", "batch / long-context / peak-offpeak price", "NA",
     "Qwen3.8 official blog", "https://qwen.ai/blog?id=qwen3.8", "2026-08-12", S,
     "No batch discount, no separate long-context tier, no peak/off-peak found."),
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
