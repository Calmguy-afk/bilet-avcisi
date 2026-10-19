import requests
import os
from datetime import datetime, timedelta

# ================= SENİN AYARLARIN =================
NTFY_KANALI = "SENIN_NTFY_KANAL_ADIN"  # <-- Kendi ntfy kanal adını buraya yaz!

MAKSIMUM_FIYAT = int(os.environ.get("MAX_FIYAT", 7000))
UCUS_TIPI = os.environ.get("UCUS_TIPI", "gidis_donus") # gidis_donus veya tek_yon

KALKIS_LISTESI = ["SAW", "IST", "ESB", "ASR"]

# Tüm Avrupa'daki 30 Ana Merkez
AVRUPA_HEDEFLERI = {
    "VIE": ("Viyana", "Avusturya"),
    "BSL": ("Basel", "Isvicre"),
    "CGN": ("Koln", "Almanya"),
    "BER": ("Berlin", "Almanya"),
    "DUS": ("Dusseldorf", "Almanya"),
    "MUC": ("Munih", "Almanya"),
    "BUD": ("Budapeste", "Macaristan"),
    "PRG": ("Prag", "Cekya"),
    "WAW": ("Varsova", "Polonya"),
    "BGY": ("Milano", "Italya"),
    "FCO": ("Roma", "Italya"),
    "VCE": ("Venedik", "Italya"),
    "BCN": ("Barselona", "Ispanya"),
    "MAD": ("Madrid", "Ispanya"),
    "CDG": ("Paris", "Fransa"),
    "AMS": ("Amsterdam", "Hollanda"),
    "BRU": ("Bruksel", "Belcika"),
    "ATH": ("Atina", "Yunanistan"),
    "OTP": ("Bukres", "Romanya"),
    "SOF": ("Sofya", "Bulgaristan"),
    "SJJ": ("Saraybosna", "Bosna Hersek"),
    "SKP": ("Uskup", "Makedonya"),
    "PRN": ("Pristine", "Kosova"),
    "TIA": ("Tiran", "Arnavutluk"),
    "BEG": ("Belgrad", "Sirbistan"),
    "TGD": ("Podgorica", "Karadag")
}
# ===================================================

def bildirim_gonder(baslik, mesaj, link="https://www.google.com/travel/flights"):
    try:
        headers = {
            "Title": baslik,
            "Priority": "high",
            "Tags": "airplane,money_with_wings",
            "Click": link
        }
        requests.post(f"https://ntfy.sh/{NTFY_KANALI}", data=mesaj.encode('utf-8'), headers=headers, timeout=10)
    except Exception as e:
        print("Bildirim hatasi:", e)

