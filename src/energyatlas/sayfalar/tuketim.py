"""Türkiye brüt elektrik tüketimi (talebi) ve tepe talep (TEİAŞ)."""

import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    df = data.teias_talep()
    aylik = data.teias_aylik()
    ilk, son = df.iloc[0], df.iloc[-1]
    yillik_artis = ((son["brut_talep_twh"] / ilk["brut_talep_twh"]) ** (1 / (len(df) - 1)) - 1) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{int(son['yil'])} brüt talep", f"{ui.sayi(son['brut_talep_twh'])} TWh")
    c2.metric(f"{int(ilk['yil'])}-{int(son['yil'])} yıllık ortalama artış", f"%{ui.sayi(yillik_artis)}")
    c3.metric(f"Tepe talep ({int(son['yil'])})", f"{ui.sayi(son['tepe_talep_mw'], 0)} MW")

    ui.bolum("01", "Brüt talep", "Brüt elektrik talebi = üretim + ithalat - ihracat, TWh. Düzey veya yıllık değişimi görün.")
    gorunum = ui.segment(["Düzey (TWh)", "Yıllık değişim (%)"], "tuketim_gorunum")
    if gorunum == "Düzey (TWh)":
        st.plotly_chart(charts.toplam_cubuk(df, "brut_talep_twh", "Türkiye brüt elektrik talebi (TWh)", "TWh"), use_container_width=True)
    else:
        st.plotly_chart(charts.yillik_degisim_cubuk(data.yillik_degisim(df, "brut_talep_twh"), "donem", "degisim_pct", "Brüt talep: yıllık değişim"), use_container_width=True)
    ui.teias_notu("talep", ek="Brüt talep, ithalat-ihracat tablosundaki üretim + ithalat - ihracat değeridir.")

    ui.bolum("02", "Tepe talep", "Yıl içindeki en yüksek anlık ve saatlik talep, MW.")
    st.plotly_chart(charts.cizgi_alan(df, "yil", "tepe_talep_mw", "Anlık tepe talep (MW)", "MW", "MW"), use_container_width=True)

    ui.bolum("03", "Aylık talep", "Aylık brüt talep, yıllara göre karşılaştırma (TWh). Aylar boyunca mevsimsellik görünür.")
    a = aylik.assign(talep_twh=aylik["gross_demand"] / 1000)
    st.plotly_chart(charts.cizgi_coklu(a.assign(yil=a["yil"].astype(str)), "ay_no", "yil", "talep_twh", "Aylık brüt talep (TWh)", "TWh"), use_container_width=True)
    ui.teias_notu("aylik")

    ui.veri_tablosu(df.drop(columns=["donem"]), "Veri tablosu (yıllık)", "teias_talep.csv")
