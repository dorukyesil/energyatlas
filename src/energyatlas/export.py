"""Sunum (PowerPoint) üretimi.

Grafikler Plotly'den PNG olarak alınır, metinler mevcut verilerden hesaplanır.
Streamlit'e bağımlı değildir; böylece hem portaldan hem testlerden çağrılabilir.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from datetime import date

import plotly.graph_objects as go
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from src.energyatlas import charts, data, theme

GENISLIK_PX = 1600
YUKSEKLIK_PX = 820


def _rgb(hex_renk: str) -> RGBColor:
    h = hex_renk.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _sayi(deger: float, ondalik: int = 1) -> str:
    return f"{deger:,.{ondalik}f}".replace(",", "§").replace(".", ",").replace("§", ".")


@dataclass
class Slayt:
    """Tek bir sunum slaytının tanımı."""

    tip: str  # "kapak", "metin", "grafik", "gosterge"
    baslik: str
    alt_baslik: str = ""
    maddeler: list[str] = field(default_factory=list)
    grafik: go.Figure | None = None
    gostergeler: list[tuple[str, str]] = field(default_factory=list)
    kaynak: str = ""


def _grafik_png(fig: go.Figure) -> bytes:
    fig.update_layout(template=theme.SABLON, paper_bgcolor="white", plot_bgcolor="white",
                      title=None, margin=dict(l=40, r=20, t=20, b=60))
    return fig.to_image(format="png", width=GENISLIK_PX, height=YUKSEKLIK_PX, scale=1)


def _metin_kutusu(slayt_s, x, y, w, h, metin, boyut=16, renk=theme.METIN, kalin=False, hizala=PP_ALIGN.LEFT, serif=False):
    kutu = slayt_s.shapes.add_textbox(x, y, w, h)
    tf = kutu.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = hizala
    run = p.add_run()
    run.text = metin
    run.font.size = Pt(boyut)
    run.font.bold = kalin
    run.font.color.rgb = _rgb(renk)
    run.font.name = "Georgia" if serif else "Calibri"
    return kutu


def _baslik_ve_altyazi(slayt_s, baslik: str, alt: str = ""):
    _metin_kutusu(slayt_s, Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.9), baslik, 30, theme.MUREKKEP, serif=True)
    if alt:
        _metin_kutusu(slayt_s, Inches(0.6), Inches(1.15), Inches(12.1), Inches(0.5), alt, 14, theme.SOLUK)


def _alt_not(slayt_s, kaynak: str, sayfa_no: int):
    _metin_kutusu(slayt_s, Inches(0.6), Inches(6.95), Inches(10.5), Inches(0.4),
                  f"Kaynak: {kaynak}" if kaynak else "Enerji Atlası", 10, theme.SOLUK)
    _metin_kutusu(slayt_s, Inches(11.8), Inches(6.95), Inches(1.0), Inches(0.4), str(sayfa_no), 10, theme.SOLUK, hizala=PP_ALIGN.RIGHT)


def sunum_olustur(slaytlar: list[Slayt]) -> bytes:
    """Slayt tanımlarından .pptx dosyasının baytlarını üretir."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    bos = prs.slide_layouts[6]

    for no, s in enumerate(slaytlar, start=1):
        sl = prs.slides.add_slide(bos)
        if s.tip == "kapak":
            bg = sl.background.fill
            bg.solid()
            bg.fore_color.rgb = _rgb(theme.MUREKKEP)
            _metin_kutusu(sl, Inches(0.9), Inches(2.4), Inches(11.5), Inches(1.4), s.baslik, 46, "#FFFFFF", serif=True)
            _metin_kutusu(sl, Inches(0.9), Inches(3.9), Inches(11.5), Inches(0.8), s.alt_baslik, 20, "#DCE7F3")
            _metin_kutusu(sl, Inches(0.9), Inches(6.5), Inches(11.5), Inches(0.5),
                          f"Veri tarihi: {date.today():%d.%m.%Y}", 12, "#DCE7F3")
            continue

        _baslik_ve_altyazi(sl, s.baslik, s.alt_baslik)
        if s.tip == "gosterge":
            kutu_g = Inches(2.9)
            for i, (etiket, deger) in enumerate(s.gostergeler[:4]):
                x = Inches(0.6) + i * (kutu_g + Inches(0.12))
                _metin_kutusu(sl, x, Inches(2.2), kutu_g, Inches(0.5), etiket, 13, theme.SOLUK)
                _metin_kutusu(sl, x, Inches(2.7), kutu_g, Inches(1.0), deger, 34, theme.MUREKKEP, serif=True)
            if s.maddeler:
                _metin_kutusu(sl, Inches(0.6), Inches(4.3), Inches(12.1), Inches(2.4), "\n".join(f"•  {m}" for m in s.maddeler), 17)
        elif s.tip == "grafik":
            if s.grafik is not None:
                png = _grafik_png(s.grafik)
                sl.shapes.add_picture(io.BytesIO(png), Inches(0.6), Inches(1.75), width=Inches(7.6))
            if s.maddeler:
                _metin_kutusu(sl, Inches(8.5), Inches(2.0), Inches(4.3), Inches(4.6), "\n\n".join(f"•  {m}" for m in s.maddeler), 15)
        else:  # metin
            _metin_kutusu(sl, Inches(0.6), Inches(1.9), Inches(12.1), Inches(4.8), "\n\n".join(f"•  {m}" for m in s.maddeler), 18)
        _alt_not(sl, s.kaynak, no)

    cikti = io.BytesIO()
    prs.save(cikti)
    return cikti.getvalue()


