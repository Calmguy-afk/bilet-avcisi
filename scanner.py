import requests
from datetime import datetime, timedelta
from fast_flights import FlightData, Passengers, Result, get_flights

# ================= SENİN AYARLARIN =================
NTFY_KANALI = "ucuz_bilet"  # <-- Kendi ntfy kanal adını buraya yaz!
MAKSIMUM_FIYAT = 2000                  # Tek yön veya kombinasyon hedef fiyat (TL)

# Türkiye Çıkış Havalimanları (Sabiha Gökçen, İstanbul, Ankara, Kayseri)
KALKIS_LISTESI = ["SAW", "IST", "ESB", "ASR"]

# Avrupa'nın En Ucuz Kampanya Merkezleri (9€-19€ biletlerin ilk düştüğü yerler)
AVRUPA_HEDEFLERI = {
    "VIE": "Viyana",
    "BSL": "Basel",
    "CGN": "Köln",
    "BUD": "Budapeşte",
    "BGY": "Milano (Bergamo)",
    "SJJ": "Saraybosna",
    "SKP": "Üsküp",
    "PRN": "Priştine"
}

# Önümüzdeki kaç gün içindeki kombinasyonlar taransın? (Örn: 15 gün sonrasından 75 gün sonrasına kadar)
BASLANGIC_GUN = 15
BITIS_GUN = 75
ADIM_GUN = 7  # Her haftanın en ucuz kombinasyonlarını tarar
# ===================================================

def bildirim_gonder(baslik, mesaj, link="https://www.google.com/travel/flights"):
    headers = {
        "Title": baslik.encode('utf-8'),
        "Priority": "high",
        "Tags": "airplane,money_with_wings",
        "Click": link
    }
    requests.post(f"https://ntfy.sh/{NTFY_KANALI}", data=mesaj.encode('utf-8'), headers=headers)

def fiyat_temizle(fiyat_str):
    if not fiyat_str:
        return 999999
    rakamlar = "".join([c for c in str(fiyat_str) if c.isdigit()])
    return int(rakamlar) if rakamlar else 999999

def google_flights_tara():
    bulunan_firsatlar = 0
    bugun = datetime.now()

    for kalkis in KALKIS_LISTESI:
        for varis_kod, varis_isim in AVRUPA_HEDEFLERI.items():
            for gun_farki in range(BASLANGIC_GUN, BITIS_GUN, ADIM_GUN):
                ucus_tarihi = (bugun + timedelta(days=gun_farki)).strftime("%Y-%m-%d")
                try:
                    result: Result = get_flights(
                        flight_data=[FlightData(date=ucus_tarihi, from_airport=kalkis, to_airport=varis_kod)],
                        trip="one-way",
                        seat="economy",
                        passengers=Passengers(adults=1),
                        fetch_mode="fallback"
                    )
                    for ucus in result.flights[:2]:
                        fiyat = fiyat_temizle(ucus.price)
                        if fiyat <= MAKSIMUM_FIYAT:
                            bulunan_firsatlar += 1
                            link = f"https://www.google.com/travel/flights?q=Flights%20to%20{varis_kod}%20from%20{kalkis}%20on%20{ucus_tarihi}%20oneway"
                            mesaj = (
                                f"Rota: {kalkis} -> {varis_isim} ({varis_kod})\n"
                                f"Tarih: {ucus_tarihi}\n"
                                f"Havayolu: {ucus.name}\n"
                                f"Fiyat: {fiyat} TL!\n"
                                f"Google Flights'ta gormek icin bildirime tikla."
                            )
                            bildirim_gonder(f"FIRSAT: {varis_isim} {fiyat} TL!", mesaj, link)
                except Exception as e:
                    continue

    if bulunan_firsatlar == 0:
        print("Tarama tamamlandı, şu an hedef fiyat altında bilet yok.")

if __name__ == "__main__":
    # İlk çalıştırmada sistemin aktif olduğunu bildiren bilgi mesajı:
    bildirim_gonder(
        "Google Flights Tarayici Aktif!",
        f"API Key gerekmeden dogrudan Google Flights uzerinden {MAKSIMUM_FIYAT} TL alti Avrupa taramasi basladi!"
    )
    google_flights_tara()
