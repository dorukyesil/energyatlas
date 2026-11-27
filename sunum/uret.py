"""Veri kitabından sunumu üretir.

Sunum şablonu (pptx) sabittir: yerleşim, renk, yazı tipi ve şekillerin hiçbiri değişmez.
Yalnızca sayılar, grafik değerleri, tablo hücreleri ve çubuk uzunlukları veri kitabındaki
(Piyasa_Veri_Kitabi.xlsx) hesaplanmış değerlerle yerinde güncellenir.

Kullanım:
    python sunum/uret.py [--kitap sunum/veri/Piyasa_Veri_Kitabi.xlsx]
                         [--sablon sunum/sablon/Enerji_Sektoru_Sunum_sablon.pptx]
                         [--cikti sunum/cikti/<ad>.pptx] [--zorla]

Kitaptaki formüller LibreOffice ile hesaplatılır. Kontrol sayfasında UYARI varsa sunum üretilmez
(--zorla ile atlanır).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import openpyxl
from lxml import etree
from pptx import Presentation

KOK = Path(__file__).resolve().parent
VARSAYILAN_KITAP = KOK / "veri" / "Piyasa_Veri_Kitabi.xlsx"
VARSAYILAN_SABLON = KOK / "sablon" / "Enerji_Sektoru_Sunum_sablon.pptx"

C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
AY_ADLARI = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


class UretimHatasi(Exception):
    """Şablon beklenen yapıda değilse ya da kitap eksikse fırlatılır; sessizce yanlış sunum üretilmez."""


# ------------------------------------------------------------------ biçim yardımcıları

def yuvarla(x: float, d: int = 0) -> Decimal:
    """Excel gibi yarımı yukarı yuvarlar."""
    q = Decimal(1).scaleb(-d)
    return Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP)


def tr(x: float, d: int = 0) -> str:
    """Türkçe sayı biçimi: binlik nokta, ondalık virgül."""
    s = f"{yuvarla(x, d):,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def yuzde(x: float, d: int = 0) -> str:
    return "%" + tr(x * 100, d)


_ONES = {1: ("i", False), 2: ("i", True), 3: ("ü", False), 4: ("ö", False), 5: ("e", False),
         6: ("ı", True), 7: ("i", True), 8: ("i", False), 9: ("u", False)}
_TENS = {10: ("o", False), 20: ("i", True), 30: ("u", False), 40: ("ı", False), 50: ("i", True),
         60: ("ı", False), 70: ("i", False), 80: ("e", False), 90: ("a", False)}


def _son_ses(n: int) -> tuple[str, bool]:
    """Sayının okunuşundaki son ünlü ve okunuşun ünlüyle bitip bitmediği."""
    n = int(n)
    if n % 10:
        return _ONES[n % 10]
    if n % 100:
        return _TENS[n % 100]
    if n % 1000:
        return ("ü", False)  # yüz
    return ("i", False) if n else ("ı", False)  # bin / sıfır


def _dort(v: str) -> str:
    return {"a": "ı", "ı": "ı", "e": "i", "i": "i", "o": "u", "u": "u", "ö": "ü", "ü": "ü"}[v]


def ek_yonelme(n: float) -> str:
    """'%63’e', '%59’a' gibi yönelme eki (’ dahil)."""
    v, ends_vowel = _son_ses(round(n))
    return "’" + ("y" if ends_vowel else "") + ("a" if v in "aıou" else "e")


def ek_belirtme(n: float) -> str:
    """'11’i', '3’ü' gibi belirtme eki."""
    v, ends_vowel = _son_ses(round(n))
    return "’" + ("y" if ends_vowel else "") + _dort(v)


def ek_iyelik_tamlayan(n: float) -> str:
    """'%15’inin', '%17’sinin' gibi iyelik + tamlayan eki."""
    v, ends_vowel = _son_ses(round(n))
    k = _dort(v)
    return "’" + ("s" if ends_vowel else "") + k + "n" + k + "n"


# ------------------------------------------------------------------ kitap okuma

def hesapla(kitap: Path, hedef_klasor: Path) -> Path:
    """Kitabı LibreOffice ile hesaplatıp değerleri önbelleğe yazılmış bir kopya döndürür."""
    kopya = hedef_klasor / "kitap.xlsx"
    shutil.copy(kitap, kopya)
    cikis = hedef_klasor / "hesap"
    sonuc = subprocess.run(
        ["soffice", "--headless", "--convert-to", "xlsx:Calc MS Excel 2007 XML", "--outdir", str(cikis), str(kopya)],
        capture_output=True, text=True, timeout=300,
    )
    hesapli = cikis / "kitap.xlsx"
    if not hesapli.exists():
        raise UretimHatasi(f"Kitap hesaplanamadı (LibreOffice gerekli): {sonuc.stderr[:300]}")
    return hesapli


class Kitap:
    """Hesaplanmış veri kitabından sunumun ihtiyaç duyduğu değerleri okur."""

    def __init__(self, hesapli_yol: Path):
        self.wb = openpyxl.load_workbook(hesapli_yol, data_only=True)

    def _satirlar(self, sayfa: str) -> list[list]:
        return [list(r) for r in self.wb[sayfa].iter_rows(values_only=True)]

    @staticmethod
    def _bul(rows: list[list], baslangic: str, sutun: int = 0) -> list:
        for r in rows:
            if r[sutun] is not None and str(r[sutun]).strip().startswith(baslangic):
                return r
        raise UretimHatasi(f"Kitapta '{baslangic}' satırı bulunamadı.")

    # -- kontrol ve parametreler
    def kontrol_tamam(self) -> tuple[bool, str]:
        rows = self._satirlar("Kontrol")
        genel = self._bul(rows, "Genel durum", 1)
        durum = str(genel[2])
        return durum.strip().upper() == "TAMAM", durum

    def parametre(self) -> dict:
        elk = self._satirlar("Parametre_Elk")
        depo = self._satirlar("Parametre_Depo")
        tarih = self._bul(elk, "Kurulu güç tarihi")[1]
        if isinstance(tarih, (datetime, date)):
            tarih = tarih.strftime("%Y-%m-%d")
        ay = int(self._bul(elk, "Rapor ayı")[1])
        yil = int(self._bul(elk, "Rapor yılı")[1])
        return {
            "yil": yil, "ay": ay, "ay_adi": AY_ADLARI[ay - 1],
            "ay_sonu_tarih": datetime.strptime(str(tarih), "%Y-%m-%d").strftime("%d.%m.%Y"),
            "cari": str(self._bul(elk, "Cari dönem etiketi")[1]),
            "onceki": str(self._bul(elk, "Önceki yıl dönemi etiketi")[1]),
            "donem_ifadesi": str(self._bul(elk, "Dönem ifadesi")[1]),
            "depo_yil": int(self._bul(depo, "Rapor yılı")[1]),
            "ortalama_yili": int(self._bul(depo, "Ortalama yılı")[1]),
        }

    # -- elektrik sayfaları (S2, S3, S5)
    def donem_tablosu(self, sayfa: str, par: dict) -> dict:
        rows = self._satirlar(sayfa)
        i0 = next(i for i, r in enumerate(rows) if r[0] == "Dönem")
        veri = []
        for r in rows[i0 + 1:]:
            if r[0] is None or str(r[0]).startswith("Büyüme"):
                break
            veri.append(r)
        yillik = [r for r in veri if re.fullmatch(r"\d{4}", str(r[0]).strip())]
        onceki = [r for r in veri if str(r[0]).startswith(par["onceki"])]
        cari = [r for r in veri if str(r[0]).startswith(par["cari"])]
        if len(onceki) != 1 or len(cari) != 1:
            raise UretimHatasi(f"{sayfa}: '{par['onceki']}' ve '{par['cari']}' satırları bulunamadı.")
        return {"yillik": yillik, "onceki": onceki[0], "cari": cari[0], "rows": rows}

    # -- slayt 4
    def kaynak_tablosu(self) -> list[list]:
        rows = self._satirlar("S4_Tablo")
        i0 = next(i for i, r in enumerate(rows) if r[0] == "Kaynak")
        out = []
        for r in rows[i0 + 1:]:
            if r[0] is None or str(r[0]).startswith("Parçalar"):
                break
            out.append(r)
        return out

    def iletim(self) -> dict:
        rows = self._satirlar("D1_Iletim")
        return {str(r[0]).strip(): r for r in rows if r[0] is not None}

    def onlisans(self) -> dict:
        rows = self._satirlar("D2_Onlisans")
        i0 = next(i for i, r in enumerate(rows) if r[0] == "Başlangıç yılı")
        yillar, toplam = [], None
        for r in rows[i0 + 1:]:
            if r[0] is None:
                continue
            if str(r[0]) == "TOPLAM":
                toplam = r
                break
            yillar.append(r)
        adet = self._bul(rows, "Ön lisans adedi")
        j0 = next(i for i, r in enumerate(rows) if r[0] == "Firma")
        firmalar = [r for r in rows[j0 + 1:] if r[0] is not None]
        return {"yillar": yillar, "toplam": toplam, "adet": adet, "firmalar": firmalar}

    def takvim(self) -> dict:
        rows = self._satirlar("D4_Takvim")
        i0 = next(i for i, r in enumerate(rows) if r[0] == "Bitiş yılı")
        yillar, toplam = [], None
        for r in rows[i0 + 1:]:
            if r[0] is None:
                continue
            if str(r[0]) == "TOPLAM":
                toplam = r
                break
            yillar.append(r)
        pay = self._bul(rows, "Rapor yılı biten")
        return {"yillar": yillar, "toplam": toplam, "pay_ges": pay[2], "pay_res": pay[4]}

    def isletme(self) -> dict:
        rows = self._satirlar("D5_Isletme")
        i0 = next(i for i, r in enumerate(rows) if r[0] == "Sıra")
        tablo = [r for r in rows[i0 + 1:] if isinstance(r[0], (int, float))]
        ozet = {str(r[1]).strip(): r for r in rows if r[0] is None and r[1] in ("Toplam", "Güneş", "Rüzgar")}
        sirket = next(r for r in rows if r[1] is not None and str(r[1]).startswith("Şirket sayısı"))
        return {"tablo": tablo, "ozet": ozet, "sirket": int(sirket[2]) if sirket[2] is not None else int(sirket[1])}

    def ptf(self) -> dict:
        rows = self._satirlar("D7_PTF")
        i0 = next(i for i, r in enumerate(rows) if r[0] == "Dönem")
        donemler = {}
        for r in rows[i0 + 1:]:
            if r[0] is None or str(r[0]).startswith("Büyüme"):
                break
            donemler[str(r[0]).strip()] = r[2]
        return {"donemler": donemler, "ybbo": self._bul(rows, "PTF YBBO")[1], "degisim": self._bul(rows, "PTF değişimi")[1]}

    def yekdem(self) -> dict:
        rows = self._satirlar("D8_Yekdem")
        bolum = None
        d = {"gunes": [], "depo": [], "katki": {}, "sure": {}, "formul": {}}
        for r in rows:
            a = None if r[0] is None else str(r[0]).strip()
            if a is None:
                continue
            if a.startswith("Güneş YEKDEM"):
                bolum = "gunes"; continue
            if a.startswith("Depolama YEKDEM"):
                bolum = "depo"; continue
            if a.startswith("Yerli katkı"):
                bolum = "katki"; continue
            if a.startswith("Süreler"):
                bolum = "sure"; continue
            if a.startswith("Formül ağırlıkları"):
                bolum = "formul"; continue
            if bolum in ("gunes", "depo"):
                d[bolum].append((a, r[1]))
            elif bolum == "katki":
                d["katki"][a] = r[1]
            elif bolum == "sure":
                if a.startswith("YEKDEM süresi"):
                    d["sure"]["yekdem"] = r[1]
                elif a.startswith("Yerli aksam süresi"):
                    d["sure"]["aksam_gunes"], d["sure"]["aksam_depo"] = r[1], r[2]
                elif a.startswith("Devreye giriş ilk"):
                    d["sure"]["ilk"] = int(r[1])
                elif a.startswith("Devreye giriş son"):
                    d["sure"]["son"] = int(r[1])
            elif bolum == "formul":
                d["formul"][a.replace("Formül ağırlığı: ", "")] = r[1]
        return d


# ------------------------------------------------------------------ şablon yardımcıları

SAYI_DESENI = r"[-%]*(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)"


def _tum_sekiller(sekiller):
    for sh in sekiller:
        if sh.shape_type == 6:
            yield from _tum_sekiller(sh.shapes)
        else:
            yield sh


class Sablon:
    def __init__(self, yol: Path):
        self.prs = Presentation(str(yol))

    def bul(self, slayt: int, ad: str):
        bulunan = [s for s in _tum_sekiller(self.prs.slides[slayt - 1].shapes) if s.name == ad]
        if len(bulunan) != 1:
            raise UretimHatasi(f"Slayt {slayt}: '{ad}' şekli {len(bulunan)} kez bulundu (1 bekleniyordu).")
        return bulunan[0]

    # -- metin
    def tek_paragraf(self, slayt: int, ad: str, yeni: str, par: int = 0):
        """Tek çalıştırmalı paragrafın metnini değiştirir (biçim aynı kalır)."""
        p = self.bul(slayt, ad).text_frame.paragraphs[par]
        if len(p.runs) != 1:
            raise UretimHatasi(f"Slayt {slayt} {ad}: tek çalıştırma bekleniyordu, {len(p.runs)} bulundu.")
        p.runs[0].text = yeni

    def calistirma(self, slayt: int, ad: str, par: int, run: int, desen: str, yeni: str):
        """Belirli çalıştırmanın tamamını doğrulayıp değiştirir; desen uymazsa durur."""
        p = self.bul(slayt, ad).text_frame.paragraphs[par]
        r = p.runs[run]
        if not re.fullmatch(desen, r.text, flags=re.S):
            raise UretimHatasi(f"Slayt {slayt} {ad} p{par} r{run}: beklenen desen '{desen}', bulunan '{r.text}'")
        r.text = yeni

    def icinde(self, slayt: int, ad: str, par: int, run: int, desen: str, yeni: str, adet: int = 1):
        """Çalıştırma içindeki bir parçayı (re.sub) değiştirir; en az `adet` eşleşme beklenir."""
        p = self.bul(slayt, ad).text_frame.paragraphs[par]
        r = p.runs[run]
        yeni_metin, n = re.subn(desen, lambda m: yeni, r.text, count=adet)
        if n < 1:
            raise UretimHatasi(f"Slayt {slayt} {ad} p{par} r{run}: '{desen}' bulunamadı: '{r.text}'")
        r.text = yeni_metin

    def ilk_sayi(self, slayt: int, ad: str, yeni: str, sira: int = 0):
        """Şeklin metnindeki `sira`'ıncı sayıyı (ilgili çalıştırmada) değiştirir."""
        sh = self.bul(slayt, ad)
        sayac = 0
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                for m in re.finditer(SAYI_DESENI, r.text):
                    if sayac == sira:
                        r.text = r.text[:m.start()] + yeni + r.text[m.end():]
                        return
                    sayac += 1
        raise UretimHatasi(f"Slayt {slayt} {ad}: {sira}. sayı bulunamadı.")

    # -- grafik (önbellek değerleri yerinde güncellenir; dış bağlantı ve biçim olduğu gibi kalır)
    def grafik(self, slayt: int, ad: str, kategoriler: dict[int, str | None], seriler: list[dict[int, float | None]]):
        sh = self.bul(slayt, ad)
        cs = sh.chart._chartSpace
        ser_list = cs.xpath(".//c:ser")
        if len(ser_list) != len(seriler):
            raise UretimHatasi(f"Slayt {slayt} {ad}: {len(ser_list)} seri var, {len(seriler)} veri verildi.")
        for ser, degerler in zip(ser_list, seriler):
            for cache_yolu, vals, is_str in ((".//c:cat//c:strCache | .//c:cat//c:numCache", kategoriler, True),
                                             (".//c:val//c:numCache", degerler, False)):
                if not vals:
                    continue
                caches = ser.xpath(cache_yolu)
                if not caches:
                    raise UretimHatasi(f"Slayt {slayt} {ad}: önbellek bulunamadı ({cache_yolu}).")
                _onbellek_yaz(caches[0], vals, is_str)

    # -- tablo hücresi
    def hucre(self, slayt: int, ad: str, satir: int, sutun: int, yeni: str):
        c = self.bul(slayt, ad).table.cell(satir, sutun)
        p = c.text_frame.paragraphs[0]
        if not p.runs:
            raise UretimHatasi(f"Slayt {slayt} {ad} [{satir},{sutun}] hücresinde çalıştırma yok.")
        p.runs[0].text = yeni
        for r in p.runs[1:]:
            r.text = ""

    def genislik(self, slayt: int, ad: str, genislik: int):
        self.bul(slayt, ad).width = int(genislik)

    def kaydet(self, yol: Path):
        self.prs.save(str(yol))


