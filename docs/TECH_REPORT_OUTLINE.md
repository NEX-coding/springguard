# 技术报告提纲（对照 AIC 参考大纲，≤15 页）

> 正文勿出现校名/校徽/指导教师。可据此扩写成 PDF。

## 1. 作品概述
- 名称：SpringGuard 智能审查增强  
- 方向：AI 开发工具与开源协作  
- 一句话：基于 Open Code Review，增加 Spring 确定性规则与可复现评测  

## 2. 问题与场景
- Spring 事务自调用、入参校验缺失、MyBatis `${}` 注入等高发  
- 纯 LLM 审查：不稳定、贵、难复核；纯静态工具：缺语义  
- 目标用户：Java/Spring 学生与中小团队  

## 3. 相关工作与开源选型
- 上游：alibaba/open-code-review（确定性工程 × Agent）  
- 对比：通用 Coding Agent、仅 Sonar 类规则  
- 选型理由：可配置规则包、JSON 输出、可接本地模型  

## 4. 方案设计
```
样例/真实 Spring 仓
   ├─ SpringGuard（自研，离线可跑）
   └─ OCR + .opencodereview/rule.json（上游 + 自研规则）
        └─ merge → 评测 / 演示页
```
- 创新点：Spring 专项确定性规则；与 OCR 混合；金标准评测  

## 5. 实现要点
- `spring_guard.py`：Controller / Service / Mapper 规则  
- 规则包：路径匹配 + merge_system_rule  
- 流水线：`run_pipeline.py`  
- 演示：`web/` + `scripts/demo.sh`  

## 6. 实验与验证
- 数据：`samples/spring-buggy` + `eval/gold.json`（6 类缺陷）  
- 指标：Recall（主）；Findings 数  
- 结果：写入 `eval/results.json` / `docs/EVAL_REPORT.md`  
  - spring_guard Recall = 1.0（本轮）  
  - OCR 作为可选增强（本地小模型耗时长，报告中说明）  

## 7. 开放成果与复用
- 仓库结构、运行说明（README）  
- CLI：`spring_guard.py` / `demo.sh`  
- 清单：`docs/开源及第三方资源使用清单.md`  

## 8. 总结与展望
- 已验证：开源审查底座 + 领域确定性规则可提升可复现性  
- 后续：扩大负例集算 Precision；CI 接入；更多 Spring 规则  

## 附件
- 资源清单、评测原始 JSON、演示截图  
