# 比赛对齐说明（AIC·AI+开源）

## 作品名称

SpringGuard 智能审查增强

## 参赛方向

**AI 开发工具与开源协作**

## 300 字简介草稿

Spring 应用中事务自调用、入参未校验、MyBatis 动态 SQL 注入等问题高发，通用大模型审查易漏报、不稳定且依赖网络。本作品基于阿里开源 Open Code Review，增加面向 Spring 的确定性规则引擎 SpringGuard 与项目级规则包，形成「确定性检测 + AI 深度审查」混合流水线；在含已知缺陷的样例仓库上对比 Guard / OCR / Hybrid 的召回表现，结果可复现。相对直接部署上游工具，本方案明确自研边界，突出开源底座与团队增强的融合，适合本地 Ollama 演示与校园工程落地。

## 三个答辩点

1. **上游选型**：Open Code Review（确定性工程 × Agent）适合 Code Review 场景。  
2. **自研增强**：SpringGuard 规则 + `.opencodereview/rule.json`，解决 Spring 特有缺陷可复现检出。  
3. **可验证**：`eval/gold.json` 六类缺陷，对比三种模式 Recall。

## 演示分镜（3–5 分钟）

1. 问题：Spring 线上事故类型（20s）  
2. 展示 `spring-buggy` 源码中的 Bug（40s）  
3. 跑 `spring_guard.py`，展示命中列表（60s）  
4. （可选）OCR + Spring 规则包补充语义问题（40s）  
5. 展示 `eval/results.json` 对比表（40s）  
6. 清单与自研边界（30s）

## 已产出材料

| 材料 | 路径 |
|------|------|
| 技术报告 PDF | `docs/TECH_REPORT.pdf` |
| 资源清单 | `docs/开源及第三方资源使用清单.md`（可导出 PDF） |
| 答辩 PPT | `docs/PPT.pdf` / `docs/PPT.html` |
| 视频分镜 / 静音草稿 | `docs/VIDEO_SHOTLIST.md` / `docs/DEMO_VIDEO_DRAFT.mp4` |
| 资源清单 PDF | `docs/开源及第三方资源使用清单.pdf` |
| 提交核对 | `docs/SUBMIT_CHECKLIST.md` |

## 材料注意

技术报告、视频、PPT **不要出现校名/校徽/指导教师信息**。
