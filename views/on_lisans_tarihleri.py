"""Depolamalı GES ve RES ön lisanslarının bitiş yılına göre dağılımı."""

import streamlit as st

from src.energyatlas import ui

from src.energyatlas import charts, data

st.title("Depolama Ön Lisansları: Bitiş Tarihleri")
st.caption("Ön lisans bitiş yılına göre proje adedi ve kapasite (MWe).")

df = data.depolama_on_lisans()
toplam = df.groupby("teknoloji")[["proje_adedi", "kapasite_mwe"]].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("GES proje adedi", f"{toplam.loc['GES', 'proje_adedi']:.0f}")
c2.metric("GES kapasitesi", f"{toplam.loc['GES', 'kapasite_mwe']:,.0f} MWe")
c3.metric("RES proje adedi", f"{toplam.loc['RES', 'proje_adedi']:.0f}")
c4.metric("RES kapasitesi", f"{toplam.loc['RES', 'kapasite_mwe']:,.0f} MWe")

st.plotly_chart(
    charts.on_lisans_yillik(df, "Bitiş yılına göre depolamalı kapasite (MWe)"),
    use_container_width=True,
)

st.subheader("Ne anlama geliyor?")
st.markdown(
    """
- EPDK, ön lisans süresi içinde proje ilerlemesini göstermeyen şirketlerin **süre uzatma taleplerini reddediyor**
  ve bu ön lisansları sonlandırıyor veya iptal ediyor.
- **Mücbir sebep** veya izin süreçlerindeki aksamalar nedeniyle EPDK **süre uzatımı** yapabiliyor.
"""
)

ui.veri_tablosu(df, "Veriyi tablo olarak göster")
