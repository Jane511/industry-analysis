from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import ALL_CONTRACT_EXPORTS, LEGACY_PARQUET_EXPORTS_DIR
from src.contract_exports import CONTRACT_EXPORT_KEYS
from src.output import save_csv


def migrate_parquet_to_csv() -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []
    for key in CONTRACT_EXPORT_KEYS:
        parquet_path = LEGACY_PARQUET_EXPORTS_DIR / f"{key}.parquet"
        csv_path = ALL_CONTRACT_EXPORTS[key]
        if not parquet_path.exists():
            summary.append({
                "key": key,
                "parquet": str(parquet_path),
                "csv": str(csv_path),
                "status": "missing parquet",
                "rows": 0,
                "columns": 0,
            })
            continue
        df = pd.read_parquet(parquet_path)
        save_csv(df, csv_path)
        summary.append({
            "key": key,
            "parquet": str(parquet_path),
            "csv": str(csv_path),
            "status": "written",
            "rows": len(df),
            "columns": len(df.columns),
        })
    return summary


def main() -> None:
    summary = migrate_parquet_to_csv()
    print("Parquet to CSV migration summary")
    for row in summary:
        print(
            f"{row['key']}: {row['status']} rows={row['rows']} "
            f"cols={row['columns']} -> {row['csv']}"
        )


if __name__ == "__main__":
    main()
