"""Küresel enerji yatırımlarında yenilenebilir kaynakların gelişimi ve bölgesel güneş yatırımları."""

import streamlit as st

from src.energyatlas import ui

from src.energyatlas import charts, data

st.title("Küresel Enerji Yatırımları")
st.caption("Milyar USD. Toplam enerji, temiz enerji ve güneş yatırımlarının 2015-2025 gelişimi.")

kuresel = data.kuresel_yatirim()
bolge = data.gunes_yatirim_bolge()
ilk = kuresel[kuresel["yil"] == 2015].iloc[0]
son = kuresel[kuresel["yil"] == 2025].iloc[0]


def yillik_artis(baslangic: float, bitis: float, yil: int = 10) -> float:
    return ((bitis / baslangic) ** (1 / yil) - 1) * 100


c1, c2, c3 = st.columns(3)
c1.metric("Güneş yatırımları (2025)", f"{son['gunes_mlrd_usd']:,.0f} milyar USD",
          f"yıllık ortalama %{yillik_artis(ilk['gunes_mlrd_usd'], son['gunes_mlrd_usd']):.1f} (2015-2025)")
c2.metric("Temiz enerji yatırımları (2025)", f"{son['temiz_enerji_mlrd_usd']:,.0f} milyar USD",
          f"yıllık ortalama %{yillik_artis(ilk['temiz_enerji_mlrd_usd'], son['temiz_enerji_mlrd_usd']):.1f}")
c3.metric("Toplam enerji yatırımları (2025)", f"{son['toplam_mlrd_usd']:,.0f} milyar USD",
          f"yıllık ortalama %{yillik_artis(ilk['toplam_mlrd_usd'], son['toplam_mlrd_usd']):.1f}")

st.plotly_chart(
    charts.kuresel_yatirim_cubuk(kuresel, "Küresel enerji yatırımları (milyar USD)"),
    use_container_width=True,
)

st.subheader("Bölgelere göre küresel güneş yatırımları")
st.plotly_chart(
    charts.bolge_yigin_cubuk(bolge, "Bölgelere göre güneş yatırımları (milyar USD)"),
    use_container_width=True,
)

pay_2025 = son["gunes_mlrd_usd"] / son["temiz_enerji_mlrd_usd"] * 100
st.info(
    f"2025'te güneş yatırımları, temiz enerji yatırımlarının yaklaşık **%{pay_2025:.0f}**'ini oluşturdu. "
    "Asya ve Pasifik, 2025'te güneş yatırımlarının en büyük bölümünü (265 milyar USD) aldı. "
    "Bölge değerleri görselde etiketli olan üç bölge için verilmiştir; geri kalan bölgeler toplamdan hesaplanmıştır."
)

ui.veri_tablosu(kuresel, "Küresel yatırım verisi", "kuresel_yatirim.csv")
ui.veri_tablosu(bolge, "Bölgesel güneş yatırım verisi", "bolgesel_gunes_yatirim.csv")
