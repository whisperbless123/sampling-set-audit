"""Export the frozen z table to a TikZ phase grid; no new decision rule."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from matplotlib import colormaps

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCES = {
    "supp/effect_sizes_z.md": "c9d14229cccc83cce16127ca3aca915b9877395c",
    "runs/k4b_verdict_table.json": "9d397329d2c31254c545d7460f9d79f57d931eb4",
}


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


def z_color(z, maximum):
    # cividis_r preserves the old light-to-dark direction and monotone luminance.
    rgb = colormaps["cividis_r"](z / maximum)[:3]
    return "{rgb,1:red," + f"{rgb[0]:.8f};green,{rgb[1]:.8f};blue,{rgb[2]:.8f}" + "}", rgb


def export():
    source_bytes = {p: subprocess.check_output(["git", "cat-file", "blob", c + ":" + p], cwd=ROOT)
                    for p, c in SOURCES.items()}
    inputs = {p: {"commit": SOURCES[p], "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
              for p, b in source_bytes.items()}
    # The already verified roster and flags are read, not re-adjudicated.
    ledger = json.loads(source_bytes["runs/k4b_verdict_table.json"])
    tables = {}
    current = None
    for line in source_bytes["supp/effect_sizes_z.md"].decode("utf-8").splitlines():
        match = re.fullmatch(r"### `([^`]+)`", line)
        if match:
            current = match[1]
            tables[current] = {}
        elif current and re.match(r"\| `G[123]_S[123]`", line):
            fields = [s.strip().strip("`") for s in line.split("|")[1:-1]]
            tables[current][fields[0]] = {"z_ddof0": fields[5], "z_ddof1": fields[8]}
    rows = []
    for pair in ledger["pairs"]:
        boundary = pair["predicates"][0]["a13_boundary"]
        for cell, values in tables[pair["pair_id"]].items():
            rows.append({"pair": pair["pair_id"], "cell": cell, **values,
                         "qualified_ddof0": boundary["versions"]["ddof_0"]["a13_qualified"],
                         "ddof_split": boundary["DDOF_SPLIT"]})
    maximum = max(float(row["z_ddof0"]) for row in rows)
    (OUT / "fig1_data.json").write_text(json.dumps({"inputs": inputs, "rows": rows}, indent=2) + "\n", encoding="utf-8")
    tex = [r"\begin{tikzpicture}[x=1mm,y=1mm,font=\fontsize{9}{10}\selectfont]", r"\path[use as bounding box] (-5,-93) rectangle (173,5);"]
    tex[0:0] = color_definitions()
    for index, pair in enumerate(ledger["pairs"]):
        name = pair["pair_id"]
        boundary = pair["predicates"][0]["a13_boundary"]
        ox, oy = (index % 5) * 35.1, -(index // 5) * 29
        pair_label = "--".join(rf"\textcolor{{{method_color(m)}}}{{{DISPLAY_NAMES.get(m, m)}}}" for m in name.split("__"))
        tex.append(rf"\node at ({ox+13},{oy+3}) {{{pair_label}}};")
        for si in range(1, 4):
            tex.append(rf"\node at ({ox+(si-1)*7+3.5},{oy-1}) {{S{si}}};")
        values = []
        for gi in range(1, 4):
            tex.append(rf"\node[anchor=east] at ({ox-0.5},{oy-4-(gi-1)*6.5-3.25}) {{G{gi}}};")
            values.append([])
            for si in range(1, 4):
                z = float(tables[name][f"G{gi}_S{si}"]["z_ddof0"])
                values[-1].append(z)
                x, y = ox+(si-1)*7, oy-4-(gi-1)*6.5
                fill, rgb = z_color(z, maximum)
                tex.append(rf"\fill[fill={fill}] ({x},{y}) rectangle ({x+7},{y-6.5});")
                # Numbers inside the graphic are derived annotations, with the same source pointer.
                pointer = f"supp/effect_sizes_z.md @ {SOURCES['supp/effect_sizes_z.md']} {name} G{gi}_S{si} z-ddof0 rounded-2dp"
                linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
                luminance = sum(a*b for a, b in zip(linear, [.2126, .7152, .0722]))
                color = "white" if luminance < .179 else "black"
                tex.append(rf"\node[text={color}] at ({x+3.5},{y-3.25}) {{\NUM{{{z:.2f}}}{{{pointer}}}}};")
        # Categorical axes: mark observed cells only; never interpolate a threshold.
        for gi in range(3):
            for si in range(3):
                if values[gi][si] > 3:
                    x, y = ox+si*7, oy-4-gi*6.5
                    box = f"({x+.20},{y-.20}) rectangle ({x+6.80},{y-6.30})"
                    tex += [rf"\draw[white,line width=1.7pt] {box};",
                            rf"\draw[black,line width=1.05pt] {box};"]
        # Panel frames replace title footnote-like symbols; split is still qualified.
        if boundary["versions"]["ddof_0"]["a13_qualified"]:
            style = "black,line width=.45pt"
            if boundary["DDOF_SPLIT"]:
                style += ",double,double distance=.8pt"
            tex.append(rf"\draw[{style}] ({ox-.8},{oy+.7}) rectangle ({ox+21.8},{oy-24.3});")
    tex.append(r"\node[anchor=east] at (41,-87) {$z$};")
    for i in range(100):
        fill, _ = z_color(maximum*i/99, maximum)
        tex.append(rf"\fill[fill={fill}] ({45+i*.8},-85) rectangle ({45+(i+1)*.8},-88);")
    for label, x in [(0, 45), (3, 45+80*3/maximum), (maximum, 125)]:
        val = f"{label:.2f}" if label == maximum else str(label)
        tex.append(rf"\node at ({x:.8f},-91) {{\NUM{{{val}}}{{supp/effect_sizes_z.md @ {SOURCES['supp/effect_sizes_z.md']} z-display-scale}}}};")
    tex.append(r"\end{tikzpicture}")
    (OUT / "fig1_phase.pgf").write_text("\n".join(tex)+"\n", encoding="utf-8")
    caption = (r"$z=|\mathrm{mean}_d|/(\mathrm{SD}_X+\mathrm{SD}_Y)$, ddof\NUM{0}{supp/effect_sizes_z.md @ "
               + SOURCES["supp/effect_sizes_z.md"] + r" section2 ddof0}; thick cell borders: crossing the protocol threshold ($z>\NUM{3}{protocol/D0_experiment_protocol.md @ "
               + "1c5f06c95129f47b5df6bcb44596d983ea81c763 sec4 separation-threshold" + r"}$). "
               + r"Solid/double panel frames: qualifying under ddof\NUM{0}{runs/k4b_verdict_table.json @ " + SOURCES["runs/k4b_verdict_table.json"]
               + r" a13-boundary ddof-0}; double frames: also below $\NUM{3}{supp/effect_sizes_z.md @ " + SOURCES["supp/effect_sizes_z.md"]
               + r" z-threshold}\sigma$ under ddof\NUM{1}{runs/k4b_verdict_table.json @ " + SOURCES["runs/k4b_verdict_table.json"] + r" a13-boundary DDOF-SPLIT}.")
    (OUT / "fig1_phase.tex").write_text("\\begin{figure*}[t]\n\\centering\n\\input{figs/fig1_phase.pgf}\n\\begingroup\n\\let\\normalsize\\small\n\\normalsize\n\\caption{"+caption+"}\n\\label{fig:phase}\n\\endgroup\n\\end{figure*}\n", encoding="utf-8")
    (OUT / "fig1_inputs.json").write_text(json.dumps({"inputs": inputs, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "display": {"contour_levels": [], "cell_border_threshold": "z > 3", "panel_frames": "solid qualified; double qualified and DDOF_SPLIT", "z_annotation_decimals": 2, "colormap": "cividis_r", "method_colors": METHOD_COLORS, "no_rejudgment": True}}, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    export()
