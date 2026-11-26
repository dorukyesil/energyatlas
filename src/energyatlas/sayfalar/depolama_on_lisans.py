"""Depolamalı GES ve RES ön lisansları: EPDK ön lisans listesinden bitiş yılı ve il dağılımı."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    ham = data.epdk_onlisans()
    ham = ham[ham["bitis"].notna()].copy()
    ham["bitis_yili"] = ham["bitis"].dt.year
    ham["teknoloji"] = ham["tesis_turu"].map({"Güneş": "GES", "Rüzgar": "RES"})
    df = (
        ham.groupby(["teknoloji", "bitis_yili"], as_index=False)
        .agg(proje_adedi=("tesis_adi", "count"), kapasite_mwe=("kurulu_mwe", "sum"))
    )

    toplam = df.groupby("teknoloji")[["proje_adedi", "kapasite_mwe"]].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GES proje adedi", f"{int(toplam.loc['GES', 'proje_adedi'])}")
    c2.metric("GES kapasitesi", f"{ui.sayi(toplam.loc['GES', 'kapasite_mwe'], 0)} MWe")
    c3.metric("RES proje adedi", f"{int(toplam.loc['RES', 'proje_adedi'])}")
    c4.metric("RES kapasitesi", f"{ui.sayi(toplam.loc['RES', 'kapasite_mwe'], 0)} MWe")

    ui.bolum("01", "Bitiş yılları", "Ön lisans bitiş yılına göre kurulu kapasite (MWe). Üzerine gelerek proje adedini görün.")
    st.plotly_chart(charts.on_lisans_yillik(df, "Bitiş yılına göre ön lisanslı kapasite (MWe)"), use_container_width=True)
    ui.kaynak("Kaynak: EPDK, ön lisanslı üretim tesisleri listesi. Bitiş yılı, ön lisans bitiş tarihinden alınmıştır.")

    ui.bolum("02", "Süre uzatımı ve iptal")
    st.markdown(
        """
- EPDK, ön lisans süresi içinde proje ilerlemesini göstermeyen şirketlerin **süre uzatma taleplerini reddediyor**
  ve bu ön lisansları sonlandırıyor veya iptal ediyor.
- **Mücbir sebep** veya izin süreçlerindeki aksamalar nedeniyle EPDK **süre uzatımı** yapabiliyor.
"""
    )

    ui.bolum("03", "Türkiye haritası: GES ve RES", "Her ilin ön lisanslı kurulu gücü (MWe). Koyu renk daha yoğun kapasite demektir.")
    harita_df = (
        ham.assign(ad_key=ham["il"].map(data.il_anahtari))
        .groupby(["ad_key", "tesis_turu"], as_index=False)["kurulu_mwe"].sum()
    )
    h1, h2 = st.columns(2)
    with h1:
        ges = harita_df[harita_df["tesis_turu"] == "Güneş"][["ad_key", "kurulu_mwe"]]
        st.plotly_chart(charts.tr_harita(ges, "kurulu_mwe", "GES ön lisansları (MWe)", "#D9A21B"), use_container_width=True)
    with h2:
        res = harita_df[harita_df["tesis_turu"] == "Rüzgar"][["ad_key", "kurulu_mwe"]]
        st.plotly_chart(charts.tr_harita(res, "kurulu_mwe", "RES ön lisansları (MWe)", "#13A89E"), use_container_width=True)
    ui.kaynak("Kaynak: EPDK ön lisans listesi. Harita sınırları: açık kaynak il sınırları (cihadturhan/tr-geojson).")

    ui.veri_tablosu(ham[["lisans_sahibi", "tesis_adi", "il", "ilce", "tesis_turu", "kurulu_mwe", "bitis"]], "Ön lisans listesi", "epdk_onlisans.csv")
