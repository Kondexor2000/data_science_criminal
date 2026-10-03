"""Interfejs wiersza poleceń."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from misconduct_mvp.analysis import load_cases, summarize
from misconduct_mvp.reporting import write_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Opisowa analiza wyników spraw (nie ocena winy ani częstości nadużyć)."
    )
    parser.add_argument("--input", type=Path, required=True, help="Ścieżka do wejściowego CSV.")
    parser.add_argument("--output", type=Path, default=Path("reports"), help="Folder raportu.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        cases = load_cases(args.input)
        summary = summarize(cases)
        write_report(summary, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    logging.info("Raport zapisano w %s", args.output.resolve())


if __name__ == "__main__":
    main()
