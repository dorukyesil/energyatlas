"""Kişi başına elektrik tüketimi karşılaştırması."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.kisi_basina().set_index("kaynak")
    turkiye = df.loc["Türkiye", "kwh_kisi"]
    oecd = df.loc["OECD", "kwh_kisi"]
    dunya = df.loc["Dünya", "kwh_kisi"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Türkiye", f"{ui.sayi(turkiye, 0)} kWh")
    c2.metric("Dünya ortalaması", f"{ui.sayi(dunya, 0)} kWh", f"Türkiye {turkiye - dunya:+,.0f} kWh".replace(",", "."))
    c3.metric("OECD ortalaması", f"{ui.sayi(oecd, 0)} kWh", f"Türkiye {turkiye - oecd:+,.0f} kWh".replace(",", "."))

    ui.bolum("01", "Karşılaştırma")
    st.plotly_chart(charts.kisi_basina_cubuk(df.reset_index(), "Kişi başına yıllık elektrik tüketimi"), use_container_width=True)
    ui.kaynak("Veri: sunum grafiklerinden okunmuştur.")

    st.info(
        f"Türkiye'nin kişi başına tüketimi dünya ortalamasının yaklaşık {ui.sayi(turkiye / dunya, 2)} katı, "
        f"OECD ortalamasının ise yaklaşık %{ui.sayi(turkiye / oecd * 100, 0)}'i düzeyinde."
    )
