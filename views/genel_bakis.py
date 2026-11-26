"""Ana sayfa: özet göstergeler, veri güncelleme, sunum indirme ve konu kartları."""

import pandas as pd
import streamlit as st

from src.energyatlas import charts, data, export, guncelleme, ui

kurulu = data.kurulu_guc()
uretim = data.uretim()
tuketim = data.tuketim()
ptf = data.ptf()
kurulu_yillik = data.teias_kurulu_guc()[["donem", "toplam_gw", "yil"]]
son_9a = {"toplam_gw": data.teias_ytbs()["kurulu_guc_gw"].sum()}


@st.cache_data(show_spinner="Sunum hazırlanıyor…")
def _sunum_bytes(surum: str) -> bytes:
    """Sunum dosyasını üretir. `surum` (son güncelleme zamanı) değiştiğinde yeniden üretilir."""
    return export.ozet_sunum_bytes()


ui.hero(
    "Enerji Atlası",
    "Türkiye ve dünya elektrik sektörü: kurulu güç, üretim, tüketim, depolama, fiyatlar ve hedefler tek yerde.",
)

ust1, ust2, ust3 = st.columns([3, 1.2, 1.4])
with ust1:
    st.caption(f"Son güncelleme: {guncelleme.son_guncelleme_metni()}")
with ust2:
    if st.button("Verileri güncelle", use_container_width=True, help="Veri dosyalarını yeniden okur ve sunumu yeniler."):
        st.cache_data.clear()
        data.yenile()
        guncelleme.guncelle()
        st.rerun()
with ust3:
    st.download_button(
        "Sunumu indir (.pptx)",
        data=_sunum_bytes(guncelleme.son_guncelleme_metni()),
        file_name="enerji_atlasi_ozet.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
    )

sol, sag = st.columns([5, 6], gap="large")
with sol:
    st.markdown(
        f"""<div class="ea-eyebrow">Türkiye elektrik sektörü verileri</div>
<div class="ea-hero-etiket">Toplam kurulu güç · güncel (YTBS)</div>
<div class="ea-hero-no">{ui.sayi(son_9a["toplam_gw"])}<small>GW</small></div>
<div class="ea-hero-not">Aşağıdaki konulardan birini seçerek ilgili sayfaya geçin.</div>""",
        unsafe_allow_html=True,
    )
with sag:
    ytbs_toplam = data.teias_ytbs()["kurulu_guc_gw"].sum()
    ytbs_tarih = pd.to_datetime(data.teias_ytbs()["tarih"].iloc[0])
    st.plotly_chart(
        charts.canli_kurulu_guc(kurulu_yillik, ytbs_toplam, ytbs_tarih, "Toplam kurulu güç (GW)"),
        use_container_width=True,
    )

ytbs = data.teias_ytbs()
ytbs_toplam = float(ytbs["kurulu_guc_gw"].sum())
ytbs_tarih = pd.to_datetime(ytbs["tarih"].iloc[0]).strftime("%d.%m.%Y")

aylik = data.teias_aylik()
o26 = aylik[(aylik["yil"] == 2026) & (aylik["ay_no"] <= 10)]
o25 = aylik[(aylik["yil"] == 2025) & (aylik["ay_no"] <= 10)]
yen26 = float(o26[["hydro", "wind", "solar", "geothermal"]].sum().sum() / o26["total_generation"].sum() * 100)
tuk26 = float(o26["gross_demand"].sum()) / 1000
tuk25 = float(o25["gross_demand"].sum()) / 1000
tuk_degisim = (tuk26 / tuk25 - 1) * 100

uretim_yillik = data.teias_uretim().copy()
yenilenebilir_yillik = (uretim_yillik["hidro_twh"] + uretim_yillik["ruzgar_jeotermal_twh"] + uretim_yillik["gunes_twh"]) / uretim_yillik["toplam_twh"] * 100
yenilenebilir_seri = yenilenebilir_yillik.tolist() + [yen26]
yenilenebilir_yillar = uretim_yillik["donem"].tolist() + ["2026 Oca-Eki"]

tuketim_yillik = data.teias_talep()
kurulu_seri = kurulu_yillik["toplam_gw"].tolist() + [ytbs_toplam]
kurulu_yillar = kurulu_yillik["donem"].tolist() + ["2026 güncel"]

ptf_yillik = data.tam_yillar(ptf)
ptf_son = ptf.set_index("donem")
ptf_seri = ptf_yillik["ptf_usd_mwh"].tolist() + [float(ptf_son.loc["2026 9A", "ptf_usd_mwh"])]
ptf_yillar = ptf_yillik["donem"].tolist() + ["2026 9A"]

