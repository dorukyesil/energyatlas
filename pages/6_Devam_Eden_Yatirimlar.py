"""Devam eden yatırımlar: depolamalı RES+GES ve YEKA projeleri, 2035 yol haritası."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"Devam Eden Yatırımlar | {APP_TITLE}", layout="wide")
st.title("Devam Eden Yatırımlar")
st.caption("Depolamalı rüzgar ve güneş santralleri ile YEKA projeleri, GW.")

yatirim = data.devam_eden_yatirim().set_index("kalem")
depolama = data.depolama_kapasite()
sirketler = data.depolama_sirketler()

c1, c2, c3 = st.columns(3)
c1.metric("Depolamalı RES+GES", f"{yatirim.loc['Depolamalı RES+GES', 'gw']:.1f} GW")
c2.metric("YEKA (2025 ve 2026)", f"{yatirim.loc['YEKA (2025 ve 2026)', 'gw']:.1f} GW")
c3.metric("Toplam devam eden", f"{yatirim.loc['Toplam', 'gw']:.1f} GW")

st.subheader("Depolamalı santral kapasitesi")
c4, c5 = st.columns(2)
with c4:
    st.plotly_chart(
        charts.pay_halkasi(
            ["Rüzgar (RES)", "Güneş (GES)"],
            [16.4, 10.5],
            "Teknolojiye göre dağılım: 26,9 GW",
        ),
        use_container_width=True,
    )
with c5:
    st.plotly_chart(
        charts.yillik_pay_cubuk(depolama, "devreye_giris", "Devreye giriş yılına göre pay (%)"),
        use_container_width=True,
    )
st.caption(
    f"Devreye giriş: 2023 {depolama.loc[0, 'kapasite_gw']} GW, "
    f"2024 {depolama.loc[1, 'kapasite_gw']} GW, 2025 {depolama.loc[2, 'kapasite_gw']} GW."
)

st.subheader("Öne çıkan şirketler (depolamalı proje kapasitesi)")
st.plotly_chart(
    charts.sirket_yigin_cubuk(sirketler, "Şirketlere göre depolamalı GES ve RES kapasitesi (MW)"),
    use_container_width=True,
)
st.caption("Enerjisa projeleri Enerjisa Grubu kapsamında gösterilmektedir.")

st.subheader("2035 yol haritası")
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown("**1. Yıllık YEKA**")
    st.markdown("Rüzgar ve GES için her yıl **2 GW** YEKA ihalesi.")
with k2:
    st.markdown("**2. Hibrit kapasite**")
    st.markdown("Rüzgar ve güneş ile depolamanın birlikte planlandığı hibrit kapasite.")
with k3:
    st.markdown("**3. Öztüketim**")
    st.markdown("Aynı veya farklı bağlantı noktasında öztüketim ve şebekeden bağımsız (off-grid) kullanım.")

with st.expander("Veriyi tablo olarak göster"):
    st.dataframe(sirketler, use_container_width=True, hide_index=True)
