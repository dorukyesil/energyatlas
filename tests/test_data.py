import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import DATA_DIR  # noqa: E402
from src.energyatlas.data import filter_by_year, load_csv  # noqa: E402


def test_load_csv_reads_sample():
    df = load_csv(DATA_DIR / "uretim_ornek.csv")
    assert {"tarih", "kaynak", "uretim_mwh"} <= set(df.columns)
    assert len(df) > 0


def test_load_csv_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "yok.csv")


def test_filter_by_year_keeps_only_that_year():
    df = load_csv(DATA_DIR / "uretim_ornek.csv")
    sonuc = filter_by_year(df, 2024)
    assert (sonuc["tarih"].dt.year == 2024).all()
    assert len(sonuc) == len(df)