def _onbellek_yaz(cache, degerler: dict[int, object], is_str: bool):
    v_tag = f"{{{C_NS}}}v"
    pt_tag = f"{{{C_NS}}}pt"
    adet = int(cache.find(f"{{{C_NS}}}ptCount").get("val"))
    mevcut = {int(pt.get("idx")): pt for pt in cache.findall(pt_tag)}
    for idx, deger in degerler.items():
        if idx >= adet:
            raise UretimHatasi(f"Grafik noktası {idx} önbellek boyutunu ({adet}) aşıyor.")
        if deger is None:
            if idx in mevcut:
                cache.remove(mevcut[idx])
            continue
        metin = deger if is_str else repr(float(deger))
        if idx in mevcut:
            mevcut[idx].find(v_tag).text = metin
        else:
            pt = etree.SubElement(cache, pt_tag)
            pt.set("idx", str(idx))
            etree.SubElement(pt, v_tag).text = metin
            # idx sırasını koru
            noktalar = sorted(cache.findall(pt_tag), key=lambda e: int(e.get("idx")))
            for e in noktalar:
                cache.remove(e)
            for e in noktalar:
                cache.append(e)


# ------------------------------------------------------------------ slayt doldurucular

def _yillik_idx(n_yil: int) -> list[int]:
    return list(range(n_yil))


