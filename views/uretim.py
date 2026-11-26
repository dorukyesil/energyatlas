"""Kaynaklara göre Türkiye elektrik üretimi (TWh), 2016-2026."""

import streamlit as st

from src.energyatlas import charts, data, ui

ui.sayfa_basligi(
    "Elektrik sistemi",
    "Kaynaklara göre üretim",
    "Türkiye brüt elektrik üretimi ve kaynak paylarının 2016'dan bugüne gelişimi.",
)

df = data.uretim()
son = df[df["donem"] == "2026 9A"].iloc[0]
ilk = df[df["donem"] == "2016"].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam üretim (2026 9A)", f"{ui.sayi(son['toplam_twh'], 0)} TWh")
c2.metric("Termik payı (2026 9A)", f"%{ui.sayi(son['termik_pct'], 0)}", f"{son['termik_pct'] - ilk['termik_pct']:+.0f} puan (2016'ya göre)", delta_color="inverse")
c3.metric("Yenilenebilir payı (2026 9A)", f"%{ui.sayi(100 - son['termik_pct'], 0)}")
c4.metric("Güneş payı (2026 9A)", f"%{ui.sayi(son['gunes_pct'], 0)}")

ui.bolum("01", "Gelişim", "Görünümü değiştirerek toplam üretimi veya kaynak paylarını inceleyin.")
gorunum = ui.segment(["Toplam (TWh)", "Kaynak payı (%)", "Isı haritası"], "uretim_gorunum")
if gorunum == "Toplam (TWh)":
    st.plotly_chart(charts.toplam_cubuk(df, "toplam_twh", "Toplam brüt üretim (TWh)", "TWh"), use_container_width=True)
elif gorunum == "Kaynak payı (%)":
    st.plotly_chart(charts.pay_yiginli_cubuk(df, "Kaynaklara göre üretim payı (%)"), use_container_width=True)
else:
    matris = df.set_index("donem")[["termik_pct", "gunes_pct", "ruzgar_pct", "diger_ye_pct"]].T
    matris.index = ["Termik", "Güneş", "Rüzgar", "Diğer yenilenebilir"]
    st.plotly_chart(
        charts.isi_haritasi(matris, "Kaynak payı ısı haritası (%)", "turkuaz", "%{z:,.0f}", "%"),
        use_container_width=True,
    )
ui.kaynak("Veri: sunum grafiklerinden okunmuştur. 9A: ocak-eylül. 2016-2018 güneş payı kaynakta belirtilmemiştir.")

ui.bolum("02", "Yıllık değişim", "Toplam üretimin bir önceki yıla göre değişimi.")
yillik = data.yillik_degisim(df, "toplam_twh")
st.plotly_chart(charts.yillik_degisim_cubuk(yillik, "donem", "degisim_pct", "Toplam üretim: yıllık değişim"), use_container_width=True)

ui.veri_tablosu(df, "Veri tablosu", "uretim.csv")
