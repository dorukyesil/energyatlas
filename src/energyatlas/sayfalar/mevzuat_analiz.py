"""Enerji mevzuatı analizleri: yıllara, türlere ve konulara göre yayımlanan metinler."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    d = data.mevzuat()
    if d.empty:
        st.info("Mevzuat verisi henüz üretilmedi.")
        return

    ui.bolum("01", "Yıllara göre yayım", "Yıl ve metin türüne göre enerjiyle ilgili Resmî Gazete metinlerinin sayısı.")
    yillik = d.groupby(["yil", "tur"]).size().reset_index(name="sayi")
    st.plotly_chart(charts.yigin_cubuk(yillik.assign(yil=yillik["yil"].astype(str)), "yil", "tur", "sayi", "Yıllara göre enerji mevzuatı (adet)", "Adet"), use_container_width=True)

    ui.bolum("02", "Değişiklik yoğunluğu", "Değişiklik içeren metinlerin yıllık payı. Mevzuatta ne kadar çok değişiklik yapıldığını gösterir.")
    yoğunluk = d.groupby("yil").agg(toplam=("baslik", "size"), degisiklik=("degisiklik", "sum")).reset_index()
    yoğunluk["pay"] = yoğunluk["degisiklik"] / yoğunluk["toplam"] * 100
    st.plotly_chart(charts.cizgi_alan(yoğunluk.assign(donem=yoğunluk["yil"]), "yil", "pay", "Değişiklik içeren metinlerin payı (%)", "%", "%"), use_container_width=True)

    ui.bolum("03", "Konu dağılımı", "Anahtar kelimelerin geçtiği metin sayısı. Bir metin birden çok kelime içerebilir.")
    kelimeler = d["anahtar_kelimeler"].fillna("").str.split(", ").explode()
    kelimeler = kelimeler[kelimeler != ""].value_counts().head(15).reset_index()
    kelimeler.columns = ["kelime", "sayi"]
    st.plotly_chart(charts.yatay_deger_cubuk(kelimeler, "kelime", "sayi", "En sık geçen enerji kavramları", "Metin sayısı"), use_container_width=True)

    ui.bolum("04", "Tür dağılımı", "Metin türlerinin toplam içindeki payı.")
    tur = d["tur"].value_counts().reset_index()
    tur.columns = ["tur", "sayi"]
    st.plotly_chart(charts.yatay_deger_cubuk(tur, "tur", "sayi", "Metin türlerine göre dağılım", "Adet"), use_container_width=True)

    ui.kaynak("Kaynak: Resmî Gazete günlük arşivi. Analizler başlık ve anahtar kelime eşleşmesine dayanır; hukuki yorum içermez.")