def _elektrik_grafigi(sb: Sablon, slayt: int, ad: str, tablo: dict, par: dict, sutunlar: list[int], bos_idx: int = 10):
    """S2/S3 yığılmış sütun grafikleri: 10 yıllık sütun, boşluk, önceki yıl dönemi, cari dönem."""
    yillik = tablo["yillik"]
    if len(yillik) != bos_idx:
        raise UretimHatasi(f"Slayt {slayt}: şablon {bos_idx} yıllık sütun için kurulmuş, kitapta {len(yillik)} yıl var. "
                           "Yıl dönümü için şablona sütun eklenmeli (elle).")
    kategoriler = {i: str(r[0]).strip() for i, r in enumerate(yillik)}
    kategoriler[bos_idx + 1] = par["onceki"]
    kategoriler[bos_idx + 2] = par["cari"]
    seriler = []
    for k in sutunlar:
        d = {i: float(r[k]) for i, r in enumerate(yillik)}
        d[bos_idx + 1] = float(tablo["onceki"][k])
        d[bos_idx + 2] = float(tablo["cari"][k])
        seriler.append(d)
    sb.grafik(slayt, ad, kategoriler, seriler)


def doldur(sb: Sablon, k: Kitap, par: dict) -> None:
    yil, ay_adi, donem_ifadesi = par["yil"], par["ay_adi"], par["donem_ifadesi"]
    ocak_ay = f"Ocak-{ay_adi} {yil}" if par["ay"] > 1 else f"Ocak {yil}"

    # ---------- Slayt 2: kurulu güç
    s2 = k.donem_tablosu("S2_KuruluGuc", par)
    r2 = s2["rows"]
    ybbo_top = Kitap._bul(r2, "Toplam kurulu güç, 2016")[1]
    ybbo_yen = Kitap._bul(r2, "Yenilenebilir kurulu güç, 2016")[1]
    yen16 = Kitap._bul(r2, "2016 yenilenebilir")
    yen_cari = Kitap._bul(r2, "Cari yenilenebilir")
    gunes_cari = Kitap._bul(r2, "Cari güneş")
    ruzgar_cari = Kitap._bul(r2, "Cari rüzgâr")
    pc = yen_cari[1] * 100
    sb.tek_paragraf(2, "TextBox 57",
                    f"2016’da {yuzde(yen16[1])} olan yenilenebilir enerjinin toplam elektrik kurulu gücü içindeki payı, "
                    f"{yil} {ay_adi} sonu itibarıyla {yuzde(yen_cari[1])}{ek_yonelme(pc)} yükselmiştir.")
    _elektrik_grafigi(sb, 2, "Chart 40", s2, par, [2, 3, 4, 5])
    sb.ilk_sayi(2, "TextBox 61", yuzde(ybbo_top, 1))
    sb.ilk_sayi(2, "TextBox 86", yuzde(ybbo_yen, 1))
    for ad, r in zip(["TextBox 63", "TextBox 64", "TextBox 65", "TextBox 66", "TextBox 68", "TextBox 69", "TextBox 70",
                      "TextBox 71", "TextBox 79", "TextBox 80"], s2["yillik"]):
        sb.ilk_sayi(2, ad, tr(r[1], 1))
    sb.ilk_sayi(2, "TextBox 43", tr(s2["onceki"][1], 1))
    sb.ilk_sayi(2, "TextBox 41", tr(s2["cari"][1], 1))
    sb.ilk_sayi(2, "TextBox 94", yuzde(yen16[1]))
    sb.ilk_sayi(2, "TextBox 95", tr(yen16[2], 1))
    sb.ilk_sayi(2, "TextBox 98", yuzde(yen_cari[1]))
    sb.ilk_sayi(2, "Oval 85", yuzde(yen_cari[1]))
    sb.ilk_sayi(2, "TextBox 99", tr(yen_cari[2], 1))
    kutu = "Rectangle: Rounded Corners 42"
    sb.calistirma(2, kutu, 0, 0, r"\d{4} yılı \w+ sonu itibarıyla ", f"{yil} yılı {ay_adi} sonu itibarıyla ")
    sb.calistirma(2, kutu, 0, 2, r"[\d\.,]+ GW", f"{tr(s2['cari'][1], 1)} GW")
    sb.calistirma(2, kutu, 0, 4, r"[\d\.,]+ ", f"{tr(yen_cari[2], 1)} ")
    # run 7 ve 8: metin ve değer ayrı çalıştırmalarda
    sb.calistirma(2, kutu, 0, 8, r"%\d+ \([\d,\.]+ GW\)", f"{yuzde(gunes_cari[1])} ({tr(gunes_cari[2], 1)} GW)")
    sb.calistirma(2, kutu, 0, 10, r"%\d+ \([\d,\.]+ GW\)", f"{yuzde(ruzgar_cari[1])} ({tr(ruzgar_cari[2], 1)} GW)")
    sb.icinde(2, "TextBox 44", 0, 1, r"\(\d{2}\.\d{2}\.\d{4}\)", f"({par['ay_sonu_tarih']})")
    sb.icinde(2, "TextBox 44", 0, 1, r"\(\d{4} \d+A\)", f"({par['onceki']})")

    # ---------- Slayt 3: üretim
    s3 = k.donem_tablosu("S3_Uretim", par)
    r3 = s3["rows"]
    ybbo3_top = Kitap._bul(r3, "Toplam üretim, 2016")[1]
    ybbo3_yen = Kitap._bul(r3, "Yenilenebilir üretim, 2016")[1]
    yen16u = Kitap._bul(r3, "2016 yenilenebilir")
    yen_cariu = Kitap._bul(r3, "Cari yenilenebilir")
    pu = yen_cariu[1] * 100
    _elektrik_grafigi(sb, 3, "Chart 47", s3, par, [2, 3, 4, 5])
    sb.tek_paragraf(3, "TextBox 81",
                    f"Türkiye elektrik üretimi içerisinde yenilenebilir enerji kaynaklarından üretilen elektriğin payı "
                    f"2016 yılında {yuzde(yen16u[1])} iken, {yil} yılının {donem_ifadesi} {yuzde(yen_cariu[1])}{ek_yonelme(pu)} yükselmiştir.")
    sb.ilk_sayi(3, "TextBox 36", yuzde(ybbo3_top, 1))
    sb.ilk_sayi(3, "TextBox 37", yuzde(ybbo3_yen, 1))
    for ad, r in zip(["TextBox 52", "TextBox 53", "TextBox 54", "TextBox 55", "TextBox 56", "TextBox 57", "TextBox 58",
                      "TextBox 59", "TextBox 60", "TextBox 45"], s3["yillik"]):
        sb.ilk_sayi(3, ad, tr(r[1], 0))
    sb.ilk_sayi(3, "TextBox 50", tr(s3["onceki"][1], 0))
    sb.ilk_sayi(3, "TextBox 49", tr(s3["cari"][1], 0))
    sb.ilk_sayi(3, "Oval 71", yuzde(yen_cariu[1]))
    sb.ilk_sayi(3, "TextBox 97", yuzde(yen_cariu[1]))
    sb.ilk_sayi(3, "TextBox 98", tr(yen_cariu[2], 0))
    sb.ilk_sayi(3, "TextBox 68", yuzde(yen16u[1]))
    sb.ilk_sayi(3, "TextBox 69", tr(yen16u[2], 0))
    kutu = "Rectangle: Rounded Corners 46"
    sb.calistirma(3, kutu, 0, 0, r"\d{4} yılının [^\d]+ ", f"{yil} yılının {donem_ifadesi} ")
    sb.calistirma(3, kutu, 0, 2, r"[\d\.,]+ TWh", f"{tr(s3['cari'][1], 0)} TWh")
    sb.calistirma(3, kutu, 0, 4, r"[\d\.,]+ ", f"{tr(yen_cariu[2], 0)} ")
    sb.calistirma(3, kutu, 0, 8, r"%\d+ ", f"{yuzde(yen_cariu[1])} ")
    sb.icinde(3, "TextBox 61", 0, 1, r"Ocak-\w+ \d{4}|Ocak \d{4}", ocak_ay)

    # ---------- Slayt 4: kaynak dağılımı
    tablo4 = k.kaynak_tablosu()
    kaynaklar = tablo4[:-1]
    toplam4 = tablo4[-1]
    if len(kaynaklar) != 7:
        raise UretimHatasi("Slayt 4: 7 kaynak satırı bekleniyordu.")
    en_buyuk = max(kaynaklar, key=lambda r: r[2])
    kisa_ad = {"HES": "HES", "Kömür": "kömür", "Doğal gaz": "doğal gaz", "Rüzgâr": "rüzgâr", "Güneş": "güneş",
               "Diğer": "diğer", "Diğer Yenilenebilir": "diğer yenilenebilir"}
    en_ad = re.sub(r" \(.*\)", "", str(en_buyuk[0]))
    sb.calistirma(4, "Title 2", 0, 1, r" \d{4} Yılı Kaynak Dağılımı", f" {yil} Yılı Kaynak Dağılımı")
    sb.calistirma(4, "TextBox 10", 0, 0, r"\d{4} yılının [^\d]+toplam üretim [\d,\.]+ ",
                  f"{yil} yılının {donem_ifadesi} toplam üretim {tr(toplam4[1] / 1000, 1)} ")
    sb.calistirma(4, "TextBox 10", 0, 2, r" seviyesinde gerçekleşirken en büyük üretim payı %[\d,]+ ile .+ kaynaklarından gelmiştir\.",
                  f" seviyesinde gerçekleşirken en büyük üretim payı {yuzde(en_buyuk[2], 1)} ile {kisa_ad.get(en_ad, en_ad)} kaynaklarından gelmiştir.")
    sol = [("Text 13", "Text 15"), ("Text 19", "Text 21"), ("Text 25", "Text 27"), ("Text 31", "Text 33"),
           ("Text 37", "Text 39"), ("Text 43", "Text 45"), ("Text 49", "Text 51")]
    sag = ["Text 63", "Text 67", "Text 71", "Text 75", "Text 79", "Text 83", "Text 87"]
    cubuk = ["Shape 62", "Shape 66", "Shape 70", "Shape 74", "Shape 78", "Shape 82", "Shape 86"]
    iz = sb.bul(4, "Shape 61").width
    for (gwh_ad, pay_ad), sag_ad, cubuk_ad, r in zip(sol, sag, cubuk, kaynaklar):
        sb.ilk_sayi(4, gwh_ad, tr(r[1], 0))
        sb.ilk_sayi(4, pay_ad, yuzde(r[2], 1))
        sb.ilk_sayi(4, sag_ad, yuzde(r[2], 1))
        sb.genislik(4, cubuk_ad, iz * float(r[3]))
    sb.ilk_sayi(4, "Text 55", tr(toplam4[1], 0))

    # ---------- Slayt 5: tüketim
    s5 = k.donem_tablosu("S5_Tuketim", par)
    ybbo5 = Kitap._bul(s5["rows"], "Brüt talep, 2016")[1]
    yillik5 = s5["yillik"]
    if len(yillik5) != 10:
        raise UretimHatasi("Slayt 5: şablon 10 yıllık sütun için kurulmuş.")
    kat5 = {i: str(r[0]).strip() for i, r in enumerate(yillik5)}
    kat5[11], kat5[12] = par["onceki"], par["cari"]
    deg5 = {i: float(r[2]) for i, r in enumerate(yillik5)}
    deg5[11], deg5[12] = float(s5["onceki"][2]), float(s5["cari"][2])
    sb.grafik(5, "Chart 37", kat5, [deg5])
    sb.ilk_sayi(5, "TextBox 49", yuzde(ybbo5, 1))
    sb.icinde(5, "TextBox 51", 0, 1, r"Ocak-\w+ \d{4}|Ocak \d{4}", ocak_ay)

    # ---------- Slayt 6: iletim ağı
    il = k.iletim()

    def ara(onek: str):
        r = [v for kk, v in il.items() if kk.startswith(onek)]
        if len(r) != 1:
            raise UretimHatasi(f"D1_Iletim: '{onek}' satırı {len(r)} kez bulundu.")
        return r[0]

    ac = ara("AC iletim hattı")
    trafo = ara("Yüksek gerilim trafo")
    sb.calistirma(6, "TextBox 192", 0, 0, r"\d{4} Yılında AC Şebekesi", f"{int(ac[2])} Yılında AC Şebekesi")
    sb.calistirma(6, "TextBox 192", 1, 1, r"[\d\.]+ km", f"{tr(ac[1], 0)} km")
    sb.calistirma(6, "TextBox 192", 2, 1, r"[\d\.]+", tr(trafo[1], 0))
    sb.calistirma(6, "TextBox 193", 1, 1, r"[\d\.]+ km", f"{tr(ara('2035 AC hat')[1], 0)} km")
    sb.calistirma(6, "TextBox 193", 2, 1, r"[\d\.]+", tr(ara("2035 AC trafo")[1], 0))
    sb.calistirma(6, "TextBox 191", 1, 1, r"[\d\.]+ GW", f"{tr(ara('2035 HVDC koridor')[1], 0)} GW")
    sb.calistirma(6, "TextBox 191", 2, 1, r"[\d\.]+ km", f"{tr(ara('2035 HVDC hat')[1], 0)} km")
    sb.calistirma(6, "TextBox 191", 3, 1, r"[\d\.]+", tr(ara("2035 HVDC çevirici")[1], 0))
    sb.calistirma(6, "TextBox 406", 0, 0, r"\d+", tr(ara("2035'e kadar")[1], 0))

    # ---------- Slayt 7: ön lisanslar (1/3)
    ol = k.onlisans()
    yillar7 = ol["yillar"]
    if len(yillar7) != 3:
        raise UretimHatasi("Slayt 7: şablon 3 başlangıç yılı için kurulmuş.")
    kat7 = {i: str(int(r[0])) for i, r in enumerate(yillar7)}
    sb.grafik(7, "Chart 12", kat7, [{i: round(float(r[3]), 1) for i, r in enumerate(yillar7)}])
    sb.grafik(7, "Chart 15", kat7, [{i: float(r[4]) for i, r in enumerate(yillar7)},
                                    {i: float(r[5]) for i, r in enumerate(yillar7)}])
    top = ol["toplam"]
    sb.grafik(7, "Chart 42", {}, [{0: float(top[4]), 1: float(top[5])}])
    for ad in ("Flowchart: Connector 53", "Flowchart: Connector 57"):
        sb.calistirma(7, ad, 1 if ad.endswith("53") else 0, 0, r"[\d,\.]+ GW", f"{tr(top[3], 1)} GW")
    sb.calistirma(7, "Callout: Line 58", 0, 0, r"[\d,\.]+ GW RES", f"{tr(top[2], 1)} GW RES")
    sb.calistirma(7, "Callout: Line 59", 0, 0, r"[\d,\.]+ GW GES", f"{tr(top[1], 1)} GW GES")
    adet = ol["adet"]
    ges_buyuk = float(top[1]) > float(top[2])
    p43 = "TextBox 43"
    sb.icinde(7, p43, 0, 0, r"\d+ adet", f"{int(adet[3])} adet")
    sb.calistirma(7, p43, 0, 1, r"(RES|GES)'ler", "GES'ler" if ges_buyuk else "RES'ler")
    sb.calistirma(7, p43, 0, 3, r"(RES|GES)'lerin", "RES'lerin" if ges_buyuk else "GES'lerin")
    kutular = [("Kalyon", "Rectangle: Rounded Corners 65", "Rectangle: Rounded Corners 66", "Rectangle: Rounded Corners 35"),
               ("Entek", "Rectangle: Rounded Corners 67", "Rectangle: Rounded Corners 68", "Rectangle: Rounded Corners 36"),
               ("Aksa", "Rectangle: Rounded Corners 69", "Rectangle: Rounded Corners 70", "Rectangle: Rounded Corners 37"),
               ("Enerjisa", "Rectangle: Rounded Corners 71", "Rectangle: Rounded Corners 72", "Rectangle: Rounded Corners 38")]
    firmalar = {str(r[0]).strip(): r for r in ol["firmalar"]}
    for firma, ges_ad, res_ad, top_ad in kutular:
        r = firmalar[firma]
        sb.ilk_sayi(7, ges_ad, tr(r[1], 0))
        sb.ilk_sayi(7, res_ad, tr(r[2], 0))
        sb.ilk_sayi(7, top_ad, tr(r[3], 0))

    # ---------- Slayt 9: ön lisans takvimi
    tk = k.takvim()
    if len(tk["yillar"]) != 4:
        raise UretimHatasi("Slayt 9: şablon 4 bitiş yılı için kurulmuş.")
    for tablo_ad, adet_i, mwe_i, top_adet, top_mwe in (("Table 40", 1, 2, tk["toplam"][1], tk["toplam"][2]),
                                                        ("Table 45", 3, 4, tk["toplam"][3], tk["toplam"][4])):
        for i, r in enumerate(tk["yillar"], start=1):
            sh = sb.bul(9, tablo_ad)
            eski_yil = sh.table.cell(i, 0).text_frame.paragraphs[0].runs[0].text
            sb.hucre(9, tablo_ad, i, 0, re.sub(r"\d{4}", str(int(r[0])), eski_yil))
            a, m = r[adet_i], r[mwe_i]
            sb.hucre(9, tablo_ad, i, 1, "-" if not a else tr(a, 0))
            sb.hucre(9, tablo_ad, i, 2, "-" if not m else tr(m, 0))
        sb.hucre(9, tablo_ad, 5, 1, tr(top_adet, 0))
        sb.hucre(9, tablo_ad, 5, 2, tr(top_mwe, 0))
    pg, pr = tk["pay_ges"] * 100, tk["pay_res"] * 100
    sb.tek_paragraf(9, "TextBox 13",
                    f"Mevcut ön lisans takvimine göre, depolamalı GES kapasitesinin yaklaşık %{tr(pg)}{ek_iyelik_tamlayan(pg)[0:]}, "
                    f"depolamalı RES kapasitesinin ise yaklaşık %{tr(pr)}{ek_iyelik_tamlayan(pr)} ön lisans süresi "
                    f"{par['depo_yil']} yılı içerisinde sona erecektir.")

    # ---------- Slayt 10: işletmedeki depolama
    isl = k.isletme()
    oz = isl["ozet"]
    tp, gn, rz = oz["Toplam"], oz["Güneş"], oz["Rüzgar"]
    n_toplam, n_gunes, n_ruzgar = int(tp[2]), int(gn[2]), int(rz[2])
    sb.icinde(10, "TextBox 19", 0, 0, r"\d+ lisanslı", f"{n_toplam} lisanslı")
    sb.icinde(10, "TextBox 19", 0, 0, r"kapasitesi [\d,\.]+ ", f"kapasitesi {tr(tp[3], 1)} ")
    sb.icinde(10, "TextBox 19", 0, 2, r"ise [\d,\.]+ ", f"ise {tr(tp[4], 1)} ")
    sb.icinde(10, "TextBox 19", 0, 4, r"\d+’[iıuü] güneş, \d+’[iıuü] rüzgâr",
              f"{n_gunes}{ek_belirtme(n_gunes)} güneş, {n_ruzgar}{ek_belirtme(n_ruzgar)} rüzgâr")
    for kutu, ozet_r, n in (("Rectangle: Rounded Corners 38", gn, n_gunes), ("Rectangle: Rounded Corners 40", rz, n_ruzgar)):
        sb.calistirma(10, kutu, 0, 1, r": \d+ ", f": {n} ")
        sb.calistirma(10, kutu, 0, 9, r" [\d,\.]+ MWh,", f" {tr(ozet_r[3], 1)} MWh,")
        sb.calistirma(10, kutu, 1, 7, r" [\d,\.]+ ", f" {tr(ozet_r[4], 1)} ")
    sb.calistirma(10, "Text 3", 0, 1, r"[\d,\.]+ ", f"{tr(tp[3], 1)} ")
    sb.calistirma(10, "Text 4", 0, 1, r"[\d,\.]+ ", f"{tr(tp[4], 1)} ")
    sb.calistirma(10, "Text 5", 0, 1, r"\d+ ", f"{isl['sirket']} ")
    sb.calistirma(10, "Text 6", 0, 1, r"Güneş: \d+", f"Güneş: {n_gunes}")
    sb.calistirma(10, "Text 6", 0, 3, r"Rüzgâr: \d+", f"Rüzgâr: {n_ruzgar}")
    if len(isl["tablo"]) < 10:
        raise UretimHatasi("Slayt 10: işletmedeki depolama tablosunda 10 satır yok.")
    for i, r in enumerate(isl["tablo"][:10]):
        taban = 12 + 5 * i
        ad = re.sub(r"A\.Ş\.?$", "A.Ş.", str(r[1]).replace("ANONİM ŞİRKETİ", "A.Ş."))
        tur = "Rüzgâr" if str(r[2]).startswith("Rüzgar") else str(r[2])
        sb.tek_paragraf(10, f"Text {taban + 1}", ad)
        sb.tek_paragraf(10, f"Text {taban + 2}", tur)
        sb.tek_paragraf(10, f"Text {taban + 3}", tr(r[3], 1))
        sb.tek_paragraf(10, f"Text {taban + 4}", tr(r[4], 1))
    sb.icinde(10, "Text 62", 0, 0, r"işletmedeki \d+ tesisten", f"işletmedeki {n_toplam} tesisten")

    # ---------- Slayt 12: PTF
    pt = k.ptf()
    d = pt["donemler"]
    yillar = [str(y) for y in range(2016, 2026)]
    if not all(y in d for y in yillar) or "2025 9A" not in d or "2026 9A" not in d:
        raise UretimHatasi("Slayt 12: PTF 2016-2025 ve 9A değerleri tam değil.")
    kat12 = {i: y for i, y in enumerate(yillar)}
    kat12[13], kat12[14] = "2025 9A", "2026 9A"
    deg12 = {i: float(d[y]) for i, y in enumerate(yillar)}
    deg12[13], deg12[14] = float(d["2025 9A"]), float(d["2026 9A"])
    sb.grafik(12, "Chart 5", kat12, [deg12])
    sb.icinde(12, "TextBox 3", 0, 0, r"%[\d,]+ seviyesinde", f"{yuzde(pt['ybbo'], 1)} seviyesinde")
    sb.calistirma(12, "Oval 8", 0, 0, r"%[\d,]+ YBBO", f"{yuzde(pt['ybbo'], 1)} YBBO")
    sb.calistirma(12, "Oval 10", 0, 0, r"-?%[\d,]+", ("-" if pt["degisim"] < 0 else "+") + yuzde(abs(pt["degisim"]), 1))

    # ---------- Slayt 13: YEKDEM
    yk = k.yekdem()
    oy = par["ortalama_yili"]
    kat13 = {0: "Taban", 1: f"{oy} Ort.", 2: "Tavan", 3: f"PTF \n({oy} Ort.)"}
    sb.grafik(13, "Chart 52", kat13, [{i: round(float(v), 2) for i, (_, v) in enumerate(yk["gunes"])}])
    sb.grafik(13, "Chart 54", kat13, [{i: round(float(v), 2) for i, (_, v) in enumerate(yk["depo"])}])
    f = yk["formul"]
    for ad, anahtar in (("Rectangle: Rounded Corners 69", "ÜFE"), ("Rectangle: Rounded Corners 70", "TÜFE"),
                        ("Rectangle: Rounded Corners 71", "Dolar/TL"), ("Rectangle: Rounded Corners 72", "Euro/TL")):
        sb.calistirma(13, ad, 0, 0, r"%\d+", yuzde(f[anahtar]))
    sb.calistirma(13, "Rectangle: Rounded Corners 73", 0, 0, r"\d+ Yıl", f"{int(yk['sure']['yekdem'])} Yıl")
    sb.calistirma(13, "Rectangle: Rounded Corners 73", 1, 0, r"\(\d{4}-\d{4}\)", f"({yk['sure']['ilk']}-{yk['sure']['son']})")
    sb.icinde(13, "Rectangle: Rounded Corners 96", 0, 0, r"[\d,\.]+", tr(yk["katki"]["Güneş"], 2))
    sb.icinde(13, "Rectangle: Rounded Corners 104", 0, 0, r"[\d,\.]+", tr(yk["katki"]["Elektrik Depolama"], 2))
    sb.calistirma(13, "Rectangle: Rounded Corners 126", 0, 0, r"\d+ Yıl", f"{int(yk['sure']['aksam_gunes'])} Yıl")
    sb.calistirma(13, "Rectangle: Rounded Corners 128", 0, 0, r"\d+ Yıl", f"{int(yk['sure']['aksam_depo'])} Yıl")


