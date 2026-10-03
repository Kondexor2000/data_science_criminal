"""Zapis wyników analizy na dysk."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from misconduct_mvp.analysis import OUTCOMES

LABELS_PL = {
    "conviction": "Skazanie",
    "acquittal": "Uniewinnienie",
    "other": "Inne",
    "unknown": "Nieznane",
}


def write_report(summary: dict[str, object], output_dir: Path) -> None:
    """Zapisz podsumowanie JSON oraz wykres liczebności rozstrzygnięć."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    outcomes = summary["outcomes"]
    counts = [outcomes[outcome]["count"] for outcome in OUTCOMES]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar([LABELS_PL[item] for item in OUTCOMES], counts, color="#3b6ea8")
    ax.bar_label(bars, padding=3)
    ax.set_title("Rozstrzygnięcia spraw w analizowanym zbiorze")
    ax.set_ylabel("Liczba spraw")
    ax.set_ylim(0, max(counts, default=0) * 1.18 + 1)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_dir / "outcomes.png", dpi=160)
    plt.close(fig)
