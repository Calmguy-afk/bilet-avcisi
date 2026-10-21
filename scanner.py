import os
import requests
from datetime import datetime, timedelta

# NTFY Konfigürasyonu
# Lütfen telefondaki ntfy uygulamasında açtığın kanal adını yaz.
NTFY_CHANNEL = "ucuz_bilet" 
NTFY_URL = f"https://ntfy.sh/{NTFY_CHANNEL}"

# Taranacak Havalimanları ve Bütçe Limiti
ORIGIN = "SAW"          # İstanbul Sabiha Gökçen
DESTINATIONS = ["SJJ", "SKP", "PRN", "TIA", "CGN", "STR", "ATH", "AUH"] # Örnek rotalar
MAX_PRICE_TRY = 7000    # Gidiş-Dönüş Maksimum Bütçe (TL)

def send_notification(title, message):
    """
    ntfy servisine emojiziz, sade metin bildirimi gönderir.
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
            print("Bildirim basariyla gonderildi.")
        else:
            print(f"Bildirim hatasi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Bildirim gonderme sirasinda hata olustu: {e}")

def scan_flights():
    """
    Bugunden itibaren Eylul 2027 dahil olmak uzere 11 aylik periyodu tarar.
    """
    bugun = datetime.now()
    
    # Bugunden itibaren 11 ay sonrasina kadar olan aylari olusturur (Eylul 2027 dahil)
    aylar = [(bugun + timedelta(days=30*i)).strftime("%Y-%m") for i in range(1, 12)]
    
    firsatlar = []

    print(f"Tarama baslatildi. Taranacak aylar: {aylar}")

    for hedef in DESTINATIONS:
        for ay in aylar:
            # Burasi havayolu / seyahat API'nizden veri çeken kisimdir.
            # Temsili tarama mantigi:
            try:
                # Örnek API çağrısı veya veri kazıma simülasyonu
                # Bilet verisi bulunduğunda ucuz biletler listeye eklenir:
                pass
            except Exception as e:
                print(f"Tarama hatasi ({hedef} - {ay}): {e}")

    # Örnek bildirim testi (Kodun çalıştığını doğrulamak için)
    test_baslik = "Ucak Bileti Tarayicisi Aktif"
    test_mesaj = f"Eylul 2027 tarihine kadar olan ucuz bilet taramasi tamamlandi. Limit: {MAX_PRICE_TRY} TL"
    
    # Bildirimi gönder
    send_notification(test_baslik, test_mesaj)

if __name__ == "__main__":
    scan_flights()