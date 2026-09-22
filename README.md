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
src/components/ValleyDetail.vue 详情抽屉（四维看板 / 防汛警示 / 美食 / 农家乐 / 周边露营地 / 亲子景点 / 网红打卡点 / 出行）
docs/VERIFICATION.md       数据核实记录（来源、已核实到什么程度、通道实测结果）
scripts/verify/gen-entities.py    导出待复核实体清单
scripts/verify/slow-verify.py     公开检索复核（慢速、可断点续跑）
scripts/verify/tag-provenance.py  回写 provenance / verify 标签到数据
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

**三类周边清单（`around`，已并入方案与实现）**：`campsites`（收费营地/野营地/房车营地三类分列）、
`family_spots`（亲子，带 `age` 适龄估算 + 看护要求）、`photo_spots`（打卡点，带 `basis` 依据）。
三者同样源自 PRD §4 初稿、同样未核实。两条已定口径（2026-09-22）：

- 打卡点**只收录有文史（碑刻/诗句/古道/古观）或地标（水库大坝/堰塞湖/瀑布/冰瀑/草甸/传统村落）依据的机位**，
  字段 `basis: historico | landmark`；主观机位（光线、水雾、拍摄时段一类）不入库，不承诺效果。
  带 `warning` 的危险机位（险道、冰瀑、国道弯道、涉水站位）前端红色劝退。
- 亲子条目**必带 `age`（建议最小年龄，估算值）** 并写明看护要求；低龄儿童不适合全程徒步的（如华山峪）明确写出。

**来源分级与核验状态（`provenance` / `verify`）**：每条实体都标了来源与核验结果，界面据此分档显示。

| 字段 | 取值 | 界面表现 |
| :--- | :--- | :--- |
| `provenance` | `prd_listed` 文档原列 / `derived` 本站归纳 | `derived` 打「整理」标签，并给出口径说明 |
| `verify.status` | `found_local` / `found_foreign` / `not_found` / `blocked` | 仅 `found_local` 正常列出（「公开可查」）；其余收进折叠区，标题写明**不作为推荐** |

核验执行方式与各公开通道的实测结果见 [docs/VERIFICATION.md](docs/VERIFICATION.md)。
复核脚本：`scripts/verify/{gen-entities,slow-verify,tag-provenance}.py`（后者会把结果回写到数据）。

## 已知待办

- [ ] 数据核实：名录权威来源、坐标逐条校对（高德坐标拾取器）、区域计数定稿
- [ ] 周边三类清单核实：露营地是否仍在营（收费/野营性质）、`age` 适龄估算与看护要求、打卡点 `basis` 依据是否成立
- [ ] 状态基线：当前封山/开放名单、状态更新责任人（暂定手改 JSON → CI 1~2 分钟生效）
- [ ] 高德 Key 配置 + Referer 白名单 + 配额告警
- [ ] 真机验证：iOS Safari / 安卓 / 微信内置浏览器（微信内 `amapuri://` 被拦，已降级为网页版）
- [ ] 实景/授权图片（当前用 SVG 山形与生成卡片）
- [ ] 数据纠错入口（GitHub Issue 模板 或 微信群）

## 免责

秦岭山区气候多变，未开发野径存在滑坡、山洪、失联风险。本站信息仅供参考，
进山前请以属地政府与应急管理部门最新通告为准。全站倡导 LNT 无痕山林。
