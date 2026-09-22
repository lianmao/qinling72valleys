# 秦岭七十二峪 · 互动导游与出游决策地图

秦岭北麓（渭南 / 西安 / 宝鸡）七十二峪的数字化名录、露营配套看板与安全状态查询。
纯静态 Jamstack 应用：无后端、无数据库，高德 JS API v2.0 打点 + 点聚合 + 一键导航。

线上地址：https://lianmao.github.io/qinling72valleys/ （GitHub Pages，main 分支推送即自动发布）

## 文档

| 文档 | 说明 |
| :--- | :--- |
| [PRD.md](PRD.md) | 产品需求规格说明书 v1.0 —— **名录正本**，第 3 节是唯一数据源 |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | 技术架构与分阶段实施计划 |
| geministudy.md | 上游原始需求稿（含已被否决的 Spring Boot / PostGIS 方案，仅存档） |

## 本地开发

```bash
npm install          # .npmrc 已指向 npmmirror
python3 scripts/gen-valleys.py   # PRD.md §3 → public/data/valleys.json
python3 scripts/gen-og.py        # → public/og.png（分享卡片，无人像/实景图，用等高线山形占位）
npm run dev          # http://localhost:5173/qinling72valleys/
npm run build        # → dist/
bash scripts/build.sh            # 安装 + 构建（带重试）
```

地图需要高德 Key，缺省时**不报错**：地图位显示「地图未启用」说明，列表/筛选/导航链接全部照常可用。

```bash
# 本地带 Key 调试
VITE_AMAP_KEY=xxx VITE_AMAP_SECURITY=yyy npm run dev
```

## 目录结构

```
scripts/gen-valleys.py     PRD 名录 → 数据（单一数据源，避免手改 JSON）
scripts/gen-og.py          生成分享卡片
public/data/valleys.json   72 峪名录（生成物，勿手改）
public/data/top10_details.json  首批 10 峪深度数据（手工维护，无联系电话字段）
src/lib/data.js            载入 + 筛选 + 状态语义
src/lib/amap.js            高德 SDK 懒加载 / 点聚合 / 区域聚焦 / 降级
src/lib/nav.js             导航唤起（含微信降级、callnative/coordinate 参数）
src/components/MapView.vue 地图视图（含无 Key 降级态）
src/components/ValleyDetail.vue 详情抽屉（四维看板 / 防汛警示 / 农家乐 / 出行）
.github/workflows/deploy.yml   构建并发布到 GitHub Pages
```

## 部署与高德 Key

CI 从仓库 Secrets 读取 Key，前端在未配置时自动降级：

- Secret `AMAP_JS_KEY` —— 高德「Web端(JS API)」Key
- Secret `AMAP_SECURITY_CODE` —— 高德安全密钥 JSCode（v2.0 必需）

静态站里 JSCode 必然暴露，必须靠高德控制台的 **Referer 白名单** 兜底：

```
lianmao.github.io/*
```

并建议在控制台设置配额上限与用量告警。个人开发者 Key 不得用于商业用途。

## ⚠️ 数据可信度声明（开发期）

`PRD.md` 第 3 节名录与坐标为**未经核实的初稿**：区域计数存在矛盾（西安 40/48、宝鸡 7/12 两种口径），
坐标疑似等步长近似值（华山峪偏西约 16km、沣峪口偏西约 7km），`竹峪` 重名两条，区县跨界归属待核。

因此数据层每条都携带：

```json
{ "source": "PRD.md §3 名录初稿", "confidence": "unverified", "verified_at": null, "needs_review": true }
```

- 状态字段 `status` 三态：`1` 开放(绿) / `0` 管制封山(红) / `null` **未核实(灰)** —— 缺省为灰灯，不默认放行。
- 界面顶部常驻黄条提示「请勿将本站坐标作为导航依据」，详情页每条同样标注来源与置信度。
- 核实一个、发布一个；在 `verified_at` 填上之前，该条数据不得作为导航或安全依据。

**农家乐范围收敛（已定）**：不收录联系电话、微信等任何联系方式（`tel` 字段已从 PRD / 计划中删除）。
只保留店名与招牌菜等文字信息，且以核实后为准；需要导航时用「在高德搜索该店名」，不做直拨。

## 已知待办

- [ ] 数据核实：名录权威来源、坐标逐条校对（高德坐标拾取器）、区域计数定稿
- [ ] 状态基线：当前封山/开放名单、状态更新责任人（暂定手改 JSON → CI 1~2 分钟生效）
- [ ] 高德 Key 配置 + Referer 白名单 + 配额告警
- [ ] 真机验证：iOS Safari / 安卓 / 微信内置浏览器（微信内 `amapuri://` 被拦，已降级为网页版）
- [ ] 实景/授权图片（当前用 SVG 山形与生成卡片）
- [ ] 数据纠错入口（GitHub Issue 模板 或 微信群）

## 免责

秦岭山区气候多变，未开发野径存在滑坡、山洪、失联风险。本站信息仅供参考，
进山前请以属地政府与应急管理部门最新通告为准。全站倡导 LNT 无痕山林。
