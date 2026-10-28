# SpringGuard 评测纪要

> 复现：`python3 eval/run_eval.py`

## 设置

| 集合 | 路径 | 作用 |
|------|------|------|
| 正例（有缺陷） | `samples/spring-buggy` | 测 **Recall** |
| 负例（干净） | `samples/spring-clean` | 测 **误报 / Precision** |
| 金标准 | `eval/gold.json`（6 类缺陷） | 命中判定 |

模式：`spring_guard` / `ocr_only` / `hybrid`

## 指标

- **Recall** = 命中金标准缺陷数 / 6  
- **Precision（buggy）** = 能对应到金标准的 findings / 全部 findings  
- **Precision（clean）** = clean 上 0 findings 则为 1.0  
- **precision_with_clean** = 综合 buggy 匹配 findings 与 clean 误报  

## 最新结果（`eval/results.json`）

| 模式 | Findings | TP | Recall | Precision |
|------|----------|----|--------|-----------|
| spring_guard | 7 | 6/6 | **1.00** | **1.00**（含 clean） |
| ocr_only（未跑 LLM） | 0 | 0 | 0.00 | — |
| hybrid | 7 | 6/6 | **1.00** | 1.00 |
| spring-clean | **0** | — | — | **1.00**（无误报） |

## 结论

1. Guard 对六类 Spring 高发缺陷可稳定召回。  
2. 在对照干净工程上当前规则 **0 误报**。  
3. OCR 适合语义补充；本轮演示以 Guard 为主。  
