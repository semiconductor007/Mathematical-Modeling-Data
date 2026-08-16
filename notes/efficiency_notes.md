# 工程效率与专项数据记录

> **阶段状态：NOT FOR MODELING / REVIEW ONLY / NOT RAW DATA**
>
> 本轮结果仅写入 `results/efficiency_staging.csv`。在 A 的候选模型表进入 `main`、团队冻结配置并完成人工复核以前，不写入正式效率 raw 表。

## 数据来源

本阶段以 [Artificial Analysis](https://artificialanalysis.ai/) 的公开模型 provider 页面作为统一第三方效率来源。采集器只访问 `scripts/artificial_analysis_targets.json` 中人工确认的 HTTPS 页面和 provider，不根据 `model_id` 猜 URL，不访问隐藏接口，也不调用任何候选大模型。

每次成功读取均保存 HTTP 状态、UTC 检索时间、来源 URL 和响应正文 SHA-256。本轮 HTML 快照保存在仓库外的本地审计目录：`work/aa_snapshots_20260816/`；快照未加入 Git。

## 指标定义

- **Time to First Token (TTFT)**：从发送请求到收到第一个响应 token 的时间。若 reasoning 模型公开 reasoning token，则第一个 reasoning token 是 TTFT 的终点。
- **Time to First Answer Token (TTFA)**：从发送请求到收到第一个正式答案 token 的时间；对 reasoning 模型包含其 thinking 时间。TTFA 与 TTFT 是不同指标，本阶段不使用 TTFA 填写 TTFT。
- **Output Speed**：收到第一个 token 后的平均输出速度，单位 `tokens/s`。本阶段直接读取 AA 公布的 `outputSpeed.median`，不自行用 token 数除以时间。
- **End-to-End Response Time**：本阶段读取 AA 公布的 `endToEndResponseTime.totalTime`。该值是标准化 **500-token response**，包括输入处理、reasoning/thinking 和答案生成时间，不代表任意长度回答的真实总耗时，也不是本项目自行用 TTFT 与速度计算的值。

## Artificial Analysis 当前测试设置

- 默认页面 workload：约 10k input tokens，至少 1,500 output tokens；single-prompt 场景。
- 1k、10k 和 vision workload 每日约测试 8 次；页面使用过去 72 小时的中位数 P50。
- 100k workload 每周测试一次，使用过去 14 天中位数；本轮没有采集 100k workload。
- 性能测试 token 计数采用 `tiktoken o200k_base` 以统一不同模型 tokenizer。
- 对未公开全部 reasoning token 的模型，AA 使用答案 chunks 的最后 80% 计算 Output Speed。
- 模型汇总页原则上使用第一方 API；无第一方 API 时使用 providers 中位数。本轮 staging 尽量选第一方 provider，并显式记录 provider；GLM-5.2 因页面未列出第一方 provider，暂选无量化后缀的 Together AI 作为待审候选。
- 页面测试服务器位于 Google Cloud `us-central1-a`，TTFT 包含网络延迟，可能对不同 provider 产生地域偏差。

## 模型配置问题

| model_id | 本轮 staging 配置 | provider | 主要待审问题 |
|---|---|---|---|
| `kimi-k3` | AA 所示 Kimi K3 reasoning 配置 | Kimi | effort 标签未显示；provider 政策未冻结 |
| `gpt-5.6-sol` | max | OpenAI | 另有 xhigh/high/medium/non-reasoning；A 版本未编码 effort |
| `claude-fable-5` | Adaptive Reasoning、Max Effort、Opus 4.8 Fallback | Anthropic | fallback 不可与无 fallback 配置混合 |
| `claude-opus-4.8` | Adaptive Reasoning、Max Effort | Anthropic | A 版本未编码 reasoning/effort |
| `gpt-5.5` | xhigh | OpenAI | 另有 high/medium/non-reasoning；AA 已标记 deprecated |
| `glm-5.2` | max | Together AI | 多 provider、多量化部署；本轮 provider 不是已确认第一方 |
| `gemini-3.1-pro-preview` | AA 所示 reasoning 配置 | Google (AI Studio) | AI Studio 与 Vertex 尚未冻结选择规则 |
| `deepseek-v4-pro-0813` | Reasoning、Max Effort | DeepSeek | exact version 匹配，但 max-effort 横向政策未冻结 |
| `qwen3.8-2.4t-a95b` | AA 所示 reasoning 配置 | Alibaba Cloud | exact page 匹配；具体 effort 仍需人工确认 |

## 当前采集状态（2026-08-16）

staging 共 27 行，9 个模型，每个模型 3 个指标：

```text
TTFT：9/9 有数值；0/9 已冻结；9/9 需人工复核
Output Speed：9/9 有数值；0/9 已冻结；9/9 需人工复核
E2E：9/9 有数值；0/9 已冻结；9/9 需人工复核
完全缺失模型：0
```

所有 27 行均由相应 provider 的公开页面直接支持，`http_status=200`，没有空字符串、`0` 代替缺失、插值、OCR 或自行 Benchmark。所有行暂为 `candidate_compatible=false`、`manual_review_required=true`。

## 数据限制

- AA 数据是滚动值，随 provider 性能和检索时间变化；本批 `retrieval_date=2026-08-16`。
- 滚动 72 小时 P50 没有唯一单日 `measurement_date`，后续正式 raw 中应使用 `NA`，并在 `test_setting` 保留统计窗口。
- staging 保存的是公开 HTML 结构化字段的完整精度；网页界面可能对显示值做四舍五入，人工复核时需决定正式 raw 的保留精度。
- 500-token E2E 只是题目“完整回答耗时”的标准化代理变量，论文必须说明定义差异。
- provider、reasoning effort、fallback 与量化策略尚未冻结，当前 staging 不代表最终核心可比队列。
- 正式入库前必须重新核对来源页面、配置、provider、哈希和可比性，并等待 A 候选模型表进入 `main`。
