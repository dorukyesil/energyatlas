"""Kurulu güç: kaynak ve dönem seçilerek incelenir (TEİAŞ yıllık tablosu ve güncel YTBS verisi).

Portal tanımı: biyokütle ve atık ısı yenilenebilir sayılır. Termik, doğal gaz, linyit, kömürler ve diğer fosil yakıtlardır.
"""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui
from src.energyatlas.theme import kaynak_rengi

# Kaynak adı -> (yıllık TEİAŞ kolonu, YTBS kaynak kodları). None: toplam satırlarıdır, ayrıca hesaplanır.
KAYNAKLAR = {
    "Doğal gaz": ("dogalgaz_gw", ["dogalgaz"]),
    "Linyit": ("linyit_gw", ["linyit"]),
    "İthal ve taş kömür": ("tas_komuru_gw", ["ithalkomur", "taskomur", "asfaltitkomur"]),
    "Diğer termik": ("diger_termik_gw", ["fueloil", "motorin", "nafta", "lpg", "lng"]),
    "Biyokütle ve atık ısı": ("atik_biyokutle_gw", ["biyokutle", "atikisi"]),
    "Jeotermal": ("jeotermal_gw", ["jeotermal"]),
    "Hidro": ("hidro_gw", ["akarsu", "barajli"]),
    "Güneş": ("gunes_gw", ["gunes"]),
    "Rüzgar": ("ruzgar_gw", ["ruzgar"]),
    "Termik (toplam)": ("termik_gw", None),
    "Yenilenebilir (toplam)": ("yenilenebilir_gw", None),
    "Toplam": ("toplam_gw", None),
}
TOPLAMLAR = ("Termik (toplam)", "Yenilenebilir (toplam)", "Toplam")
YENILENEBILIR_KAYNAKLAR = ["Hidro", "Jeotermal", "Rüzgar", "Güneş", "Biyokütle ve atık ısı"]
TERMIK_KAYNAKLAR = ["Doğal gaz", "Linyit", "İthal ve taş kömür", "Diğer termik"]


def _guncel_etiket() -> str:
    """YTBS anlık verisinin tarihini içeren dönem etiketi (ör. '2026 (25.11.2026)')."""
    tarih = pd.to_datetime(data.teias_ytbs()["tarih"].iloc[0]).strftime("%d.%m.%Y")
    return f"2026 ({tarih})"


GUNCEL = _guncel_etiket()


def _tablo() -> pd.DataFrame:
    """Yıllık TEİAŞ satırları ve en güncel YTBS satırını birlikte döndürür. Her kaynak için GW ve % kolonu vardır."""
    yillik = data.teias_kurulu_guc().copy()
    yillik["diger_termik_gw"] = yillik["termik_gw"] - yillik["dogalgaz_gw"] - yillik["linyit_gw"] - yillik["tas_komuru_gw"]

    ytbs = data.teias_ytbs()
    kaynak_gw = ytbs.groupby("kaynak")["kurulu_guc_gw"].sum()
    toplam = float(ytbs["kurulu_guc_gw"].sum())
    satir = {"donem": GUNCEL}
    for ad, (gw_kol, kodlar) in KAYNAKLAR.items():
        if kodlar is not None:
            satir[gw_kol] = float(sum(kaynak_gw.get(k, 0.0) for k in kodlar))
    satir["termik_gw"] = sum(satir[KAYNAKLAR[k][0]] for k in TERMIK_KAYNAKLAR)
    satir["yenilenebilir_gw"] = sum(satir[KAYNAKLAR[k][0]] for k in YENILENEBILIR_KAYNAKLAR)
    satir["toplam_gw"] = toplam

    df = pd.concat([yillik, pd.DataFrame([satir])], ignore_index=True)
    for ad, (gw_kol, _) in KAYNAKLAR.items():
        df[f"{gw_kol}_pct"] = df[gw_kol] / df["toplam_gw"] * 100
    return df


