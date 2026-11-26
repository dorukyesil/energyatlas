"""Dünya CO2 emisyonları (IEA WEO 2026): sektörlere göre, senaryo seçmeli."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    senaryo = ui.segment(data.WEO_SENARYOLAR, "emisyon_senaryo")
    toplam = data.weo_seri("CO2 total", "Total energy supply", "Total", senaryo)
    sektorler = {"Elektrik sektörü": "Power sector inputs", "Sanayi": "Industry", "Ulaştırma": "Transport", "Binalar": "Buildings"}
    parcalar = []
    for ad, akis in sektorler.items():
        s = data.weo_seri("CO2 total", akis, "Total", senaryo)
        if not s.empty:
            parcalar.append(s.assign(urun=ad))
    sektor_df = pd.concat(parcalar, ignore_index=True)

    son = toplam.iloc[-1]
    ilk = toplam[toplam.yil == 2010].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Toplam enerji kaynaklı CO2 ({int(son['yil'])})", f"{ui.sayi(son['deger'], 0)} Mt")
    c2.metric(f"2010'a göre değişim ({int(son['yil'])})", f"%{ui.sayi((son['deger'] / ilk['deger'] - 1) * 100, 0)}")
    yakalanan = data.weo_seri("CO2 total captured", "Total energy supply", "Total", senaryo)
    c3.metric(f"Yakalanan CO2 ({int(yakalanan.iloc[-1]['yil'])})", f"{ui.sayi(yakalanan.iloc[-1]['deger'], 0)} Mt")

    ui.bolum("01", "Toplam emisyon", "Enerji kaynaklı toplam CO2 emisyonu, Mt CO2.")
    st.plotly_chart(charts.toplam_cubuk(toplam.assign(donem=toplam["yil"].astype(str)), "deger", f"Toplam CO2 emisyonu, {senaryo.lower()} (Mt CO2)", "Mt CO2"), use_container_width=True)

    ui.bolum("02", "Sektörlere göre", "Elektrik, sanayi, ulaştırma ve binalar. Son kullanım sektörlerinin kendi emisyonu gösterilir.")
    st.plotly_chart(charts.yigin_cubuk(sektor_df.assign(yil=sektor_df["yil"].astype(str)), "yil", "urun", "deger", "Sektörlere göre CO2 emisyonu (Mt CO2)", "Mt CO2"), use_container_width=True)

    ui.bolum("03", "Elektrik üretiminin karbon yoğunluğu", "Elektrik üretiminin birim başına CO2 emisyonu (gCO2/kWh).")
    yogunluk = data.weo_seri("CO2 total intensity", "Electricity generation", "Electricity", senaryo)
    st.plotly_chart(charts.cizgi_alan(yogunluk, "yil", "deger", "Elektrik üretiminin CO2 yoğunluğu (gCO2/kWh)", "gCO2/kWh", "gCO2/kWh"), use_container_width=True)
    ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A ücretsiz veri seti.")
    ui.veri_tablosu(data.weo_tum().query("kapsam == 'Dünya' and kategori.str.startswith('CO2')"), "Veri tablosu", "weo_2026.csv")
