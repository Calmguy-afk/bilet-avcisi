import requests
import os
from datetime import datetime, timedelta

# ================= SENİN AYARLARIN =================
NTFY_KANALI = "ucuz_bilet"  # <-- Kendi ntfy kanal adını buraya yaz!

# Telefondan girdiğin ayarları otomatik alır (Girmezsen varsayılanları kullanır)
MAKSIMUM_FIYAT = int(os.environ.get("MAX_FIYAT", 7000))
KALKIS_LISTESI = [x.strip() for x in os.environ.get("KALKIS_YERLERI", "SAW,IST,ESB,ASR").split(",")]
UCUS_TIPI = os.environ.get("UCUS_TIPI", "hepsi") # hepsi, gidis_donus, tek_yon
TARANACAK_AY_SAYISI = int(os.environ.get("AY_SAYISI", 6))

# Avrupa Kıtasındaki Tüm Ülkelerin Kodları (40+ Ülke - Hiçbir Avrupa şehri kaçmaz!)
AVRUPA_ULKELERI = {
    "AT", "BE", "BA", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", 
    "GR", "HU", "IE", "IT", "XK", "LV", "LT", "LU", "MT", "MD", "ME", "NL", 
    "MK", "NO", "PL", "PT", "RO", "RS", "SK", "SI", "ES", "SE", "CH", "GB", "AL"
}
# ===================================================

def bildirim_gonder(baslik, mesaj, link="https://www.google.com/travel/flights"):
    try:
        headers = {
            "Title": baslik,
            "Priority": "high",
            "Tags": "airplane,fire",
            "Click": link
        }
        requests.post(f"https://ntfy.sh/{NTFY_KANALI}", data=mesaj.encode('utf-8'), headers=headers, timeout=10)
    except Exception as e:
        print("Bildirim hatasi:", e)

def tum_avrupayi_tara():
    bulunan_firsatlar = []
    bugun = datetime.now()
    bitis_tarihi = bugun + timedelta(days=30 * TARANACAK_AY_SAYISI)

    for kalkis in KALKIS_LISTESI:
        # 1. TEK KOMUTLA KALKIS NOKTASINDAN DÜNYADAKİ TÜM ŞEHİRLERE EN UCUZ HARİTA VERİSİNİ ÇEKER!
        harita_url = f"https://api.travelpayouts.com/v2/prices/latest?currency=try&origin={kalkis}&period_type=year&limit=300&show_to_affiliates=false"
        try:
            res = requests.get(harita_url, timeout=12)
            if res.status_code == 200:
                ucuslar = res.json().get("data", [])
                for u in ucuslar:
                    fiyat = u.get("value", 999999)
                    varis_kod = u.get("destination", "")
                    gidis_tarih = u.get("depart_date", "")
                    donus_tarih = u.get("return_date", "")
                    aktarma = u.get("number_of_changes", 0)

                    if not gidis_tarih:
                        continue
                    
                    ucus_gunu = datetime.strptime(gidis_tarih, "%Y-%m-%d")
                    if not (bugun <= ucus_gunu <= bitis_tarihi):
                        continue

                    if fiyat <= MAKSIMUM_FIYAT:
                        tip_etiketi = "Gidis-Donus" if donus_tarih else "Tek Yon"
                        if UCUS_TIPI == "gidis_donus" and not donus_tarih:
                            continue
                        if UCUS_TIPI == "tek_yon" and donus_tarih:
                            continue

                        link = f"https://www.google.com/travel/flights?q=Flights%20to%20{varis_kod}%20from%20{kalkis}%20on%20{gidis_tarih}&curr=TRY"
                        bulunan_firsatlar.append((kalkis, varis_kod, fiyat, gidis_tarih, donus_tarih, tip_etiketi, aktarma, link))
        except Exception:
            continue

    # Tekrar edenleri temizle ve en ucuz 5 kombinasyonu bildir
    benzersiz = {}
    for f in bulunan_firsatlar:
        anahtar = f"{f[0]}-{f[1]}-{f[3]}"
        if anahtar not in benzersiz or f[2] < benzersiz[anahtar][2]:
            benzersiz[anahtar] = f

    sirali_liste = sorted(benzersiz.values(), key=lambda x: x[2])

    if sirali_liste:
        for u in sirali_liste[:4]:
            kalkis, varis_kod, fiyat, gidis, donus, tip, aktarma, link = u
            tarih_bilgisi = f"{gidis} ⇄ {donus}" if donus else f"{gidis} (Tek Yon)"
            aktarma_bilgisi = "Direkt Ucus" if aktarma == 0 else f"{aktarma} Aktarma"
            mesaj = (
                f"Rota: {kalkis} -> {varis_kod} ({aktarma_bilgisi})\n"
                f"En Uygun Kombinasyon: {tarih_bilgisi}\n"
                f"Fiyat: {fiyat} TL!\n"
                f"Google Flights'ta acmak icin bildirime tikla."
            )
            bildirim_gonder(f"AVRUPA FIRSATI: {kalkis}->{varis_kod} {fiyat} TL!", mesaj, link)
    else:
        print(f"Su an {MAKSIMUM_FIYAT} TL altinda kombinasyon yok. Sessizce bekleniyor...")

if __name__ == "__main__":
    tum_avrupayi_tara()
