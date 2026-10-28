# SpringGuard

> AIC·AI+开源参赛作品｜方向：AI 开发工具与开源协作  
> 基于阿里开源 [Open Code Review](https://github.com/alibaba/open-code-review) 的 **Spring 安全审查增强工具**

## 一句话

用 **自研 Spring 确定性规则引擎（SpringGuard）** + **上游 OCR（可选 LLM）**，专门抓 Spring 项目里的事务失效、入参未校验、MyBatis `${}` 注入等“工程味”问题，并给出可复现评测。

## 为什么不是“只跑 OCR”

| 能力 | 裸 OCR | SpringGuard 混合 |
|------|--------|------------------|
| Spring 事务自调用 | 依赖模型临场发挥 | **确定性规则可复现** |
| `@RequestBody` 缺 `@Valid` | 可能漏/飘 | **稳定命中** |
| MyBatis `${}` | 可能提到 | **强制检出** |
| 可量化评测 | 需自建 | **`eval/` 金标准 + Recall/Precision** |
| 无网/无 API Key | 难 | **Guard 可离线跑** |

## 架构

```
Spring 仓库 / samples/spring-buggy
        │
        ├─► SpringGuard（自研静态规则）──► findings.json
        │
        └─► Open Code Review（上游，可选 Ollama）
                 + .opencodereview/rule.json（Spring 规则包）
                 ──► ocr findings
        │
        └─► merge + eval（对比 Guard / OCR / Hybrid）
```

## 快速开始

### 1. 安装上游 OCR（可选，用于 LLM 审查）

```bash
npm install -g @alibaba-group/open-code-review
ocr config set custom_providers.ollama.url http://127.0.0.1:11434/v1
ocr config set custom_providers.ollama.protocol openai
ocr config set provider ollama
ocr config set model qwen3.5:4b
# Ollama 通常可用任意非空 key
ocr config set custom_providers.ollama.api_key ollama
ocr llm test
```

### 2. 只跑自研 Guard（推荐演示保底）

```bash
cd springguard
python3 scripts/spring_guard.py --project samples/spring-buggy --out out/spring_guard.json
python3 eval/run_eval.py
```

### 3. 混合流水线（Guard + OCR）

```bash
python3 scripts/run_pipeline.py --project samples/spring-buggy --skip-ocr   # 仅 Guard
python3 scripts/run_pipeline.py --project samples/spring-buggy             # Guard + OCR scan
python3 eval/run_eval.py
```

### 4. 一键 Web（本机 / 局域网他人可用）

```bash
./scripts/demo.sh
# 本机:    http://127.0.0.1:5193/
# 局域网:  http://<你的IP>:5193/
```

页面可直接：**扫描官方样例**、**上传 Spring/Java 工程 ZIP**、**跑金标准评测**。无需先手跑流水线。

演示视频：`docs/DEMO_VIDEO.mp4`  
技术报告：`docs/TECH_REPORT.md` / `docs/TECH_REPORT.pdf`  
答辩 PPT：`docs/PPT.html` / `docs/PPT.pdf`  
资源清单：`docs/开源及第三方资源使用清单.md` / `.pdf`  
报名粘贴文案：`docs/FORM_COPY.md`

> 说明：本地小模型完整 OCR scan 较慢；比赛演示以 **SpringGuard（Recall=1.0，干净样例 0 误报）** 为主。负例工程：`samples/spring-clean`。

## 自研 vs 上游

| 模块 | 归属 |
|------|------|
| `alibaba/open-code-review` CLI | 上游 Apache-2.0 |
| `.opencodereview/rule.json` Spring 规则包 | **团队** |
| `scripts/spring_guard.py` 确定性检测 | **团队** |
| `scripts/run_pipeline.py` 编排与合并 | **团队** |
| `eval/*` 金标准与评测 | **团队** |
| `samples/spring-buggy` 含缺陷样例 | **团队** |
| `web/` 结果可视化 | **团队** |

## 目录

```
.opencodereview/rule.json   OCR Spring 规则
scripts/spring_guard.py     确定性引擎
scripts/run_pipeline.py     混合流水线
samples/spring-buggy/       含 6 类典型 Bug
eval/                       gold + results
docs/                       比赛材料
web/                        演示页
```
