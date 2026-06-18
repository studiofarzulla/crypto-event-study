"""
Corrected C2 figure + summary CSV (scope-condition framing).
Separates the primary curated sample from the nested mechanical impact-screen
sweep on the reconstructed 135-pool, and marks statistical significance.
Numbers: c2-summary-table.csv (curated/1-asset/no-filter/3-asset) + c2b run (2-asset).
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent  # r1-revision/

rows = [
    # label, n, infra, reg, mult, p, kind
    ("Curated\n(n=50)",     50, 1.978, 0.405, 4.88, 0.0015, "curated"),
    ("No filter\n(135)",   135, 0.209, 0.364, 0.58, 0.4464, "mech"),
    (r"$\geq$1 asset""\n(115)", 115, 1.403, 0.944, 1.49, 0.3205, "mech"),
    (r"$\geq$2 assets""\n(93)", 93, 2.889, 1.793, 1.61, 0.1635, "mech"),
    (r"$\geq$3 assets""\n(77)", 77, 3.834, 2.924, 1.31, 0.4029, "mech"),
]
df = pd.DataFrame(rows, columns=["label","n","mean_infra","mean_reg","multiplier","welch_p","kind"])
df_csv = df.drop(columns="label").copy()
df_csv.insert(0, "spec", ["primary_curated","nofilter_135","oneasset_115","twoasset_93","threeasset_77"])
df_csv["note"] = ["5.7x under canonical rolling winsorisation; significant",
                  "not significant","not significant",
                  "like-for-like analogue of curated criterion; not significant",
                  "not significant"]
df_csv.to_csv(OUT / "c2-summary-CORRECTED.csv", index=False)

fig, ax = plt.subplots(figsize=(8.2, 4.6))
colors = ["#7a1f3d" if k=="curated" else "#c8b58c" for k in df["kind"]]
bars = ax.bar(df["label"], df["multiplier"], color=colors, edgecolor="black", linewidth=0.6)
for b, p, m in zip(bars, df["welch_p"], df["multiplier"]):
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.08, f"{m:.2f}x\n({sig})",
            ha="center", va="bottom", fontsize=9)
ax.axhline(1.0, color="gray", ls="--", lw=0.8)
ax.set_ylabel(r"$\bar{\delta}_{\mathrm{infra}}/\bar{\delta}_{\mathrm{reg}}$ multiplier")
ax.set_title("Infrastructure/regulatory multiplier: curated sample vs nested mechanical screens\n"
             "(only the curated sample is statistically significant)", fontsize=10)
ax.set_ylim(0, 5.6)
# divider between curated (distinct selection process) and the mechanical sweep
ax.axvline(0.5, color="black", lw=0.8, ls=":")
ax.text(3.0, 5.25, "mechanical impact screen on reconstructed 135-pool (nested, all n.s.)",
        ha="center", fontsize=8, color="#5a5a3d")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "c2-multiplier-CORRECTED.png", dpi=150)
fig.savefig(OUT / "c2-multiplier-CORRECTED.pdf")
print("wrote c2-summary-CORRECTED.csv, c2-multiplier-CORRECTED.{png,pdf}")
print(df_csv.to_string(index=False))
