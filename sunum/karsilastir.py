"""İki sunumu (şablon ve üretilen) metin, tablo, grafik ve şekil geometrisi bakımından karşılaştırır."""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation

C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"


def _sekiller(sekiller, yol=""):
    for sh in sekiller:
        if sh.shape_type == 6:
            yield from _sekiller(sh.shapes, yol + sh.name + "/")
        else:
            yield yol + sh.name, sh


def ozet(yol: Path) -> dict:
    prs = Presentation(str(yol))
    sonuc = {"metin": {}, "geometri": {}, "grafik": {}, "tablo": {}}
    for i, slayt in enumerate(prs.slides, 1):
        sayac: dict[str, int] = {}
        for ad, sh in _sekiller(slayt.shapes):
            sayac[ad] = sayac.get(ad, 0) + 1
            anahtar = (i, ad, sayac[ad])
            sonuc["geometri"][anahtar] = (sh.left, sh.top, sh.width, sh.height)
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                sonuc["metin"][anahtar] = [[r.text for r in p.runs] for p in sh.text_frame.paragraphs]
            if getattr(sh, "has_table", False) and sh.has_table:
                sonuc["tablo"][anahtar] = [[c.text for c in r.cells] for r in sh.table.rows]
            if getattr(sh, "has_chart", False) and sh.has_chart:
                cs = sh.chart._chartSpace
                seriler = []
                for ser in cs.xpath(".//c:ser"):
                    cat = {int(pt.get("idx")): pt[0].text for pt in ser.xpath("./c:cat//c:pt")}
                    val = {int(pt.get("idx")): float(pt[0].text) for pt in ser.xpath("./c:val//c:pt")}
                    seriler.append((cat, val))
                sonuc["grafik"][anahtar] = seriler
    return sonuc


def karsilastir(a: Path, b: Path, cubuk_toleransi: float = 0.01, deger_toleransi: float = 5e-4) -> list[str]:
    """Farkları metin olarak döndürür. Boş liste: iki sunum aynı."""
    x, y = ozet(a), ozet(b)
    farklar = []
    for tur in ("metin", "tablo"):
        for k in sorted(set(x[tur]) | set(y[tur])):
            if x[tur].get(k) != y[tur].get(k):
                farklar.append(f"{tur} slayt {k[0]} {k[1]}: {x[tur].get(k)!r} -> {y[tur].get(k)!r}")
    for k in sorted(set(x["geometri"]) | set(y["geometri"])):
        ga, gb = x["geometri"].get(k), y["geometri"].get(k)
        if ga is None or gb is None:
            farklar.append(f"şekil slayt {k[0]} {k[1]}: yalnız birinde var")
            continue
        if ga[:2] != gb[:2] or ga[3] != gb[3]:
            farklar.append(f"konum/yükseklik slayt {k[0]} {k[1]}: {ga} -> {gb}")
        elif ga[2] != gb[2] and abs(ga[2] - gb[2]) > cubuk_toleransi * max(ga[2], 1):
            farklar.append(f"genişlik slayt {k[0]} {k[1]}: {ga[2]} -> {gb[2]}")
    for k in sorted(set(x["grafik"]) | set(y["grafik"])):
        sa, sb = x["grafik"].get(k), y["grafik"].get(k)
        if sa is None or sb is None or len(sa) != len(sb):
            farklar.append(f"grafik slayt {k[0]} {k[1]}: seri sayısı farklı")
            continue
        for n, ((ca, va), (cb, vb)) in enumerate(zip(sa, sb)):
            if ca != cb:
                farklar.append(f"grafik kategori slayt {k[0]} {k[1]} seri {n}: {ca} -> {cb}")
            for idx in sorted(set(va) | set(vb)):
                u, v = va.get(idx), vb.get(idx)
                if u is None or v is None or abs(u - v) > deger_toleransi * max(abs(u), 1e-9):
                    farklar.append(f"grafik değer slayt {k[0]} {k[1]} seri {n} nokta {idx}: {u} -> {v}")
    return farklar


if __name__ == "__main__":
    f = karsilastir(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{len(f)} fark")
    for satir in f:
        print(" -", satir)