def render() -> None:
    df = _tablo()
    donemler = df["donem"].tolist()
    secenekler = list(KAYNAKLAR.keys())
    c1, c2 = st.columns([1, 2])
    with c1:
        kaynak = st.selectbox("Kaynak", secenekler, index=secenekler.index("Toplam"), key="kg_kaynak")
    with c2:
        donem = st.select_slider("Dönem", options=donemler, value=donemler[-1], key="kg_donem")

    gw_kol = KAYNAKLAR[kaynak][0]
    pct_kol = f"{gw_kol}_pct"
    secili = df[df["donem"] == donem].iloc[0]
    ilk = df[df["donem"] == "2016"].iloc[0]
    gw = float(secili[gw_kol])
    toplam = float(secili["toplam_gw"])

    yen_gw = float(secili["yenilenebilir_gw"])
    yen_pct = yen_gw / toplam * 100
    ilk_yen_pct = float(ilk["yenilenebilir_gw_pct"])
    k0, k1, k2, k3 = st.columns(4)
    k0.metric(f"Yenilenebilir toplamı ({donem})", f"{ui.sayi(yen_gw)} GW",
              f"%{ui.sayi(yen_pct)} · {yen_pct - ilk_yen_pct:+.1f} puan (2016'ya göre)".replace(".", ","), delta_color="off")
    k1.metric(f"{kaynak} kurulu gücü ({donem})", f"{ui.sayi(gw)} GW")
    if kaynak == "Toplam":
        k2.metric("Toplam kurulu güç", f"{ui.sayi(toplam)} GW", f"{toplam - float(ilk['toplam_gw']):+.1f} GW (2016'ya göre)".replace(".", ","), delta_color="off")
    else:
        pay = gw / toplam * 100
        ilk_pay = float(ilk[pct_kol])
        k2.metric(f"{kaynak} payı ({donem})", f"%{ui.sayi(pay)}", f"{pay - ilk_pay:+.1f} puan (2016'ya göre)".replace(".", ","), delta_color="off")
    k3.metric("Kaynağın 2016'dan bu yana değişimi", f"{ui.sayi(gw - float(ilk[gw_kol]))} GW")
    st.caption("Yenilenebilir toplamı: hidro, jeotermal, rüzgar, güneş ve biyokütle ve atık ısı. "
               "Termik: doğal gaz, linyit, kömürler ve diğer fosil yakıtlar.")

    ui.bolum("01", f"{kaynak}: zaman içinde", "Seçilen kaynağın kurulu gücü (sütun) ve toplam içindeki payı (çizgi).")
    if kaynak == "Toplam":
        st.plotly_chart(charts.toplam_cubuk(df, "toplam_gw", "Toplam kurulu güç (GW)", "GW"), use_container_width=True)
    else:
        st.plotly_chart(charts.toplam_cubuk(df, gw_kol, f"{kaynak} kurulu gücü (GW)", "GW", renk=kaynak_rengi(kaynak)), use_container_width=True)
        st.plotly_chart(charts.cizgi_alan(df.iloc[:-1], "donem", pct_kol, f"{kaynak} payı (%)", "%", "%"), use_container_width=True)
    ui.teias_notu("kurulu_guc", ek=f"{GUNCEL} satırı YTBS güncel gün verisidir; yıllık TEİAŞ tablosuyla tam karşılaştırılabilir değildir. "
                                  "Yıllık 'İthal ve taş kömür' TEİAŞ'te birleşik yazıldığından YTBS değeri ithal, taş ve asfaltiti toplar.")

    ui.bolum("02", "Kaynaklara göre karşılaştırma", f"{donem} itibarıyla kaynak kırılımı.")
    satirlar = [(ad, float(secili[gw])) for ad, (gw, _) in KAYNAKLAR.items() if ad not in TOPLAMLAR]
    karsilastirma = pd.DataFrame(satirlar, columns=["kaynak", "gw"])
    st.plotly_chart(charts.yatay_deger_cubuk(karsilastirma, "kaynak", "gw", f"Kaynaklara göre kurulu güç, {donem} (GW)", "GW"), use_container_width=True)

    ui.veri_tablosu(df, "Veri tablosu", "teias_kurulu_guc.csv")
