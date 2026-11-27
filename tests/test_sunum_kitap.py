"""Veri kitabından sunum üretimi: Türkçe ekler, şablonla birebir eşitlik ve hatalı kitapta üretimin reddi."""

import shutil
import tempfile
from pathlib import Path

import openpyxl
import pytest

from sunum import karsilastir, uret

KITAP = uret.VARSAYILAN_KITAP
SABLON = uret.VARSAYILAN_SABLON
soffice_var = shutil.which("soffice") is not None


def test_turkce_ekler():
    assert uret.ek_yonelme(63) == "’e"      # %63’e
    assert uret.ek_yonelme(59) == "’a"      # %59’a
    assert uret.ek_yonelme(62) == "’ye"     # %62’ye
    assert uret.ek_yonelme(60) == "’a"      # %60’a
    assert uret.ek_yonelme(6) == "’ya"
    assert uret.ek_iyelik_tamlayan(15) == "’inin"   # %15’inin
    assert uret.ek_iyelik_tamlayan(17) == "’sinin"  # %17’sinin
    assert uret.ek_belirtme(11) == "’i"     # 11’i
    assert uret.ek_belirtme(3) == "’ü"      # 3’ü
    assert uret.ek_belirtme(2) == "’yi"


def test_sayi_bicimi():
    assert uret.tr(127.85, 1) == "127,9"
    assert uret.tr(91079.5, 0) == "91.080"      # yarım yukarı
    assert uret.yuzde(0.2942, 1) == "%29,4"
    assert uret.yuzde(0.6301) == "%63"
    assert uret.tr(1532.3, 0) == "1.532"


@pytest.mark.skipif(not soffice_var, reason="LibreOffice (soffice) gerekli")
def test_uretilen_sunum_sablonla_ayni():
    """Kitap değişmediğinde üretilen sunum şablonla aynı olmalı (tek bilinçli fark: Oval 85 artık metni)."""
    with tempfile.TemporaryDirectory() as g:
        cikti = uret.uret(KITAP, SABLON, Path(g) / "uretim.pptx")
        farklar = karsilastir.karsilastir(SABLON, cikti)
    beklenmeyen = [f for f in farklar if "Oval 85" not in f]
    assert not beklenmeyen, "\n".join(beklenmeyen)


@pytest.mark.skipif(not soffice_var, reason="LibreOffice (soffice) gerekli")
def test_hatali_kitapta_uretim_reddedilir():
    """Rapor ayı verisi olmayan bir aya çekilirse Kontrol UYARI verir ve sunum üretilmez."""
    with tempfile.TemporaryDirectory() as g:
        bozuk = Path(g) / "bozuk.xlsx"
        wb = openpyxl.load_workbook(KITAP)
        wb["Parametre_Elk"]["B5"] = 12   # Girdi_Aylik'te Aralık 2026 yok
        wb.save(bozuk)
        with pytest.raises(uret.UretimHatasi):
            uret.uret(bozuk, SABLON, Path(g) / "cikti.pptx")
