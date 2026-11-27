"""Kurulu güç: kaynak ve dönem seçilerek incelenir (TEİAŞ yıllık tablosu ve güncel YTBS verisi)."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, ui

KAYNAKLAR = {
    "Güneş": ("gunes_gw", "gunes_pct"),
    "Rüzgar": ("ruzgar_gw", "ruzgar_pct"),
    "Termik": ("termik_gw", "termik_pct"),
    "Hidro": ("hidro_gw", "hidro_pct"),
    "Jeotermal": ("jeotermal_gw", "jeotermal_pct"),
    "Yenilenebilir (toplam)": ("yenilenebilir_gw", "yenilenebilir_pct"),
    "Toplam": ("toplam_gw", None),
}
YTBS_KAYNAK = {"Güneş": "Güneş", "Rüzgar": "Rüzgar", "Termik": "Termik", "Hidro": "Hidro", "Jeotermal": "Jeotermal"}
GUNCEL = "2026 (güncel)"


def _tablo() -> pd.DataFrame:
    """Yıllık TEİAŞ satırları ve en güncel YTBS satırını birlikte döndürür."""
    yillik = data.teias_kurulu_guc().copy()
    yillik["yenilenebilir_gw"] = yillik[["gunes_gw", "ruzgar_gw", "hidro_gw", "jeotermal_gw"]].sum(axis=1)
    yillik["yenilenebilir_pct"] = yillik["yenilenebilir_gw"] / yillik["toplam_gw"] * 100
    ytbs = data.teias_ytbs()
    grup = ytbs.groupby("grup")["kurulu_guc_gw"].sum()
    toplam = float(ytbs["kurulu_guc_gw"].sum())
    satir = {"donem": GUNCEL, "toplam_gw": toplam}
    for ad, (gw, pct) in KAYNAKLAR.items():
        if ad in ("Toplam", "Yenilenebilir (toplam)"):
            continue
        deger = float(grup.get(YTBS_KAYNAK[ad], 0.0))
        satir[gw] = deger
        satir[pct] = deger / toplam * 100
    satir["yenilenebilir_gw"] = sum(satir[KAYNAKLAR[k][0]] for k in ["Güneş", "Rüzgar", "Hidro", "Jeotermal"])
    satir["yenilenebilir_pct"] = satir["yenilenebilir_gw"] / toplam * 100
    return pd.concat([yillik, pd.DataFrame([satir])], ignore_index=True)


def render() -> None:
    df = _tablo()
    donemler = df["donem"].tolist()
    c1, c2 = st.columns([1, 2])
    with c1:
        kaynak = st.selectbox("Kaynak", list(KAYNAKLAR.keys()), index=list(KAYNAKLAR.keys()).index("Toplam"), key="kg_kaynak")
    with c2:
        donem = st.select_slider("Dönem", options=donemler, value=donemler[-1], key="kg_donem")

    gw_kol, pct_kol = KAYNAKLAR[kaynak]
    secili = df[df["donem"] == donem].iloc[0]
    ilk = df[df["donem"] == "2016"].iloc[0]
    gw = float(secili[gw_kol])
    toplam = float(secili["toplam_gw"])

    yen_gw = float(secili["yenilenebilir_gw"])
    yen_pct = yen_gw / toplam * 100
    ilk_yen_pct = float(ilk["yenilenebilir_pct"])
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
    st.caption("Yenilenebilir toplamı: güneş, rüzgar, hidro ve jeotermal. Termik dışındaki kaynakların toplamıdır.")

    ui.bolum("01", f"{kaynak}: zaman içinde", "Seçilen kaynağın kurulu gücü (sütun) ve toplam içindeki payı (çizgi).")
    yillik_df = df.copy()
    yillik_df["etiket"] = yillik_df["donem"]
    if kaynak == "Toplam":
        st.plotly_chart(charts.toplam_cubuk(yillik_df, "toplam_gw", "Toplam kurulu güç (GW)", "GW"), use_container_width=True)
    else:
        st.plotly_chart(charts.toplam_cubuk(yillik_df, gw_kol, f"{kaynak} kurulu gücü (GW)", "GW"), use_container_width=True)
        st.plotly_chart(charts.cizgi_alan(yillik_df.iloc[:-1], "donem", pct_kol, f"{kaynak} payı (%)", "%", "%"), use_container_width=True)
    ui.teias_notu("kurulu_guc", ek=f"{GUNCEL} satırı YTBS güncel gün verisidir; yıllık TEİAŞ tablosuyla tam karşılaştırılabilir değildir.")

    ui.bolum("02", "Kaynaklara göre karşılaştırma", f"{donem} itibarıyla tüm kaynaklar.")
    satirlar = [(ad, float(secili[gw])) for ad, (gw, _) in KAYNAKLAR.items() if ad not in ("Toplam", "Yenilenebilir (toplam)")]
    karsilastirma = pd.DataFrame(satirlar, columns=["kaynak", "gw"])
    st.plotly_chart(charts.yatay_deger_cubuk(karsilastirma, "kaynak", "gw", f"Kaynaklara göre kurulu güç, {donem} (GW)", "GW"), use_container_width=True)

    ui.veri_tablosu(df.drop(columns=["donem"]).assign(donem=df["donem"]), "Veri tablosu", "teias_kurulu_guc.csv")
