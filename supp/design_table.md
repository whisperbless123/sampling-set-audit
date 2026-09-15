# S2 · 60-cell design table

> 转录/汇总件，非新判据，不铸发现。

`protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909`；内容 sha256 `33d02885962f3c00fff96e6a884b7696d80140e7a291d22b5fad4b947a40c850`，§2；以下三轴与 A/B/C 表行逐字转录。

**Axis-G 图族**（`G_sel` 的生成分布）：
- G1 = Erdős–Rényi(N, p)，p 取平均度 ≈ 8
- G2 = SBM(N, C=4 社区, p_in/p_out 取平均度 ≈ 8、社区内外比 8:1)
- G3 = Watts–Strogatz(N, 环邻居 8, β=0.1)

**Axis-S 信号族**（精确定义，S1/S2 必须可区分）：
- S1 精确带限 + 噪声：x = U_{:,1:r}·c，c ~ N(0, I)，r = ⌈0.1N⌉，观测噪声 SNR = 20 dB
- S2 扩散/GMRF 平滑（全带低通）：x ~ N(0, (L + εI)⁻¹)，ε = 1e-2，同 SNR
- S3 平滑底 + 局部异常：S2 信号叠加空间聚簇尖峰（支撑 = 5% 节点、取单个社区/邻域内，幅值 = 底信号 SD × 5）

**Axis-D 漂移**（选点期 → 评估期）：
- D0 无漂移：G_eval = G_sel，M_eval = M_sel
- D-G 结构漂移：度序保持随机重连，比例 ρ ∈ {5%, 15%, 30%}；信号在 G_eval 上生成，重构仍用 L_sel（端到端 stale）
- D-S 模型误设：(M_sel = S1, 实际 = S3) 与 (M_sel = S2, 实际 = S3) 两组，ρ = 0

**Cell 清单（冻结；裁剪顺序见括号）**：

| Block | 内容 | cell 数 |
|---|---|---|
| A | D0 主表：3G × 3S × 3 个 k | 27 |
| B | 结构漂移：3G × 3S × 3ρ，k=10%（时间不够先砍 ρ=5%） | 27 |
| C | 模型误设：2 组 × 3G，k=10% | 6 |


§1 采样率原句：

```text
**规模**：主规模 N = 100；N = 300 仅作规模稳健性检验（§2 Block D）。采样率 k/N ∈ {5%, 10%, 20%}（仅 Block A 全扫，其余 Block 固定 10%）。
```

## Cell 清点

协议 §2 给出 Block 和轴组合，未逐项给出落档文件中的 cell_id 字符串；该字符串列记 `not found`。下表仅展开原设计笛卡尔积，非新增 cell；每行来源均为上述协议 §2，k 值另见 §1。

| Block | G | M_sel → M_eval | Drift | k/N | cell_id 原字串 | 来源 |
|---|---|---|---|---|---|---|
| A | G1 | S1 → S1 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S1 → S1 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S1 → S1 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S2 → S2 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S2 → S2 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S2 → S2 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S3 → S3 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S3 → S3 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G1 | S3 → S3 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S1 → S1 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S1 → S1 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S1 → S1 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S2 → S2 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S2 → S2 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S2 → S2 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S3 → S3 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S3 → S3 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G2 | S3 → S3 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S1 → S1 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S1 → S1 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S1 → S1 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S2 → S2 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S2 → S2 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S2 → S2 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S3 → S3 | D0 | 5% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S3 → S3 | D0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| A | G3 | S3 → S3 | D0 | 20% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block A |
| B | G1 | S1 → S1 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S1 → S1 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S1 → S1 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S2 → S2 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S2 → S2 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S2 → S2 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S3 → S3 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S3 → S3 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G1 | S3 → S3 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S1 → S1 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S1 → S1 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S1 → S1 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S2 → S2 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S2 → S2 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S2 → S2 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S3 → S3 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S3 → S3 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G2 | S3 → S3 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S1 → S1 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S1 → S1 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S1 → S1 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S2 → S2 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S2 → S2 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S2 → S2 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S3 → S3 | D-G; rho=5% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S3 → S3 | D-G; rho=15% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| B | G3 | S3 → S3 | D-G; rho=30% | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block B |
| C | G1 | S1 → S3 | D-S; rho=0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block C |
| C | G1 | S2 → S3 | D-S; rho=0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block C |
| C | G2 | S1 → S3 | D-S; rho=0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block C |
| C | G2 | S2 → S3 | D-S; rho=0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block C |
| C | G3 | S1 → S3 | D-S; rho=0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block C |
| C | G3 | S2 → S3 | D-S; rho=0 | 10% | not found | protocol/D0_experiment_protocol.md @ 967f7e80cf135db1257cdd8302f3caa8903e8909 §1/§2 Block C |

