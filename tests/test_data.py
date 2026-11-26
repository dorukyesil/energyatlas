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


def test_on_lisans_toplamlari_gorsele_uygun():
    df = data.depolama_on_lisans()
    ges = df[df["teknoloji"] == "GES"]
    res = df[df["teknoloji"] == "RES"]
    assert ges["proje_adedi"].sum() == 297
    assert res["proje_adedi"].sum() == 233
    assert abs(ges["kapasite_mwe"].sum() - 10555) <= 5  # görseldeki yuvarlama farkı
    assert abs(res["kapasite_mwe"].sum() - 16399) <= 5


def test_isletmedeki_toplamlar():
    df = data.isletmedeki_depolama()
    assert len(df) == 10
    assert abs(df["kapasite_mwh"].sum() - 419.5) < 0.05
    assert abs(df["guc_mwe"].sum() - 388.5) < 0.05
    assert abs(df[df["tesis_turu"] == "Güneş"]["kapasite_mwh"].sum() - 278.9) < 0.05
    assert abs(df[df["tesis_turu"] == "Rüzgar"]["kapasite_mwh"].sum() - 140.6) < 0.05


def test_tarife_tek_zamanli_pozitif():
    df = data.tarife()
    assert (df["tek_zamanli"] > 0).all()


def test_ptf_2026_dusus_yuzde_35():
    df = data.ptf().set_index("donem")
    degisim = df.loc["2026 9A", "ptf_usd_mwh"] / df.loc["2025 9A", "ptf_usd_mwh"] - 1
    assert round(degisim * 100, 1) == -34.8 or round(degisim * 100, 0) == -35


def test_yeni_grafikler_olusur_2():
    assert len(charts.on_lisans_yillik(data.depolama_on_lisans(), "t").data) == 2
    assert len(charts.isletmedeki_cubuk(data.isletmedeki_depolama(), "t").data) == 1
    assert len(charts.ptf_cubuk(data.ptf(), "t").data) == 1


def test_yekdem_formul_toplam_100():
    assert data.yekdem_formul()["agirlik_pct"].sum() == 100


def test_yekdem_duyuru_her_kaynak_uc_ay():
    df = data.yekdem_duyuru()
    assert df.groupby("kaynak")["donem"].nunique().eq(3).all()
    assert len(df["kaynak"].unique()) == 12


def test_yekdem_yerli_katki_asagi_yukari_mantik():
    df = data.yekdem_fiyat()
    for teknoloji, alt in df.groupby("teknoloji"):
        taban = alt[alt["gosterge"] == "Taban"]["usd_mwh"].iloc[0]
        tavan = alt[alt["gosterge"] == "Tavan"]["usd_mwh"].iloc[0]
        assert taban < tavan


def test_dunya_gunes_payi_hesapla_tutarli():
    kurulu = data.dunya_kurulu_guc().set_index("donem")
    pay = data.dunya_gunes_payi().set_index("donem")
    for donem in [2024, 2035, 2040, 2050]:
        hesap = kurulu.loc[donem, "gunes_gw"] / kurulu.loc[donem, "toplam_gw"] * 100
        assert abs(hesap - pay.loc[donem, "gunes_toplam_pct"]) < 1.0


def test_ulke_tablosu_turkiye_var():
    assert "Türkiye" in data.ulke_gunes_2024()["ulke"].tolist()


def test_yeni_grafikler_olusur_3():
    assert len(charts.yekdem_cizgi(data.yekdem_duyuru(), "t").data) == 12
    assert len(charts.dunya_pay_nokta(data.dunya_gunes_payi(), "t").data) == 2
    assert len(charts.ulke_yatay_cubuk(data.ulke_gunes_2024(), "t").data) == 1


def test_kuresel_yatirim_temiz_toplamdan_kucuk():
    df = data.kuresel_yatirim()
    assert (df["temiz_enerji_mlrd_usd"] <= df["toplam_mlrd_usd"]).all()
    assert (df["gunes_mlrd_usd"] <= df["temiz_enerji_mlrd_usd"]).all()


def test_gunes_bolge_toplami_asmiyor():
    df = data.gunes_yatirim_bolge()
    etiketli = df["asya_pasifik_mlrd_usd"] + df["kuzey_amerika_mlrd_usd"] + df["avrupa_mlrd_usd"]
    assert (etiketli <= df["toplam_mlrd_usd"]).all()


def test_gunes_toplami_iki_veri_setinde_ayni():
    k = data.kuresel_yatirim().set_index("yil")["gunes_mlrd_usd"]
    b = data.gunes_yatirim_bolge().set_index("yil")["toplam_mlrd_usd"]
    assert (k == b).all()


def test_kuresel_yatirim_grafikleri():
    assert len(charts.kuresel_yatirim_cubuk(data.kuresel_yatirim(), "t").data) == 3
    assert len(charts.bolge_yigin_cubuk(data.gunes_yatirim_bolge(), "t").data) == 4


