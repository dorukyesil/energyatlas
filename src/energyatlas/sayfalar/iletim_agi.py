"""Türkiye elektrik iletim ağı: hat uzunlukları ve trafo kapasitesi (TEİAŞ)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.teias_iletim()
    ilk, son = df.iloc[0], df.iloc[-1]

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Toplam iletim hattı ({int(son['yil'])})", f"{ui.sayi(son['total_line_km'], 0)} km",
              f"{son['total_line_km'] - ilk['total_line_km']:+,.0f} km ({int(ilk['yil'])}'dan beri)".replace(",", "."), delta_color="off")
    c2.metric(f"Trafo sayısı ({int(son['yil'])})", f"{ui.sayi(son['total_transformers'], 0)}")
    c3.metric(f"Toplam trafo kapasitesi ({int(son['yil'])})", f"{ui.sayi(son['total_capacity_mva'] / 1000, 0)} GVA")

    ui.bolum("01", "İletim hatları", "Gerilim seviyesine göre hat uzunluğu, km.")
    uzun = pd.concat([
        df[["donem", "line_380kv_km"]].rename(columns={"line_380kv_km": "deger"}).assign(seviye="380 kV"),
        df[["donem", "line_220kv_km"]].rename(columns={"line_220kv_km": "deger"}).assign(seviye="220 kV"),
        df[["donem", "line_154kv_km"]].rename(columns={"line_154kv_km": "deger"}).assign(seviye="154 kV"),
        df[["donem", "line_66kv_km"]].rename(columns={"line_66kv_km": "deger"}).assign(seviye="66 kV"),
    ])
    st.plotly_chart(charts.yigin_cubuk(uzun, "donem", "seviye", "deger", "İletim hattı uzunluğu, gerilim seviyesine göre (km)", "km"), use_container_width=True)

    ui.bolum("02", "Trafo merkezleri", "Trafo sayısı ve toplam trafo kapasitesi.")
    k1, k2 = st.columns(2)
    with k1:
        st.plotly_chart(charts.toplam_cubuk(df, "total_transformers", "Toplam trafo sayısı", "adet"), use_container_width=True)
    with k2:
        st.plotly_chart(charts.toplam_cubuk(df.assign(kapasite_gva=df["total_capacity_mva"] / 1000), "kapasite_gva", "Toplam trafo kapasitesi (GVA)", "GVA"), use_container_width=True)
    ui.teias_notu("iletim", ek="Hat uzunlukları km, trafo kapasiteleri MVA cinsindendir.")

    ui.veri_tablosu(df.drop(columns=["donem"]), "Veri tablosu", "teias_iletim.csv")
