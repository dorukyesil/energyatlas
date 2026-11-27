"""Lisanssız elektrik üretimi: gelişim, mevzuat, kurulu güç, yönetmelik ve hesaplamalar."""

from src.energyatlas import ui

ui.sayfa_basligi("Türkiye Lisanssız Elektrik Üretimi Piyasası", "Türkiye Lisanssız Elektrik Üretimi Piyasası",
                 "Gelişim süreci, mevzuat, kurulu güç, yönetmelik değişiklikleri ve ihtiyaç fazlası hesaplamaları.")
ui.geri_linki()

BOLUMLER = [
    "Gelişim süreci, neden böyle bir modele ihtiyaç var, kimler yatırım yapıyor, temel amaç: öz tüketim, bugün için kısa özet",
    "Lisanssız mevzuatının gelişimi tarihçesi",
    "Lisanssız santrallerin gelişimi, kurulu güç ve temel sürükleyiciler",
    "2 Nisan 2026 yönetmelik değişikliklerinin etkileri",
    "İhtiyaç fazlası enerji hesaplamaları: örnekler ve interaktif hesaplama seçeneği",
    "Saatlik mahsuplaşmada ihtiyaç fazlası enerji hesaplamaları: örnekler ve interaktif hesaplama seçeneği",
    "İhtiyaç fazlası enerji: aylık mahsuplaşma ve saatlik mahsuplaşma kıyaslamaları",
    "Lisanssız üretimde satış limiti",
    "YEKDEM süresi sona erecek lisanssız tesisler",
]

for no, baslik in enumerate(BOLUMLER, start=1):
    ui.yakinda(baslik, f"{no:02d}")