def test_yillik_degisim_sadece_tam_yillar():
    df = data.yillik_degisim(data.kurulu_guc(), "toplam_gw")
    assert df["donem"].astype(str).str.fullmatch(r"\d{4}").all()
    assert "2016" not in df["donem"].astype(str).tolist()  # ilk yıl değişim yok
    assert abs(df.iloc[0]["degisim_pct"] - (84.9 / 78.7 - 1) * 100) < 0.01


def test_tam_yillar_9a_haric():
    df = data.tam_yillar(data.uretim())
    assert len(df) == 10


def test_sayi_turkce_bicim():
    from src.energyatlas.ui import sayi
    assert sayi(1234.5) == "1.234,5"
    assert sayi(0.5, 2) == "0,50"
    assert sayi(127.2) == "127,2"


def test_yeni_gorsel_grafikler():
    k = data.kurulu_guc()
    assert len(charts.cizgi_alan(data.tam_yillar(k), "donem", "toplam_gw", "t", "GW", "GW", 3).data) == 2
    assert len(charts.yillik_degisim_cubuk(data.yillik_degisim(k, "toplam_gw"), "donem", "degisim_pct", "t").data) == 1
    matris = k.set_index("donem")[["termik_pct", "ruzgar_pct"]].T
    assert len(charts.isi_haritasi(matris, "t", "turkuaz").data) == 1
    assert len(charts.depolama_kabarcik(data.isletmedeki_depolama(), "t").data) == 2


def test_sunum_ozet_slayt_sayisi_ve_format():
    import io
    from pptx import Presentation
    from src.energyatlas import export

    prs = Presentation(io.BytesIO(export.ozet_sunum_bytes()))
    assert len(prs.slides) == len(export.PLAN)
    assert len(prs.slides) >= 25


def test_guncelleme_kaydi(tmp_path, monkeypatch):
    from src.energyatlas import guncelleme

    monkeypatch.setattr(guncelleme, "KAYIT_DOSYASI", tmp_path / "g.json")
    kayit = guncelleme.guncelle()
    assert kayit["son_guncelleme"]
    assert guncelleme.oku()["son_guncelleme"] == kayit["son_guncelleme"]


def test_her_tablonun_kaynagi_var():
    import re
    from pathlib import Path as _P
    from src.energyatlas.ui import TABLO_KAYNAKLARI

    kok = _P(__file__).resolve().parent.parent
    kaynak_dosyalar = list((kok / "views").glob("*.py")) + list((kok / "src" / "energyatlas" / "sayfalar").glob("*.py"))
    dosyalar = re.findall(r'veri_tablosu\([^\n]*?"([^"]+\.csv)"', "\n".join(p.read_text(encoding="utf-8") for p in kaynak_dosyalar))
    eksik = sorted(set(d for d in dosyalar if d not in TABLO_KAYNAKLARI))
    assert not eksik, f"Kaynağı tanımsız tablolar: {eksik}"


def test_weo_birlesik_veri_tutarli():
    df = data.weo_tum()
    assert {"Dünya"} <= set(df["kapsam"].unique())
    assert df["senaryo"].isin(["Gerçekleşen"] + data.WEO_SENARYOLAR).all()
    toplam_2025 = df[(df.kapsam == "Dünya") & (df.kategori == "Capacity: installed") & (df.urun == "Total") & (df.yil == 2025) & (df.senaryo == "Gerçekleşen")]["deger"].iloc[0]
    parca = df[(df.kapsam == "Dünya") & (df.kategori == "Capacity: installed") & (df.urun.isin(["Solar PV", "Wind", "Hydro", "Nuclear"])) & (df.yil == 2025) & (df.senaryo == "Gerçekleşen")]["deger"].sum()
    assert parca < toplam_2025


def test_yatirim_bolge_toplam_ayrik_bolgelerin_toplami():
    df = data.yatirim_bolge()
    dunya = df[(df.bolge == "World") & (df.kategori == "Toplam") & (df.yil == 2025)]["deger"].iloc[0]
    ayrik = df[(df.bolge.isin(["İleri ekonomiler", "Gelişmekte olan ekonomiler (Çin dahil)"])) & (df.kategori == "Toplam") & (df.yil == 2025)]["deger"].sum()
    # Dünya toplamı, bölge toplamından biraz büyüktür (kayıtlı kalan küçük fark).
    assert 0 < dunya - ayrik < 150


def test_weo_sayfa_grafikleri():
    assert len(charts.cizgi_coklu(data.weo_coklu("Energy", "Total energy supply", ["Coal", "Oil"], "Mevcut politikalar"), "yil", "urun", "deger", "t", "EJ").data) == 2
    assert len(charts.yigin_cubuk(data.weo_coklu("Energy", "Electricity generation", ["Wind", "Solar PV"], "Net sıfır (2050)"), "yil", "urun", "deger", "t", "TWh").data) == 2
