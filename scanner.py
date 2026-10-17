import requests
import os

# ================= SENİN AYARLARIN =================
NTFY_KANALI = "ucuz_bilet"
KALIS_YERLERI = "ASR,SAW,IST,ESB"      # Kayseri, Sabiha Gökçen, İstanbul, Ankara
VARIS_BOLGESI = "europe"               # Tüm Avrupa ("europe")
MAKSIMUM_FIYAT = 1800                  # Bu fiyatın (TL) altına düşerse alarm çalar!
TARIH_BASLANGIC = "01/11/2026"         # Hangi tarihten itibaren baksın?
TARIH_BITIS = "31/03/2027"             # Hangi tarihe kadar tüm kombinasyonları denesin?
UCUS_TIPI = "round"                    # "round" = Gidiş-Dönüş kombinasyonları | "oneway" = Tek yön
MIN_GECE = 2                           # Gidiş-dönüş arası en az kaç gece kalınsın?
MAX_GECE = 6                           # Gidiş-dönüş arası en fazla kaç gece kalınsın?
# ===================================================

API_KEY = os.environ.get("TEQUILA_API_KEY", "")

def bildirim_gonder(baslik, mesaj, link="https://www.google.com/travel/flights"):
    headers = {
        "Title": baslik.encode('utf-8'),
        "Priority": "high",
        "Tags": "airplane,rotating_light",
        "Click": link
    }
    requests.post(f"https://ntfy.sh/{NTFY_KANALI}", data=mesaj.encode('utf-8'), headers=headers)

def kombinasyonlari_tara():
    # Eğer henüz API Key bağlanmadıysa sistemin çalıştığını kanıtlamak için telefonuna TEST bildirimi atar!
    if not API_KEY:
        bildirim_gonder(
            "TEST: Sistemin Calisiyor!",
            f"Harika! Bulut robotun aktif. {KALIS_YERLERI} -> Avrupa icin {MAKSIMUM_FIYAT} TL alti bilet dustugu an buradan bildirim alacaksin!"
        )
        print("Test bildirimi gönderildi!")
        return

    # Gerçek Kombinasyon Tarama Sorgusu (Tequila Matrix API)
    url = "https://api.tequila.kiwi.com/v2/search"
    params = {
        "fly_from": KALIS_YERLERI,
        "fly_to": VARIS_BOLGESI,
        "date_from": TARIH_BASLANGIC,
        "date_to": TARIH_BITIS,
        "curr": "TRY",
        "price_to": MAKSIMUM_FIYAT,
        "flight_type": UCUS_TIPI,
        "sort": "price",
        "limit": 3
    }
    if UCUS_TIPI == "round":
        params["nights_in_dst_from"] = MIN_GECE
        params["nights_in_dst_to"] = MAX_GECE

    res = requests.get(url, headers={"apikey": API_KEY}, params=params)
    if res.status_code == 200:
        ucuslar = res.json().get("data", [])
        for u in ucuslar:
            sehir_nereden = f"{u['cityFrom']} ({u['flyFrom']})"
            sehir_nereye = f"{u['cityTo']} ({u['flyTo']})"
            fiyat = u['price']
            tarih = u['local_departure'][:10]
            gece = u.get('nightsInDest', 0)
            link = u.get('deep_link', 'https://www.kiwi.com')

            mesaj = f"Rota: {sehir_nereden} -> {sehir_nereye}\nTarih: {tarih} ({gece} Gece)\nToplam Fiyat: {fiyat} TL!\nHemen bakmak icin bildirime tikla."
            bildirim_gonder(f"UCUZ BILET: {sehir_nereye} {fiyat} TL!", mesaj, link)

if __name__ == "__main__":
    kombinasyonlari_tara()
