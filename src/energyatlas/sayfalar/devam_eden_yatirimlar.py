"""Devam eden yatırımlar: depolamalı RES+GES ve YEKA projeleri, 2035 yol haritası."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    yatirim = data.devam_eden_yatirim().set_index("kalem")
    depolama = data.depolama_kapasite()
    sirketler = data.depolama_sirketler()

    c1, c2, c3 = st.columns(3)
    c1.metric("Depolamalı RES+GES", f"{ui.sayi(yatirim.loc['Depolamalı RES+GES', 'gw'])} GW")
    c2.metric("YEKA (2025 ve 2026)", f"{ui.sayi(yatirim.loc['YEKA (2025 ve 2026)', 'gw'])} GW")
    c3.metric("Toplam devam eden", f"{ui.sayi(yatirim.loc['Toplam', 'gw'])} GW")

    ui.bolum("01", "Depolamalı santral kapasitesi", "Teknolojiye göre dağılım ve devreye giriş yılına göre güneş-rüzgar payı.")
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            charts.pay_halkasi(["Rüzgar (RES)", "Güneş (GES)"], [16.4, 10.5], "Teknolojiye göre dağılım: 26,9 GW"),
            use_container_width=True,
        )
    with g2:
        st.plotly_chart(
            charts.yillik_pay_cubuk(depolama, "devreye_giris", "Devreye giriş yılına göre pay (%)"),
            use_container_width=True,
        )
    ui.kaynak(
        f"Devreye giriş: 2023 {ui.sayi(depolama.loc[0, 'kapasite_gw'])} GW, 2024 {ui.sayi(depolama.loc[1, 'kapasite_gw'])} GW, "
        f"2025 {ui.sayi(depolama.loc[2, 'kapasite_gw'])} GW. Veri: sunum grafiklerinden okunmuştur."
    )

    ui.bolum("02", "Öne çıkan şirketler", "Depolamalı proje kapasitesi, MW.")
    st.plotly_chart(charts.sirket_yigin_cubuk(sirketler, "Şirketlere göre depolamalı GES ve RES kapasitesi (MW)"), use_container_width=True)
    ui.kaynak("Enerjisa projeleri Enerjisa Grubu kapsamında gösterilmektedir.")

    ui.bolum("03", "2035 yol haritası")
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

    ui.veri_tablosu(sirketler, "Veri tablosu", "depolama_sirketler.csv")
