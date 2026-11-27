# Enerji Atlası

Türkiye ve dünya elektrik sektörünü kurulu güç, üretim, tüketim, depolama, fiyatlar ve hedefler üzerinden
gösteren Streamlit tabanlı web portalı.

## Bölümler

| Kategori | Sayfalar |
|---|---|
| Genel | Enerji Atlası (ana sayfa), Hakkında |
| Türkiye Elektrik Piyasası | Kurulu güç, üretim, tüketim (etkileyen faktörler yakında), elektrik iletim ağı (yakında), elektrik depolama piyasası (şebeke, kullanım türleri (yakında), ön lisanslar, işletmedeki depolama) |
| Türkiye Elektrik Piyasası Hedefleri ve Güncel Gelişmeler | Geçmiş ve yeni hedefler, devam eden yatırımlar; iletim ağı hedefleri ve güncel gelişmeler (yakında) |
| Türkiye Lisanssız Elektrik Üretimi Piyasası | Gelişim, mevzuat, yönetmelik değişiklikleri ve hesaplamalar (yakında) |
| Yenilenebilir Enerji Santralleri için Fiyatlandırma Mekanizmaları | EPDK tarifeleri, PTF, YEKDEM; lisanslı ve lisanssız mekanizmalar, karşılaştırma (yakında) |
| Dünya İstatistikleri | Dünya enerji görünümü (IEA WEO 2026), bölgesel ve ülke karşılaştırmaları, küresel yatırımlar |

## Proje yapısı

```
app.py              Giriş noktası: tema, gezinme menüsü ve kategoriler
views/              Her sayfa bir dosya
src/energyatlas/
  theme.py          Renk paleti, Plotly şablonu, CSS (sıcak kağıt zemin, serif başlıklar)
  ui.py             Ortak bileşenler (sayfa başlığı, bölüm, KPI şeridi, segment, veri tablosu + CSV indirme)
  charts.py         Grafik üreticileri (Streamlit'ten bağımsız)
  data.py           Veri okuma katmanı
data/               CSV veri dosyaları ve KAYNAKLAR.md (kaynak notları)
.streamlit/         Streamlit tema ayarı (config.toml)
config.py           Ayarlar (ortam değişkenleri)
tests/              Testler
```

## Kurulum ve çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Testler

```bash
pip install -r requirements-dev.txt
pytest
```

## Ayarlar

| Ortam değişkeni    | Varsayılan      | Açıklama                  |
|--------------------|-----------------|---------------------------|
| `ENERJI_DATA_DIR`  | `<proje>/data`  | Veri dosyalarının klasörü |
| `ENERJI_APP_TITLE` | `Enerji Atlası` | Uygulama başlığı          |

## Streamlit Community Cloud'a dağıtım

1. Depo herkese açık olmalı.
2. [share.streamlit.io](https://share.streamlit.io) adresinde GitHub ile giriş yapın ve **Create app** deyin.
3. Ayarlar:
   - Repository: `dorukyesil/energyatlas`
   - Branch: `claude/energyatlas-portal` (veya birleştirildikten sonra `main`)
   - Main file path: `app.py`
4. Python sürümünü 3.11 veya 3.12 olarak seçin.

Veriler depoda CSV olarak tutulur, dağıtım için ayrıca bir gizli anahtar gerekmez.

## Veri notları

Veriler resmi raporlardan ve kurum duyurularından alınmıştır. Bazı değerler grafiklerden okunmuştur.
Kullanmadan önce `data/KAYNAKLAR.md` dosyasındaki notlara bakın ve resmi kaynaktan doğrulayın.
