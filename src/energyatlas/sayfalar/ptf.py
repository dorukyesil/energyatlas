"""Piyasa takas fiyatı (PTF): yıllık değerler ve son dönem değişimi."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.ptf()
    seri = df.set_index("donem")
    yillik = data.tam_yillar(df)
    on_yil = seri.loc["2016", "ptf_usd_mwh"]
    son_yil = seri.loc["2025", "ptf_usd_mwh"]
    ortalama_artis = ((son_yil / on_yil) ** (1 / 9) - 1) * 100
    degisim = (seri.loc["2026 9A", "ptf_usd_mwh"] / seri.loc["2025 9A", "ptf_usd_mwh"] - 1) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("2025 PTF", f"{ui.sayi(son_yil, 0)} USD/MWh")
    c2.metric("2016-2025 yıllık ortalama artış (USD)", f"%{ui.sayi(ortalama_artis)}")
    c3.metric("2026 9A (2025 9A'ya göre)", f"{ui.sayi(seri.loc['2026 9A', 'ptf_usd_mwh'], 0)} USD/MWh", f"{degisim:+.1f}%".replace(".", ","), delta_color="inverse")

    ui.bolum("01", "Fiyat gelişimi", "Görünümü seçin: yıllık çizgi, 9A dönemleri dahil sütun veya yıllık değişim.")
    gorunum = ui.segment(["Çizgi (yıllık)", "Sütun (9A dahil)", "Yıllık değişim (%)"], "ptf_gorunum")
    if gorunum == "Çizgi (yıllık)":
        st.plotly_chart(
            charts.cizgi_alan(yillik, "donem", "ptf_usd_mwh", "Yıllık PTF (USD/MWh)", "USD/MWh", "USD/MWh", hareketli_ortalama=3),
            use_container_width=True,
        )
    elif gorunum == "Sütun (9A dahil)":
        st.plotly_chart(charts.ptf_cubuk(df, "Yıllık PTF (USD/MWh)"), use_container_width=True)
    else:
        st.plotly_chart(
            charts.yillik_degisim_cubuk(data.yillik_degisim(df, "ptf_usd_mwh"), "donem", "degisim_pct", "PTF: yıllık değişim"),
            use_container_width=True,
        )
    ui.kaynak("Veri: sunum grafiklerinden okunmuştur (kaynak: EPİAŞ). Kesikli çizgi 3 yıllık hareketli ortalamadır. 9A: ocak-eylül.")

    ui.bolum("02", "Öne çıkan gelişme")
    st.markdown(
        """
    - **2022** en yüksek seviyeye ulaştı: **147 USD/MWh**. Sonraki yıllarda fiyat geriledi.
    - **2026 9A**'da PTF, 2025 9A'ya göre yaklaşık **%35 düştü**. Bunun temel nedeni, aşırı yağışlar sonucu hidroelektrik üretiminin yükselmesi.
    """
    )

    ui.veri_tablosu(df, "Veri tablosu", "ptf.csv")