## 墙钟与特征分解成本

以下仅给已落档字段与口径；未从预算外推实际方法成本。

| 项目 | 已落档指针/状态 |
|---|---|
| 单次管线评估墙钟；非闭式判据特征分解计时 | runs/timing_budget.json @ 967f7e80cf135db1257cdd8302f3caa8903e8909；sha256 2ac87220588d4db32103497c50d65f640401738f8449e74da540804fbf5d1e4a；$.single_eval["100"].median_seconds / $.single_eval["300"].median_seconds |
| 逐 run 墙钟记录；非单独特征分解计时 | runs/d0_G1_S1_k10_N100.jsonl @ 967f7e80cf135db1257cdd8302f3caa8903e8909；sha256 3951d09c77b0db952995483c76aa83bcff273e6b54cfb5cc030851399280e755；各 JSONL 行 $.method / $.elapsed_seconds |
| 单独特征分解成本 | not measured；上述落档未给出独立特征分解成本字段 |

## 从 §2 下沉的三项原文

出处：§2 of the paper，正文 CEM 计费句、DQN 观测句与四角色表。仅转录，不新增判据。

### CEM billing

```tex
CEM bills every candidate and reuses the incumbent\textquotesingle s previously billed score.
```

### DQN observation detail

```tex
DQN observes the graph/model encoding and selected-set mask, adds one unselected node per action, and receives zero intermediate reward; only the completed set invokes the evaluator.
```

### Four graph/distribution roles

```tex
\begin{center}
\begin{tabular}{ll}
Signal generation & $G_{\rm eval},M_{\rm eval}$\\
Selection information & $G_{\rm sel},M_{\rm sel}$\\
Reconstruction graph & $G_{\rm sel}$\\
Search development distribution & $G_{\rm sel},M_{\rm sel}$
\end{tabular}
\end{center}
```

## 本轮观测句压缩的原文

出处：§2 of the paper，正文DQN观测句；不新增判据。CEM计费及四角色表已在前述段下沉，本轮不重复计入砍减。

### DQN observation sentence before this revision

```tex
DQN~\cite{mnih} observes graph/model encodings and selected-set masks, adds unselected nodes sequentially, and evaluates only completed sets.
```


## §2 结论节对冲所下沉的记账说明

出处：§2 of the paper。下文逐字保存本次移出正文的句/从句；不改变计费口径。

```tex
Each call draws a fresh batch keyed by cell, graph seed, method seed, and evaluation ordinal.
```

CODE_AUDIT_SIXPACK item 1；逐次抽批实现说明，移入 S2；保留条25评估定义及条26信息流。

```tex
CEM billing is given in Supp.~S2.
```

the recorded rule / the recorded rule / the recorded rule；CEM 原文已在 S2，下沉重复指引；§2 首段保留 S2 链接，终态计费句保留。

```tex
; wall-clock and eigendecomposition costs are given in Supp.~S2.
```

条44后半；the recorded rule / the recorded rule 已准下沉；零额外开发查询及其校准/冻结前提保留。

抽批说明的实现出处：[internal record, not released]。CEM 计费原文见本文件 CEM billing；墙钟与特征分解成本见本文件对应表，其中独立特征分解计时仍为 not measured。
