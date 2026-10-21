import os
import requests
from datetime import datetime, timedelta

# ==========================================
# KONFIGURASYON
# ==========================================
# Telefondaki ntfy uygulamasinda actigin kanal adini yaz
NTFY_CHANNEL = "ucuz_bilet" 
NTFY_URL = f"https://ntfy.sh/{NTFY_CHANNEL}"

# Tarama Parametreleri
ORIGIN = "SAW"           # Istanbul Sabiha Gokcen
DESTINATIONS = ["SJJ", "SKP", "PRN", "TIA", "CGN", "STR", "ATH", "AUH"] # Hedef Havalimanlari
MAX_PRICE_TRY = 7000     # Maksimum Gidis-Donus Butcesi (TL)

def send_notification(title, message):
    """
    ntfy servisine güvenli, emojisiz metin bildirimi gonderir.
    """
    try:
        headers = {
            "Title": title.encode('utf-8')
        }
        response = requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers=headers
        )
        if response.status_code == 200:
            print(f"Bildirim gonderildi: {title}")
        else:
            print(f"Bildirim hatasi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Bildirim gonderme hatasi: {e}")

def fetch_flights_for_month(origin, dest, year_month):
    """
    Serbest bilet verisi tarama motoru. 
    Gercek senaryoda Skyscanner, Kiwi veya Amadeus API verisi cekilir.
    """
    found_deals = []
    
    # Ornek: API/Kazima Entegrasyonu
    # Bu kisim ilgili ucus servisinin ucuz bilet endpoint'ine baglanir.
    # Limit alti bilet bulundugunda listeye eklenir:
    # Example format: {"dest": dest, "date": year_month, "price": 4200}
    
    return found_deals

def scan_flights():
    bugun = datetime.now()
    
    # Bugunden itibaren Eylul 2027 dahil 11 aylik periyot
    aylar = [(bugun + timedelta(days=30*i)).strftime("%Y-%m") for i in range(1, 12)]
    
    bulunan_firsatlar = []

    print(f"Tarama basliyor... Toplam {len(aylar)} ay taranacak.")

    for dest in DESTINATIONS:
        for ay in aylar:
            deals = fetch_flights_for_month(ORIGIN, dest, ay)
            if deals:
                bulunan_firsatlar.extend(deals)

    # Eger limit alti bilet bulunduysa detayli bildirim at
    if bulunan_firsatlar:
        baslik = f"UCCUZ BILET BULUNDU ({len(bulunan_firsatlar)} Adet)"
        mesaj_satirlari = []
        for deal in bulunan_firsatlar[:5]: # Ilk 5 en ucuz bilet
            mesaj_satirlari.append(f"Rota: {ORIGIN} -> {deal['dest']} | Tarih: {deal['date']} | Fiyat: {deal['price']} TL")
        
        mesaj = "\n".join(mesaj_satirlari)
        send_notification(baslik, mesaj)
    else:
        # Firsat bulunamadiginda konsola yazar, telefona gereksiz bildirim atmaz
        print("7000 TL altinda yeni bir bilet bulunamadi.")

if __name__ == "__main__":
    scan_flights()
