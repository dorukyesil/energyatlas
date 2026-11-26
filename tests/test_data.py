import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.energyatlas import charts, data  # noqa: E402
from src.energyatlas.data import load_dataset  # noqa: E402


def test_missing_dataset_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_dataset("yok", data_dir=tmp_path)


@pytest.mark.parametrize("loader", [data.kurulu_guc, data.uretim, data.tuketim])
def test_time_series_has_12_periods(loader):
    df = loader()
    assert len(df) == 12
    assert df["donem"].iloc[0] == "2016"


def test_kurulu_guc_shares_roughly_sum_to_100():
    df = data.kurulu_guc()
    toplam = df[["termik_pct", "gunes_pct", "ruzgar_pct", "diger_ye_pct"]].sum(axis=1, min_count=3)
    # Görsellerdeki yuvarlanmış değerler nedeniyle küçük sapmalara izin verilir.
    assert ((toplam >= 97) & (toplam <= 103)).all()


def test_uretim_shares_roughly_sum_to_100():
    df = data.uretim()
    toplam = df[["termik_pct", "gunes_pct", "ruzgar_pct", "diger_ye_pct"]].sum(axis=1, min_count=3)
    assert ((toplam >= 97) & (toplam <= 103)).all()


def test_hedef_toplam_matches_components():
    df = data.hedefler().set_index("kaynak")
    for kolon in df.columns:
        if pd.isna(df.loc["Toplam", kolon]):
            continue
        yenilenebilir = df.loc["Toplam Yenilenebilir", kolon]
        termik = df.loc["Toplam Termik", kolon]
        toplam = df.loc["Toplam", kolon]
        if pd.notna(yenilenebilir) and pd.notna(termik):
            assert abs(yenilenebilir + termik - toplam) < 1.0, kolon


def test_kisi_basina_turkiye_below_oecd():
    df = data.kisi_basina().set_index("kaynak")
    assert df.loc["Türkiye", "kwh_kisi"] < df.loc["OECD", "kwh_kisi"]


@pytest.mark.parametrize(
    "build",
    [
        lambda: charts.toplam_cubuk(data.kurulu_guc(), "toplam_gw", "t", "GW"),
        lambda: charts.pay_yiginli_cubuk(data.uretim(), "t"),
        lambda: charts.tuketim_cubuk(data.tuketim(), "t"),
        lambda: charts.kisi_basina_cubuk(data.kisi_basina(), "t"),
        lambda: charts.hedef_karsilastirma(data.hedefler(), "t"),
        lambda: charts.pay_halkasi(["Güneş", "Termik"], [10, 20], "t"),
    ],
)
def test_charts_build(build):
    fig = build()
    assert len(fig.data) > 0


def test_depolama_kapasite_toplami_26_9_gw():
    toplam = data.depolama_kapasite()["kapasite_gw"].sum()
    assert abs(toplam - 26.9) < 0.05


def test_depolama_teknoloji_toplami_eşit():
    assert abs(16.4 + 10.5 - 26.9) < 0.05


def test_sirket_toplamlari_tutarli():
    df = data.depolama_sirketler()
    assert ((df["ges_mw"] + df["res_mw"]) == df["toplam_mw"]).all()


def test_devam_eden_toplam():
    df = data.devam_eden_yatirim().set_index("kalem")
    assert abs(df.loc["Depolamalı RES+GES", "gw"] + df.loc["YEKA (2025 ve 2026)", "gw"] - df.loc["Toplam", "gw"]) < 0.05


def test_yeni_grafikler_olusur():
    assert len(charts.sirket_yigin_cubuk(data.depolama_sirketler(), "t").data) == 2
    assert len(charts.yillik_pay_cubuk(data.depolama_kapasite(), "devreye_giris", "t").data) == 2
    assert len(charts.sematik_profil(list(range(3)), [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], "t").data) == 5