def uret(kitap: Path, sablon: Path, cikti: Path, zorla: bool = False) -> Path:
    with tempfile.TemporaryDirectory() as gecici:
        hesapli = hesapla(kitap, Path(gecici))
        k = Kitap(hesapli)
        tamam, durum = k.kontrol_tamam()
        if not tamam and not zorla:
            raise UretimHatasi(f"Kitaptaki genel kontrol '{durum}'. Önce kitabı düzeltin (Kontrol sayfası). "
                               "Zorla üretmek için --zorla kullanın.")
        par = k.parametre()
        sb = Sablon(sablon)
        doldur(sb, k, par)
        cikti.parent.mkdir(parents=True, exist_ok=True)
        sb.kaydet(cikti)
    return cikti


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kitap", type=Path, default=VARSAYILAN_KITAP)
    ap.add_argument("--sablon", type=Path, default=VARSAYILAN_SABLON)
    ap.add_argument("--cikti", type=Path, default=None)
    ap.add_argument("--zorla", action="store_true", help="Kontrol UYARI verse de üret")
    a = ap.parse_args()
    cikti = a.cikti
    if cikti is None:
        with tempfile.TemporaryDirectory() as g:
            par = Kitap(hesapla(a.kitap, Path(g))).parametre()
        cikti = KOK / "cikti" / f"Enerji_Sektoru_Sunum_{par['yil']}-{par['ay']:02d}.pptx"
    print("Üretildi:", uret(a.kitap, a.sablon, cikti, a.zorla))


if __name__ == "__main__":
    main()
