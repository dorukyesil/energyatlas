"""İşletmedeki depolama lisanslı projeler: şirketler ve tesis dağılımı."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"İşletmedeki Depolama | {APP_TITLE}", layout="wide")
st.title("İşletmedeki Depolama Lisanslı Projeler")
st.caption("İşletmeye alınmış depolama tesisleri. Sıralama işletmedeki kapasiteye göre yapılmıştır.")

df = data.isletmedeki_depolama().sort_values("kapasite_mwh", ascending=False).reset_index(drop=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam depolama kapasitesi", f"{df['kapasite_mwh'].sum():,.1f} MWh")
c2.metric("Toplam depolama gücü", f"{df['guc_mwe'].sum():,.1f} MWe")
c3.metric("Şirket sayısı", len(df))
c4.metric("Tesis dağılımı", f"Güneş {int((df['tesis_turu'] == 'Güneş').sum())} | Rüzgar {int((df['tesis_turu'] == 'Rüzgar').sum())}")

st.plotly_chart(
    charts.isletmedeki_cubuk(df, "Şirketlere göre işletmedeki depolama kapasitesi (MWh)"),
    use_container_width=True,
)

st.subheader("Teknolojiye göre özet")
ozet = df.groupby("tesis_turu")[["kapasite_mwh", "guc_mwe"]].sum()
o1, o2 = st.columns(2)
o1.metric(
    "Güneş (GES)",
    f"{ozet.loc['Güneş', 'kapasite_mwh']:,.1f} MWh",
    f"{ozet.loc['Güneş', 'guc_mwe']:,.1f} MWe toplam güç",
    delta_color="off",
)
o2.metric(
    "Rüzgar (RES)",
    f"{ozet.loc['Rüzgar', 'kapasite_mwh']:,.1f} MWh",
    f"{ozet.loc['Rüzgar', 'guc_mwe']:,.1f} MWe toplam güç",
    delta_color="off",
)

st.caption(
    "Not: Erguvan, Soma ve Meltem Enerji, Polat Holding'in kontrolündedir. İğdır Hoşhaber Elektrik, "
    "Kazancı Holding (Kazancı ailesi) kontrolündedir. Oze Enerji, Gündüzkanat ailesi/grubu kontrolündedir. "
    "Artuklu GES Elektrik, Egesa mülkiyetindedir."
)

with st.expander("Tabloyu göster"):
    st.dataframe(df, use_container_width=True, hide_index=True)
