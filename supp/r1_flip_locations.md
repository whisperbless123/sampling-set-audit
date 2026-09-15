# R1 翻转位置核查

> R1 翻转位置的落档核查；**非新判据、非重判**。附核出具，用于核实「七对全部存活、零翻转」是否成立。
> 本表不铸造发现。

## 来源与口径

- runs/r1_verdict_table.json @ 9d397329d2c31254c545d7460f9d79f57d931eb4，465653 字节，原始 blob 内容 sha256 `26b9614f284168626923a86924c7afbd949651678b6586681aacd9726959b6f0`。
- runs/k4b_verdict_table.json @ 9d397329d2c31254c545d7460f9d79f57d931eb4，内容 sha256 `4ae5ec6e396c08e08f4810c625edefc6391d354040a936428160d7f433d84c71`。
- 均以 git cat-file blob 读取原始字节；不使用 git show。
- 执行指令所列 R1 哈希 `9077b9f4f2d4f47e9dc0ca30b34bf99b7a7f56de99e01e18da6b171fa5b827d1` 与原始 blob 不符。只在内存中将 LF 转 CRLF 后恰得该哈希，确认其采用了换行转换后的口径。本表仍以指定 path @ commit 的原始 blob 为源，未改源文件，未把转换后哈希作为内容哈希。
- 计数来自 `$.cells[*].comparisons[*].full.comparison_to_main`，六 cell × 十五对 = 90；`cond_filtered.comparison_to_main` 的 90 个状态与 full 逐格一致，不重复加总。

## 计数

| 范围 | order_preserved | order_flipped | order_lost | 合计 |
|---|---:|---:|---:|---:|
| 全局 | 55 | 3 | 32 | 90 |
| 七对 × 六 cell | 40 | 0 | 2 | 42 |

## 三处翻转

每个字段路径均属于上述 runs/r1_verdict_table.json @ commit。方向 X/Y 按 pair_id 左右方法解释；状态为已存储字段，不另算门槛。

| 方法对 | cell | 落点 | 翻转方向 | 状态字段全路径 |
|---|---|---|---|---|
| B3a__CEM | D0_G2_S1_k10 | 七对外 | Y_better → X_better | `$.cells[1].comparisons[11].full.comparison_to_main` |
| B3a__CEM | rho15_G1_S1_k10 | 七对外 | Y_better → X_better | `$.cells[3].comparisons[11].full.comparison_to_main` |
| B3a__B3c | rho15_G2_S1_k10 | 七对外 | Y_better → X_better | `$.cells[4].comparisons[10].full.comparison_to_main` |

方向前值字段：对应行 `.main_reconstructor_direction`；后值字段：对应行 `.full.direction`。以上三条均从 Y_better 变为 X_better。

## 七对来源全路径

以下均为 runs/k4b_verdict_table.json @ 9d397329d2c31254c545d7460f9d79f57d931eb4，字段值均为 true。

| 方法对 | 字段全路径 |
|---|---|
| Random__B3a | `$.pairs[1].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |
| Random__B3c | `$.pairs[3].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |
| Random__CEM | `$.pairs[4].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |
| Degree__B3a | `$.pairs[5].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |
| Degree__B3c | `$.pairs[7].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |
| Degree__CEM | `$.pairs[8].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |
| B3a__B3b | `$.pairs[9].predicates[0].a13_boundary.versions.ddof_0.a13_qualified` |

## 校验与机械结论

1. 全局三状态和 55 + 3 + 32 = 90，成立。
2. 七对三状态逐项不超过全局：40 ≤ 55、0 ≤ 3、2 ≤ 32，成立。
3. 三处翻转七对内 0、七对外 3，与七对 flipped = 0 一致。

按 CODEX_CHECKER_SEC4_R1.md §3-2 的机械分支：三处翻转全在七对之外，故该指令所述「七对全部存活、零翻转」判定成立；本次翻转附核不要求改写其相应句。此结论不能扩展为七对在全部六 cell 的 42 个比较都 order_preserved：其中有两处已落档的 order_lost，必须连同计数展示，不重新判读。

| 七对内失效的方法对 | cell | 状态字段全路径 | 方向 |
|---|---|---|---|
| Degree__CEM | rho15_G1_S1_k10 | `$.cells[3].comparisons[8].full.comparison_to_main` | Y_better → none |
| Degree__CEM | rho15_G2_S1_k10 | `$.cells[4].comparisons[8].full.comparison_to_main` | Y_better → none |

未修改任何 .tex，未落盘 §5。
