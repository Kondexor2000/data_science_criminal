"""Walidacja i statystyki opisowe dla wyników spraw."""

from __future__ import annotations

import logging
from pathlib import Path
from statistics import NormalDist

import pandas as pd

LOGGER = logging.getLogger(__name__)
OUTCOMES = ("conviction", "acquittal", "other", "unknown")
REQUIRED_COLUMNS = ("case_id", "outcome")


def load_cases(path: Path) -> pd.DataFrame:
    """Wczytaj CSV i sprawdź minimalny schemat oraz unikalność identyfikatorów."""
    frame = pd.read_csv(path, dtype={"case_id": "string", "outcome": "string"})
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Brak wymaganych kolumn: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("Plik nie zawiera żadnych spraw.")
    if frame["case_id"].isna().any() or frame["case_id"].str.strip().eq("").any():
        raise ValueError("case_id nie może być pusty.")
    if frame["case_id"].duplicated().any():
        raise ValueError("case_id musi być unikalny (jeden wiersz na sprawę).")

    frame["outcome"] = frame["outcome"].str.strip().str.lower()
    invalid = sorted(set(frame["outcome"].dropna()) - set(OUTCOMES))
    if frame["outcome"].isna().any() or invalid:
        raise ValueError(f"Nieprawidłowe outcome. Dozwolone wartości: {', '.join(OUTCOMES)}")
    if "year" in frame.columns:
        frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    LOGGER.info("Wczytano %d spraw z %s", len(frame), path)
    return frame


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    """Przedział Wilsona dla proporcji; zwraca ułamki z zakresu 0–1."""
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Wymagane: total > 0 oraz 0 <= successes <= total.")
    if not 0 < confidence < 1:
        raise ValueError("confidence musi należeć do przedziału (0, 1).")
    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    proportion = successes / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = z * ((proportion * (1 - proportion) / total + z**2 / (4 * total**2)) ** 0.5)
    margin /= denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def summarize(frame: pd.DataFrame) -> dict[str, object]:
    """Policz rozkład rozstrzygnięć i niepewność odsetka skazań."""
    counts = frame["outcome"].value_counts().reindex(OUTCOMES, fill_value=0)
    total = int(counts.sum())
    lower, upper = wilson_interval(int(counts["conviction"]), total)
    return {
        "n_cases": total,
        "outcomes": {
            label: {"count": int(counts[label]), "share": float(counts[label] / total)}
            for label in OUTCOMES
        },
        "conviction_share_wilson_95": {"lower": lower, "upper": upper},
        "interpretation": (
            "Opis wyników w dostarczonym zbiorze. Odsetek rozstrzygnięć nie mierzy częstości "
            "rzeczywistych nadużyć i sam w sobie nie dowodzi winy ani niewinności."
        ),
        "data_notice": "Wyniki zależą od doboru spraw, jurysdykcji, okresu i kodowania danych.",
    }
