"""Kaynaklara göre Türkiye elektrik üretimi (TEİAŞ yıllık ve aylık tabloları)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.teias_uretim()
    aylik = data.teias_aylik()
    ilk, son = df.iloc[0], df.iloc[-1]
    yenilenebilir = data.teias_yenilenebilir().iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Toplam brüt üretim ({int(son['yil'])})", f"{ui.sayi(son['toplam_twh'])} TWh")
    c2.metric(f"Termik payı ({int(son['yil'])})", f"%{ui.sayi(son['termik_pct'])}",
              f"{son['termik_pct'] - ilk['termik_pct']:+.1f} puan ({int(ilk['yil'])}'ya göre)".replace(".", ","), delta_color="inverse")
    c3.metric(f"Yenilenebilir payı ({int(yenilenebilir['yil'])})", f"%{ui.sayi(yenilenebilir['renewable_generation_share_percent'])}")
    c4.metric(f"Güneş payı ({int(son['yil'])})", f"%{ui.sayi(son['gunes_pct'])}")

    ui.bolum("01", "Gelişim", "Görünümü değiştirerek toplam üretimi veya kaynak paylarını inceleyin.")
    gorunum = ui.segment(["Toplam (TWh)", "Kaynaklara göre (TWh)", "Kaynak payı (%)", "Isı haritası"], "uretim_gorunum")
    etiket = {"Termik": "termik", "Hidro": "hidro", "Rüzgar + jeotermal": "ruzgar_jeotermal", "Güneş": "gunes"}
    if gorunum == "Toplam (TWh)":
        st.plotly_chart(charts.toplam_cubuk(df, "toplam_twh", "Toplam brüt üretim (TWh)", "TWh"), use_container_width=True)
    elif gorunum == "Kaynaklara göre (TWh)":
        uzun = pd.concat([df[["donem", f"{k}_twh"]].rename(columns={f"{k}_twh": "deger"}).assign(kaynak=e) for e, k in etiket.items()])
        st.plotly_chart(charts.yigin_cubuk(uzun, "donem", "kaynak", "deger", "Kaynaklara göre brüt üretim (TWh)", "TWh"), use_container_width=True)
    elif gorunum == "Kaynak payı (%)":
        st.plotly_chart(charts.pay_yigin_genel(df, "donem", {e: f"{k}_pct" for e, k in etiket.items()}, "Kaynaklara göre üretim payı (%)"), use_container_width=True)
    else:
        matris = df.set_index("donem")[[f"{k}_pct" for k in etiket.values()]].T
        matris.index = list(etiket.keys())
        st.plotly_chart(charts.isi_haritasi(matris, "Kaynak payı ısı haritası (%)", "turkuaz", "%{z:,.1f}", "%"), use_container_width=True)
    ui.teias_notu("uretim", ek="Rüzgar ve jeotermal, TEİAŞ yıllık tablosunda tek sütunda birleşiktir. Termik, atık ve biyokütleyi de içerir.")

    ui.bolum("02", "Yıllık değişim", "Toplam üretimin bir önceki yıla göre değişimi.")
    st.plotly_chart(charts.yillik_degisim_cubuk(data.yillik_degisim(df, "toplam_twh"), "donem", "degisim_pct", "Toplam üretim: yıllık değişim"), use_container_width=True)

    ui.bolum("03", "Aylık üretim", "Aylık brüt üretim, kaynaklara göre (TWh). Aylık seri 2021'den itibaren, son yayımlanan aya kadar vardır.")
    kaynak_kolonlari = {"Termik": "thermal", "Hidro": "hydro", "Rüzgar": "wind", "Güneş": "solar", "Jeotermal": "geothermal"}
    uzun_ay = pd.concat([aylik[["ay", k]].rename(columns={k: "deger"}).assign(kaynak=e, deger_twh=lambda d: d["deger"] / 1000) for e, k in kaynak_kolonlari.items()])
    st.plotly_chart(charts.yigin_cubuk(uzun_ay.assign(deger=uzun_ay["deger_twh"]), "ay", "kaynak", "deger", "Aylık brüt üretim (TWh)", "TWh"), use_container_width=True)
    son_ay = aylik.iloc[-1]
    onceki = aylik[(aylik["yil"] == son_ay["yil"] - 1) & (aylik["ay_no"] <= son_ay["ay_no"])]
    simdiki = aylik[(aylik["yil"] == son_ay["yil"]) & (aylik["ay_no"] <= son_ay["ay_no"])]
    degisim = (simdiki["total_generation"].sum() / onceki["total_generation"].sum() - 1) * 100
    k1, k2 = st.columns(2)
    k1.metric(f"{int(son_ay['yil'])} Ocak-{son_ay['ay_no']}. ay üretim", f"{ui.sayi(simdiki['total_generation'].sum() / 1000)} TWh",
              f"{degisim:+.1f}% (önceki yılın aynı dönemine göre)".replace(".", ","), delta_color="off")
    k2.metric("Son yayımlanan ay", son_ay["ay"])
    ui.teias_notu("aylik", ek="Güncel yıl değerleri TEİAŞ tarafından geçici olarak işaretlenebilir.")

    ui.veri_tablosu(df.drop(columns=["donem"]), "Veri tablosu (yıllık)", "teias_uretim.csv")
    ui.veri_tablosu(aylik, "Veri tablosu (aylık)", "teias_aylik.csv")
