# Enerji Atlası

Enerji sektörüne ilişkin verileri görselleştiren Streamlit tabanlı web portalı.

## Proje yapısı

```
app.py            Giriş sayfası
pages/            Diğer sayfalar (Streamlit çok sayfalı yapısı)
src/energyatlas/  Veri okuma ve iş mantığı (Streamlit'e bağımlı değil)
data/             Veri dosyaları
config.py         Ayarlar (ortam değişkenlerinden okunur)
tests/            Testler
```

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
streamlit run app.py
```

## Testler

```bash
pytest
```

## Ayarlar

| Ortam değişkeni    | Varsayılan            | Açıklama                 |
|--------------------|-----------------------|--------------------------|
| `ENERJI_DATA_DIR`  | `<proje>/data`        | Veri dosyalarının klasörü |
| `ENERJI_APP_TITLE` | `Enerji Atlası`       | Uygulama başlığı         |

> `data/uretim_ornek.csv` örnek veridir; gerçek veriler hazır olduğunda değiştirilecektir.
