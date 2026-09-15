"""Export A-57-authorized graph-family means for display only."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
COMMIT = "24713b48d5dd026bf3102d1f1b7f3e65ae2b790d"
SOURCES = ["runs/fig3_dose_table.json", "runs/oracle_reference.json"]


# Okabe-Ito method identities; reference condition has its own legend identity.
METHOD_COLORS = {
    "Random": "000000", "Degree": "E69F00", "B3a": "0072B2",
    "B3b": "009E73", "B3c": "D55E00", "CEM": "CC79A7",
    "B3a-evaluation-graph": "56B4E9",
}


DISPLAY_NAMES = {"B3a": "E-opt", "B3b": r"$\lambda_{\min}$", "B3c": "A-opt"}


def method_color(method):
    return "method" + method.replace("-", "")


def color_definitions():
    return [rf"\definecolor{{{method_color(m)}}}{{HTML}}{{{c}}}" for m, c in METHOD_COLORS.items()]


def export():
    raw = {p: subprocess.check_output(["git", "cat-file", "blob", COMMIT+":"+p], cwd=ROOT) for p in SOURCES}
    inputs = {p: {"commit": COMMIT, "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)} for p, b in raw.items()}
    dose, reference = (json.loads(raw[p]) for p in SOURCES)
    assert reference["selection_graph"] == "G_eval" and reference["reconstruction_laplacian"] == "L_eval"
    groups = defaultdict(list)
    for i, row in enumerate(dose["rows"]):
        groups[row["rho_percent"], row["signal_family"], row["method"]].append({"graph_family": row["graph_family"], "value": row["cross_graph_mean"], "source": SOURCES[0], "field": f"$.rows[{i}].cross_graph_mean"})
    for i, row in enumerate(reference["cells"]):
        groups[row["rho_percent"], row["signal_family"], "B3a-evaluation-graph"].append({"graph_family": row["graph_family"], "value": row["cross_graph_mean"], "source": SOURCES[1], "field": f"$.cells[{i}].cross_graph_mean"})
    rows = []
    for (rho, signal, method), members in sorted(groups.items()):
        assert sorted(m["graph_family"] for m in members) == ["G1", "G2", "G3"]
        rows.append({"rho_percent": rho, "signal_family": signal, "method": method, "mean_across_graph_families": sum(m["value"] for m in members)/len(members), "members": members})
    assert len(rows) == 63
    table = {"usage": "display only; not evidence for any statement or decision", "aggregation": "arithmetic mean of archived cross_graph_mean by (rho_percent, signal_family, method)", "inputs": inputs, "rows": rows}
    (OUT / "fig2_dose_aggregated.json").write_text(json.dumps(table, indent=2)+"\n", encoding="utf-8")
    methods = ["Random", "Degree", "B3a", "B3b", "B3c", "CEM", "B3a-evaluation-graph"]
    styles = [
        "solid,line width=.4pt,mark=o,mark size=1.8pt",
        "dashed,line width=.4pt,mark=square,mark size=2.0pt",
        "densely dotted,line width=.4pt,mark=triangle,mark size=2.2pt",
        "dash dot,line width=.4pt,mark=triangle,mark size=2.4pt,mark options={rotate=180}",
        "dash pattern=on 5pt off 2pt,line width=.4pt,mark=diamond,mark size=2.6pt",
        "dash pattern=on 3pt off 1pt on .5pt off 1pt on .5pt off 1pt,line width=.4pt,mark=star,mark size=2.8pt",
        "black!55,dash dot,line width=.85pt,mark=none",
    ]
    tex = [r"\begin{tikzpicture}[x=1mm,y=1mm,font=\fontsize{9}{10}\selectfont]", r"\path[use as bounding box] (-4,-93.5) rectangle (82,1);"]
    tex[0:0] = color_definitions()
    # Direct legend: line patterns and shapes both carry method identity.
    for i, (method, style) in enumerate(zip(methods, styles)):
        x, y = [(0, 0), (24, 0), (47, 0), (65, 0), (0, -5), (18, -5), (37, -5)][i]
        label = DISPLAY_NAMES.get(method, method) if i < 6 else "E-opt on evaluation graph"
        tex += [rf"\draw[black,{style},draw={method_color(method)}] plot coordinates {{({x},{y}) ({x+5},{y})}};", rf"\node[anchor=west,text={method_color(method)}] at ({x+6},{y}) {{{label}}};"]
    for si, signal in enumerate(["S1", "S2", "S3"]):
        top, bottom = -11.5-si*25, -30.5-si*25
        tex += [rf"\draw[black] (8,{top}) -- (8,{bottom}) -- (78,{bottom});", rf"\node[anchor=west] at (9,{top-2}) {{{signal}}};"]
        for tick in [0, .5, 1]:
            y = bottom+19*tick
            tex.append(rf"\draw[black!15] (8,{y}) -- (78,{y});")
            tex.append(rf"\node[anchor=east] at (7,{y}) {{\NUM{{{tick:g}}}{{runs/fig3_dose_table.json @ {COMMIT} NMSE-display-scale}}}};")
        for rho in [5, 15, 30]:
            x = 8+70*(rho-5)/25
            tex.append(rf"\draw ({{{x}}},{bottom}) -- ({{{x}}},{bottom-1});")
            if si == 2:
                tex.append(rf"\node at ({x},{bottom-3}) {{\NUM{{{rho}}}{{runs/fig3_dose_table.json @ {COMMIT} rows-rho-percent}}}};")
        # Authorized display envelope: min/max of the seven existing plotted values.
        lower, upper = [], []
        for rho in [5, 15, 30]:
            at_rho = [r["mean_across_graph_families"] for r in rows
                      if r["signal_family"] == signal and r["rho_percent"] == rho]
            assert len(at_rho) == 7
            x = 8+70*(rho-5)/25
            lower.append((x, bottom+19*min(at_rho)))
            upper.append((x, bottom+19*max(at_rho)))
        polygon = " -- ".join(f"({x:.8f},{y:.8f})" for x,y in lower+upper[::-1])
        tex.append(rf"\fill[black!20,opacity=.4] {polygon} -- cycle;")
        # Draw the wide reference behind the six hollow-marker method curves.
        for method, style in [(methods[-1], styles[-1]), *list(zip(methods[:-1], styles[:-1]))]:
            values = sorted([row for row in rows if row["signal_family"] == signal and row["method"] == method], key=lambda r: r["rho_percent"])
            coords = " ".join(f"({8+70*(r['rho_percent']-5)/25:.8f},{bottom+19*r['mean_across_graph_families']:.8f})" for r in values)
            tex.append(rf"\draw[black,{style},draw={method_color(method)}] plot coordinates {{{coords}}};")
    tex += [r"\node[rotate=90] at (-3,-46.5) {NMSE};", r"\node at (43,-89.5) {edge perturbation $\rho$ (\%)};", r"\end{tikzpicture}"]
    (OUT / "fig2_dose.pgf").write_text("\n".join(tex)+"\n", encoding="utf-8")
    caption = "NMSE versus edge perturbation, averaged across graph families. The reference uses B3a selection and reconstruction on the evaluation graph. The shaded band spans the seven curves at each perturbation level."
    (OUT / "fig2_dose.tex").write_text("\\begin{figure}[t]\n\\centering\n\\input{figs/fig2_dose.pgf}\n\\begingroup\n\\let\\normalsize\\small\n\\normalsize\n\\caption{"+caption+"}\n\\label{fig:dose}\n\\endgroup\n\\end{figure}\n", encoding="utf-8")
    (OUT / "fig2_inputs.json").write_text(json.dumps({"inputs": inputs, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "source_rows": 162, "reference_cells": 27, "display_rows": 63, "aggregation_is_not_a_claim": True}, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    export()
