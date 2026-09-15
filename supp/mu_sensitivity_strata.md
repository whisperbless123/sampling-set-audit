# μ 出口 B 的分层计数

> 稳健性检查的分层计数；**不改变预立出口 B**；三类分列不合并；状态映射沿用 R1 口径——基准方向为 `none` 时，扰动后仍为 `none` 或出现方向，**两向变化均记 `order_lost`**，该约定为保守方向。

输入：`runs/mu_sensitivity.json` @ `cfa6c924de31bb348506f633e46364530d581af0`，内容 SHA-256 `3bebbbbc31b82329f80a3d9bb5d083e9bd10499e06a1dc1f22e0dda6e9fa0a6a`。

字段路径：`cells[*].perturbations.<μ档>.comparisons[*].baseline_mu_direction`、`cells[*].perturbations.<μ档>.comparisons[*].direction`、`cells[*].perturbations.<μ档>.comparisons[*].comparison_to_baseline`。七对由 `a13_boundary.versions.ddof_0.a13_qualified = true` 的七个方法对限定。

## 1. 七对 × 九 cell × 两档

| 信号层 | 格数 | `order_preserved` | `order_flipped` | `order_lost` | 其中 `none→none` | 其中有向→`none` | 其中 `none`→有向 |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1（G1_S1 / G2_S1 / G3_S1） | 42 | 42 | 0 | 0 | 0 | 0 | 0 |
| S2（G1_S2 / G2_S2 / G3_S2） | 42 | 38 | 0 | 4 | 4 | 0 | 0 |
| S3（G1_S3 / G2_S3 / G3_S3） | 42 | 24 | 0 | 18 | 10 | 6 | 2 |
| **合计** | **126** | **104** | **0** | **22** | **14** | **6** | **2** |

校验：各层三状态之和等于层格数；各层 `order_lost` 的三类之和等于该层 `order_lost`；三层格数之和为 126。

## 2. 七对在三个 S1 cell 上

42 格汇总：`order_preserved=42`、`order_flipped=0`、`order_lost=0`。

| 方法对 | 格数 | `order_preserved` | `order_flipped` | `order_lost` |
|---|---:|---:|---:|---:|
| Random__B3a | 6 | 6 | 0 | 0 |
| Random__B3c | 6 | 6 | 0 | 0 |
| Degree__B3a | 6 | 6 | 0 | 0 |
| Degree__B3c | 6 | 6 | 0 | 0 |
| Random__CEM | 6 | 6 | 0 | 0 |
| Degree__CEM | 6 | 6 | 0 | 0 |
| B3a__B3b | 6 | 6 | 0 | 0 |
| **合计** | **42** | **42** | **0** | **0** |

逐对逐格明细：

| 方法对 | G1 μ/10 | G1 10μ | G2 μ/10 | G2 10μ | G3 μ/10 | G3 10μ |
|---|---|---|---|---|---|---|
| Random__B3a | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |
| Random__B3c | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |
| Degree__B3a | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |
| Degree__B3c | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |
| Random__CEM | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |
| Degree__CEM | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |
| B3a__B3b | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved | order_preserved |

## 3. 全体 15 对对照

| 信号层 | 格数 | `order_preserved` | `order_flipped` | `order_lost` | 其中 `none→none` | 其中有向→`none` | 其中 `none`→有向 |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 | 90 | 77 | 0 | 13 | 8 | 1 | 4 |
| S2 | 90 | 80 | 0 | 10 | 10 | 0 | 0 |
| S3 | 90 | 41 | 0 | 49 | 29 | 13 | 7 |
| **合计** | **270** | **198** | **0** | **72** | **47** | **14** | **11** |

子集核验：七对在 S1、S2、S3 的每一种状态与每一个 `order_lost` 子类计数，均不超过全体 15 对的对应计数。

## 4. 七对 / 其余八对分组

> 追加块；上文既有三表未改动。两组计数并列出示，不附推断词或因果连接。解读留给读者。

| 信号层 | 组 | 格数 | `order_preserved` | `order_flipped` | `order_lost` | `none→none` | 有向→`none` | `none`→有向 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S1 | 七对 | 42 | 42 | 0 | 0 | 0 | 0 | 0 |
| S1 | 其余八对 | 48 | 35 | 0 | 13 | 8 | 1 | 4 |
| S2 | 七对 | 42 | 38 | 0 | 4 | 4 | 0 | 0 |
| S2 | 其余八对 | 48 | 42 | 0 | 6 | 6 | 0 | 0 |
| S3 | 七对 | 42 | 24 | 0 | 18 | 10 | 6 | 2 |
| S3 | 其余八对 | 48 | 17 | 0 | 31 | 19 | 7 | 5 |
