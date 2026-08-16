# 工程效率与专项数据记录

> **阶段状态：PHASE 1 PROMOTED TO RAW**
>
> 27 条 staging 记录已逐项复核并提升为 `data/raw/cost_efficiency.csv` 的 9 条模型级记录，逐指标证据写入 `data/sources/efficiency_sources.csv`。staging 文件保留采集哈希和完整溯源，不作为正式建模输入。

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

所有 27 行均由相应 provider 的公开页面直接支持，`http_status=200`，没有空字符串、`0` 代替缺失、插值、OCR 或自行 Benchmark。正式 raw 按统一 workload 和配置政策逐模型标记 `compatible`，而不是默认放行。

## 数据限制

- AA 数据是滚动值，随 provider 性能和检索时间变化；本批 `retrieval_date=2026-08-16`。
- 滚动 72 小时 P50 没有唯一单日 `measurement_date`，后续正式 raw 中应使用 `NA`，并在 `test_setting` 保留统计窗口。
- staging 保存的是公开 HTML 结构化字段的完整精度；网页界面可能对显示值做四舍五入，人工复核时需决定正式 raw 的保留精度。
- 500-token E2E 只是题目“完整回答耗时”的标准化代理变量，论文必须说明定义差异。
- provider、reasoning effort、fallback 与量化策略已按下述配置规则冻结；`compatible=false` 的记录只作补充分析。
- 正式 raw 已复核来源页面、配置、provider、哈希和模型身份。

## Phase 2.5 配置复核结论

配置级历史复核表见 `results/efficiency_configuration_review.csv`；最终决定以正式 raw 的 `compatible` 字段和本文件的冻结规则为准。

| 队列 | 模型 | 冻结条件 |
|---|---|---|
| Core Set A / PASS | `gpt-5.6-sol` | GPT-5.6 Sol (max) / OpenAI |
| Core Set A / PASS | `claude-opus-4.8` | Adaptive Reasoning、Max Effort / Anthropic |
| Core Set A / PASS | `gpt-5.5` | xhigh / OpenAI；保留 deprecated 生命周期说明 |
| Core Set A / PASS | `deepseek-v4-pro-0813` | Reasoning、Max Effort / DeepSeek |
| Core Set B / CONDITIONAL | `kimi-k3` | 团队接受“AA 默认 reasoning 配置（无命名 effort）”作为冻结配置 |
| Core Set B / CONDITIONAL | `gemini-3.1-pro-preview` | 团队明确选用 Google AI Studio 而不是 Vertex，并接受未命名 reasoning 配置 |
| Core Set B / CONDITIONAL | `qwen3.8-2.4t-a95b` | 团队接受“AA 默认 reasoning 配置（无命名 effort）”作为冻结配置 |
| Hold | `claude-fable-5` | fallback 可能改变实际执行模型；现有页面不能分离 Fable 与 Opus 4.8 观测 |
| Hold | `glm-5.2` | Together AI 为第三方部署，具体精度/量化未披露；同页存在 FP4、FP8、NVFP4 变体 |

团队接受 Kimi 的“AA default reasoning configuration”作为命名配置，但不猜测 effort；Claude Fable 5 因 Opus fallback、GLM-5.2 因第三方部署与量化未知而保持 `compatible=false`。效率指标在 Phase 2/6 建模时须按兼容队列单独做缺失处理，不能以候选覆盖率代替配置可比性。

## Core Efficiency Configuration Proposal

1. **Exact version**：效率页面的模型身份必须严格匹配 A 候选表；不得用同系列旧版本或相似模型替代。reasoning effort 是配置标签，必须与 exact model version 一并保留。
2. **Provider**：优先级为第一方官方 API/provider、官方云平台、明确标记的第三方 provider。若有第一方性能数据，不无理由采用第三方量化部署。`Google (AI Studio)` 与 `Google (Vertex)` 即使模型 slug 相同也作为不同 provider 配置。
3. **Reasoning effort**：`max`、`xhigh`、`high`、`medium`、`low`、`non-reasoning`、`Adaptive Reasoning` 均为不同测试配置。页面未给 effort 名称时写 `NA`，只可命名为“AA default reasoning configuration”，不得猜测为 max/high。
4. **Fallback**：必须显式记录 fallback 目标。若 fallback 会改变实际执行模型身份，默认排除严格核心；只有团队明确接受“策略型路由配置”，且论文不把结果误称为单一模型性能时才可另建分析队列。
5. **Quantization / deployment**：FP4、FP8、NVFP4 等精度与 FAST 等部署标签均不可省略。没有披露具体精度时写 `NA`；第三方部署不自动视为与第一方 API 完全可比。
6. **Workload**：核心统一使用 Artificial Analysis 默认 10k input-token workload、single prompt、P50 rolling 72-hour window。不同 workload 必须标记不兼容并排除当前核心。
7. **三指标同配置**：TTFT、Output Speed、E2E 必须来自同一 exact version、configuration、provider/provider scope、workload 和统计窗口，不跨 provider 拼接。
8. **E2E 定义**：统一表述为“Artificial Analysis 标准化 500-token 端到端响应时间”（`Artificial Analysis standardized end-to-end response time for 500 output tokens`），不解释为任意回答长度的完整总耗时。

## Raw data precision policy

- TTFT raw：保存 AA 结构化字段 `timeToFirstToken.median` 的原始可用精度，单位 seconds。
- Output Speed raw：保存 `outputSpeed.median` 的原始可用精度，单位 tokens/s。
- E2E raw：保存 `endToEndResponseTime.totalTime` 的原始可用精度，单位 seconds。
- processed / paper：只在处理层或论文展示层统一舍入，建议秒数与 tokens/s 显示 2 位小数，并保留可复现的 raw 值；不为表格美观提前改写 raw 精度。

## Date policy for rolling measurements

- `measurement_date = NA`：72 小时滚动 P50 没有唯一单日测量日期。
- `retrieval_date = 2026-08-16`：表示本批公开页面的检索日期，不冒充测量日期。
- `test_setting/notes` 保留：`P50 over rolling past 72 hours, retrieved 2026-08-16`。
- 若未来来源明确给出单次测量日期，才填写对应 `measurement_date`；不得用 retrieval date 自动代替。

## Phase 2/6 使用约束

候选表、元数据表和效率表的 `model_id` 已对齐。后续只允许 `candidate_status=final` 且相应数据行 `compatible=true` 的效率记录进入严格横向分析；Fable 与 GLM 的数值可用于个案说明，不进入该队列。