def ozet_slaytlari() -> list[Slayt]:
    """Portal verilerinden otomatik oluşturulan özet sunumun slaytları."""
    kurulu = data.kurulu_guc()
    uretim = data.uretim()
    tuketim = data.tuketim()
    ptf = data.ptf()
    hedef = data.hedefler().set_index("kaynak")
    kisi = data.kisi_basina().set_index("kaynak")

    son = kurulu.set_index("donem").loc["2026 9A"]
    ilk = kurulu.set_index("donem").loc["2016"]
    ye_payi = 100 - uretim.set_index("donem").loc["2026 9A", "termik_pct"]
    tuk = data.tam_yillar(tuketim)
    p = ptf.set_index("donem")

    slaytlar = [
        Slayt("kapak", "Enerji Atlası", "Türkiye ve dünya elektrik sektörü özeti"),
        Slayt(
            "gosterge", "Genel durum", "Son veriler (2026 9A: ocak-eylül)",
            gostergeler=[
                ("Kurulu güç", f"{_sayi(son['toplam_gw'])} GW"),
                ("Yenilenebilir üretim payı", f"%{_sayi(ye_payi, 0)}"),
                ("Brüt tüketim (2025)", f"{_sayi(tuk['tuketim_twh'].iloc[-1], 0)} TWh"),
                ("PTF (2026 9A)", f"{_sayi(p.loc['2026 9A', 'ptf_usd_mwh'], 0)} USD/MWh"),
            ],
            maddeler=[
                f"2016'dan bu yana kurulu güç {_sayi(son['toplam_gw'] - ilk['toplam_gw'])} GW arttı.",
                f"Güneş payı %{_sayi(son['gunes_pct'], 0)}, rüzgar payı %{_sayi(son['ruzgar_pct'], 0)}.",
            ],
            kaynak="TEİAŞ, EPİAŞ, EPDK; sunum grafiklerinden okunmuştur",
        ),
        Slayt(
            "grafik", "Kaynaklara göre kurulu güç", "Toplam kurulu güç, 2016-2026 (GW)",
            grafik=charts.toplam_cubuk(kurulu, "toplam_gw", "", "GW"),
            maddeler=[
                f"2016'da {_sayi(ilk['toplam_gw'])} GW olan kurulu güç 2026 9A'da {_sayi(son['toplam_gw'])} GW'a ulaştı.",
                f"Termik payı 2016'da %{_sayi(ilk['termik_pct'], 0)}, 2026 9A'da %{_sayi(son['termik_pct'], 0)}.",
            ],
            kaynak="TEİAŞ; sunum grafiklerinden okunmuştur",
        ),
        Slayt(
            "grafik", "Brüt elektrik tüketimi", "TWh, 2016-2025",
            grafik=charts.tuketim_cubuk(tuk, ""),
            maddeler=[
                f"2025'te tüketim {_sayi(tuk['tuketim_twh'].iloc[-1], 0)} TWh oldu.",
                "2020-2023 arasında Covid, normalleşme ve deprem bölgesi etkileri görülüyor.",
            ],
            kaynak="TEİAŞ; sunum grafiklerinden okunmuştur",
        ),
        Slayt(
            "grafik", "Piyasa takas fiyatı (PTF)", "USD/MWh, 2016-2026 9A",
            grafik=charts.ptf_cubuk(ptf, ""),
            maddeler=[
                "2022'de 147 USD/MWh ile zirve yapıldı.",
                f"2026 9A, 2025 9A'ya göre %{_sayi(abs((p.loc['2026 9A', 'ptf_usd_mwh'] / p.loc['2025 9A', 'ptf_usd_mwh'] - 1) * 100), 0)} düşük.",
            ],
            kaynak="EPİAŞ; sunum grafiklerinden okunmuştur",
        ),
        Slayt(
            "grafik", "Kişi başına elektrik tüketimi", "kWh / kişi",
            grafik=charts.kisi_basina_cubuk(kisi.reset_index(), ""),
            maddeler=[
                f"Türkiye: {_sayi(kisi.loc['Türkiye', 'kwh_kisi'], 0)} kWh.",
                f"OECD ortalaması {_sayi(kisi.loc['OECD', 'kwh_kisi'], 0)} kWh, dünya ortalaması {_sayi(kisi.loc['Dünya', 'kwh_kisi'], 0)} kWh.",
            ],
            kaynak="Sunum grafiklerinden okunmuştur (OECD: 38 ülke)",
        ),
        Slayt(
            "grafik", "Kurulu güç hedefleri", "GW: 2025 gerçekleşen, 2028 ve 2035 hedefleri",
            grafik=charts.hedef_karsilastirma(data.hedefler(), ""),
            maddeler=[
                f"2028 Stratejik Plan hedefi: {_sayi(hedef.loc['Toplam', 'hedef_2028_stratejik_plan_gw'])} GW.",
                f"2035 yenilenebilir yol haritası: {_sayi(hedef.loc['Toplam', 'hedef_2035_yenilenebilir_yol_haritasi_gw'])} GW.",
            ],
            kaynak="Enerji ve Tabii Kaynaklar Bakanlığı; sunum grafiklerinden okunmuştur",
        ),
    ]
    return slaytlar


def ozet_sunum_bytes() -> bytes:
    return sunum_olustur(ozet_slaytlari())
