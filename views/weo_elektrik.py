"""Dünya elektrik üretimi ve kurulu kapasitesi (IEA WEO 2026): kaynaklara göre, senaryo seçmeli."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya enerji görünümü",
    "Elektrik üretimi ve kapasite",
    "IEA WEO 2026. Dünya elektrik üretimi (TWh) ve kurulu kapasitesi (GW), kaynaklara göre.",
)

senaryo = ui.segment(data.WEO_SENARYOLAR, "elektrik_senaryo")
uretim_kaynaklari = ["Coal: unabated", "Natural gas: unabated", "Oil", "Nuclear", "Hydro", "Wind", "Solar PV", "Modern bioenergy and renewable waste", "Geothermal"]
uretim = data.weo_coklu("Energy", "Electricity generation", uretim_kaynaklari, senaryo)
toplam_uretim = data.weo_seri("Energy", "Electricity generation", "Total", senaryo)
kapasite_toplam = data.weo_seri("Capacity: installed", "Electrical capacity", "Total", senaryo)
kapasite_gunes = data.weo_seri("Capacity: installed", "Electrical capacity", "Solar PV", senaryo)
kapasite_ruzgar = data.weo_seri("Capacity: installed", "Electrical capacity", "Wind", senaryo)
kapasite_batarya = data.weo_seri("Capacity: installed", "Electrical capacity", "Battery storage", senaryo)

son = toplam_uretim.iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Elektrik üretimi ({int(son['yil'])})", f"{ui.sayi(son['deger'], 0)} TWh")
c2.metric(f"Toplam kapasite ({int(kapasite_toplam.iloc[-1]['yil'])})", f"{ui.sayi(kapasite_toplam.iloc[-1]['deger'], 0)} GW")
c3.metric("Güneş PV kapasitesi", f"{ui.sayi(kapasite_gunes.iloc[-1]['deger'], 0)} GW")
c4.metric("Batarya depolama", f"{ui.sayi(kapasite_batarya.iloc[-1]['deger'], 0)} GW")

ui.bolum("01", "Üretim: kaynaklara göre", "Elektrik üretimi, TWh. Yığılmış görünüm.")
st.plotly_chart(charts.yigin_cubuk(uretim.assign(yil=uretim["yil"].astype(str)), "yil", "urun", "deger", f"Dünya elektrik üretimi, {senaryo.lower()} (TWh)", "TWh"), use_container_width=True)
ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A. Yenilenebilir tanımı: güneş, rüzgar, hidro, biyoenerji, jeotermal ve atık.")

ui.bolum("02", "Kapasite", "Seçilen teknolojilerin kurulu kapasitesi, GW.")
kap = pd.concat([
    kapasite_gunes.assign(urun="Güneş PV"),
    kapasite_ruzgar.assign(urun="Rüzgar"),
    kapasite_batarya.assign(urun="Batarya depolama"),
])
st.plotly_chart(charts.cizgi_coklu(kap, "yil", "urun", "deger", f"Kurulu kapasite, {senaryo.lower()} (GW)", "GW"), use_container_width=True)

ui.veri_tablosu(data.weo_tum().query("kapsam == 'Dünya' and kategori in ['Energy','Capacity: installed'] and akis in ['Electricity generation','Electrical capacity']"), "Veri tablosu", "weo_2026.csv")
