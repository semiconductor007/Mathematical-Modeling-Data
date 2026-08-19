第一届天津市五校数学建模联赛支撑材料说明

1. 文件夹结构
   source/  完整可运行源程序、配置文件、依赖清单与统一运行入口
   data/    论文使用的冻结原始数据、处理后数据、元数据和来源索引
   results/ 论文所依据的正式结果、稳健性结果及必要图表
   人工智能工具使用详情.pdf  AI 工具使用披露

2. 运行环境
   推荐系统：Windows 10/11 或兼容的 Python 环境
   Python：3.11 及以上
   主要依赖：见 source/requirements.txt（NumPy、pandas、Matplotlib、PyMuPDF）

3. 推荐运行顺序与主入口
   在 PowerShell 中进入 source/，执行：
       powershell -ExecutionPolicy Bypass -File .\run_all.ps1
   入口会按冻结流水线顺序完成数据处理、CRITIC、TOPSIS、场景评价、成本/Pareto、
   工程效率、回归、稳健性和可视化，并把正式输出写入外层 results/。

4. 数据边界
   数据截止日期：2026-08-17。
   原始缺失值保持为 NA，不进行估算、插值、均值填补或零值填补。
   运行程序不会抓取截止日期之后的新数据。

5. 结果说明
   论文通用能力评价、三类场景、成本/Pareto、部署效率、回归和稳健性结果均可由
   source/run_all.ps1 调用的现有程序复现。AI 详情文件不参与模型计算。
