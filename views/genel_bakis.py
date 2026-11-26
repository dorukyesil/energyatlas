"""Ana sayfa: özet göstergeler, veri güncelleme, sunum indirme ve konu kartları."""

import streamlit as st

from src.energyatlas import charts, data, export, guncelleme, ui

kurulu = data.kurulu_guc()
uretim = data.uretim()
tuketim = data.tuketim()
ptf = data.ptf()
kurulu_yillik = data.tam_yillar(kurulu)
son_9a = kurulu.set_index("donem").loc["2026 9A"]


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
    ("🗺️", "Dünya karşılaştırma", "Bölgesel karşılaştırma, ülke güneş üretimi ve küresel yatırımlar.",
     ["Bölgesel karşılaştırma", "Ülke ve bölge güneş üretimi", "Küresel enerji yatırımları"],
     "views/dunya_karsilastirma.py", "Karşılaştırmaya git"),
]
for i in range(0, len(kartlar), 3):
    for kolon, (ikon, baslik, aciklama, maddeler, yol, etiket) in zip(st.columns(3, gap="medium"), kartlar[i:i + 3]):
        with kolon:
            ui.kategori_karti_basit(ikon, baslik, aciklama, maddeler, yol, etiket)
    st.write("")

sol, sag = st.columns([5, 6], gap="large")
with sol:
    st.markdown(
        f"""<div class="ea-eyebrow">Türkiye elektrik sektörü verileri</div>
<div class="ea-hero-etiket">Toplam kurulu güç · 2026 9A</div>
<div class="ea-hero-no">{ui.sayi(son_9a['toplam_gw'])}<small>GW</small></div>
<div class="ea-hero-not">Aşağıdaki konulardan birini seçerek ilgili sayfaya geçin.</div>""",
        unsafe_allow_html=True,
    )
with sag:
    st.plotly_chart(
        charts.cizgi_alan(kurulu_yillik, "donem", "toplam_gw", "Toplam kurulu güç (GW)", "GW", "GW"),
        use_container_width=True,
    )

uretim_yillik = data.tam_yillar(uretim)
tuketim_yillik = data.tam_yillar(tuketim)
ptf_yillik = data.tam_yillar(ptf)
ye_payi = 100 - uretim.set_index("donem").loc["2026 9A", "termik_pct"]
ye_payi_seri = (100 - uretim_yillik["termik_pct"]).tolist()
ptf_son = ptf.set_index("donem")

ui.kpi_serit(
    [
        {"etiket": "Kurulu güç, yıllık", "deger": ui.sayi(kurulu_yillik["toplam_gw"].iloc[-1]), "birim": "GW",
         "alt": f"2016: {ui.sayi(kurulu_yillik['toplam_gw'].iloc[0])} GW", "ton": "p", "seri": kurulu_yillik["toplam_gw"].tolist()},
        {"etiket": "Yenilenebilir üretim payı (2026 9A)", "deger": ui.sayi(ye_payi, 0), "birim": "%",
         "alt": f"2016: %{ui.sayi(ye_payi_seri[0], 0)}", "ton": "p", "seri": ye_payi_seri},
        {"etiket": "Brüt tüketim, yıllık", "deger": ui.sayi(tuketim_yillik["tuketim_twh"].iloc[-1], 0), "birim": "TWh",
         "alt": f"2016: {ui.sayi(tuketim_yillik['tuketim_twh'].iloc[0], 0)} TWh", "ton": "p", "seri": tuketim_yillik["tuketim_twh"].tolist()},
        {"etiket": "PTF, yıllık ortalama", "deger": ui.sayi(ptf_yillik["ptf_usd_mwh"].iloc[-1], 0), "birim": "USD/MWh",
         "alt": f"2026 9A: {ui.sayi(ptf_son.loc['2026 9A', 'ptf_usd_mwh'], 0)} USD/MWh", "ton": "n", "seri": ptf_yillik["ptf_usd_mwh"].tolist()},
    ]
)
ui.kaynak("Mini grafikler 2016-2025 tam yıl değerlerini gösterir. 9A: ocak-eylül dönemi.")

st.page_link("views/hakkinda.py", label="Hakkında ve veri kaynakları →", icon="📘")
