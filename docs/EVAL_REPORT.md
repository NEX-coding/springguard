# SpringGuard 评测纪要

> 复现：`python3 eval/run_eval.py`（可先跑 `scripts/run_pipeline.py`）

## 设置

- 样例：`samples/spring-buggy`（人工植入 6 类 Spring 缺陷）  
- 金标准：`eval/gold.json`  
- 模式：
  1. **spring_guard**：仅确定性引擎  
  2. **ocr_only**：仅 Open Code Review（若未跑则为空）  
  3. **hybrid**：两者合并  

## 指标

本轮以 **Recall（金标准缺陷命中率）** 为主；Precision 可在扩大负例集后补充。

最新 `eval/results.json`（Guard-only 流水线）：

| 模式 | Findings | TP | Recall |
|------|----------|----|--------|
| spring_guard | 见 results | 6/6 | **1.00** |
| ocr_only（未跑 LLM 时） | 0 | 0 | 0.00 |
| hybrid | 同 Guard | 6/6 | **1.00** |

> 接入 OCR 后请重跑 `run_pipeline.py`（去掉 `--skip-ocr`）更新本表。

## 结论模板

1. Guard 对事务自调用、缺 `@Valid`、`${}` 等模式可稳定召回。  
2. OCR 适合补充语义/跨文件问题，单独使用不够稳。  
3. Hybrid 在样例上召回不低于 Guard，体现「开源 AI 审查 + 自研规则」融合价值。