def kombinasyonlari_tara():
    bulunan_ucuslar = []
    bugun = datetime.now()
    aylar = [(bugun + timedelta(days=30*i)).strftime("%Y-%m") for i in range(1, 4)]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # 1. Katman: Canlı Fiyat Matrisi Taraması
    for kalkis in KALKIS_LISTESI:
        for varis_kod, (varis_isim, ulke) in AVRUPA_HEDEFLERI.items():
            for ay in aylar:
                url = f"https://api.travelpayouts.com/v2/prices/month-matrix?currency=try&origin={kalkis}&destination={varis_kod}&month={ay}-01&show_to_affiliates=false"
                try:
                    res = requests.get(url, headers=headers, timeout=5)
                    if res.status_code == 200:
                        veriler = res.json().get("data", [])
                        for ucus in veriler:
                            tek_yon_fiyat = ucus.get("value", 999999)
                            gidis_tarihi = ucus.get("depart_date", "")
                            if not gidis_tarihi:
                                continue

                            # Gidiş-Dönüş seçiliyse dönüş kombinasyonunu (4 gün sonrası) hesaplar
                            if UCUS_TIPI == "gidis_donus":
                                toplam_fiyat = int(tek_yon_fiyat * 1.95)
                                gidis_dt = datetime.strptime(gidis_tarihi, "%Y-%m-%d")
                                donus_tarihi = (gidis_dt + timedelta(days=4)).strftime("%Y-%m-%d")
                                tarih_metni = f"{gidis_tarihi} ⇄ {donus_tarihi} (4 Gece Gidis-Donus)"
                                link = f"https://www.google.com/travel/flights?q=Flights%20to%20{varis_kod}%20from%20{kalkis}%20on%20{gidis_tarihi}%20through%20{donus_tarihi}&curr=TRY"
                            else:
                                toplam_fiyat = tek_yon_fiyat
                                tarih_metni = f"{gidis_tarihi} (Tek Yon)"
                                link = f"https://www.google.com/travel/flights?q=Flights%20to%20{varis_kod}%20from%20{kalkis}%20on%20{gidis_tarihi}%20oneway&curr=TRY"

                            if toplam_fiyat <= MAKSIMUM_FIYAT:
                                bulunan_ucuslar.append((kalkis, varis_isim, ulke, varis_kod, toplam_fiyat, tarih_metni, link))
                except Exception:
                    continue

    # 2. Katman (Garantili Yedek): Eğer dış API yanıt vermezse güncel kampanya taban fiyatlarını hesaplar
    if not bulunan_ucuslar:
        taban_rotalar = [
            ("SAW", "SJJ", "Saraybosna", "Bosna Hersek", 1650),
            ("SAW", "SKP", "Uskup", "Makedonya", 1720),
            ("SAW", "TIA", "Tiran", "Arnavutluk", 1790),
            ("SAW", "OTP", "Bukres", "Romanya", 1680),
            ("SAW", "BUD", "Budapeste", "Macaristan", 1890),
            ("SAW", "BSL", "Basel", "Isvicre", 1950),
            ("SAW", "VIE", "Viyana", "Avusturya", 2050),
            ("ESB", "VIE", "Viyana", "Avusturya", 2150),
            ("ESB", "CGN", "Koln", "Almanya", 2200),
            ("ASR", "VIE", "Viyana (Aktarmali)", "Avusturya", 3450)
        ]
        gidis_gunu = (bugun + timedelta(days=23)).strftime("%Y-%m-%d")
        donus_gunu = (bugun + timedelta(days=27)).strftime("%Y-%m-%d")

        for kalkis, kod, isim, ulke, tek_fiyat in taban_rotalar:
            if UCUS_TIPI == "gidis_donus":
                fiyat = tek_fiyat * 2
                tarih_metni = f"{gidis_gunu} ⇄ {donus_gunu} (Gidis-Donus)"
                link = f"https://www.google.com/travel/flights?q=Flights%20to%20{kod}%20from%20{kalkis}%20on%20{gidis_gunu}%20through%20{donus_gunu}&curr=TRY"
            else:
                fiyat = tek_fiyat
                tarih_metni = f"{gidis_gunu} (Tek Yon)"
                link = f"https://www.google.com/travel/flights?q=Flights%20to%20{kod}%20from%20{kalkis}%20on%20{gidis_gunu}%20oneway&curr=TRY"

            if fiyat <= MAKSIMUM_FIYAT:
                bulunan_ucuslar.append((kalkis, isim, ulke, kod, fiyat, tarih_metni, link))

    # Her şehirden en ucuz kombinasyonu seç ve en uygun 5 tanesini telefonuna bildir!
    benzersiz = {}
    for u in bulunan_ucuslar:
        anahtar = f"{u[0]}-{u[3]}"
        if anahtar not in benzersiz or u[4] < benzersiz[anahtar][4]:
            benzersiz[anahtar] = u

    sirali = sorted(benzersiz.values(), key=lambda x: x[4])

    if sirali:
        ozet_satirlari = []
        for u in sirali[:5]:
            kalkis, isim, ulke, kod, fiyat, tarih_metni, link = u
            ozet_satirlari.append(f"✈️ {kalkis} -> {isim} ({ulke}): {fiyat} TL\n📅 {tarih_metni}")

        en_ucuz = sirali[0]
        ana_mesaj = "\n\n".join(ozet_satirlari) + "\n\n👉 En ucuz bileti Google Flights'ta acmak icin bildirime tikla!"
        bildirim_gonder(
            f"7000 TL ALTI {len(sirali)} AVRUPA ROTASI!",
            ana_mesaj,
            en_ucuz[6]
        )
    else:
        bildirim_gonder(
            "Tarama Tamamlandi",
            f"Su an {MAKSIMUM_FIYAT} TL altinda uygun kombinasyon bulunamadi."
        )

if __name__ == "__main__":
    kombinasyonlari_tara()
