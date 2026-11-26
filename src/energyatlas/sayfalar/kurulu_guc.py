"""Kaynaklara göre Türkiye elektrik kurulu gücü (TEİAŞ yıllık tablosu ve güncel YTBS verisi)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.teias_kurulu_guc()
    ytbs = data.teias_ytbs()
    ilk, son = df.iloc[0], df.iloc[-1]
    ytbs_toplam = ytbs["kurulu_guc_gw"].sum()
    ytbs_tarih = pd.to_datetime(ytbs["tarih"].iloc[0]).strftime("%d.%m.%Y")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Toplam kurulu güç ({int(son['yil'])}, TEİAŞ)", f"{ui.sayi(son['toplam_gw'])} GW",
              f"{son['toplam_gw'] - ilk['toplam_gw']:+.1f} GW ({int(ilk['yil'])}'dan beri)".replace(".", ","), delta_color="off")
    c2.metric(f"Güncel kurulu güç ({ytbs_tarih}, YTBS)", f"{ui.sayi(ytbs_toplam)} GW",
              f"{ytbs_toplam - son['toplam_gw']:+.1f} GW ({int(son['yil'])} sonuna göre)".replace(".", ","), delta_color="off")
    c3.metric(f"Güneş payı ({int(son['yil'])})", f"%{ui.sayi(son['gunes_pct'])}")
    c4.metric(f"Termik payı ({int(son['yil'])})", f"%{ui.sayi(son['termik_pct'])}",
              f"{son['termik_pct'] - ilk['termik_pct']:+.1f} puan ({int(ilk['yil'])}'ya göre)".replace(".", ","), delta_color="inverse")

    ui.bolum("01", "Gelişim", "Görünümü değiştirerek toplam kapasiteyi veya kaynak paylarını inceleyin.")
    gorunum = ui.segment(["Toplam (GW)", "Kaynaklara göre (GW)", "Kaynak payı (%)", "Isı haritası"], "kurulu_guc_gorunum")
    if gorunum == "Toplam (GW)":
        st.plotly_chart(charts.toplam_cubuk(df, "toplam_gw", "Toplam kurulu güç (GW)", "GW"), use_container_width=True)
    elif gorunum == "Kaynaklara göre (GW)":
        uzun = pd.concat([
            df[["donem", "termik_gw"]].rename(columns={"termik_gw": "deger"}).assign(kaynak="Termik"),
            df[["donem", "hidro_gw"]].rename(columns={"hidro_gw": "deger"}).assign(kaynak="Hidro"),
            df[["donem", "jeotermal_gw"]].rename(columns={"jeotermal_gw": "deger"}).assign(kaynak="Jeotermal"),
            df[["donem", "ruzgar_gw"]].rename(columns={"ruzgar_gw": "deger"}).assign(kaynak="Rüzgar"),
            df[["donem", "gunes_gw"]].rename(columns={"gunes_gw": "deger"}).assign(kaynak="Güneş"),
        ])
        st.plotly_chart(charts.yigin_cubuk(uzun, "donem", "kaynak", "deger", "Kaynaklara göre kurulu güç (GW)", "GW"), use_container_width=True)
    elif gorunum == "Kaynak payı (%)":
        st.plotly_chart(
            charts.pay_yigin_genel(df, "donem", {"Termik": "termik_pct", "Hidro": "hidro_pct", "Jeotermal": "jeotermal_pct", "Rüzgar": "ruzgar_pct", "Güneş": "gunes_pct"},
                                   "Kaynaklara göre kurulu güç payı (%)"),
            use_container_width=True,
        )
    else:
        matris = df.set_index("donem")[["termik_pct", "hidro_pct", "jeotermal_pct", "ruzgar_pct", "gunes_pct"]].T
        matris.index = ["Termik", "Hidro", "Jeotermal", "Rüzgar", "Güneş"]
        st.plotly_chart(charts.isi_haritasi(matris, "Kaynak payı ısı haritası (%)", "turkuaz", "%{z:,.1f}", "%"), use_container_width=True)
    ui.teias_notu("kurulu_guc", ek="TEİAŞ 'termik' tanımı atık ve biyokütleyi de içerir.")

    ui.bolum("02", "Yıllık artış", "Toplam kurulu gücün bir önceki yıla göre değişimi.")
    yillik = data.yillik_degisim(df, "toplam_gw")
    st.plotly_chart(charts.yillik_degisim_cubuk(yillik, "donem", "degisim_pct", "Toplam kurulu güç: yıllık değişim"), use_container_width=True)

    ui.bolum("03", "Termik santral ayrıntısı", "Termik kurulu güç, yakıt türüne göre (GW). Çoklu yakıtlı santraller ayrı gösterilir.")
    termik = pd.concat([
        df[["donem", "tas_komuru_gw"]].rename(columns={"tas_komuru_gw": "deger"}).assign(yakit="Taş kömürü"),
        df[["donem", "linyit_gw"]].rename(columns={"linyit_gw": "deger"}).assign(yakit="Linyit"),
        df[["donem", "dogalgaz_gw"]].rename(columns={"dogalgaz_gw": "deger"}).assign(yakit="Doğalgaz"),
        df[["donem", "sivi_yakit_gw"]].rename(columns={"sivi_yakit_gw": "deger"}).assign(yakit="Sıvı yakıtlar"),
        df[["donem", "atik_biyokutle_gw"]].rename(columns={"atik_biyokutle_gw": "deger"}).assign(yakit="Atık ve biyokütle"),
        df[["donem", "coklu_yakit_gw"]].rename(columns={"coklu_yakit_gw": "deger"}).assign(yakit="Çoklu yakıtlı"),
    ])
    st.plotly_chart(charts.yigin_cubuk(termik, "donem", "yakit", "deger", "Termik kurulu güç, yakıta göre (GW)", "GW"), use_container_width=True)

    ui.bolum("04", f"Güncel durum ({ytbs_tarih})", "TEİAŞ yük tevzi bilgi sistemi (YTBS) verisine göre kaynak gruplarına göre kurulu güç. YTBS geçici işletme verisidir.")
    grup = ytbs.groupby("grup", as_index=False)["kurulu_guc_gw"].sum().rename(columns={"grup": "kaynak"})
    st.plotly_chart(charts.yatay_deger_cubuk(grup, "kaynak", "kurulu_guc_gw", f"Kaynak grubuna göre güncel kurulu güç (GW), {ytbs_tarih}", "GW"), use_container_width=True)
    ui.kaynak("Kaynak: TEİAŞ YTBS. Sınıflama: termik grubu, TEİAŞ yıllık tablosundaki gibi atık ısı ve biyokütleyi içerir. Yıllık tablodan farklı olabilir.")

    ui.veri_tablosu(df.drop(columns=["donem"]), "Veri tablosu (yıllık)", "teias_kurulu_guc.csv")
    ui.veri_tablosu(ytbs[["tarih", "kaynak", "grup", "kurulu_guc_mw", "santral_sayisi"]], "Güncel kurulu güç (YTBS)", "teias_ytbs_kurulu_guc.csv")
