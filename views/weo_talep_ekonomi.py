"""Dünya son enerji tüketimi ve ekonomi göstergeleri (IEA WEO 2026)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya enerji görünümü",
    "Enerji talebi ve ekonomi",
    "IEA WEO 2026. Son enerji tüketimi taşıyıcılara ve sektörlere göre; ekonomi, nüfus ve enerji yoğunluğu.",
)

senaryo = ui.segment(data.WEO_SENARYOLAR, "talep_senaryo")
sekme_talep, sekme_ekonomi = st.tabs(["Son enerji tüketimi", "Ekonomi ve yoğunluk"])

with sekme_talep:
    tasiyicilar = ["Electricity", "Natural gas", "Oil", "Coal", "Hydrogen", "Biomethane", "Modern bioenergy: liquid", "Modern bioenergy: solid"]
    uzun = data.weo_coklu("Energy", "Total final consumption", tasiyicilar, senaryo)
    toplam = data.weo_seri("Energy", "Total final consumption", "Total", senaryo)
    son = toplam.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Son enerji tüketimi ({int(son['yil'])})", f"{ui.sayi(son['deger'], 0)} EJ")
    elektrik = data.weo_seri("Energy", "Total final consumption", "Electricity", senaryo)
    c2.metric("Elektriğin payı", f"%{ui.sayi(elektrik.iloc[-1]['deger'] / son['deger'] * 100, 0)}")
    hidrojen = data.weo_seri("Energy", "Total final consumption", "Hydrogen", senaryo)
    c3.metric("Hidrojen (son tüketim)", f"{ui.sayi(hidrojen.iloc[-1]['deger'], 2)} EJ")

    ui.bolum("01", "Taşıyıcılara göre", "Son tüketimde elektrik, doğalgaz, petrol ve diğer taşıyıcılar, EJ.")
    st.plotly_chart(charts.yigin_cubuk(uzun.assign(yil=uzun["yil"].astype(str)), "yil", "urun", "deger", f"Son enerji tüketimi, {senaryo.lower()} (EJ)", "EJ"), use_container_width=True)

    ui.bolum("02", "Sektörlere göre", "Sanayi, ulaştırma ve binalar. Bu sektörlerin son tüketimi EJ cinsinden.")
    sektorler = {"Sanayi": "Industry", "Ulaştırma": "Transport", "Binalar": "Buildings"}
    parcalar = []
    for ad, akis in sektorler.items():
        s = data.weo_seri("Energy", akis, "Total", senaryo)
        if not s.empty:
            parcalar.append(s.assign(urun=ad))
    if parcalar:
        sek = pd.concat(parcalar, ignore_index=True)
        st.plotly_chart(charts.cizgi_coklu(sek, "yil", "urun", "deger", f"Sektör bazında enerji tüketimi, {senaryo.lower()} (EJ)", "EJ"), use_container_width=True)
    ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A ücretsiz veri seti.")

with sekme_ekonomi:
    gsyh = data.weo_seri("Economic indicators", "Gross domestic product", "Total", senaryo)
    nufus = data.weo_seri("Population indicators", "Population", "Total", senaryo)
    kisi_gsyh = data.weo_seri("Economic indicators", "GDP per capita", "Total", senaryo)
    yogunluk = data.weo_seri("Energy intensity", "TES per GDP", "Total", senaryo)
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Dünya GSYH ({int(gsyh.iloc[-1]['yil'])})", f"{ui.sayi(gsyh.iloc[-1]['deger'], 0)} mlrd USD")
    c2.metric(f"Nüfus ({int(nufus.iloc[-1]['yil'])})", f"{ui.sayi(nufus.iloc[-1]['deger'], 0)} milyon")
    c3.metric("Kişi başına GSYH", f"{ui.sayi(kisi_gsyh.iloc[-1]['deger'], 0)} USD")

    ui.bolum("01", "Enerji yoğunluğu", "GSYH birimi başına birincil enerji arzı (GJ / bin USD, 2025 PPP). Düşüş, verimlilik artışı demektir.")
    st.plotly_chart(charts.cizgi_alan(yogunluk, "yil", "deger", "Birincil enerji / GSYH", "GJ / bin USD", "GJ/bin USD"), use_container_width=True)

    ui.bolum("02", "GSYH ve nüfus", "Dünya GSYH (milyar USD, 2025 PPP) ve nüfus (milyon kişi).")
    st.plotly_chart(charts.cizgi_alan(gsyh, "yil", "deger", "Dünya GSYH (milyar USD, 2025 PPP)", "milyar USD", "milyar USD"), use_container_width=True)
    ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A. Ekonomi göstergeleri 2025 PPP fiyatlarıdır.")

ui.veri_tablosu(data.weo_tum().query("kapsam == 'Dünya' and kategori in ['Energy','Economic indicators','Population indicators','Energy intensity']"), "Veri tablosu", "weo_2026.csv")
