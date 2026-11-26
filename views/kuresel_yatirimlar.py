"""Küresel enerji yatırımlarında yenilenebilir kaynakların gelişimi ve bölgesel güneş yatırımları."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Dünya ve karşılaştırma",
    "Küresel enerji yatırımları",
    "Milyar USD. Toplam enerji, temiz enerji ve güneş yatırımlarının 2015-2025 gelişimi.",
)

kuresel = data.kuresel_yatirim()
bolge = data.gunes_yatirim_bolge()
ilk = kuresel[kuresel["yil"] == 2015].iloc[0]
son = kuresel[kuresel["yil"] == 2025].iloc[0]


def yillik_artis(baslangic: float, bitis: float, yil: int = 10) -> float:
    return ((bitis / baslangic) ** (1 / yil) - 1) * 100


c1, c2, c3 = st.columns(3)
c1.metric("Güneş yatırımları (2025)", f"{ui.sayi(son['gunes_mlrd_usd'], 0)} milyar USD", f"yıllık ortalama %{ui.sayi(yillik_artis(ilk['gunes_mlrd_usd'], son['gunes_mlrd_usd']))} (2015-2025)", delta_color="off")
c2.metric("Temiz enerji yatırımları (2025)", f"{ui.sayi(son['temiz_enerji_mlrd_usd'], 0)} milyar USD", f"yıllık ortalama %{ui.sayi(yillik_artis(ilk['temiz_enerji_mlrd_usd'], son['temiz_enerji_mlrd_usd']))}", delta_color="off")
c3.metric("Toplam enerji yatırımları (2025)", f"{ui.sayi(son['toplam_mlrd_usd'], 0)} milyar USD", f"yıllık ortalama %{ui.sayi(yillik_artis(ilk['toplam_mlrd_usd'], son['toplam_mlrd_usd']))}", delta_color="off")

ui.bolum("01", "Yatırımların gelişimi", "Toplam enerji, temiz enerji ve güneş yatırımları, milyar USD.")
st.plotly_chart(charts.kuresel_yatirim_cubuk(kuresel, "Küresel enerji yatırımları (milyar USD)"), use_container_width=True)

ui.bolum("02", "Bölgelere göre güneş yatırımları", "Asya ve Pasifik, Kuzey Amerika ve Avrupa. Diğer bölgeler toplamdan hesaplanmıştır.")
st.plotly_chart(charts.bolge_yigin_cubuk(bolge, "Bölgelere göre güneş yatırımları (milyar USD)"), use_container_width=True)

pay_2025 = son["gunes_mlrd_usd"] / son["temiz_enerji_mlrd_usd"] * 100
st.info(
    f"2025'te güneş yatırımları, temiz enerji yatırımlarının yaklaşık **%{ui.sayi(pay_2025, 0)}**'ini oluşturdu. "
    "Asya ve Pasifik, 2025'te güneş yatırımlarının en büyük bölümünü (265 milyar USD) aldı."
)
ui.kaynak("Veri: sunum grafiklerinden okunmuştur. Bölge değerleri yalnızca görselde etiketli bölgeler için verilmiştir.")

ui.veri_tablosu(kuresel, "Küresel yatırım verisi", "kuresel_yatirim.csv")
ui.veri_tablosu(bolge, "Bölgesel güneş yatırım verisi", "bolgesel_gunes_yatirim.csv")
