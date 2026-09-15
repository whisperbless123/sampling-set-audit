# S7 · Best-of-budget control

> 转录/汇总件，非新判据，不铸发现。
> not preregistered as a comparison; disclosure only

拆封授权记录见后述提交；SEAL 单独提交 `553199edd514a473815c66688a70ac607ae14bba` 后读取且仅读取 `runs/sealed/best_of_budget_A24_2.jsonl`。

- runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba；内容 sha256 c0fe44129f13741e74722cae75461ae1c17861fa869e875a749f3f4888605c2b；逐行 $.cell / $.graph_seed / $.method_seed / $.test_nmse。
- runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba；内容 sha256 9711c2c6dcff5681d16a5b45bb97b13c2b78fc206944f3c8faeac12b955143e6；下表五部署方法直接取已落档跨图均值。
- runs/best_of_budget.json @ 16ae25549d29d2746f6e061ef84e022426c7718b；内容 sha256 202096d418c63e993dd40cddb4b9ebc434f9e65290a8b700c4d22e288b558384；只有计数、耗时等字段，无两项预注册预测布尔。

控制组按协议 §4 的既有汇总单位：先按图对三个方法 seed 的 test_nmse 取均值，再对十图取均值；不新增比较。各表值使用完整浮点表示。

| cell | Random | 控制组 | B3a | B3b | B3c | CEM | 预测一布尔（指针见 §2.2） | 预测二布尔（指针见 §2.2） | 均值字段与控制组行指针 |
|---|---|---|---|---|---|---|---|---|---|
| G1_S1 | 0.7773627574507529 | 0.563310356913577 | 0.41896487167846147 | 0.8230245302787031 | 0.437828317734455 | 0.4082645017976649 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[0].methods.Random.cross_graph_mean / $.cells[0].methods.B3a.cross_graph_mean / $.cells[0].methods.B3b.cross_graph_mean / $.cells[0].methods.B3c.cross_graph_mean / $.cells[0].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 $.test_nmse |
| G1_S2 | 0.3685361625285305 | 0.3679118620158964 | 0.35709126249815865 | 0.3695609235123895 | 0.3424328665089083 | 0.3653834056908572 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[1].methods.Random.cross_graph_mean / $.cells[1].methods.B3a.cross_graph_mean / $.cells[1].methods.B3b.cross_graph_mean / $.cells[1].methods.B3c.cross_graph_mean / $.cells[1].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60 $.test_nmse |
| G1_S3 | 0.504832070278256 | 0.5043865814870442 | 0.48928200928764254 | 0.5052968124610648 | 0.5091381468045161 | 0.5019908983713078 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[2].methods.Random.cross_graph_mean / $.cells[2].methods.B3a.cross_graph_mean / $.cells[2].methods.B3b.cross_graph_mean / $.cells[2].methods.B3c.cross_graph_mean / $.cells[2].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90 $.test_nmse |
| G2_S1 | 0.728244296268767 | 0.5497753678422381 | 0.43739402255219206 | 0.7476222477756534 | 0.44121162612504705 | 0.41203155971293437 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[3].methods.Random.cross_graph_mean / $.cells[3].methods.B3a.cross_graph_mean / $.cells[3].methods.B3b.cross_graph_mean / $.cells[3].methods.B3c.cross_graph_mean / $.cells[3].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120 $.test_nmse |
| G2_S2 | 0.3682175171668359 | 0.36918517639597986 | 0.35213736894257885 | 0.3679223477541489 | 0.34191379879631134 | 0.365193182016927 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[4].methods.Random.cross_graph_mean / $.cells[4].methods.B3a.cross_graph_mean / $.cells[4].methods.B3b.cross_graph_mean / $.cells[4].methods.B3c.cross_graph_mean / $.cells[4].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150 $.test_nmse |
| G2_S3 | 0.5061218704918578 | 0.5067611398196714 | 0.4951917646518969 | 0.5071549819708261 | 0.4947839744457849 | 0.5064412534650835 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[5].methods.Random.cross_graph_mean / $.cells[5].methods.B3a.cross_graph_mean / $.cells[5].methods.B3b.cross_graph_mean / $.cells[5].methods.B3c.cross_graph_mean / $.cells[5].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180 $.test_nmse |
| G3_S1 | 0.556765561559883 | 0.4351800898629775 | 0.33789182677550905 | 0.4680973418985487 | 0.4160982333497058 | 0.38093214098647526 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[6].methods.Random.cross_graph_mean / $.cells[6].methods.B3a.cross_graph_mean / $.cells[6].methods.B3b.cross_graph_mean / $.cells[6].methods.B3c.cross_graph_mean / $.cells[6].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210 $.test_nmse |
| G3_S2 | 0.353411716405044 | 0.3528050022519907 | 0.33247325010879963 | 0.3440878501735169 | 0.33649182441178893 | 0.3529603496209438 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[7].methods.Random.cross_graph_mean / $.cells[7].methods.B3a.cross_graph_mean / $.cells[7].methods.B3b.cross_graph_mean / $.cells[7].methods.B3c.cross_graph_mean / $.cells[7].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240 $.test_nmse |
| G3_S3 | 0.5096763743732712 | 0.5135717047726773 | 0.4995645475849952 | 0.5096903647661988 | 0.5067486303391739 | 0.5115983763529177 | not found | not found | runs/k2_aggregate.json @ 553199edd514a473815c66688a70ac607ae14bba $.cells[8].methods.Random.cross_graph_mean / $.cells[8].methods.B3a.cross_graph_mean / $.cells[8].methods.B3b.cross_graph_mean / $.cells[8].methods.B3c.cross_graph_mean / $.cells[8].methods.CEM.cross_graph_mean; runs/sealed/best_of_budget_A24_2.jsonl @ 553199edd514a473815c66688a70ac607ae14bba JSONL 行 241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270 $.test_nmse |

预测字段缺口：指定 JSON 的顶层字段如下（逐字字段名）；未以 all_eval_counts_exact 等计数布尔充当预测，未重算预测，未用其他文件替换指定来源。

`authorization, scope, method, performance_location, performance_fields_exposed, run_count, all_eval_counts_exact, rows, total_wall_seconds, worker_processes, git_commit_at_generation`

## 两预测布尔的来源指针

两布尔列统一指向 DIAGNOSTICS_REPORT.md @ 8857f2c52f6bcf0f3a59bf53a6bda2d108e94132 §2.2；内容 sha256 2ab9d35246c9417ef7d70552e78702da2f3f0c852fbdc11f90c00cd531cbe774。boolean not present in best_of_budget.json。既有单元格 not found 保留，不从数值重算或补写。

该落档 §2.2 原文：

> 只记命中与否，不据以调整口径：
> 
> - S1“胜均值随机、逊最好贪心与 CEM”：G1/G2/G3 均命中，3/3。
> - S2“≈ 均值随机”：以同一预注册等价界 `3×(SD_X+SD_Y)` 并列检查 ddof=0/1，G1/G2/G3 均命中且无两版分歧，3/3。
> - S3 没有预注册预测，本报告不制造事后命中标签。
> 
> 性能数值继续遵守密封边界；这里只公开预注册预测的布尔核对。该诊断不进入 K4/K4-b 十五方法对，不据以谓词化，只供图注和 limitation。
