from __future__ import annotations

import importlib
from pathlib import Path

import pandas as pd


def ensure_parquet_engine_available() -> str:
    engines = ("pyarrow", "fastparquet")
    for engine in engines:
        try:
            importlib.import_module(engine)
            return engine
        except Exception:
            continue
    raise RuntimeError(
        "Parquet export requires `pyarrow` or `fastparquet`, but neither is installed. "
        "Install dependencies with `python -m pip install -r requirements.txt`."
    )

def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = ensure_parquet_engine_available()
    df.to_parquet(path, index=False, engine=engine)
