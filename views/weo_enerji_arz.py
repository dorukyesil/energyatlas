"""Dünya birincil enerji arzı (IEA WEO 2026): kaynaklara göre, senaryo seçmeli."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya enerji görünümü",
    "Birincil enerji arzı",
    "IEA WEO 2026. Dünyanın enerji arzı kaynaklara göre, EJ. Senaryo seçerek 2050'ye kadar olan yolu görün.",
)

senaryo = ui.segment(data.WEO_SENARYOLAR, "arz_senaryo")
kaynaklar = ["Coal", "Oil", "Natural gas", "Nuclear", "Hydro", "Wind", "Solar", "Modern bioenergy: solid", "Modern bioenergy: liquid", "Modern bioenergy: gas", "Traditional use of biomass"]
uzun = data.weo_coklu("Energy", "Total energy supply", kaynaklar, senaryo)
toplam = data.weo_seri("Energy", "Total energy supply", "Total", senaryo)
son = toplam.iloc[-1]
ilk = toplam.iloc[0]
yenilenebilir = data.weo_seri("Energy", "Total energy supply", "Renewables", senaryo)

c1, c2, c3 = st.columns(3)
c1.metric(f"Toplam enerji arzı ({int(son['yil'])})", f"{ui.sayi(son['deger'], 0)} EJ")
c2.metric("2010'dan bu yana değişim (gerçekleşen)", f"%{ui.sayi((toplam[toplam.yil == 2025]['deger'].iloc[0] / ilk['deger'] - 1) * 100, 0)}")
c3.metric("Yenilenebilir payı", f"%{ui.sayi(yenilenebilir.iloc[-1]['deger'] / son['deger'] * 100, 0)}")

ui.bolum("01", "Kaynaklara göre arz", "Yığılmış görünüm: fosil yakıtlar, nükleer ve yenilenebilir kaynaklar.")
st.plotly_chart(charts.yigin_cubuk(uzun.assign(yil=uzun["yil"].astype(str)), "yil", "urun", "deger", f"Birincil enerji arzı, {senaryo.lower()} (EJ)", "EJ"), use_container_width=True)
ui.kaynak("Kaynak: IEA World Energy Outlook 2026, Annex A ücretsiz veri seti. 2010-2025 gerçekleşen; sonrası seçilen senaryo.")

ui.bolum("02", "Toplam enerji arzı: senaryo karşılaştırması", "Üç senaryonun toplam enerji arzı yolu.")
karsilastirma = []
for s in data.WEO_SENARYOLAR:
    seri = data.weo_seri("Energy", "Total energy supply", "Total", s).assign(senaryo=s)
    karsilastirma.append(seri)

kar = pd.concat(karsilastirma)
st.plotly_chart(charts.cizgi_coklu(kar, "yil", "senaryo", "deger", "Toplam enerji arzı, senaryolara göre (EJ)", "EJ"), use_container_width=True)

ui.veri_tablosu(data.weo_tum().query("kapsam == 'Dünya' and kategori == 'Energy' and akis == 'Total energy supply'"), "Veri tablosu", "weo_2026.csv")
