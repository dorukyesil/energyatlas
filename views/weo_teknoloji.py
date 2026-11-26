"""Hidrojen, CCUS ve karbon yakalama (IEA WEO 2026)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya enerji görünümü",
    "Hidrojen ve karbon yakalama",
    "IEA WEO 2026. Düşük emisyonlu hidrojen, karbon yakalama ve depolama (CCUS) ve doğrudan hava yakalama.",
)

senaryo = ui.segment(data.WEO_SENARYOLAR, "teknoloji_senaryo")
sekme_h2, sekme_ccus = st.tabs(["Hidrojen", "Karbon yakalama (CCUS)"])

with sekme_h2:
    h2 = data.weo_seri("Energy", "Hydrogen production: offsite", "Hydrogen: low-emissions", senaryo)
    h2_talep = data.weo_seri("Energy", "Total final consumption", "Hydrogen", senaryo)
    c1, c2 = st.columns(2)
    if not h2.empty:
        c1.metric(f"Düşük emisyonlu hidrojen üretimi ({int(h2.iloc[-1]['yil'])})", f"{ui.sayi(h2.iloc[-1]['deger'], 2)} EJ")
    if not h2_talep.empty:
        c2.metric(f"Hidrojen son tüketimi ({int(h2_talep.iloc[-1]['yil'])})", f"{ui.sayi(h2_talep.iloc[-1]['deger'], 2)} EJ")
    ui.bolum("01", "Hidrojen", "Düşük emisyonlu hidrojen üretimi ve son tüketimi, EJ.")
    seri = pd.concat([
        h2.assign(urun="Düşük emisyonlu hidrojen üretimi"),
        h2_talep.assign(urun="Son tüketimde hidrojen"),
    ], ignore_index=True)
    if not seri.empty:
        st.plotly_chart(charts.cizgi_coklu(seri, "yil", "urun", "deger", f"Hidrojen, {senaryo.lower()} (EJ)", "EJ"), use_container_width=True)
    ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A.")

with sekme_ccus:
    yakalama = data.weo_seri("CO2 total captured", "Total energy supply", "Total", senaryo)
    depolama = data.weo_seri("CO2 total stored", "Direct air capture", "Total", senaryo)
    kaldirma = data.weo_seri("CO2 total removed", "Total energy supply", "Total", senaryo)
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Yakalanan CO2 ({int(yakalama.iloc[-1]['yil'])})", f"{ui.sayi(yakalama.iloc[-1]['deger'], 0)} Mt")
    if not depolama.empty:
        c2.metric("Doğrudan hava yakalama ile depolama", f"{ui.sayi(depolama.iloc[-1]['deger'], 1)} Mt")
    if not kaldirma.empty:
        c3.metric("Toplam kaldırılan CO2", f"{ui.sayi(kaldirma.iloc[-1]['deger'], 0)} Mt")

    ui.bolum("01", "Yakalanan ve kaldırılan CO2", "Mt CO2 cinsinden, seçilen senaryoya göre.")
    seri = pd.concat([
        yakalama.assign(urun="Yakalanan CO2"),
        kaldirma.assign(urun="Kaldırılan CO2 (toplam)"),
        depolama.assign(urun="Doğrudan hava yakalama"),
    ], ignore_index=True)
    st.plotly_chart(charts.cizgi_coklu(seri, "yil", "urun", "deger", f"Karbon yakalama ve kaldırma, {senaryo.lower()} (Mt CO2)", "Mt CO2"), use_container_width=True)

    ui.bolum("02", "CCUS kapasitesi", "Karbon yakalamalı elektrik santrallerinin kurulu gücü, GW.")
    ccus = pd.concat([
        data.weo_seri("Capacity: installed", "Electrical capacity", "Coal: with CCUS", senaryo).assign(urun="Kömür (CCUS)"),
        data.weo_seri("Capacity: installed", "Electrical capacity", "Natural gas: with CCUS", senaryo).assign(urun="Doğalgaz (CCUS)"),
        data.weo_seri("Capacity: installed", "Electrical capacity", "Bioenergy: with CCUS", senaryo).assign(urun="Biyoenerji (CCUS)"),
    ], ignore_index=True)
    st.plotly_chart(charts.cizgi_coklu(ccus, "yil", "urun", "deger", f"CCUS santral kapasitesi, {senaryo.lower()} (GW)", "GW"), use_container_width=True)
    ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A.")

ui.veri_tablosu(data.weo_tum().query("kapsam == 'Dünya' and (akis.str.contains('CCUS|captured|stored|removed|offsite|Hydrogen') or urun.str.contains('CCUS|Hydrogen'))"), "Veri tablosu", "weo_2026.csv")
