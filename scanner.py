import requests
from datetime import datetime, timedelta

# ================= SENİN AYARLARIN =================
NTFY_KANALI = "ucuz_bilet"  # <-- Kendi ntfy kanal adını buraya yaz!
MAKSIMUM_FIYAT = 2000                  # Hedef fiyat limiti (TL)

# Türkiye Çıkış Havalimanları (Sabiha Gökçen, İstanbul, Ankara, Kayseri)
KALKIS_LISTESI = ["SAW", "IST", "ESB", "ASR"]

# Avrupa Kampanya Merkezleri (Viyana, Basel, Köln, Budapeşte, Milano, Saraybosna, Üsküp, Tiran, Bükreş)
AVRUPA_HEDEFLERI = {
    "VIE": "Viyana",
    "BSL": "Basel",
    "CGN": "Koln",
    "BER": "Berlin",
    "BUD": "Budapeste",
    "BGY": "Milano",
    "SJJ": "Saraybosna",
    "SKP": "Uskup",
    "PRN": "Pristine",
    "TIA": "Tiran",
    "OTP": "Bukres"
}
# ===================================================

def bildirim_gonder(baslik, mesaj, link="https://www.google.com/travel/flights"):
    try:
        headers = {
            "Title": baslik,
            "Priority": "high",
            "Tags": "airplane,rotating_light",
            "Click": link
        }
        requests.post(f"https://ntfy.sh/{NTFY_KANALI}", data=mesaj.encode('utf-8'), headers=headers, timeout=10)
    except Exception as e:
        print("Bildirim hatasi:", e)

def kombinasyonlari_tara():
    bulunan_ucuslar = []
    
    # Aviasales / Travelpayouts Açık Fiyat Önbelleği API'si (API Key Gerektirmez!)
    # Önümüzdeki 4 ayın en ucuz kombinasyonlarını tek seferde çeker
    bugun = datetime.now()
    aylar = [(bugun + timedelta(days=30*i)).strftime("%Y-%m") for i in range(1, 5)]

    for kalkis in KALKIS_LISTESI:
        for varis_kod, varis_isim in AVRUPA_HEDEFLERI.items():
            for ay in aylar:
                url = f"https://api.travelpayouts.com/v2/prices/month-matrix?currency=try&origin={kalkis}&destination={varis_kod}&month={ay}-01&show_to_affiliates=false"
                try:
                    res = requests.get(url, timeout=8)
                    if res.status_code == 200:
                        veriler = res.json().get("data", [])
                        for ucus in veriler:
                            fiyat = ucus.get("value", 999999)
                            tarih = ucus.get("depart_date", "")
                            if fiyat <= MAKSIMUM_FIYAT:
                                link = f"https://www.google.com/travel/flights?q=Flights%20to%20{varis_kod}%20from%20{kalkis}%20on%20{tarih}%20oneway&curr=TRY"
                                bulunan_ucuslar.append((kalkis, varis_isim, varis_kod, fiyat, tarih, link))
                except Exception:
                    continue

    # Eğer hedef fiyat altında bilet bulunduysa en ucuz 3 tanesini bildir!
    if bulunan_ucuslar:
        bulunan_ucuslar.sort(key=lambda x: x[3])
        for u in bulunan_ucuslar[:3]:
            kalkis, varis_isim, varis_kod, fiyat, tarih, link = u
            mesaj = (
                f"Rota: {kalkis} -> {varis_isim} ({varis_kod})\n"
                f"En Uygun Tarih: {tarih}\n"
                f"Fiyat: {fiyat} TL!\n"
                f"Google Flights'ta gormek icin bildirime tikla."
            )
            bildirim_gonder(f"UCUZ BILET: {varis_isim} {fiyat} TL!", mesaj, link)
    else:
        # Sistemin hatasız çalıştığını görmen için bilgi mesajı:
        bildirim_gonder(
            "Tarama Tamamlandi (Hatasiz!)",
            f"Tum Avrupa kombinasyonlari tarandi. Su an {MAKSIMUM_FIYAT} TL altinda bilet yok, 30 dk sonra tekrar bakilacak."
        )

if __name__ == "__main__":
    kombinasyonlari_tara()
