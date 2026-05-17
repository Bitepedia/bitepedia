# Bitepedia 模型选型实验 — model-selection-probe

跟 Codex 主开发线(`ai-creative-product` repo 的 `codex/bitepedia-race-mvp` 分支)物理隔离的独立实验产物。本仓库分支专门承载图像模型横评数据,**不进 Bitepedia 主 codebase**。

## 结论先行

见 [`report/REPORT.md`](./report/REPORT.md) §1。

Demo 阶段三体裁分配:
- **Anatomy / Ingredient** → FLUX.1 [dev] + Engrave LoRA
- **Component** → Recraft V4

## 仓库结构

```
prompts/        共用 prompt 模板 + 编译后的 built_prompts.json
scripts/        实验脚本(Recraft V4 / FLUX / GPT-Image-2[未跑])+ env loader
output/
  recraft-v4/   6 PNG + 6 JSON metadata ✅
  flux-dev-lora/ 6 PNG + 6 JSON metadata ✅
  gpt-image-2/  empty (未测,等后续启动)
report/         REPORT.md 最终版
```

## 复现方法

凭据来源:`/Users/staff/Projects/AI创意作品/drilldown/.dev.vars`(本地路径,不入库)。
依赖:`pip3 install fal-client requests pillow openai`。

```bash
# 重新编译 prompts(改 prompts.json 之后)
python3 scripts/build_prompts.py

# 跑 Recraft V4 全批
python3 scripts/run_recraft_v4.py

# 跑 FLUX dev + Engrave 全批(脚本内嵌 inline,见 git log)
# 跑 GPT-Image-2 全批(需要 OPENAI_API_KEY)
python3 scripts/run_gpt_image_2.py
```

## 重启条件

demo 上线后,若需要进一步优化产品架构轨的模型选型,再启 —— 此时优先补完 GPT-Image-2 + Botanica 双 LoRA 对照组(见 REPORT §2 / §3)。