ui.kpi_serit(
    [
        {"etiket": "Kurulu güç (2026 güncel, YTBS)", "deger": ui.sayi(ytbs_toplam), "birim": "GW",
         "alt": f"TEİAŞ 2025: {ui.sayi(kurulu_yillik['toplam_gw'].iloc[-1])} GW · {ytbs_tarih}", "ton": "p",
         "seri": kurulu_seri, "yillar": kurulu_yillar},
        {"etiket": "Yenilenebilir üretim payı (2026 Ocak-Ekim)", "deger": ui.sayi(yen26, 0), "birim": "%",
         "alt": f"2025 tam yıl: %{ui.sayi(yenilenebilir_yillik.iloc[-1], 0)}", "ton": "p",
         "seri": yenilenebilir_seri, "yillar": yenilenebilir_yillar, "ondalik": 0},
        {"etiket": "Brüt tüketim (2026 Ocak-Ekim)", "deger": ui.sayi(tuk26, 0), "birim": "TWh",
         "alt": f"2025 aynı dönem: {ui.sayi(tuk25, 0)} TWh ({tuk_degisim:+.1f}%)".replace(".", ","), "ton": "p" if tuk_degisim >= 0 else "n",
         "seri": tuketim_yillik["brut_talep_twh"].tolist(), "yillar": tuketim_yillik["donem"].tolist(), "ondalik": 0},
        {"etiket": "PTF (2026 9A ortalama)", "deger": ui.sayi(float(ptf_son.loc["2026 9A", "ptf_usd_mwh"]), 0), "birim": "USD/MWh",
         "alt": f"2025 tam yıl: {ui.sayi(float(ptf_son.loc['2025', 'ptf_usd_mwh']), 0)} USD/MWh", "ton": "n",
         "seri": ptf_seri, "yillar": ptf_yillar, "ondalik": 0},
    ]
)
ui.kaynak("Mini grafikler her dönem için en güncel değeri de içerir; noktanın üzerine gelerek yıl ve değeri görebilirsiniz. Parantez içinde dönem yazılıdır. Kurulu güç: YTBS (günlük), diğerleri TEİAŞ/EPİAŞ.")

ui.bolum("01", "Konular", "Her kart bir konu sayfasını açar. Sayfalar kendi içinde sekmelere ayrılmıştır.")

kartlar = [
    ("⚡", "Elektrik sistemi", "Kurulu güç, üretim, tüketim ve kişi başına tüketim.",
     ["Kaynaklara göre kurulu güç", "Kaynaklara göre üretim", "Brüt tüketim", "Kişi başına tüketim"],
     "views/elektrik.py", "Elektrik sistemine git"),
    ("🔋", "Depolama ve yatırımlar", "Depolamalı santraller, ön lisanslar ve yatırımlar.",
     ["Şebeke ilişkisi", "Devam eden yatırımlar", "Ön lisanslar", "İşletmedeki depolama", "EPDK santral listesi"],
     "views/depolama.py", "Depolama sayfasına git"),
    ("💲", "Fiyatlar ve tarifeler", "Piyasa takas fiyatı, EPDK tarifeleri ve YEKDEM.",
     ["PTF (piyasa takas fiyatı)", "EPDK elektrik tarifeleri", "YEKDEM fiyatlandırması ve duyuruları"],
     "views/fiyatlar.py", "Fiyatlara git"),
    ("🎯", "Altyapı ve hedefler", "Elektrik iletim ağı ve piyasa hedefleri.",
     ["İletim ağı (AC ve HVDC)", "Kurulu güç hedefleri"],
     "views/altyapi.py", "Altyapıya git"),
    ("🌍", "Dünya enerji görünümü", "IEA WEO 2026 verileri: enerji arzı, elektrik, emisyonlar, talep ve teknolojiler.",
     ["Güneş kapasitesi", "Birincil enerji arzı", "Elektrik üretimi ve kapasite", "CO2 emisyonları", "Talep ve ekonomi", "Hidrojen ve CCUS"],
     "views/dunya_enerji.py", "Dünya görünümüne git"),
    ("📜", "Mevzuat", "Enerji mevzuatı: Resmî Gazete metinleri, değişiklikler ve analizler.",
     ["Yayımlanan metinler ve filtreler", "Değişiklik yoğunluğu ve analizler", "Son yayımlananlar ve takip"],
     "views/mevzuat.py", "Mevzuata git"),
    ("🗺️", "Dünya karşılaştırma", "Bölgesel karşılaştırma, ülke güneş üretimi ve küresel yatırımlar.",
     ["Bölgesel karşılaştırma", "Ülke ve bölge güneş üretimi", "Küresel enerji yatırımları"],
     "views/dunya_karsilastirma.py", "Karşılaştırmaya git"),
]
for i in range(0, len(kartlar), 3):
    for kolon, (ikon, baslik, aciklama, maddeler, yol, etiket) in zip(st.columns(3, gap="medium"), kartlar[i:i + 3]):
        with kolon:
            ui.kategori_karti_basit(ikon, baslik, aciklama, maddeler, yol, etiket)
    st.write("")

st.page_link("views/hakkinda.py", label="Hakkında ve veri kaynakları →", icon="📘")
