import pandas as pd

from src.energyatlas import data, ptf_analiz as pa


def test_gunluk_veri_tam_ve_24_saatli():
    g = data.ptf_gunluk()
    assert (g["saat_sayisi"] == 24).all()
    assert g["tarih"].is_monotonic_increasing
    assert not g["tarih"].duplicated().any()


def test_yillik_ortalamalar_ve_kur():
    y = pa.yillik(data.ptf_gunluk())
    assert {"tl", "usd", "kur", "kismi"}.issubset(y.columns)
    assert ((y["kur"] - y["tl"] / y["usd"]).abs() < 1e-9).all()
    # 2016 USD ortalaması, mevcut yıllık PTF tablosuyla (ptf.csv) uyumlu olmalı
    assert abs(float(y.loc[y["yil"] == 2016, "usd"].iloc[0]) - 46) < 1
    assert bool(y.loc[y["yil"] == y["yil"].max(), "kismi"].iloc[0])


def test_profil_matrisi_boyutu_ve_saat_ozeti():
    p = data.ptf_profil()
    m = pa.profil_matrisi(p, 2025, "usd")
    assert m.shape == (24, 12)
    ozet = pa.saat_ozeti(p, 2025, "usd")
    assert ozet["en_yuksek"] >= ozet["en_dusuk"]
    assert 0 <= ozet["en_yuksek_saat"] <= 23


def test_aylik_on_eki_ve_yil_dizisi():
    a = pa.aylik(data.ptf_gunluk(), "usd")
    assert set(a["ay_adi"]) <= set(pa.AYLAR)
    assert a["ay"].between(1, 12).all()
    assert isinstance(a["yil"].iloc[0], str)


def test_cagr_hesabi():
    # 100 -> 200 iki yılda: yıllık yaklaşık %41,4
    assert abs(pa.cagr(100, 200, 2020, 2022) - 41.42) < 0.01
    assert pa.cagr(100, 100, 2020, 2025) == 0
    assert pa.cagr(0, 100, 2020, 2025) is None
    assert pa.cagr(100, 200, 2025, 2025) is None
