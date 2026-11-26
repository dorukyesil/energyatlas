"""TEİAŞ verilerini turkiye-energy-mcp üzerinden çekip portal CSV'lerine yazar.

Bu betik görsellerden veri okumaz; yalnızca MCP'nin döndürdüğü resmi TEİAŞ tablolarını kullanır.

Kurulum (bir kez):
    git clone https://github.com/emresoykan/turkiye-energy-mcp
    cd turkiye-energy-mcp && python -m venv .venv && .venv/bin/pip install -e .

Çalıştırma (MCP ortamının Python'u ile):
    <mcp-klasörü>/.venv/bin/python scripts/teias_cek.py [--cikti data] [--baslangic 2016]

Üretilen dosyalar (data/ klasörü):
    teias_kurulu_guc.csv      yıllık kurulu güç, kaynak bazında (MW)
    teias_uretim.csv          yıllık brüt üretim, kaynak bazında (GWh)
    teias_talep.csv           yıllık brüt talep, tepe talep, ithalat, ihracat
    teias_dis_ticaret.csv     ülke bazında ithalat/ihracat (GWh)
    teias_iletim.csv          iletim hatları ve trafo istatistikleri
    teias_yenilenebilir.csv   yenilenebilir kurulu güç ve üretim payları
    teias_aylik.csv           aylık üretim ve talep (GWh), 2021'den itibaren
    teias_ytbs_kurulu_guc.csv güncel kurulu güç (YTBS, en son gün, MW)
    teias_kaynak.json         her veri setinin kaynak URL'si ve yayın tarihi
"""

import argparse
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

# YTBS verisi için herkese açık veri deposu (MCP belgelerindeki varsayılan).
os.environ.setdefault("YTBS_DATA_REPO", "emresoykan/turkiye-energy-mcp")
os.environ.setdefault("YTBS_DATA_REF", "ytbs-data")

from turkiye_energy_mcp.server import mcp  # noqa: E402


async def cagir(arac: str, **parametreler) -> dict:
    sonuc = await mcp.call_tool(arac, parametreler)
    veri = json.loads(sonuc.content[0].text)
    if veri.get("error"):
        raise RuntimeError(f"{arac}: {veri.get('code')} {veri.get('message')}")
    return veri


async def yillik(arac: str, baslangic: int, bitis: int) -> dict:
    """Son yıl henüz yayımlanmamışsa bir yıl geriye giderek çağırır."""
    for son in range(bitis, baslangic, -1):
        try:
            return await cagir(arac, start_year=baslangic, end_year=son)
        except RuntimeError:
            continue
    raise RuntimeError(f"{arac}: veri alınamadı")


def kaynak_notu(veri: dict) -> dict:
    m = veri.get("metadata", {})
    return {
        "kaynak_url": m.get("source_url"),
        "dosya": m.get("selected_source_name"),
        "yayin_tarihi": m.get("publication_date"),
        "son_donem": m.get("latest_available_period"),
        "alinma_zamani": m.get("retrieved_at"),
        "notlar": m.get("notes"),
    }


