"""Üretim: kaynak ve dönem seçilerek incelenir (TEİAŞ yıllık ve aylık tabloları)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

KAYNAKLAR = {
    "Termik": ("termik_twh", "termik_pct"),
    "Hidro": ("hidro_twh", "hidro_pct"),
    "Rüzgar + jeotermal": ("ruzgar_jeotermal_twh", "ruzgar_jeotermal_pct"),
    "Güneş": ("gunes_twh", "gunes_pct"),
    "Toplam": ("toplam_twh", None),
}
GUNCEL = "2026 Ocak-Ekim"


def _tablo() -> pd.DataFrame:
    """Yıllık TEİAŞ satırları ve 2026 Ocak-Ekim (aylık toplam) satırını birlikte döndürür."""
    yillik = data.teias_uretim().copy()
    aylik = data.teias_aylik()
    s = aylik[(aylik["yil"] == 2026) & (aylik["ay_no"] <= 10)]
    toplam = float(s["total_generation"].sum()) / 1000
    satir = {
        "donem": GUNCEL,
        "toplam_twh": toplam,
        "termik_twh": float(s["thermal"].sum()) / 1000,
        "hidro_twh": float(s["hydro"].sum()) / 1000,
        "ruzgar_jeotermal_twh": float((s["wind"] + s["geothermal"]).sum()) / 1000,
        "gunes_twh": float(s["solar"].sum()) / 1000,
    }
    for k in ["termik", "hidro", "ruzgar_jeotermal", "gunes"]:
        satir[f"{k}_pct"] = satir[f"{k}_twh"] / toplam * 100
    return pd.concat([yillik, pd.DataFrame([satir])], ignore_index=True)


def render() -> None:
    df = _tablo()
    donemler = df["donem"].tolist()
    c1, c2 = st.columns([1, 2])
    with c1:
        kaynak = st.selectbox("Kaynak", list(KAYNAKLAR.keys()), index=0, key="uretim_kaynak")
    with c2:
        donem = st.select_slider("Dönem", options=donemler, value=donemler[-1], key="uretim_donem")

    twh_kol, pct_kol = KAYNAKLAR[kaynak]
    secili = df[df["donem"] == donem].iloc[0]
    ilk = df[df["donem"] == "2016"].iloc[0]
    twh = float(secili[twh_kol])
    toplam = float(secili["toplam_twh"])

    k1, k2, k3 = st.columns(3)
    k1.metric(f"{kaynak} üretimi ({donem})", f"{ui.sayi(twh)} TWh")
    if kaynak == "Toplam":
        k2.metric(f"Toplam üretim ({donem})", f"{ui.sayi(toplam)} TWh", f"{toplam - float(ilk['toplam_twh']):+.1f} TWh (2016'ya göre)".replace(".", ","), delta_color="off")
    else:
        pay = twh / toplam * 100
        k2.metric(f"{kaynak} payı ({donem})", f"%{ui.sayi(pay)}", f"{pay - float(ilk[pct_kol]):+.1f} puan (2016'ya göre)".replace(".", ","), delta_color="off")
    k3.metric("Dönem", donem)

    ui.bolum("01", f"{kaynak}: zaman içinde", "Seçilen kaynağın üretimi (sütun) ve toplam içindeki payı (çizgi). 2026 satırı Ocak-Ekim toplamıdır.")
    if kaynak == "Toplam":
        st.plotly_chart(charts.toplam_cubuk(df, "toplam_twh", "Toplam brüt üretim (TWh)", "TWh"), use_container_width=True)
    else:
        st.plotly_chart(charts.toplam_cubuk(df, twh_kol, f"{kaynak} üretimi (TWh)", "TWh"), use_container_width=True)
        st.plotly_chart(charts.cizgi_alan(df[df["donem"] != GUNCEL], "donem", pct_kol, f"{kaynak} payı (%)", "%", "%"), use_container_width=True)
    ui.teias_notu("uretim", "aylik", ek="2026 Ocak-Ekim satırı TEİAŞ aylık tablosundan hesaplanmıştır; rüzgar ve jeotermal birleşiktir, atık termik içindedir.")

    ui.bolum("02", "Kaynaklara göre karşılaştırma", f"{donem} dönemi, tüm kaynaklar.")
    satirlar = [(ad, float(secili[twh])) for ad, (twh, _) in KAYNAKLAR.items() if ad != "Toplam"]
    st.plotly_chart(charts.yatay_deger_cubuk(pd.DataFrame(satirlar, columns=["kaynak", "twh"]), "kaynak", "twh", f"Kaynaklara göre üretim, {donem} (TWh)", "TWh"), use_container_width=True)

    ui.veri_tablosu(df.assign(donem=df["donem"]), "Veri tablosu (yıllık ve 2026)", "teias_uretim.csv")
