# 演示脚本（3–5 分钟）

## 开场（20s）
Spring 项目里常见：事务自调用失效、`@RequestBody` 没校验、MyBatis `${}` 注入。  
通用 AI 审查不稳定；我们基于阿里开源 **Open Code Review**，加上自研 **SpringGuard**。

## 展示缺陷样例（40s）
打开 `samples/spring-buggy`：
1. `UserController`：缺 `@Valid` + `name.toLowerCase()` NPE  
2. `UserService`：`this.saveInternal` 事务自调用 + catch 吞异常 + SQL 拼接  
3. `UserMapper`：`@Select("${clause}")`

## 跑自研引擎（60s）
```bash
python3 scripts/run_pipeline.py --skip-ocr
python3 eval/run_eval.py
```
强调：**无大模型也能稳定检出**，`eval/results.json` 中 spring_guard Recall = 1.0。

## 可选：接上游 OCR（40s）
说明已配置 Ollama；规则包在 `.opencodereview/rule.json`。  
若时间紧，展示配置与规则文件即可，不必等长推理。

## 演示页（30s）
打开 http://127.0.0.1:5193/ → 加载 `merged.json` → 看严重级别列表。

## 自研边界（30s）
- 上游：Open Code Review（Apache-2.0）  
- 自研：SpringGuard、规则包、评测、样例、演示页  
对照 `docs/开源及第三方资源使用清单.md`

## 收尾（20s）
价值：把「开源 AI 审查底座」变成「可复现的 Spring 工程安全网」。
