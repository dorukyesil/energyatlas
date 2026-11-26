"""Piyasa takas fiyatı (PTF): yıllık değerler ve son dönem değişimi."""

import streamlit as st

from src.energyatlas import ui

from src.energyatlas import charts, data

st.title("Fiyatlandırma: PTF")
st.caption("Piyasa takas fiyatı (PTF), USD/MWh. Serbest piyasa elektrik fiyatlarının ABD doları bazındaki seyri.")

df = data.ptf().set_index("donem")
on_yil = df.loc["2016", "ptf_usd_mwh"]
son_yil = df.loc["2025", "ptf_usd_mwh"]
ortalama_artis = ((son_yil / on_yil) ** (1 / 9) - 1) * 100
degisim = (df.loc["2026 9A", "ptf_usd_mwh"] / df.loc["2025 9A", "ptf_usd_mwh"] - 1) * 100

c1, c2, c3 = st.columns(3)
c1.metric("2025 PTF", f"{son_yil:.0f} USD/MWh")
c2.metric("2016-2025 yıllık ortalama artış (USD)", f"%{ortalama_artis:.1f}")
c3.metric("2026 9A (2025 9A'ya göre)", f"{df.loc['2026 9A', 'ptf_usd_mwh']:.0f} USD/MWh", f"%{degisim:.1f}", delta_color="inverse")

st.plotly_chart(
    charts.ptf_cubuk(data.ptf(), "Yıllık PTF (USD/MWh)"),
    use_container_width=True,
)

st.subheader("Öne çıkan gelişme")
st.markdown(
    """
- **2022** en yüksek seviyeye ulaştı: **147 USD/MWh**. Sonraki yıllarda fiyat geriledi.
- **2026 9A**'da PTF, 2025 9A'ya göre yaklaşık **%35 düştü**. Bunun temel nedeni, aşırı yağışlar sonucu
  hidroelektrik üretiminin yükselmesi.
"""
)

ui.veri_tablosu(df.reset_index(), "Veriyi tablo olarak göster")
