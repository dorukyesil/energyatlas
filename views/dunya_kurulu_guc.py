"""Dünya toplam kurulu gücü ve güneş kapasitesinin gelişimi (GW)."""

import streamlit as st

from src.energyatlas import ui

from src.energyatlas import charts, data

st.title("Dünya Güneş Paneli Sektörü: Kurulu Güç")
st.caption("Dünya toplam kurulu gücü ve güneş enerjisi kapasitesi, GW. Kaynak: IEA World Energy Outlook 2025.")

df = data.dunya_kurulu_guc()
son = df[df["donem"] == 2024].iloc[0]
ilk = df[df["donem"] == 2010].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Dünya güneş kurulu gücü (2024)", f"{son['gunes_gw']:,.0f} GW")
c2.metric("Dünya toplam kurulu gücü (2024)", f"{son['toplam_gw']:,.0f} GW")
c3.metric("Güneşin toplam kurulu güç içindeki payı (2024)", f"%{son['gunes_gw'] / son['toplam_gw'] * 100:.0f}")

st.plotly_chart(
    charts.dunya_kurulu_cubuk(df.astype({"donem": str}), "Dünya toplam kurulu güç ve güneş (GW)"),
    use_container_width=True,
)

st.subheader("Öne çıkanlar")
st.markdown(
    f"""
- 2010'da **{ilk['gunes_gw']:.0f} GW** olan dünya güneş kapasitesi 2024'te **{son['gunes_gw']:,.0f} GW**'a ulaştı.
- 2050 için tahmin edilen güneş kapasitesi **{df[df['donem'] == 2050].iloc[0]['gunes_gw']:,.0f} GW**.
- 2024 itibarıyla Türkiye'nin güneş kurulu gücü yaklaşık **20 GW** seviyesinde ve dünya güneş kapasitesinin yaklaşık **%1**'i.
"""
)

ui.veri_tablosu(df, "Veriyi tablo olarak göster")
