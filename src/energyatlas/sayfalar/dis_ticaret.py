"""Türkiye elektrik ithalatı ve ihracatı (TEİAŞ): yıllık ve ülke bazında."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    talep = data.teias_talep()
    ulke = data.teias_dis_ticaret()
    son = talep.iloc[-1]

    c1, c2, c3 = st.columns(3)
    c1.metric(f"İthalat ({int(son['yil'])})", f"{ui.sayi(son['ithalat_twh'], 2)} TWh")
    c2.metric(f"İhracat ({int(son['yil'])})", f"{ui.sayi(son['ihracat_twh'], 2)} TWh")
    c3.metric("Net durum", "Net ihracatçı" if son["net_ithalat_twh"] < 0 else "Net ithalatçı", f"{ui.sayi(abs(son['net_ithalat_twh']), 2)} TWh", delta_color="off")

    ui.bolum("01", "Yıllara göre ithalat ve ihracat", "TWh.")
    uzun = pd.concat([
        talep[["donem", "ithalat_twh"]].rename(columns={"ithalat_twh": "deger"}).assign(yon="İthalat"),
        talep[["donem", "ihracat_twh"]].rename(columns={"ihracat_twh": "deger"}).assign(yon="İhracat"),
    ])
    st.plotly_chart(charts.gruplu_cubuk(uzun, "donem", "yon", "deger", "Elektrik ithalatı ve ihracatı (TWh)", "TWh"), use_container_width=True)
    ui.teias_notu("dis_ticaret")

    ui.bolum("02", "Ülkelere göre", "Seçilen yıl ve yön için ülke bazında elektrik alışverişi (TWh).")
    yil = st.segmented_control("Yıl", sorted(ulke["yil"].unique().tolist())[-5:], default=int(ulke["yil"].max()), key="dis_ticaret_yil") or int(ulke["yil"].max())
    yon = ui.segment(["İthalat", "İhracat"], "dis_ticaret_yon")
    secim = ulke[(ulke["yil"] == yil) & (ulke["yon"] == yon.lower())]
    if secim.empty or secim["twh"].sum() == 0:
        st.info("Bu yıl ve yön için ülke bazında alışveriş yok.")
    else:
        st.plotly_chart(charts.yatay_deger_cubuk(secim, "ulke", "twh", f"{yon}: ülkelere göre ({yil}, TWh)", "TWh"), use_container_width=True)
    ui.kaynak("Kaynak: TEİAŞ, ülkeler bazında ithalat-ihracat. Bağlantılı ülkeler: " + ", ".join(sorted(ulke["ulke"].unique())) + ".")

    ui.veri_tablosu(ulke[["yil", "yon", "ulke", "twh"]], "Veri tablosu (ülke bazında)", "teias_dis_ticaret.csv")
