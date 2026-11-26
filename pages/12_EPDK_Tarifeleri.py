"""EPDK elektrik tarifeleri: tek zamanlı ve çok zamanlı enerji bedelleri (4 Nisan 2026 itibarıyla)."""

import plotly.express as px
import streamlit as st

from config import APP_TITLE
from src.energyatlas import charts, data

st.set_page_config(page_title=f"EPDK Tarifeleri | {APP_TITLE}", layout="wide")
st.title("EPDK Elektrik Tarifeleri")
st.caption(
    "Enerji bedelleri, kuruş/kWh (kr/kWh). 4 Nisan 2026 tarihinden itibaren geçerli, vergiler hariç. "
    "100 kr = 1 TL. Kaynak: EPDK, elektrik faturalarına esas tarife tabloları."
)

df = data.tarife()
df["grup_etiket"] = df["baglanti"] + " | " + df["grup"]


def satir(baglanti: str, grup: str) -> float:
    return float(df[(df["baglanti"] == baglanti) & (df["grup"] == grup)]["tek_zamanli"].iloc[0])


c1, c2, c3 = st.columns(3)
c1.metric("Mesken (AG, 8 kWh/gün üstü)", f"{satir('AG Tek Terim', 'Mesken (8 kWh/gün üstü)') / 100:.2f} TL/kWh")
c2.metric("Sanayi (OG Tek Terim)", f"{satir('OG Tek Terim', 'Sanayi') / 100:.2f} TL/kWh")
c3.metric("Aydınlatma (AG Tek Terim)", f"{satir('AG Tek Terim', 'Aydınlatma') / 100:.2f} TL/kWh")

st.subheader("Tek zamanlı enerji bedeli")
st.caption("Grup seçerek karşılaştırın. Varsayılan olarak tüm gruplar gösterilir.")
secilen = st.multiselect(
    "Kullanıcı grubu",
    options=df["grup_etiket"].tolist(),
    default=df["grup_etiket"].tolist(),
)
alt = df[df["grup_etiket"].isin(secilen)]
if alt.empty:
    st.info("Gösterilecek grup seçilmedi.")
else:
    fig = px.bar(
        alt.sort_values("tek_zamanli", ascending=False),
        x="tek_zamanli",
        y="grup_etiket",
        orientation="h",
        color="baglanti",
        labels={"tek_zamanli": "kr/kWh", "grup_etiket": "", "baglanti": "Bağlantı"},
        color_discrete_map={
            "İletim Sistemi": "#6b7280",
            "OG Çift Terim": "#1f4e79",
            "OG Tek Terim": "#2a7f62",
            "AG Tek Terim": "#f5b400",
            "Genel Aydınlatma": "#c8102e",
        },
    )
    fig.update_layout(template="plotly_white", yaxis=dict(autorange="reversed"), height=max(400, 30 * len(alt)))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Çok zamanlı tarifeler (gündüz, puant, gece)")
cok = df[df["gunduz"].notna()]
grup_secim = st.selectbox("Grup", options=cok["grup_etiket"].tolist())
secili = cok[cok["grup_etiket"] == grup_secim]
st.plotly_chart(
    charts.tarife_karsilastirma(
        secili.assign(grup=["Gündüz / Puant / Gece"]),
        f"{grup_secim}: çok zamanlı enerji bedelleri",
    ),
    use_container_width=True,
)
st.caption(
    "Gündüz, puant ve gece dilimleri. Puant dilimi en pahalı, gece dilimi en ucuz dilimdir."
)

with st.expander("Tam tabloyu göster"):
    st.dataframe(df.drop(columns=["grup_etiket"]), use_container_width=True, hide_index=True)
st.caption("AG: Alçak Gerilim. OG: Orta Gerilim. Çift terim ve tek terim bağlantı türleri EPDK tablosundaki gibi listelenmiştir.")
