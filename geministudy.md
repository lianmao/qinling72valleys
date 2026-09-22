

---

## 秦岭七十二峪互动导游系统（Antigravity 专案规格书）

## 1. 业务需求说明（Requirement Definition）

## 1.1 项目背景与目标

本项目旨在打造一个聚焦于秦岭北麓（西安、宝鸡、渭南段）七十二峪的数字化互动导游与户外决策平台。通过结构化呈现各峪口的露营配套、徒步路线、当地美食及即时安全管制状态，解决用户户外出游信息碎片化、安全盲区多的痛点。

## 1.2 核心史诗与用户故事（Epics & User Stories）

## Epic 1：空间检索与高德地图联动

- US-1.1（行政区划筛选）：用户能通过选择“西安市（48峪）”、“宝鸡市（12峪）”、“渭南市（12峪）”快速切换地图视觉焦点，高德地图自动执行 Panning 与 Zoom 动画。
- US-1.2（点聚合海量渲染）：当地图层级缩小（远景）时，密集峪口需自动聚合成带有数字的集群图标；放大（近景）时展开具体峪口（Marker）。
- US-1.3（地图交互弹窗）：点击特定峪口 Marker 需弹出高德 InfoWindow，展示该峪口的核心摘要（如：子午峪 - 荔枝道历史、金仙观）。

## Epic 2：高精度露营配套指标

- US-2.1（露营设施四维看板）：峪口详情页须强制展示露营核心配置标签（是否可过夜、有无水源、车辆直达/需徒步、有无公共厕所）。
- US-2.2（营地评级与免责提示）：区分“成熟收费营地”与“野外自建营地”，对无组织野营点进行免责与环保（无痕山林）提示。

## Epic 3：动态安全预警与防汛风控

- US-3.1（红绿灯管制状态）：系统根据后台或气象接口，实时变更峪口状态（绿灯：通行无阻；红灯：汛期封山/冬季结冰管制）。
- US-3.2（河滩夜宿高危警告）：针对存在山洪、落石风险的河滩自建营地，在露营板块强制弹出黄色高亮警告：“禁止河滩夜宿”。

## Epic 4：自驾导航与出行周边

- US-4.1（高德一键拉起导航）：提供“高德导航”按钮，点击后根据峪口经纬度，移动端唤起高德地图 App，网页端跳转至高德 Web 导航。
- US-4.2（在地美食与农家乐）：展示峪口周边特色美食标签（如：沣峪锅盔、大峪鳟鱼）及推荐农家乐列表。

---

## 2. 技术方案与系统架构（Technical Solution）

## 2.1 技术选型（Tech Stack Summary）

|架构层级|推荐选型|方案选型理由与 Antigravity 部署角色|
|---|---|---|
|前端 (Frontend)|Vue 3 + TailwindCSS + 高德 JS API v2.0|完全免费且额度充足。利用 Web 端 SDK 动态渲染点聚合、自定义多样式标记（Marker）与轻量信息窗。|
|网关 (Gateway)|Spring Cloud Gateway / MSE|负责外部天气/防汛接口调用的限流、安全鉴权与动态路由分发。|
|微服务 (Backend)|Spring Boot / Go-Kratos|拆分为 `Valley-Service`（空间数据）、`Camp-Service`（露营设施）、`Risk-Service`（天气与红绿灯管制）。|
|空间数据库|PostgreSQL + PostGIS 扩展|用于精准存储和检索秦岭七十二峪的 空间几何点（WGS84 坐标系/火星坐标系）。支持地理围栏计算。|
|缓存 (Cache)|Redis (ApsaraDB for Redis)|缓存高德地理编码数据、各峪口当日天气与实时防汛红绿灯状态，降低 PostGIS 压力。|

## 2.2 核心数据模型设计 (Data Model)

## 峪口主表 (PostgreSQL / `t_qinling_valley`)

```sql
CREATE TABLE t_qinling_valley (
    valley_id VARCHAR(64) PRIMARY KEY,
    valley_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL, -- 西安/宝鸡/渭南
    geom GEOMETRY(Point, 4326),  -- 空间地理坐标点
    hiking_difficulty VARCHAR(20),-- 徒步难度：休閒/進階/專業
    status INT DEFAULT 1        -- 1:开放(绿灯), 0:管制(红灯)
);
```

## 露营配套详情表 (`t_valley_campsite`)

```json
{
  "valley_id": "VALLEY_012_CHANGAN_XI_AN",
  "camp_id": "CAMP_001_DAYU_STAR",
  "camp_name": "大峪星空野奢营地",
  "camp_type": "commercial", // commercial收费营地 / wild野营
  "facilities": {
    "allow_overnight": true,
    "water_source": "spring_natural",
    "vehicle_accessible": "direct",
    "toilet_available": true
  },
  "safety_risk_level": "warning_flash_flood" // 黄色山洪警告
}
```

---

## 3. 高德地图核心 API 集成方案（Amap Integration）

为了确保在高德地图免费额度内平稳运行，前端实施以下策略：

1. 点聚合插件（AMap.MarkerCluster）：  
    初始化地图后，加载 `AMap.MarkerCluster` 插件，将七十二个峪口的物理坐标数组一次性注入聚合器，避免高频创建销毁 DOM 节点导致卡顿。
2. 自定义 Marker 样式（Content 属性）：  
    利用 AMap.Marker 的 `content` 属性直接渲染自定义 HTML。根据后端返回的 `status`（红绿灯），动态更改 Marker 顶部的呼吸灯颜色（红色封山、绿色安全）。
3. 高德 URI 唤起导航组件：  
    通过特定 Scheme 协议，前端按钮点击直接拼接 URL：`https://amap.com{lng},${lat},${valley_name}&mode=car&src=qinling_guide`，该组件调用完全免费且不占用 Web API 的每日配额。

---

## 4. 阶段性交付里程碑（Milestones）

- M1（原型与数据库设计）：完成 PostGIS 空间数据库建表，录入首批 10 个核心峪口（如沣峪、子午峪、大峪）的精细坐标与露营指标。
- M2（高德地图前端打点）：前端跑通高德地图 JS API v2.0，实现分区缩放、点聚合与红绿灯 Marker 样式渲染。
- M3（联动安全与上线）：上线后台管理系统（支持手动一键封山/解封变灯），配置营地安全提示后正式交付上线。

---