import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import CODING_FOLDER

# Script jobs
# 1- Load the coding outputs of 05_code_provisions.py
# 2- Panel A: share of statements carrying each conservation logic, per document (ordered by year)
# 3- Panel B: ES statements by function and operationality
# 4- Save the figure as PDF and PNG

# File locations

logic_file = CODING_FOLDER / "logic_by_document.csv"
es_file = CODING_FOLDER / "es_statements.csv"

figure_pdf = CODING_FOLDER / "figure_coding.pdf"
figure_png = CODING_FOLDER / "figure_coding.png"

# Colours and labels

logic_styles = {
    "command_control_share": ("Command-and-control", "#2a78d6", "s"),
    "market_valuation_share": ("Market-valuation", "#eb6834", "o"),
    "participatory_plural_share": ("Participatory-plural", "#1baf7a", "^")
}

operationality_styles = {
    "declarative": ("Declarative", "#9ec5f4"),
    "deferring": ("Deferring", "#3987e5"),
    "operational": ("Operational", "#104281")
}

function_labels = {
    "market_valuation": "Market-valuation",
    "general_es": "General ES",
    "participatory_plural": "Participatory-plural",
    "command_control": "Command-and-control"
}

ink = "#3d3d3a"
muted = "#8a8984"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.edgecolor": muted,
    "axes.labelcolor": ink,
    "xtick.color": ink,
    "ytick.color": ink,
    "axes.spines.top": False,
    "axes.spines.right": False
})

# Data

logic = pd.read_csv(logic_file).sort_values(["year", "label_en"], ascending=[False, False])
logic["ylabel"] = logic["label_en"] + " (" + logic["year"].astype(str) + ")"

es = pd.read_csv(es_file)
counts = (
    es.groupby(["es_function", "operationality"]).size()
    .unstack(fill_value=0)
    .reindex(columns=list(operationality_styles), fill_value=0)
    .reindex(list(function_labels))
    .fillna(0)
)
counts = counts.loc[counts.sum(axis=1) > 0].iloc[::-1]

# Figure

fig, (ax_a, ax_b) = plt.subplots(
    2, 1,
    figsize=(6.3, 7.6),
    gridspec_kw={"height_ratios": [3.2, 1]}
)

positions = range(len(logic))

for column, (label, colour, marker) in logic_styles.items():
    ax_a.scatter(
        logic[column] * 100,
        positions,
        s=26,
        color=colour,
        marker=marker,
        edgecolor="white",
        linewidth=0.8,
        label=label,
        zorder=3
    )

ax_a.set_yticks(list(positions))
ax_a.set_yticklabels(logic["ylabel"])
ax_a.set_xlabel("Share of statements carrying each logic (%)")
ax_a.grid(axis="x", color="#e6e5e0", linewidth=0.6, zorder=0)
ax_a.set_xlim(left=0)
ax_a.legend(frameon=False, loc="lower right", handletextpad=0.3)
ax_a.set_title("A. Conservation logics within each selected document", loc="left", fontsize=9, color=ink)

left = pd.Series(0, index=counts.index, dtype=float)

for column, (label, colour) in operationality_styles.items():
    values = counts[column]
    bars = ax_b.barh(
        [function_labels[f] for f in counts.index],
        values,
        left=left,
        color=colour,
        edgecolor="white",
        linewidth=1.5,
        label=label,
        height=0.6
    )

    for bar, value in zip(bars, values):
        if value >= 2:
            ax_b.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + bar.get_height() / 2,
                str(int(value)),
                ha="center",
                va="center",
                fontsize=7,
                color="white" if column != "declarative" else ink
            )

    left += values

ax_b.set_xlabel("Number of ES statements")
ax_b.legend(frameon=False, loc="lower right", ncol=3, handletextpad=0.3)
ax_b.set_title("B. ES statements by function and operationality", loc="left", fontsize=9, color=ink)

fig.tight_layout()
fig.savefig(figure_pdf)
fig.savefig(figure_png, dpi=200)

print(f"Saved to: {figure_pdf}")
