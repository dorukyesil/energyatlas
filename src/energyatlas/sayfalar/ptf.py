"""Piyasa takas fiyatı (PTF): TL ve USD bazlı tarihsel ortalamalar, kur etkisi, aylık ve saatlik profil."""

import streamlit as st

from src.energyatlas import charts, data, ptf_analiz as pa, ui

PARA = {"USD/MWh": "usd", "TL/MWh": "tl"}
PARA_BIRIM = {"usd": "USD/MWh", "tl": "TL/MWh"}


def _donem_ortalama(g, yil: int, son_gun: int, kolon: str) -> float:
    """Yılın ilk `son_gun` gününün ortalaması (yıllar arası aynı dönemi karşılaştırmak için)."""
    s = g[(g["tarih"].dt.year == yil) & (g["tarih"].dt.dayofyear <= son_gun)][kolon]
    return float(s.mean())


def render() -> None:
    g = data.ptf_gunluk()
    p = data.ptf_profil()
    y = pa.yillik(g)
    yil_son = int(g["tarih"].dt.year.max())
    son_gun = int(g[g["tarih"].dt.year == yil_son]["tarih"].dt.dayofyear.max())
    son_tarih = g["tarih"].max().strftime("%d.%m.%Y")

    y16 = y[y.yil == 2016].iloc[0]
    y25 = y[y.yil == 2025].iloc[0]
    ysn = y[y.yil == yil_son].iloc[0]
    ayni25_usd = _donem_ortalama(g, yil_son - 1, son_gun, "usd_ort")
    ayni25_tl = _donem_ortalama(g, yil_son - 1, son_gun, "tl_ort")
    ysn_usd = _donem_ortalama(g, yil_son, son_gun, "usd_ort")
    ysn_tl = _donem_ortalama(g, yil_son, son_gun, "tl_ort")
    degisim_usd = (ysn_usd / ayni25_usd - 1) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("2025 ortalama (USD/MWh)", f"{ui.sayi(y25.usd, 1)}", f"2016: {ui.sayi(y16.usd, 1)}", delta_color="off")
    c2.metric("2025 ortalama (TL/MWh)", f"{ui.sayi(y25.tl, 0)}", f"2016: {ui.sayi(y16.tl, 0)}", delta_color="off")
    c3.metric(f"{yil_son} (1 Oca–{son_tarih[:5]}) USD/MWh", f"{ui.sayi(ysn_usd, 1)}",
              f"{degisim_usd:+.1f}% (geçen yıl aynı dönem)".replace(".", ","), delta_color="inverse")
    c4.metric("TL/USD (ima edilen kur)", f"{ui.sayi(ysn.kur, 2)}", f"2016: {ui.sayi(y16.kur, 2)}", delta_color="off")

    ui.bolum("01", "Yıllık gelişim", "Yıllık ortalama PTF. Kur seçeneği, TL fiyatının kaç TL'ye karşılık geldiğini gösterir.")
    gorunum = ui.segment(["USD/MWh", "TL/MWh", "TL/USD kuru"], "ptf_yillik_para")
    if gorunum == "TL/USD kuru":
        st.plotly_chart(charts.cizgi_alan(y, "donem", "kur", "Yıllık ortalama TL/USD kuru (ima edilen)", "TL/USD", "TL/USD"),
                        use_container_width=True)
    else:
        kolon = "usd" if gorunum == "USD/MWh" else "tl"
        st.plotly_chart(charts.cizgi_alan(y, "donem", kolon, f"Yıllık ortalama PTF ({gorunum})", gorunum, gorunum),
                        use_container_width=True)
    ui.kaynak(f"Veri: EPİAŞ saatlik PTF, 2016–{yil_son} ({son_tarih} itibarıyla). {yil_son} yılı kısmidir. "
              "TL/USD kuru, TL ortalamasının USD ortalamasına oranıdır.")

    ui.bolum("02", "Yıl karşılaştırması", "Aylık ortalamalar; seçilen yılların aynı aydaki değerlerini yan yana gösterir.")
    cp1, cp2 = st.columns([2, 3])
    with cp1:
        para_ad = ui.segment(["USD/MWh", "TL/MWh"], "ptf_aylik_para")
    tum_yillar = sorted(g["tarih"].dt.year.unique().tolist())
    with cp2:
        secilen = st.multiselect("Yıllar", options=tum_yillar, default=tum_yillar[-5:], key="ptf_aylik_yillar")
    if secilen:
        aylik = pa.aylik(g, PARA[para_ad])
        aylik = aylik[aylik["yil"].isin([str(s) for s in secilen])]
        st.plotly_chart(charts.cizgi_coklu(aylik, "ay_adi", "yil", "deger", f"Aylık ortalama PTF ({para_ad})", para_ad),
                        use_container_width=True)
    else:
        st.info("Karşılaştırmak için en az bir yıl seçin.")

    ui.bolum("03", "Günlük dağılım", "Her yılın günlük ortalama fiyatlarının dağılımı. Kutu ne kadar genişse, fiyat o yıl o kadar oynak demektir.")
    dag_para = ui.segment(["USD/MWh", "TL/MWh"], "ptf_dagilim_para")
    st.plotly_chart(charts.ptf_kutu(g, "usd_ort" if dag_para == "USD/MWh" else "tl_ort",
                                    f"Günlük ortalama PTF dağılımı ({dag_para})", dag_para),
                    use_container_width=True)
    ui.kaynak("Kutu: ortanca ve çeyrek değerler; kesikli çizgi: ortalama. Her nokta bir günün 24 saatlik ortalamasıdır.")

    ui.bolum("04", "Saatlik profil", "Ay ve saat bazında ortalama PTF. Koyu renk yüksek fiyatı gösterir.")
    cs1, cs2 = st.columns([2, 3])
    with cs1:
        profil_para = ui.segment(["USD/MWh", "TL/MWh"], "ptf_profil_para")
    with cs2:
        profil_yil = st.selectbox("Yıl", options=sorted(p["yil"].unique().tolist(), reverse=True), key="ptf_profil_yil")
    kolon = PARA[profil_para]
    matris = pa.profil_matrisi(p, int(profil_yil), kolon)
    st.plotly_chart(charts.isi_haritasi(matris, f"{profil_yil}: saat × ay ({profil_para})", "pas", "%{z:,.0f}", profil_para),
                    use_container_width=True)
    ui.kaynak("Yatay eksen: ay. Dikey eksen: günün saati (0–23). Boş hücreler, o ayın verisinin henüz olmadığını gösterir.")

    # --- Analiz: tüm sayılar yukarıdaki verilerden hesaplanır
    s25 = pa.saat_ozeti(p, 2025, "usd")
    ui.bolum("05", "Analiz", "Verilerden hesaplanan öne çıkan gelişmeler.")
    tl_kat = y25.tl / y16.tl
    usd_kat = y25.usd / y16.usd
    en_yuksek_yil = y.loc[y["usd"].idxmax()]
    st.markdown(
        f"""
- **Kur etkisi.** 2016–2025 arasında TL ortalama fiyatı **{ui.sayi(tl_kat, 1)} kat**, USD ortalaması **{ui.sayi(usd_kat, 1)} kat** arttı.
  TL/USD kuru {ui.sayi(y16.kur, 2)}'dan {ui.sayi(y25.kur, 2)}'e yükseldi. Bu nedenle TL cinsinden artışın büyük kısmı kur kaynaklıdır.
- **Zirve ve düşüş.** En yüksek USD ortalaması **{en_yuksek_yil.donem}** yılında ({ui.sayi(en_yuksek_yil.usd, 1)} USD/MWh) görüldü.
  {yil_son} (1 Oca–{son_tarih[:5]}) ortalaması **{ui.sayi(ysn_usd, 1)} USD/MWh**, geçen yılın aynı döneminin {ui.sayi(ayni25_usd, 1)} USD/MWh değerinin {'altında' if ysn_usd < ayni25_usd else 'üzerinde'}.
- **Saatlik profil (2025).** En yüksek ortalama saat **{s25['en_yuksek_saat']:02d}:00** ({ui.sayi(s25['en_yuksek'], 1)} USD),
  en düşük saat **{s25['en_dusuk_saat']:02d}:00** ({ui.sayi(s25['en_dusuk'], 1)} USD). Gündüz güneş üretiminin yoğun olduğu saatlerde fiyat düşüyor,
  akşam talebi arttığında yükseliyor.
- **Oynaklık.** Günlük ortalamaların standart sapması 2025'te {ui.sayi(y25.usd_std, 1)}, {yil_son}'de {ui.sayi(ysn.usd_std, 1)} USD/MWh'tir.
  {yil_son} yılı kısmi olduğu için yıl sonu değerleri bu tablodan farklılaşabilir.
"""
    )

    ui.bolum("06", "Veri tablosu", "Yıllık özet. Günlük ayrıntı için CSV dosyasını indirin.")
    tablo = y[["donem", "usd", "tl", "eur", "kur", "usd_min", "usd_max", "usd_std", "gun"]].rename(columns={
        "donem": "Yıl", "usd": "USD/MWh", "tl": "TL/MWh", "eur": "EUR/MWh", "kur": "TL/USD",
        "usd_min": "USD en düşük (günlük)", "usd_max": "USD en yüksek (günlük)", "usd_std": "USD std. sapma", "gun": "Gün sayısı",
    })
    ui.veri_tablosu(tablo, "Yıllık özet", "ptf_gunluk.csv",
                    kaynak="EPİAŞ Piyasa Takas Fiyatı, saatlik dosyalardan türetilmiş günlük özetler (ptf_gunluk.csv).")
