"""Üretim: kaynak ve dönem seçilerek incelenir (TEİAŞ yıllık ve aylık tabloları)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

KAYNAKLAR = {
    "Termik": ("termik_twh", "termik_pct"),
    "Hidro": ("hidro_twh", "hidro_pct"),
    "Rüzgar + jeotermal": ("ruzgar_jeotermal_twh", "ruzgar_jeotermal_pct"),
    "Güneş": ("gunes_twh", "gunes_pct"),
    "Biyokütle ve atık ısı": ("atik_biyokutle_twh", "atik_biyokutle_pct"),
    "Yenilenebilir (toplam)": ("yenilenebilir_twh", "yenilenebilir_pct"),
    "Toplam": ("toplam_twh", None),
}
TOPLAMLAR = ("Yenilenebilir (toplam)", "Toplam")
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def _satir(donem: str, toplam: float, termik: float, hidro: float, rj: float, gunes: float, bio: float) -> dict:
    """Bir dönemin kaynak satırı. Termik biyokütle ve atık hariçtir; yenilenebilir bu iki kalemi de içerir."""
    satir = {
        "donem": donem, "toplam_twh": toplam, "termik_twh": termik, "hidro_twh": hidro,
        "ruzgar_jeotermal_twh": rj, "gunes_twh": gunes, "atik_biyokutle_twh": bio,
        "yenilenebilir_twh": hidro + rj + gunes + bio,
    }
    for k in ["termik", "hidro", "ruzgar_jeotermal", "gunes", "atik_biyokutle", "yenilenebilir"]:
        satir[f"{k}_pct"] = satir[f"{k}_twh"] / toplam * 100 if toplam else 0.0
    return satir


def _aylik_2026() -> pd.DataFrame:
    """2026 yılının her ayı için TEİAŞ aylık üretimi (TWh). Veri olan aylar listelenir."""
    aylik = data.teias_aylik()
    s = aylik[aylik["yil"] == 2026].sort_values("ay_no")
    satirlar = []
    for _, r in s.iterrows():
        satirlar.append(_satir(
            f"2026 {AYLAR[int(r['ay_no']) - 1]}",
            float(r["total_generation"]) / 1000,
            float(r["thermal"] - r["waste_and_biomass"]) / 1000,
            float(r["hydro"]) / 1000,
            float((r["wind"] + r["geothermal"])) / 1000,
            float(r["solar"]) / 1000,
            float(r["waste_and_biomass"]) / 1000,
        ))
    return pd.DataFrame(satirlar)


def _yillik() -> pd.DataFrame:
    return data.teias_uretim().copy()


def render() -> None:
    yillik = _yillik()
    aylik = _aylik_2026()
    tum = pd.concat([yillik, aylik], ignore_index=True)
    donemler = tum["donem"].tolist()
    c1, c2 = st.columns([1, 2])
    with c1:
        kaynak = st.selectbox("Kaynak", list(KAYNAKLAR.keys()), index=0, key="uretim_kaynak")
    with c2:
        donem = st.select_slider("Dönem", options=donemler, value=donemler[-1], key="uretim_donem")

    twh_kol, pct_kol = KAYNAKLAR[kaynak]
    secili = tum[tum["donem"] == donem].iloc[0]
    aylik_mi = donem.startswith("2026 ")
    ilk = yillik[yillik["donem"] == "2016"].iloc[0]
    twh = float(secili[twh_kol])
    toplam = float(secili["toplam_twh"])

    k1, k2, k3 = st.columns(3)
    k1.metric(f"{kaynak} üretimi ({donem})", f"{ui.sayi(twh)} TWh")
    if kaynak == "Toplam":
        if aylik_mi:
            k2.metric(f"Toplam üretim ({donem})", f"{ui.sayi(toplam)} TWh")
        else:
            k2.metric(f"Toplam üretim ({donem})", f"{ui.sayi(toplam)} TWh", f"{toplam - float(ilk['toplam_twh']):+.1f} TWh (2016'ya göre)".replace(".", ","), delta_color="off")
    else:
        pay = twh / toplam * 100
        if aylik_mi:
            k2.metric(f"{kaynak} payı ({donem})", f"%{ui.sayi(pay)}")
        else:
            k2.metric(f"{kaynak} payı ({donem})", f"%{ui.sayi(pay)}", f"{pay - float(ilk[pct_kol]):+.1f} puan (2016'ya göre)".replace(".", ","), delta_color="off")
    k3.metric("Dönem", donem)

    ui.bolum("01", f"{kaynak}: yıllık gelişim", "Seçilen kaynağın yıllık üretimi (sütun) ve toplam içindeki payı (çizgi).")
    if kaynak == "Toplam":
        st.plotly_chart(charts.toplam_cubuk(yillik, "toplam_twh", "Yıllık toplam brüt üretim (TWh)", "TWh"), use_container_width=True)
    else:
        st.plotly_chart(charts.toplam_cubuk(yillik, twh_kol, f"{kaynak} üretimi (TWh)", "TWh"), use_container_width=True)
        st.plotly_chart(charts.cizgi_alan(yillik, "donem", pct_kol, f"{kaynak} payı (%)", "%", "%"), use_container_width=True)

    ui.bolum("02", "2026 aylık üretim", "Her ayın kendi üretimi (TWh). Veri olan aylar gösterilir.")
    if aylik.empty:
        st.info("2026 için aylık veri yok.")
    else:
        if kaynak == "Toplam":
            st.plotly_chart(charts.toplam_cubuk(aylik, "toplam_twh", "2026 aylık toplam brüt üretim (TWh)", "TWh"), use_container_width=True)
        else:
            st.plotly_chart(charts.toplam_cubuk(aylik, twh_kol, f"2026 aylık {kaynak} üretimi (TWh)", "TWh"), use_container_width=True)
            st.plotly_chart(charts.cizgi_alan(aylik, "donem", pct_kol, f"2026 aylık {kaynak} payı (%)", "%", "%"), use_container_width=True)
    ui.teias_notu("uretim", "aylik", ek="2026 satırları TEİAŞ aylık tablosundan hesaplanmıştır; rüzgar ve jeotermal birleşiktir, atık termik içindedir.")

    ui.bolum("03", "Kaynaklara göre karşılaştırma", f"{donem} dönemi, tüm kaynaklar.")
    satirlar = [(ad, float(secili[twh])) for ad, (twh, _) in KAYNAKLAR.items() if ad not in TOPLAMLAR]
    st.plotly_chart(charts.yatay_deger_cubuk(pd.DataFrame(satirlar, columns=["kaynak", "twh"]), "kaynak", "twh", f"Kaynaklara göre üretim, {donem} (TWh)", "TWh"), use_container_width=True)

    ui.veri_tablosu(tum, "Veri tablosu (yıllık ve 2026 aylık)", "teias_uretim.csv")
