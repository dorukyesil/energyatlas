"""EPİAŞ YEKDEM duyuruları: 2026 Ağustos-Ekim fiyatları ve yerli akşam desteği."""

import plotly.express as px
import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"YEKDEM Duyurular | {APP_TITLE}", layout="wide")
st.title("EPİAŞ YEKDEM Duyuruları")
st.caption(
    "01.07.2021 - 31.12.2030 arasında işletmeye girecek YEK belgeli tesisler için uygulanacak fiyatlar. "
    "Birim: TL kr/kWh. Kaynak: EPİAŞ, Kayıt ve Uzlaştırma duyuruları."
)

df = data.yekdem_duyuru()
donemler = sorted(df["donem"].unique())
secim = st.selectbox("Dönem", options=donemler, index=len(donemler) - 1, format_func=lambda d: f"{d[-2:]}.{d[:4]}")
alt = df[df["donem"] == secim].sort_values("fiyat_kr_kwh", ascending=False)

fiyat_max = alt.iloc[0]
fiyat_min = alt.iloc[-1]
gunes = alt[alt["kaynak"] == "Güneş Enerjisine Dayalı Üretim Tesisi"].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("En yüksek fiyat", f"{fiyat_max['fiyat_kr_kwh']:.2f} kr/kWh", fiyat_max["kaynak"], delta_color="off")
c2.metric("En düşük fiyat", f"{fiyat_min['fiyat_kr_kwh']:.2f} kr/kWh", fiyat_min["kaynak"], delta_color="off")
c3.metric("Güneş fiyatı", f"{gunes['fiyat_kr_kwh']:.2f} kr/kWh", f"yerli akşam desteği {gunes['yerli_aksam_kr_kwh']:.2f}", delta_color="off")

st.subheader(f"{secim} dönemi: kaynaklara göre fiyat ve yerli akşam desteği")
st.plotly_chart(
    px.bar(
        alt,
        x="fiyat_kr_kwh",
        y="kaynak",
        orientation="h",
        labels={"fiyat_kr_kwh": "Fiyat (TL kr/kWh)", "kaynak": ""},
        text="fiyat_kr_kwh",
    ).update_layout(template="plotly_white", yaxis=dict(autorange="reversed"), height=520, margin=dict(l=10, r=40, t=20, b=10))
    .update_traces(texttemplate="%{text:,.2f}", textposition="outside"),
    use_container_width=True,
)

st.subheader("Aylara göre değişim")
secili_kaynak = st.multiselect(
    "Kaynak seçin",
    options=sorted(df["kaynak"].unique()),
    default=["Güneş Enerjisine Dayalı Üretim Tesisi", "Karasal Rüzgar Enerjisine Dayalı Üretim Tesisi"],
)
if secili_kaynak:
    st.plotly_chart(
        charts.yekdem_cizgi(df[df["kaynak"].isin(secili_kaynak)], "Seçilen kaynakların aylık fiyatı"),
        use_container_width=True,
    )
else:
    st.info("Grafik için en az bir kaynak seçin.")

with st.expander("Tam tabloyu göster"):
    st.dataframe(df, use_container_width=True, hide_index=True)
