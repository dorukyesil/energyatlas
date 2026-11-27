"""Hedefler ve vizyon: 2023'ten 2040'a Türkiye enerji hedefleri, infografik düzeninde."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui


def render() -> None:
    h = data.hedefler().set_index("kaynak")
    kg = data.hedef_2040().set_index("gosterge")["deger"]

    # Dört dönemin kurulu güç dağılımı (GW): Güneş, Rüzgar, Diğer (termik, hidro, nükleer vb.)
    toplam_2025 = float(h.loc["Toplam", "gerceklesen_2025_gw"])
    gunes = {"2025": float(h.loc["Güneş", "gerceklesen_2025_gw"]), "2028": float(h.loc["Güneş", "hedef_2028_stratejik_plan_gw"]),
             "2035": float(h.loc["Güneş", "hedef_2035_yenilenebilir_yol_haritasi_gw"]), "2040": float(kg["Güneş kurulu gücü 2040"])}
    ruzgar = {"2025": float(h.loc["Rüzgar", "gerceklesen_2025_gw"]), "2028": float(h.loc["Rüzgar", "hedef_2028_stratejik_plan_gw"]),
              "2035": float(h.loc["Rüzgar", "hedef_2035_yenilenebilir_yol_haritasi_gw"]), "2040": float(kg["Rüzgar kurulu gücü 2040"])}
    toplam = {"2025": toplam_2025, "2028": float(h.loc["Toplam", "hedef_2028_stratejik_plan_gw"]),
              "2035": float(h.loc["Toplam", "hedef_2035_yenilenebilir_yol_haritasi_gw"]), "2040": float(kg["Kurulu güç 2040"])}
    # Yenilenebilir: 2025, 2028 ve 2035 için hedef tablosu; 2040 için yenilenebilir payından türetilir (kaynakta GW olarak yok).
    yenilenebilir = {"2025": float(h.loc["Toplam Yenilenebilir", "gerceklesen_2025_gw"]),
                     "2028": float(h.loc["Toplam Yenilenebilir", "hedef_2028_stratejik_plan_gw"]),
                     "2035": float(h.loc["Toplam Yenilenebilir", "hedef_2035_yenilenebilir_yol_haritasi_gw"]),
                     "2040": float(kg["Kurulu güç 2040"]) * float(kg["Yenilenebilir payı 2040"]) / 100}
    diger_yenilenebilir = {d: yenilenebilir[d] - gunes[d] - ruzgar[d] for d in toplam}
    termik = {d: toplam[d] - yenilenebilir[d] for d in toplam}
    kaynaklar = [("Güneş", gunes), ("Rüzgar", ruzgar), ("Diğer yenilenebilir", diger_yenilenebilir), ("Termik", termik)]
    donemler = ["2025", "2028", "2035", "2040"]
    etiket = {"2025": "2025 gerçekleşen", "2028": "2028 Stratejik Plan", "2035": "2035 Yol Haritası", "2040": "2040 Milli Enerji"}

    ui.sayfa_basligi("Hedefler ve vizyon", "Türkiye enerji hedefleri: 2023'ten 2040'a",
                     "Ulusal Enerji Planı'ndan Milli Enerji 2040'a kadar açıklanan hedefler ve gerçekleşen değerler.")
    ui.geri_linki()

    ui.bolum("01", "Zaman çizgisi", "Hedefler hangi tarihte açıklandı ve hangi yılı hedefliyor.")
    ui.zaman_cizgisi([
        ("2023 Ocak", "Ulusal Enerji Planı", "2035 hedeflerinin ilk kez yayımlandığı plan (2020-2035)."),
        ("2024 Ekim", "2035 Yenilenebilir Enerji Yol Haritası", "120 GW rüzgar ve güneş hedefi, COP29'da ilan edildi."),
        ("2024 Kasım", "2024-2028 Stratejik Plan", "2028 hedefi: 145 GW toplam kurulu güç, 10 GW batarya."),
        ("2025 yıl sonu", "Gerçekleşen", f"Kurulu güç {ui.sayi(toplam['2025'])} GW; güneş {ui.sayi(gunes['2025'])} GW, rüzgar {ui.sayi(ruzgar['2025'])} GW."),
        ("2035", "Yenilenebilir yol haritası", f"Toplam {ui.sayi(toplam['2035'])} GW; güneş + rüzgar {ui.sayi(gunes['2035'] + ruzgar['2035'])} GW."),
        ("2040", "Milli Enerji 2040", f"Toplam {ui.sayi(toplam['2040'], 0)} GW; güneş + rüzgar {ui.sayi(float(kg['Güneş + rüzgar 2040']), 0)} GW; yenilenebilir %77."),
    ])
    ui.kaynak("Kaynak: Enerji ve Tabii Kaynaklar Bakanlığı; 2040 değerleri Milli Enerji 2040 lansmanındaki açıklanan hedeflerdir.")

    ui.bolum("02", "Kurulu güç yolu", "Güneş ve rüzgar ayrı; diğer yenilenebilir ve termik kaynakların dört dönemdeki kurulu gücü (GW).")
    uzun = pd.DataFrame([
        {"donem": etiket[d], "kaynak": k, "deger": v[d]}
        for d in donemler
        for k, v in kaynaklar
    ])
    st.plotly_chart(charts.yigin_cubuk(uzun, "donem", "kaynak", "deger", "Kurulu güç: dönemlere göre (GW)", "GW"), use_container_width=True)
    ui.kaynak("2028 ve 2035 değerleri hedef, 2025 değeri TEİAŞ'a yakın gerçekleşmedir. 2040 yenilenebilir değeri, Milli Enerji 2040 yenilenebilir payından (%77) türetilmiştir; termik, nükleer dahil kalan kısmı içerir.")

    ui.bolum("03", "Kaynak payı", "Her dönemde toplam kurulu gücün kaynaklara göre dağılımı.")
    cols = st.columns(4)
    for col, d in zip(cols, donemler):
        with col:
            st.plotly_chart(charts.pay_halkasi([k for k, _ in kaynaklar], [v[d] for _, v in kaynaklar], f"{etiket[d]}: {ui.sayi(toplam[d], 0)} GW"), use_container_width=True)

    ui.bolum("04", "Elektrik talebi", "Brüt elektrik talebi: 2025 gerçekleşen ve hedefler (TWh).")
    talep = pd.DataFrame({"donem": ["2025", "2035 Ulusal Plan", "2040 Milli Enerji"],
                          "twh": [float(h.loc["Elektrik Tüketimi (TWh)", "gerceklesen_2025_gw"]), float(h.loc["Elektrik Tüketimi (TWh)", "hedef_2035_ulusal_enerji_plani_gw"]), float(kg["Elektrik talebi 2040"])]})
    st.plotly_chart(charts.toplam_cubuk(talep, "twh", "Elektrik talebi (TWh)", "TWh"), use_container_width=True)

    ui.bolum("05", "2040 vizyonu", "Milli Enerji 2040'ta açıklanan başlıca hedefler.")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Toplam yatırım", f"{kg['Toplam yatırım 2040']:,.0f} milyar USD".replace(",", "."))
    k2.metric("Elektrikleşme", f"%{kg['Elektrikleşme oranı 2040']:,.0f}")
    k3.metric("Batarya depolama", f"{kg['Batarya depolama 2040']:,.0f} GWh")
    k4.metric("Elektrikli ve hibrit araç", f"{kg['Elektrikli ve hibrit araç 2040']:,.0f} milyon")
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Nükleer kurulu güç", f"{kg['Nükleer kurulu gücü 2040']:,.0f} GW")
    k6.metric("Pompajlı depolamalı HES", f"{kg['Pompajlı depolamalı HES 2040']:,.0f} GW")
    k7.metric("Enterkonneksiyon", f"{kg['Enterkonneksiyon kapasitesi 2040']:,.0f} GW")
    k8.metric("Şebeke yatırımı", f"{kg['Şebeke yatırımı 2040']:,.0f} milyar USD")
    ui.kaynak("Kaynak: Milli Enerji 2040 lansmanı (ETKB), Kalkınma Yatırım Bankası 'Milli Enerji 2040 Vizyonu Bilgi Notu' (09.11.2026). Ayrıntılı senaryo belgesi henüz yayımlanmamıştır.")
