"""YEKDEM fiyatları: güneş ve elektrik depolama için taban, ortalama, tavan ve PTF karşılaştırması."""

import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"YEKDEM | {APP_TITLE}", layout="wide")
st.title("YEKDEM Fiyatlandırması")
st.caption("Yenilenebilir enerji kaynakları destekleme mekanizması (YEKDEM) fiyatları, USD/MWh.")

fiyat = data.yekdem_fiyat()
formul = data.yekdem_formul()
katki = data.yekdem_yerli_katki().set_index("teknoloji")

ptf_2025 = float(fiyat[fiyat["gosterge"].str.startswith("PTF")]["usd_mwh"].iloc[0])

c1, c2, c3 = st.columns(3)
c1.metric("Güneş YEKDEM (2025 ortalaması)", "56,6 USD/MWh", f"{56.6 - ptf_2025:+.1f} USD (PTF'e göre)", delta_color="off")
c2.metric("Elektrik depolama YEKDEM (2025 ortalaması)", "66,8 USD/MWh", f"{66.8 - ptf_2025:+.1f} USD (PTF'e göre)", delta_color="off")
c3.metric("2025 ortalama PTF", f"{ptf_2025:.1f} USD/MWh")

st.subheader("Taban, ortalama ve tavan")
g1, g2 = st.columns(2)
for kolon, teknoloji, renk in [(g1, "Güneş", "#f5b400"), (g2, "Elektrik Depolama", "#1f4e79")]:
    alt = fiyat[fiyat["teknoloji"] == teknoloji]
    with kolon:
        st.plotly_chart(
            charts.deger_cubuk(
                alt["gosterge"].tolist(),
                alt["usd_mwh"].tolist(),
                [renk, renk, renk, "#9ca3af"],
                f"{teknoloji} YEKDEM (USD/MWh)",
                "USD/MWh",
                sablon="%{text:,.1f}",
            ),
            use_container_width=True,
        )

st.subheader("YEKDEM formülü ve süresi")
f1, f2 = st.columns([2, 1])
with f1:
    st.plotly_chart(
        charts.deger_cubuk(
            formul["bilesen"].tolist(),
            formul["agirlik_pct"].tolist(),
            ["#1f4e79", "#2a7f62", "#f5b400", "#c8102e"],
            "Formül bileşenlerinin ağırlığı (%)",
            "%",
            sablon="%{text:.0f}%",
        ),
        use_container_width=True,
    )
with f2:
    st.markdown("**Süre:** 10 yıl (2021-2030)")
    st.markdown("**Güncelleme:** Her ay güncellenir.")

st.subheader("Yerli katkı")
y1, y2 = st.columns(2)
y1.metric("Güneş yerli katkı", f"{katki.loc['Güneş', 'yerli_katki_usd_mwh']:.2f} USD/MWh", f"{katki.loc['Güneş', 'sure_yil']} yıl", delta_color="off")
y2.metric("Elektrik depolama yerli katkı", f"{katki.loc['Elektrik Depolama', 'yerli_katki_usd_mwh']:.2f} USD/MWh", f"{katki.loc['Elektrik Depolama', 'sure_yil']} yıl", delta_color="off")
st.caption(
    "Yerli katkı fiyatı, %100 yerli aksam kullanılması halinde alınabilecek azami tutarları gösterir."
)

with st.expander("Veriyi tablo olarak göster"):
    st.dataframe(fiyat, use_container_width=True, hide_index=True)
