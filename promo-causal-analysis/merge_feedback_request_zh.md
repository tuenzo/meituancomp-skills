# 第一次合并后的反馈请求

## 背景

本次第一次合并已经按你在当前回合给出的新边界完成，统一主线已扩展为：

`原始三表 -> category-day 面板 -> EDA -> PSM + DID / event study -> LocalGap -> GPS -> uplift -> recommendation`

但磁盘中的源文件 [SKILL-version2.md](E:\CodingProject\meituancomp-skills\SKILL-version2.md) 仍然是旧版 `LocalGap + DID + decomposition` 草稿，没有直接包含这次你明确要求的 `PSM`、`GPS`、`uplift`。因此，下面这些点我已做了合理裁决，但仍建议你确认。

## 需要你确认的点

### 1. GPS 的主 treatment 变量

当前合并版允许把以下变量作为连续处理强度：

- `discount_rate`
- `view_uv`
- 组合强度指标

当前裁决：

- skill 不写死 treatment，要求调用时显式指定
- 文档默认把 GPS 解释为“连续剂量反应层”

希望你确认：

- 你更希望 GPS 以 `discount_rate` 为主，还是以 `view_uv` 为主，还是明确支持两条并行曲线

### 2. uplift 的决策粒度

当前合并版把 uplift 的默认工作粒度定义为：

- `category x day`
- 或基于 `category x day` 聚合出来的 category slice

当前裁决：

- 不做用户级 uplift
- 最终输出以 category-level priority bucket 为主

希望你确认：

- 你更希望 uplift 的最终汇报粒度是“品类级”，还是“品类 x 活动窗级”

### 3. recommendation 中的 full-category / head-category 边界

当前合并版保留了：

- `overall strategy`
- `full-category strategy`
- `head-category strategy`

当前裁决：

- 只给出结构，不在 skill 中硬编码 head-category 的阈值

希望你确认：

- head-category 是否有固定业务定义，例如按 GMV 前 20%、前 30%、或运营既有名单

### 4. PSM 的默认匹配变量

当前脚本默认使用以下 baseline covariates 候选：

- `gmv`
- `view_uv`
- `discount_rate`
- `sale_num`
- `order_cnt`
- `buy_uv`

当前裁决：

- 如果这些变量不足，就降级为弱匹配或未匹配 DID，并在结果中披露

希望你确认：

- 是否有一组你希望固化的标准匹配变量

### 5. uplift action bucket 的数量和命名

当前合并版使用四档：

- `Prioritize`
- `Selective`
- `Observe`
- `Do Not Disturb`

当前裁决：

- 这是为了兼顾“进攻”和“保守”两类建议

希望你确认：

- 你是否要保留四档，还是改成三档更适合业务汇报

### 6. 旧版 version2 文件与本轮边界不一致

当前情况：

- 你口头定义的 version2 明显比磁盘里的 `SKILL-version2.md` 更完整
- 我已经以你本轮明确提出的结构和功能边界为主完成合并

希望你确认：

- 后续是否把 [SKILL-version2.md](E:\CodingProject\meituancomp-skills\SKILL-version2.md) 也同步改写为最新 merged draft，避免后续继续混淆

## 建议的下一步

如果你确认以上几点，我建议第二轮继续做两件事：

1. 把 `GPS` 和 `uplift` 的默认 treatment / bucket / 粒度进一步固化
2. 再起一次子进程，用新的 merged skill 针对比赛第一题做一次完整 forward-test