async def main(cikti: Path, baslangic: int) -> None:
    cikti.mkdir(parents=True, exist_ok=True)
    bitis = datetime.now().year
    notlar: dict[str, dict] = {}

    # 1) Kurulu güç (MW, kaynak bazında)
    v = await yillik("teias_get_installed_capacity", baslangic, bitis)
    kg = pd.DataFrame(v["data"]).pivot(index="year", columns="source", values="capacity_mw").reset_index()
    kg = kg.rename(columns={"year": "yil"})
    kg.to_csv(cikti / "teias_kurulu_guc.csv", index=False, encoding="utf-8-sig")
    notlar["kurulu_guc"] = kaynak_notu(v)

    # 2) Brüt üretim (GWh, kaynak bazında)
    v = await yillik("teias_get_generation", baslangic, bitis)
    uretim = pd.DataFrame(v["data"]).pivot(index="year", columns="source", values="generation_gwh").reset_index()
    uretim = uretim.rename(columns={"year": "yil"})
    uretim.to_csv(cikti / "teias_uretim.csv", index=False, encoding="utf-8-sig")
    notlar["uretim"] = kaynak_notu(v)

    # 3) Talep, tepe talep, ithalat/ihracat
    v_tepe = await yillik("teias_get_peak_demand", baslangic, bitis)
    v_dis = await yillik("teias_get_import_export", baslangic, bitis)
    tepe = pd.DataFrame(v_tepe["data"])
    dis = pd.DataFrame(v_dis["data"])
    # Brüt talep: üretim + ithalat - ihracat. Tepe talep tablosundaki brüt talep 2020 ve 2025'te üretime eşit
    # göründüğü için, brüt talep ithalat-ihracat tablosundan alınır (sistem özeti ile de örtüşür).
    tepe = tepe.drop(columns=["gross_demand_gwh"])
    talep = tepe.merge(
        dis[["year", "gross_demand_gwh", "imports_gwh", "exports_gwh", "net_import_gwh"]], on="year", how="left"
    ).rename(columns={"year": "yil"})
    talep.to_csv(cikti / "teias_talep.csv", index=False, encoding="utf-8-sig")
    notlar["talep"] = kaynak_notu(v_tepe)
    notlar["talep"]["notlar"] = (
        "Brüt talep = üretim + ithalat - ihracat (ithalat-ihracat tablosu). Tepe talep değerleri tepe talep tablosundandır."
    )

    # 4) Ülke bazında ithalat/ihracat
    satirlar = []
    for _, r in dis.iterrows():
        for ulke, deger in (r.get("import_by_country_gwh") or {}).items():
            satirlar.append({"yil": r["year"], "yon": "ithalat", "ulke": ulke, "gwh": deger})
        for ulke, deger in (r.get("export_by_country_gwh") or {}).items():
            satirlar.append({"yil": r["year"], "yon": "ihracat", "ulke": ulke, "gwh": deger})
    pd.DataFrame(satirlar).to_csv(cikti / "teias_dis_ticaret.csv", index=False, encoding="utf-8-sig")
    notlar["dis_ticaret"] = kaynak_notu(v_dis)

    # 5) İletim istatistikleri
    v = await yillik("teias_get_transmission_statistics", baslangic, bitis)
    pd.DataFrame(v["data"]).rename(columns={"year": "yil"}).to_csv(cikti / "teias_iletim.csv", index=False, encoding="utf-8-sig")
    notlar["iletim"] = kaynak_notu(v)

    # 6) Yenilenebilir özet
    v = await yillik("teias_get_renewable_summary", baslangic, bitis)
    pd.DataFrame(v["data"]).rename(columns={"year": "yil"}).to_csv(cikti / "teias_yenilenebilir.csv", index=False, encoding="utf-8-sig")
    notlar["yenilenebilir"] = kaynak_notu(v)

    # 7) Aylık enerji (2021'den itibaren mevcut)
    v = await cagir("teias_get_monthly_energy", start_date="2021-01-01", end_date=f"{bitis}-12-31")
    aylik = pd.DataFrame(v["data"]).pivot(index="date", columns="metric", values="value").reset_index().rename(columns={"date": "ay"})
    aylik.to_csv(cikti / "teias_aylik.csv", index=False, encoding="utf-8-sig")
    notlar["aylik"] = kaynak_notu(v)

    # 8) Güncel kurulu güç (YTBS, en son gün)
    try:
        v = await cagir("ytbs_get_installed_capacity")
        ytbs = pd.DataFrame(v["data"])
        ytbs.to_csv(cikti / "teias_ytbs_kurulu_guc.csv", index=False, encoding="utf-8-sig")
        notlar["ytbs_kurulu_guc"] = kaynak_notu(v)
    except RuntimeError as hata:
        print("YTBS atlandı:", hata)

    (cikti / "teias_kaynak.json").write_text(json.dumps(notlar, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Tamamlandı:", ", ".join(sorted(p.name for p in cikti.glob("teias_*"))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cikti", default="data")
    ap.add_argument("--baslangic", type=int, default=2016)
    args = ap.parse_args()
    asyncio.run(main(Path(args.cikti), args.baslangic))
