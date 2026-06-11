from __future__ import annotations

import pandas as pd

from src.csv_io import DATE_COLUMNS, INTEGER_COLUMNS, READERS, STRING_COLUMNS
from src.output import save_csv
from src.overlays.export_contracts import export_contracts


def test_canonical_csv_helpers_preserve_declared_dtypes(tmp_path) -> None:
    exports = export_contracts()

    for key, df in exports.items():
        path = tmp_path / f"{key}.csv"
        save_csv(df, path)
        roundtrip = READERS[key](path)

        assert list(roundtrip.columns) == list(df.columns)
        assert len(roundtrip) == len(df)

        for col in STRING_COLUMNS.get(key, []):
            if col in roundtrip.columns:
                assert pd.api.types.is_string_dtype(roundtrip[col]), f"{key}.{col} should be string"

        for col in INTEGER_COLUMNS.get(key, []):
            if col in roundtrip.columns:
                assert str(roundtrip[col].dtype) == "Int64", f"{key}.{col} should be nullable Int64"

        for col in DATE_COLUMNS.get(key, []):
            if col in roundtrip.columns:
                assert pd.api.types.is_datetime64_any_dtype(roundtrip[col]), f"{key}.{col} should be datetime"
