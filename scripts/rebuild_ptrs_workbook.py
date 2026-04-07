from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ptrs_reconstruction import reconstruct_ptrs_workbook_from_downloads


def main() -> None:
    workbook_path = reconstruct_ptrs_workbook_from_downloads()
    print(f"Rebuilt PTRS workbook -> {workbook_path}")


if __name__ == "__main__":
    main()
