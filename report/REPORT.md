# Bitepedia 模型选型实验 v1 — Demo 阶段结论

**实验日期**:2026-05-17
**覆盖**:2/3 模型路径(Recraft V4 + FLUX.1 [dev] + Engrave LoRA),12/18 矩阵
**未测(等后续启动)**:GPT-Image-2 + Botanica LoRA 对照组 — 见 §3

---

## 1. 结论 — Demo 阶段三体裁的模型分配

**按体裁分配,不统一模型。**Worker 层 dispatch 时按 genre 路由 provider,不引入新依赖、不做后处理 pipeline。

| 体裁 | Demo 用什么 | 一句话理由 |
|---|---|---|
| **Anatomy**(剖面) | **FLUX.1 [dev] + Engrave LoRA** | Recraft V4 把小笼包形态画失真、馅心识别为"米饭/颗粒堆";FLUX 剖面形态准、皮褶皱 + 汤汁分层接近 1850s 解剖图谱。Anatomy 是 Bitepedia 死命题,视觉品质必须扛住 |
| **Component**(多对象) | **Recraft V4** | FLUX 在 component 体裁 2/2 出现伪艺术家签名 / 标本编号("Marmig" / "Forabb" / "DANIJ.GONI:ZWE"),系统性违反"无文字"硬锚;Recraft V4 6/6 零文字泄漏。底图假文字会跟前端 SVG 标签层冲突,Component 必须 Recraft 兜底 |
| **Ingredient**(原料 specimen row) | **FLUX.1 [dev] + Engrave LoRA** | 两者都稳定,FLUX 视觉品质略高、specimen row 构图更标准,无文字泄漏 |

---

## 2. Demo 上线后再决策的两个点

1. **是否统一切 FLUX**(架构简化):加 Botanica + Engrave 双 LoRA 重跑 component 体裁,看能否堵掉文字泄漏。能堵 → 单模型简化;堵不掉 → 保持双 provider 分发。**需要 Civitai API token**
2. **是否引入 GPT-Image-2**:若 demo 用户反馈 anatomy / component 视觉品质仍不够,补一轮 GPT-Image-2 对比。**需要 OpenAI 账号余额 + key 注入**

---

## 3. 未测部分

| 路径 | 跳过原因 | 重启条件 |
|---|---|---|
| **GPT-Image-2** (`gpt-image-2-2026-04-21`) | demo 阶段对最终交付无直接价值,不值得维护 OpenAI 账号余额 + key 注入注意力成本 | demo 上线后若需要进一步优化,加测 |
| **Botanica + Engrave 双 LoRA** | Civitai `api/download/models/1285200` 实测 401,需要 Civitai API token;单 Engrave 已通过 anatomy / ingredient 验证 | demo 上线后若想统一切 FLUX,补此对照组 |

---

## 附录 A — 实测矩阵 (12/18 张)

| 体裁 \ 模型 | Recraft V4 | FLUX dev + Engrave |
|---|---|---|
| anatomy seed1 | `output/recraft-v4/anatomy_seed1.png` | `output/flux-dev-lora/anatomy_seed1.png` |
| anatomy seed2 | `output/recraft-v4/anatomy_seed2.png` | `output/flux-dev-lora/anatomy_seed2.png` |
| component seed1 | `output/recraft-v4/component_seed1.png` | `output/flux-dev-lora/component_seed1.png` ⚠ 文字泄漏 |
| component seed2 | `output/recraft-v4/component_seed2.png` | `output/flux-dev-lora/component_seed2.png` ⚠ 文字泄漏 |
| ingredient seed1 | `output/recraft-v4/ingredient_seed1.png` | `output/flux-dev-lora/ingredient_seed1.png` |
| ingredient seed2 | `output/recraft-v4/ingredient_seed2.png` | `output/flux-dev-lora/ingredient_seed2.png` |

每张图同名 `.json` 文件记录 prompt、provider、参数、单价、latency、image_url。

## 附录 B — 实验参数(公平性约束)

- 分辨率统一 1024×1024(`square_hd`)
- Recraft V4:`style: any`(不上风格预设,跟 FLUX prompt-driven 公平)
- FLUX dev:单 LoRA(Engrave scale 0.85)+ trigger prefix `NGRVNG engrave,`,28 步,guidance 3.5
- 共用 prompt 模板:`prompts/prompts.json`(4 条 vintage 风格锚点 + 3 个体裁 subject/composition clause)
- 所有 prompt 字面相同,只换 provider —— 隔离模型变量

风格锚点(逐字落地到每条 prompt):
1. `1890s botanical specimen plate by Pierre-Joseph Redouté`
2. `hand-drawn ink line engraving with minimal watercolor wash`
3. `cream-colored aged paper, muted ochre / sepia / olive green tones`
4. `no text, no labels, no typography, no captions, no annotations`

## 附录 C — 成本

| 路径 | 张数 | 单价 (USD) | 小计 |
|---|---|---|---|
| Recraft V4 | 6 | $0.04 | $0.24 |
| FLUX dev + Engrave | 6 | $0.037 | $0.22 |
| **实际合计** | **12** | | **$0.46** |

预算上限 $8,实际占用 5.75%。
