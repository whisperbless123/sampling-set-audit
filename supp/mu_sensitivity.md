# μ 敏感性

> 稳健性检查，非发现；不改变任何既有判读落点。复用冻结选集，只换重构参数。

预注册出口 commit：`958fb6f82e3d1481fece59e1a8bff6c7db99c343`（早于本次计算）。

原范围说明未载 cell 范围，本检查执行九个 D0 cell。模式层定义为逐图配对方向至少 8/10 同号；状态映射与 R1一致。

| cell | 方法对 | 基准 μ 方向 | μ/10 方向（同号数；状态） | 10μ 方向（同号数；状态） |
|---|---|---|---|---|
| G1_S1 | Random__Degree | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G1_S1 | Random__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | Random__B3b | X_better | X_better (8/10; order_preserved) | X_better (8/10; order_preserved) |
| G1_S1 | Random__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | Random__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | Degree__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | Degree__B3b | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | Degree__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | Degree__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | B3a__B3b | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G1_S1 | B3a__B3c | none | none (5/10; order_lost) | X_better (8/10; order_lost) |
| G1_S1 | B3a__CEM | none | none (7/10; order_lost) | none (6/10; order_lost) |
| G1_S1 | B3b__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | B3b__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S1 | B3c__CEM | none | none (6/10; order_lost) | Y_better (8/10; order_lost) |
| G1_S2 | Random__Degree | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G1_S2 | Random__B3a | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G1_S2 | Random__B3b | X_better | X_better (8/10; order_preserved) | X_better (8/10; order_preserved) |
| G1_S2 | Random__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S2 | Random__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G1_S2 | Degree__B3a | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S2 | Degree__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S2 | Degree__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S2 | Degree__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G1_S2 | B3a__B3b | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G1_S2 | B3a__B3c | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G1_S2 | B3a__CEM | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G1_S2 | B3b__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S2 | B3b__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G1_S2 | B3c__CEM | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G1_S3 | Random__Degree | none | none (5/10; order_lost) | X_better (10/10; order_lost) |
| G1_S3 | Random__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S3 | Random__B3b | none | none (5/10; order_lost) | none (6/10; order_lost) |
| G1_S3 | Random__B3c | none | none (7/10; order_lost) | none (6/10; order_lost) |
| G1_S3 | Random__CEM | Y_better | Y_better (8/10; order_preserved) | none (7/10; order_lost) |
| G1_S3 | Degree__B3a | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G1_S3 | Degree__B3b | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G1_S3 | Degree__B3c | none | X_better (10/10; order_lost) | Y_better (9/10; order_lost) |
| G1_S3 | Degree__CEM | Y_better | none (5/10; order_lost) | Y_better (10/10; order_preserved) |
| G1_S3 | B3a__B3b | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G1_S3 | B3a__B3c | X_better | X_better (10/10; order_preserved) | X_better (8/10; order_preserved) |
| G1_S3 | B3a__CEM | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G1_S3 | B3b__B3c | none | X_better (10/10; order_lost) | none (7/10; order_lost) |
| G1_S3 | B3b__CEM | none | none (5/10; order_lost) | Y_better (8/10; order_lost) |
| G1_S3 | B3c__CEM | none | Y_better (9/10; order_lost) | none (6/10; order_lost) |
| G2_S1 | Random__Degree | X_better | X_better (9/10; order_preserved) | X_better (10/10; order_preserved) |
| G2_S1 | Random__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | Random__B3b | none | none (7/10; order_lost) | X_better (9/10; order_lost) |
| G2_S1 | Random__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | Random__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | Degree__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | Degree__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | Degree__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | Degree__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | B3a__B3b | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G2_S1 | B3a__B3c | none | none (5/10; order_lost) | none (7/10; order_lost) |
| G2_S1 | B3a__CEM | Y_better | Y_better (8/10; order_preserved) | none (5/10; order_lost) |
| G2_S1 | B3b__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | B3b__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S1 | B3c__CEM | none | none (7/10; order_lost) | Y_better (8/10; order_lost) |
| G2_S2 | Random__Degree | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G2_S2 | Random__B3a | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S2 | Random__B3b | none | none (6/10; order_lost) | none (6/10; order_lost) |
| G2_S2 | Random__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S2 | Random__CEM | none | none (7/10; order_lost) | none (7/10; order_lost) |
| G2_S2 | Degree__B3a | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S2 | Degree__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S2 | Degree__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S2 | Degree__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G2_S2 | B3a__B3b | X_better | X_better (9/10; order_preserved) | X_better (10/10; order_preserved) |
| G2_S2 | B3a__B3c | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G2_S2 | B3a__CEM | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G2_S2 | B3b__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G2_S2 | B3b__CEM | none | none (6/10; order_lost) | none (7/10; order_lost) |
| G2_S2 | B3c__CEM | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G2_S3 | Random__Degree | X_better | none (7/10; order_lost) | none (7/10; order_lost) |
| G2_S3 | Random__B3a | Y_better | Y_better (9/10; order_preserved) | none (7/10; order_lost) |
| G2_S3 | Random__B3b | none | none (6/10; order_lost) | Y_better (8/10; order_lost) |
| G2_S3 | Random__B3c | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G2_S3 | Random__CEM | none | none (6/10; order_lost) | none (5/10; order_lost) |
| G2_S3 | Degree__B3a | Y_better | Y_better (10/10; order_preserved) | none (7/10; order_lost) |
| G2_S3 | Degree__B3b | Y_better | none (7/10; order_lost) | none (7/10; order_lost) |
| G2_S3 | Degree__B3c | Y_better | Y_better (9/10; order_preserved) | none (7/10; order_lost) |
| G2_S3 | Degree__CEM | none | none (6/10; order_lost) | none (5/10; order_lost) |
| G2_S3 | B3a__B3b | X_better | X_better (10/10; order_preserved) | none (5/10; order_lost) |
| G2_S3 | B3a__B3c | none | none (6/10; order_lost) | none (6/10; order_lost) |
| G2_S3 | B3a__CEM | X_better | X_better (10/10; order_preserved) | none (7/10; order_lost) |
| G2_S3 | B3b__B3c | Y_better | Y_better (8/10; order_preserved) | none (6/10; order_lost) |
| G2_S3 | B3b__CEM | none | none (5/10; order_lost) | none (7/10; order_lost) |
| G2_S3 | B3c__CEM | X_better | X_better (9/10; order_preserved) | X_better (8/10; order_preserved) |
| G3_S1 | Random__Degree | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S1 | Random__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Random__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Random__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Random__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Degree__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Degree__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Degree__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | Degree__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | B3a__B3b | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S1 | B3a__B3c | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S1 | B3a__CEM | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S1 | B3b__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | B3b__CEM | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S1 | B3c__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G3_S2 | Random__Degree | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G3_S2 | Random__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S2 | Random__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (9/10; order_preserved) |
| G3_S2 | Random__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S2 | Random__CEM | none | none (7/10; order_lost) | none (5/10; order_lost) |
| G3_S2 | Degree__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S2 | Degree__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S2 | Degree__B3c | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S2 | Degree__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S2 | B3a__B3b | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S2 | B3a__B3c | none | none (7/10; order_lost) | none (7/10; order_lost) |
| G3_S2 | B3a__CEM | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S2 | B3b__B3c | Y_better | Y_better (9/10; order_preserved) | Y_better (9/10; order_preserved) |
| G3_S2 | B3b__CEM | X_better | X_better (9/10; order_preserved) | X_better (9/10; order_preserved) |
| G3_S2 | B3c__CEM | X_better | X_better (10/10; order_preserved) | X_better (10/10; order_preserved) |
| G3_S3 | Random__Degree | X_better | X_better (10/10; order_preserved) | X_better (9/10; order_preserved) |
| G3_S3 | Random__B3a | Y_better | Y_better (8/10; order_preserved) | Y_better (8/10; order_preserved) |
| G3_S3 | Random__B3b | none | none (6/10; order_lost) | none (6/10; order_lost) |
| G3_S3 | Random__B3c | none | none (7/10; order_lost) | none (7/10; order_lost) |
| G3_S3 | Random__CEM | none | none (5/10; order_lost) | none (6/10; order_lost) |
| G3_S3 | Degree__B3a | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S3 | Degree__B3b | Y_better | Y_better (10/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S3 | Degree__B3c | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S3 | Degree__CEM | Y_better | Y_better (9/10; order_preserved) | Y_better (10/10; order_preserved) |
| G3_S3 | B3a__B3b | X_better | X_better (9/10; order_preserved) | X_better (8/10; order_preserved) |
| G3_S3 | B3a__B3c | X_better | X_better (8/10; order_preserved) | none (6/10; order_lost) |
| G3_S3 | B3a__CEM | X_better | X_better (8/10; order_preserved) | X_better (8/10; order_preserved) |
| G3_S3 | B3b__B3c | none | none (7/10; order_lost) | none (7/10; order_lost) |
| G3_S3 | B3b__CEM | none | none (6/10; order_lost) | none (6/10; order_lost) |
| G3_S3 | B3c__CEM | none | none (6/10; order_lost) | none (7/10; order_lost) |

## 运行与守卫

- A_S 奇异：无；1800/1800 次计算前 Cholesky 守卫通过；全局最小 Cholesky 对角元 `0.0207184267767`。
- 实测墙钟：总计 `6.231083` s；μ/10 累计 `2.836084` s；10μ 累计 `2.644507` s。
- 复用冻结选集、未重选点、未重训练、未重校准 μ；测试信号与噪声 seed 沿用原 run。
- 未做措辞层，未计算 δ，未做 TOST。
- 模式层状态：preserved 198 / flipped 0 / lost 72。

预注册出口：**B**。

正文句：μ 扰动下模式层序有变；完整状态见 Supp，C2 的辖域绑定冻结的重构规格，既有 limitation 句保留。
