"""Depolamalı GES ve RES ön lisansları: EPDK ön lisans listesinden bitiş yılı dağılımı."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Depolama ve yatırımlar",
    "Depolama ön lisansları",
    "EPDK ön lisanslı tesislerin bitiş yılına göre dağılımı. Tek tek tesisler için EPDK santral listesine bakın.",
)

ham = data.epdk_onlisans()
ham = ham[ham["bitis"].notna()].copy()
ham["bitis_yili"] = ham["bitis"].dt.year
ham["teknoloji"] = ham["tesis_turu"].map({"Güneş": "GES", "Rüzgar": "RES"})
df = (
    ham.groupby(["teknoloji", "bitis_yili"], as_index=False)
    .agg(proje_adedi=("tesis_adi", "count"), kapasite_mwe=("kurulu_mwe", "sum"))
    .rename(columns={"bitis_yili": "bitis_yili"})
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

ui.bolum("03", "Bölgesel yoğunluk", "Ön lisans başvurularının il bazında yoğunluğu.")
il_toplam = (
    ham.assign(teknoloji=ham["teknoloji"])
    .groupby(["il", "teknoloji"], as_index=False)["kurulu_mwe"].sum()
)
ozet = il_toplam.pivot_table(index="il", columns="teknoloji", values="kurulu_mwe", fill_value=0)
ozet["Toplam"] = ozet.sum(axis=1)
ozet = ozet.sort_values("Toplam", ascending=False).head(15)
st.plotly_chart(
    charts.isi_haritasi(ozet[["GES", "RES"]].T, "İllere göre ön lisanslı kapasite (MWe), en büyük 15 il", "turkuaz", "%{z:,.0f}", "MWe"),
    use_container_width=True,
)

ui.veri_tablosu(ham[["lisans_sahibi", "tesis_adi", "il", "ilce", "tesis_turu", "kurulu_mwe", "bitis"]], "Ön lisans listesi", "epdk_onlisans.csv")
