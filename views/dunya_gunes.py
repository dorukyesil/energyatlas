"""Dünya güneş kapasitesi: toplam kurulu güç, güneşin payı ve Türkiye'nin konumu."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya ve karşılaştırma",
    "Dünya güneş kapasitesi",
    "Dünya toplam kurulu gücü, güneş kapasitesi ve güneşin payı. Kaynak: IEA World Energy Outlook 2025.",
)

kurulu = data.dunya_kurulu_guc()
pay = data.dunya_gunes_payi().astype({"donem": str})
son = kurulu[kurulu["donem"] == 2024].iloc[0]
ilk = kurulu[kurulu["donem"] == 2010].iloc[0]
son_pay = pay[pay["donem"] == "2024"].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Dünya güneş kurulu gücü (2024)", f"{ui.sayi(son['gunes_gw'], 0)} GW")
c2.metric("Dünya toplam kurulu gücü (2024)", f"{ui.sayi(son['toplam_gw'], 0)} GW")
c3.metric("Güneş / toplam (2024)", f"%{ui.sayi(son_pay['gunes_toplam_pct'], 0)}")
c4.metric("Güneş / yenilenebilir (2024)", f"%{ui.sayi(son_pay['gunes_yenilenebilir_pct'], 0)}")

sekme_kapasite, sekme_pay = st.tabs(["Kapasite (GW)", "Güneşin payı (%)"])

with sekme_kapasite:
    ui.bolum("01", "Toplam kapasite ve güneş", "2010-2050 arası dünya toplam kurulu gücü ve güneş kapasitesi, GW.")
    st.plotly_chart(charts.dunya_kurulu_cubuk(kurulu.astype({"donem": str}), "Dünya toplam kurulu güç ve güneş (GW)"), use_container_width=True)
    ui.kaynak("2035, 2040 ve 2050 değerleri senaryo tahminleridir.")
    st.markdown(
        f"""
- 2010'da **{ui.sayi(ilk['gunes_gw'], 0)} GW** olan dünya güneş kapasitesi 2024'te **{ui.sayi(son['gunes_gw'], 0)} GW**'a ulaştı.
- 2050 için tahmin edilen güneş kapasitesi **{ui.sayi(kurulu[kurulu['donem'] == 2050].iloc[0]['gunes_gw'], 0)} GW**.
- 2024 itibarıyla Türkiye'nin güneş kurulu gücü yaklaşık **20 GW** seviyesinde ve dünya güneş kapasitesinin yaklaşık **%1**'i.
"""
    )

with sekme_pay:
    ui.bolum("01", "Güneşin kurulu güç içindeki payı", "Dünya toplam ve yenilenebilir kurulu güç içinde güneşin payı, %.")
    st.plotly_chart(charts.dunya_pay_nokta(pay, "Güneşin kurulu güç içindeki payı (%)"), use_container_width=True)
    ui.bolum("02", "Türkiye 2024")
    tr1, tr2 = st.columns(2)
    tr1.metric("Türkiye: güneş / toplam", "%17", "toplam kurulu güç ~116 GW", delta_color="off")
    tr2.metric("Türkiye: güneş / yenilenebilir", "%29", "yenilenebilir kurulu güç ~69 GW", delta_color="off")
    ui.kaynak("Türkiye yüzdeleri sunumdaki açıklama metninden alınmıştır. Dünya değerleri grafiklerden okunmuştur.")

veri = kurulu.merge(pay.astype({"donem": int}), on="donem", how="left")
ui.veri_tablosu(veri, "Veri tablosu", "dunya_gunes.csv")
