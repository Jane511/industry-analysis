from __future__ import annotations

from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PUBLIC_SOURCE_URLS, RAW_PUBLIC_DIR_PTRS
from src.ptrs_reconstruction import reconstruct_ptrs_workbook_from_downloads


PTRS_DOWNLOAD_KEYS = [
    "ptrs_cycle_8_pdf",
    "ptrs_cycle_9_pdf",
    "ptrs_guidance",
]


def _filename_from_url(url: str) -> str:
    return Path(urlparse(url).path).name


def download_public_data() -> Path:
    RAW_PUBLIC_DIR_PTRS.mkdir(parents=True, exist_ok=True)
    print("Downloading public PTRS source files (network-dependent step).")
    print(f"Target directory: {RAW_PUBLIC_DIR_PTRS}")
    print("Note: optional manual context extracts should be staged under data/raw/manual/.")

    for key in PTRS_DOWNLOAD_KEYS:
        url = PUBLIC_SOURCE_URLS[key]
        destination = RAW_PUBLIC_DIR_PTRS / _filename_from_url(url)
        print(f"Downloading {key} -> {destination.name}")
        try:
            urlretrieve(url, destination)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                f"Failed to download `{key}` from `{url}`. "
                f"This script requires outbound network access to fetch PTRS public files. "
                f"If running in a restricted environment, manually stage the file at `{destination}` "
                "and rerun the script."
            ) from exc

    print(f"Saved PTRS public files to {RAW_PUBLIC_DIR_PTRS}")
    workbook_path = reconstruct_ptrs_workbook_from_downloads(RAW_PUBLIC_DIR_PTRS)
    print(f"Rebuilt PTRS workbook -> {workbook_path.name}")
    return workbook_path


def main() -> None:
    try:
        download_public_data()
    except RuntimeError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
