import requests, json, re, time, urllib3
from pathlib import Path
from bs4 import BeautifulSoup

urllib3.disable_warnings()

OUTPUT = Path(r"D:\nu\borsa\bist_semboller.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"}
TIMEOUT = 20

SYMBOL_RE = re.compile(r"^[A-Z0-9]{2,8}$")

# Master list of known BIST symbol -> company name (used for naming + fallback)
KNOWN = {
    "AEFES": "Anadolu Efes Biracilik ve Malt Sanayii A.S.", "AFYON": "Afyon Cimento Sanayi T.A.S.",
    "AGESA": "Agesa Hayat ve Emeklilik A.S.", "AGHOL": "Anadolu Grubu Holding A.S.",
    "AKBNK": "Akbank T.A.S.", "AKFGY": "Akfen Gayrimenkul Yatirim Ortakligi A.S.",
    "AKSA": "Aksa Akrilik Kimya Sanayii A.S.", "AKSEN": "Aksa Enerji Uretim A.S.",
    "AKSU": "Aksu Enerji ve Ticaret A.S.", "ALARK": "Alarko Holding A.S.",
    "ALBRK": "Albaraka Turk Katilim Bankasi A.S.", "ALFAS": "Alfa Solar Enerji Sanayi ve Ticaret A.S.",
    "ALGYO": "Alarko Gayrimenkul Yatirim Ortakligi A.S.", "ANELE": "Anele Elektrik Elektronik ve Yatirim Holding A.S.",
    "ANSGR": "Anadolu Anonim Turk Sigorta Sirketi", "ARASE": "Arabaci Enerji Sanayi ve Ticaret A.S.",
    "ARCLK": "Arcelik A.S.", "ARDYZ": "Ard Grup Bilisim Teknolojileri A.S.",
    "ARMDA": "Armada Bilgisayar Sistemleri Sanayi ve Ticaret A.S.", "ARTMS": "Artemis Hali Iplik Sanayi ve Ticaret A.S.",
    "ASELS": "Aselsan Elektronik Sanayi ve Ticaret A.S.", "ASGYO": "Asce Gayrimenkul Yatirim Ortakligi A.S.",
    "ASTOR": "Astor Enerji A.S.", "ASUZU": "Anadolu Isuzu Otomotiv Sanayi ve Ticaret A.S.",
    "ATAGY": "Ata Gayrimenkul Yatirim Ortakligi A.S.", "ATEKS": "Akteks Akrilik Iplik Sanayi ve Ticaret A.S.",
    "ATLAS": "Atlas Menkul Kiymetler Yatirim Ortakligi A.S.", "AVOD": "Avod Textil Sanayi ve Ticaret A.S.",
    "AVPGY": "Avrupa Gayrimenkul Yatirim Ortakligi A.S.", "AYCES": "Altinyag Kombinalari A.S.",
    "AYDEM": "Aydem Enerji A.S.", "AYGAZ": "Aygaz A.S.",
    "BAGFS": "Bagfas Bandirma Gubre Fabrikalari A.S.", "BAHAR": "Bahar Gayrimenkul Yatirim Ortakligi A.S.",
    "BALAT": "Balatacilar Balatacilik Sanayi ve Ticaret A.S.", "BANVT": "Banvit Bandirma Vitaminli Yem Sanayi A.S.",
    "BASAS": "Basis Sanayi ve Ticaret A.S.", "BERA": "Bera Holding A.S.",
    "BFREN": "Bosch Fren Sistemleri Sanayi ve Ticaret A.S.", "BIMAS": "BIM Birlesik Magazalar A.S.",
    "BLCYT": "Bilici Yatirim Sanayi ve Ticaret A.S.", "BMSCH": "Bms Cimento ve Yapi Malzemeleri Sanayi ve Ticaret A.S.",
    "BOSSA": "Bossa Ticaret ve Sanayi Isletmeleri A.S.", "BRISA": "Brisa Bridgestone Sabanci Lastik Sanayi ve Ticaret A.S.",
    "BRSAN": "Borusan Birlesik Boru Fabrikalari Sanayi ve Ticaret A.S.", "BRYAT": "Borusan Yatirim Pazarlama A.S.",
    "BTCIM": "Baticim Bati Anadolu Cimento Sanayii A.S.", "BUCIM": "Bursa Cimento Fabrikasi A.S.",
    "CANTE": "Can2 Termik A.S.", "CCOLA": "Coca-Cola Icecek A.S.",
    "CELHA": "Celik Halat ve Tel Sanayii A.S.", "CEMTS": "Cemtas Celik Makina Sanayi ve Ticaret A.S.",
    "CEOEM": "Ceo Event Medya A.S.", "CIMSA": "Cimsa Cimento Sanayi ve Ticaret A.S.",
    "CLEBI": "Celebi Hava Servisi A.S.", "COSMO": "Cosmos Yatirim Holding A.S.",
    "CRDFA": "Cardata Bilgi Teknolojileri A.S.", "CVKMD": "CVK Maden Isletmeleri Sanayi ve Ticaret A.S.",
    "DAGI": "Dagi Giyim Sanayi ve Ticaret A.S.", "DAPGM": "DAP Gayrimenkul Gelistirme A.S.",
    "DARDL": "Dardanel Onentas Gida Sanayi A.S.", "DENGE": "Denge Yatirim Holding A.S.",
    "DERIM": "Derimod Konfeksiyon Ayakkabi Deri Sanayi ve Ticaret A.S.", "DESPC": "Despec Bilgisayar Pazarlama ve Ticaret A.S.",
    "DGATE": "Datatec Bilgi Islem Merkezi ve Ticaret A.S.", "DITP": "Dita Dokum ve Makina Sanayi A.S.",
    "DMRGD": "Dimerco Gayrimenkul Yatirim Ortakligi A.S.", "DNZGD": "Deniz Gayrimenkul Yatirim Ortakligi A.S.",
    "DOAS": "Dogus Otomotiv Servis ve Ticaret A.S.", "DOFER": "Doganlar Mobilya Grubu Imalat Sanayi ve Ticaret A.S.",
    "DOHOL": "Dogan Holding A.S.", "DOKTA": "Doktas Dokumculuk Ticaret ve Sanayi A.S.",
    "DURDO": "Duran Dogan Basim ve Ambalaj Sanayi A.S.", "DYOBY": "Dyoboy Kimya Sanayi ve Ticaret A.S.",
    "EBEBK": "Ebebek Magazacilik Sanayi ve Ticaret A.S.", "ECILC": "Eczacibasi Ilac Sanayi ve Ticaret A.S.",
    "ECZYT": "Eczacibasi Yatirim Holding Ortakligi A.S.", "EDATA": "Edata Bilgi Teknolojileri ve Saglik Hizmetleri A.S.",
    "EDIP": "Edip Gayrimenkul Yatirim Sanayi ve Ticaret A.S.", "EGEEN": "Ege Endustri ve Ticaret A.S.",
    "EGSER": "Ege Seramik Sanayi ve Ticaret A.S.", "EKGYO": "Emlak Konut Gayrimenkul Yatirim Ortakligi A.S.",
    "EKIZ": "Ekiz Kimya Sanayi ve Ticaret A.S.", "EMKEL": "Emmueller Kagit Ambalaj Sanayi ve Ticaret A.S.",
    "EMNIS": "Emniyet Sigorta A.S.", "ENERY": "Enerji Yatirimlari Holding A.S.",
    "ENFA": "Enfa Gayrimenkul Yatirim Ortakligi A.S.", "ENJSA": "Enerjisa Enerji A.S.",
    "ENKAI": "Enka Insaat ve Sanayi A.S.", "EPLAS": "Egeplast Ege Plastik Ticaret ve Sanayi A.S.",
    "ERBOS": "Erbosan Erciyas Boru Sanayi ve Ticaret A.S.", "EREGL": "Eregli Demir ve Celik Fabrikalari T.A.S.",
    "ESCOM": "Escort Teknoloji Yatirim A.S.", "ETILR": "Etiler Gida Sanayi ve Ticaret A.S.",
    "EUKYO": "Euro Kapital Yatirim Ortakligi A.S.", "EUYO": "Euro Yatirim Ortakligi A.S.",
    "FADE": "Fade Gayrimenkul Yatirim Ortakligi A.S.", "FENER": "Fenerbahce Futbol A.S.",
    "FLAP": "Flap Kongre Toplanti Hizmetleri Otomotiv ve Turizm A.S.", "FONET": "Fonet Bilgi Teknolojileri A.S.",
    "FORMT": "Formet Metal ve Cam Sanayi A.S.", "FORTE": "Forte Bilgi Iletisim Teknolojileri ve Savunma Sanayi A.S.",
    "FRIGO": "Frigo Pak Gida Maddeleri Sanayi ve Ticaret A.S.", "FROTO": "Ford Otomotiv Sanayi A.S.",
    "FZLGY": "Fuzul Gayrimenkul Yatirim Ortakligi A.S.", "GALAT": "Galatasaray Sportif Sinai ve Ticari Yatirimlar A.S.",
    "GARAN": "Turkiye Garanti Bankasi A.S.", "GEDIK": "Gedik Yatirim Menkul Degerler A.S.",
    "GENTS": "Gentas Genel Metal Sanayi ve Ticaret A.S.", "GENIL": "Gen Ilac ve Saglik Urunleri Sanayi ve Ticaret A.S.",
    "GEREL": "Geresan Elektrik Ticaret ve Sanayi A.S.", "GIMAT": "Gimat Magazacilik Sanayi ve Ticaret A.S.",
    "GLBMD": "Global Media Danismanlik ve Yatirim A.S.", "GLYHO": "Global Yatirim Holding A.S.",
    "GOKNR": "Goknur Gida Maddeleri Enerji Imalat Ithalat Ihracat Ticaret ve Sanayi A.S.",
    "GOLTS": "Gozde Girisim Sermayesi Yatirim Ortakligi A.S.", "GOODY": "Goodyear Lastikleri T.A.S.",
    "GRNYO": "Girisim Yatirim Ortakligi A.S.", "GSDHO": "GSD Holding A.S.",
    "GSRAY": "Galatasaray Sportif Sinai ve Ticari Yatirimlar A.S.", "GUBRF": "Gubre Fabrikalari T.A.S.",
    "HACGY": "Haci Gayrimenkul Yatirim Ortakligi A.S.", "HALKB": "Turkiye Halk Bankasi A.S.",
    "HALKS": "Halk Gayrimenkul Yatirim Ortakligi A.S.", "HATEK": "Hatek Dogalgaz ve Petrol Urunleri Sanayi ve Ticaret A.S.",
    "HATSN": "Hatsan Makina Sanayi ve Ticaret A.S.", "HDFGS": "Hedef Girisim Sermayesi Yatirim Ortakligi A.S.",
    "HEKTS": "Hektas Ticaret T.A.S.", "HKTM": "Hektas Ticaret T.A.S.",
    "HTTBT": "Hitit Bilgisayar Hizmetleri A.S.", "HUBVC": "Hub Girisim Sermayesi Yatirim Ortakligi A.S.",
    "HURGZ": "Hurriyet Gazetecilik ve Matbaacilik A.S.", "ICBCT": "ICBC Turkey Bank A.S.",
    "IDEAL": "Idealist Gayrimenkul Yatirim Ortakligi A.S.", "IEYHO": "IEY Holding A.S.",
    "IHAAS": "Ihlas Haber Ajansi A.S.", "IHLAS": "Ihlas Holding A.S.",
    "IHYAY": "Ihlas Yayin Holding A.S.", "IMASM": "Imas Makina Sanayi A.S.",
    "INDES": "Indeks Bilgisayar Sistemleri Muhendislik Sanayi ve Ticaret A.S.", "INFO": "Info Yatirim A.S.",
    "INGYO": "In Gayrimenkul Yatirim Ortakligi A.S.", "INTEK": "Integral Yatirim Holding A.S.",
    "INVEO": "Inveo Yatirim Holding A.S.", "ISCTR": "Turkiye Is Bankasi A.S.",
    "ISFIN": "Is Finansal Kiralama A.S.", "ISGSY": "Is Girisim Sermayesi Yatirim Ortakligi A.S.",
    "ISGYO": "Is Gayrimenkul Yatirim Ortakligi A.S.", "ISKPL": "Iskur Plastik Sanayi ve Ticaret A.S.",
    "ISMEN": "Is Yatirim Menkul Degerler A.S.", "IZENR": "Izmir Enerji ve Su Isleri A.S.",
    "IZFAS": "Izmir Firca Sanayi ve Ticaret A.S.", "IZMDC": "Izmir Demir Celik Sanayi A.S.",
    "KARSN": "Karsan Otomotiv Sanayii ve Ticaret A.S.", "KARTN": "Kartonsan Karton Sanayi ve Ticaret A.S.",
    "KATMR": "Katmerciler Arac Ustu Ekipman Sanayi ve Ticaret A.S.", "KAYSE": "Kayseri Seker Fabrikasi A.S.",
    "KBORU": "Kibris Boru Sanayi ve Ticaret A.S.", "KCAER": "Kocaer Celik Sanayi ve Ticaret A.S.",
    "KCHOL": "Koc Holding A.S.", "KERVT": "Kervansaray Yatirim Holding A.S.",
    "KFEIN": "Kafein Yazilim Hizmetleri Ticaret A.S.", "KGYO": "Koray Gayrimenkul Yatirim Ortakligi A.S.",
    "KIMMR": "Kimteks Kimya Tekstil Sanayi ve Ticaret A.S.", "KLGYO": "Kiler Gayrimenkul Yatirim Ortakligi A.S.",
    "KLSYN": "Koleksiyon Mobilya Sanayi ve Ticaret A.S.", "KNFRT": "Konfrut Gida Sanayi ve Ticaret A.S.",
    "KOCMT": "Koc Metalurji Sanayi ve Ticaret A.S.", "KONKA": "Konka Gayrimenkul Yatirim Ortakligi A.S.",
    "KONTR": "Kontrolmatik Teknoloji Enerji ve Muhendislik A.S.", "KORDS": "Kordsa Teknik Tekstil A.S.",
    "KOTON": "Koton Magazacilik Tekstil Sanayi ve Ticaret A.S.", "KOZAA": "Koza Anadolu Metal Madencilik Isletmeleri A.S.",
    "KOZAL": "Koza Altin Isletmeleri A.S.", "KPLPN": "Kaplamin Ambalaj Sanayi ve Ticaret A.S.",
    "KRDMD": "Kardemir Karabuk Demir Celik Sanayi ve Ticaret A.S.", "KRGYO": "Koruma Gayrimenkul Yatirim Ortakligi A.S.",
    "KRONT": "Kron Teknoloji A.S.", "KRPLS": "Karel Plastik ve Ambalaj Sanayi Ticaret A.S.",
    "KRSTL": "Kristal Kola ve Mesrubat Sanayi Ticaret A.S.", "KRTEK": "Kartek Kart ve Teknoloji Hizmetleri A.S.",
    "KSTUR": "Kustur Kusadasi Turizm ve Yatirim A.S.", "KUTPO": "Kutahya Porselen Sanayi A.S.",
    "LIDER": "Lider Faktoring A.S.", "LIOYO": "Lio Yatirim Ortakligi A.S.",
    "LKMKN": "Lokman Hekim Engurusag Saglik Egitim Hizmetleri A.S.", "LMKDC": "Limak Dogu Anadolu Cimento Sanayi ve Ticaret A.S.",
    "LOGO": "Logo Yazilim Sanayi ve Ticaret A.S.", "MACKO": "Mackolik Internet Hizmetleri Ticaret A.S.",
    "MAGEN": "Margun Enerji Sanayi ve Ticaret A.S.", "MAKTE": "Makina Takim Endustrisi A.S.",
    "MANAS": "Manas Enerji Yonetimi Sanayi ve Ticaret A.S.", "MARBL": "Marble Ithalat Ihracat ve Sanayi A.S.",
    "MARKA": "Marka Yatirim Holding A.S.", "MARTI": "Marti Otel Isletmeleri A.S.",
    "MATAS": "Matas Madencilik Sanayi ve Ticaret A.S.", "MATRK": "Matriks Bilgi Dagitim Hizmetleri A.S.",
    "MAVI": "Mavi Giyim Sanayi ve Ticaret A.S.", "MEGAP": "Megapol Insaat ve Ticaret A.S.",
    "MEKAG": "Meka Beton ve Yapi Malzemeleri Sanayi ve Ticaret A.S.", "MEPET": "Mepet Metro Petrol ve Tesisleri Sanayi Ticaret A.S.",
    "MERIT": "Merit Turizm ve Yatirim A.S.", "MERKO": "Merko Gida Sanayi ve Ticaret A.S.",
    "METRO": "Metro Ticari ve Mali Yatirimlar A.S.", "MGROS": "Migros Ticaret A.S.",
    "MIATK": "Mia Teknoloji A.S.", "MIGYO": "Mistral Gayrimenkul Yatirim Ortakligi A.S.",
    "MIPAZ": "Mipaz Pazarlama ve Ticaret A.S.", "MMCAS": "Mmc Sanayi ve Ticari Yatirimlar A.S.",
    "MNDRS": "Menderes Tekstil Sanayi ve Ticaret A.S.", "MNDTR": "Menderes Tekstil Sanayi ve Ticaret A.S.",
    "MOBIL": "Mobil Yatirim Ortakligi A.S.", "MPARK": "MLP Saglik Hizmetleri A.S.",
    "MTRYO": "Metro Yatirim Ortakligi A.S.", "MZHLD": "Muzede Kozmetik ve Tekstil Sanayi Ticaret A.S.",
    "NIBAS": "Nibas Yatirim Holding A.S.", "NPAPEL": "Nippon Paper Istanbul Seluloz Sanayi ve Ticaret A.S.",
    "NTHOL": "Net Holding A.S.", "NTTUR": "Net Turizm Ticaret ve Sanayi A.S.",
    "NUHCM": "Nuh Cimento Sanayi A.S.", "OBSBV": "Oba Bilisim Teknolojileri A.S.",
    "ODAS": "Odas Elektrik Uretim Sanayi Ticaret A.S.", "ODINE": "Odine Teknoloji A.S.",
    "OFIX": "Ofis Yem Gida Sanayi ve Ticaret A.S.", "OFSYM": "Ofis Yem Gida Sanayi ve Ticaret A.S.",
    "ONCSM": "Oncosem Onkolojik Sistemler Sanayi ve Ticaret A.S.", "ORCAY": "Orcay Ortakoy Cay Sanayi ve Ticaret A.S.",
    "ORGE": "Orge Enerji Elektrik Taahhut Muhendislik Sanayi ve Ticaret A.S.", "OTKAR": "Otokar Otomotiv ve Savunma Sanayi A.S.",
    "OYAKC": "Oyak Cimento Fabrikalari A.S.", "OYLUM": "Oylum Sinai Yatirimlar A.S.",
    "PAGYO": "Panora Gayrimenkul Yatirim Ortakligi A.S.", "PAMEL": "Pamukova Enerji ve Madencilik A.S.",
    "PAPIL": "Papilon Savunma Teknolojileri ve Ticaret A.S.", "PARSN": "Parsan Makina Parcalari Sanayii A.S.",
    "PCILT": "Pci Bilisim Teknolojileri Sanayi ve Ticaret A.S.", "PEKGY": "Peker Gayrimenkul Yatirim Ortakligi A.S.",
    "PENGD": "Penguen Gida Sanayi A.S.", "PENTA": "Penta Teknoloji Urunleri Dagitim Ticaret A.S.",
    "PETKM": "Petkim Petrokimya Holding A.S.", "PGSUS": "Pegasus Hava Tasimaciligi A.S.",
    "PINSU": "Pinar Su ve Icecek Sanayi ve Ticaret A.S.", "PKART": "Plastikkart Akilli Kart Iletisim Sistemleri Sanayi ve Ticaret A.S.",
    "PNSUT": "Pinar Sut Mamulleri Sanayii A.S.", "PRKME": "Park Elektrik Madencilik ve Petrol Sanayi ve Ticaret A.S.",
    "PRZMA": "Prizer Makina ve Yedek Parca Sanayi ve Ticaret A.S.", "PSGYO": "Pasifik Gayrimenkul Yatirim Ortakligi A.S.",
    "QUAGR": "Qua Granite Hayal Yapi ve Urunleri Sanayi Ticaret A.S.", "RGYAS": "Ronesans Gayrimenkul Yatirim Ortakligi A.S.",
    "SAFKR": "Safkar Ege Sogutmacilik Klima Soguk Hava Tesisleri Ihracat Ithalat Sanayi ve Ticaret A.S.",
    "SAHOL": "Haci Omer Sabanci Holding A.S.", "SANEL": "Sanel Muhendislik Sanayi ve Ticaret A.S.",
    "SANKO": "Sanko Pazarlama Ithalat Ihracat A.S.", "SARKY": "Sarkuysan Elektrolitik Bakir Sanayi ve Ticaret A.S.",
    "SASA": "Sasa Polyester Sanayi A.S.", "SEKUR": "Sekuro Plastik Ambalaj Sanayi A.S.",
    "SELEC": "Select Enerji Gida Sanayi ve Ticaret A.S.", "SILVR": "Silverline Endustri ve Ticaret A.S.",
    "SISE": "Turkiye Sise ve Cam Fabrikalari A.S.", "SKBNK": "Sekerbank T.A.S.",
    "SKTAS": "Soktas Tekstil Sanayi ve Ticaret A.S.", "SMART": "Smartiks Yazilim A.S.",
    "SODA": "Soda Sanayii A.S.", "SOKE": "Soke Degirmencilik Sanayi ve Ticaret A.S.",
    "SOKM": "Sok Marketler T.A.S.", "SUWEN": "Suwen Tekstil Sanayi ve Ticaret A.S.",
    "TATGD": "Tat Gida Sanayi A.S.", "TAVHL": "TAV Havalimanlari Holding A.S.",
    "TBORG": "Trakya Cam Sanayii A.S.", "TCELL": "Turkcell Iletisim Hizmetleri A.S.",
    "THYAO": "Turk Hava Yollari A.O.", "TKFEN": "Tekfen Holding A.S.",
    "TMSN": "Tumosan Motor ve Traktor Sanayi A.S.", "TOASO": "Tofas Turk Otomobil Fabrikasi A.S.",
    "TRCAS": "Turcas Petrol A.S.", "TRGYO": "Turkiye Gayrimenkul Yatirim Ortakligi A.S.",
    "TRILC": "Turkiye Ilac ve Serum Sanayi A.S.", "TSGYO": "T.S. Gayrimenkul Yatirim Ortakligi A.S.",
    "TSKB": "Turkiye Sinai Kalkinma Bankasi A.S.", "TSPOR": "Trabzonspor Sportif Yatirim ve Futbol Isletmeciligi Ticaret A.S.",
    "TUPRS": "Tupras Turkiye Petrol Rafinerileri A.S.", "TUREX": "Tureks Turizm Tasimacilik ve Gida Sanayi Ticaret A.S.",
    "ULKER": "Ulker Biskuvi Sanayi A.S.", "USAK": "Usak Seramik Sanayi A.S.",
    "VAKBN": "Turkiye Vakiflar Bankasi T.A.O.", "VANGD": "Vanet Gida Sanayi ve Ticaret A.S.",
    "VERUS": "Verusatk Girisim Sermayesi Yatirim Ortakligi A.S.", "VESTL": "Vestel Elektronik Sanayi ve Ticaret A.S.",
    "VKGYO": "Vakif Gayrimenkul Yatirim Ortakligi A.S.", "YATAS": "Yatas Yatak ve Yorgan Sanayi ve Ticaret A.S.",
    "YAYLA": "Yayla Enerji Uretim Turizm ve Insaat Ticaret A.S.", "YESIL": "Yesil Gayrimenkul Yatirim Ortakligi A.S.",
    "YGGYO": "Yeni Gimat Gayrimenkul Yatirim Ortakligi A.S.", "YKSBL": "Yuksel Insaat A.S.",
    "YKBNK": "Yapi ve Kredi Bankasi A.S.", "YYAPI": "Yeni Yapi ve Yatirim A.S.",
    "ZOREN": "Zorlu Enerji Elektrik Uretim A.S.",
}

VALID_SYMBOLS = set(KNOWN.keys())


def try_kap():
    print("[1] KAP sayfasi taranarak semboller bulunuyor...")
    url = "https://www.kap.org.tr/tr/bist-sirketler"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text()
    found = {sym for sym in VALID_SYMBOLS if sym in text}
    results = {}
    for sym in sorted(found):
        results[f"{sym}.IS"] = KNOWN.get(sym, sym)
    if len(found) > 50:
        print(f"   KAP: {len(found)} sembol bulundu (isimler eklenerek kaydedildi).")
        return results
    print(f"   KAP: sadece {len(found)} sembol.")
    return None


def try_bigpara_canli():
    print("[2] Bigpara canli-borsa sayfasi taranıyor...")
    url = "https://bigpara.hurriyet.com.tr/borsa/canli-borsa/"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text()
    found = {sym for sym in VALID_SYMBOLS if sym in text}
    if len(found) > 50:
        results = {}
        for sym in sorted(found):
            results[f"{sym}.IS"] = KNOWN.get(sym, sym)
        print(f"   Bigpara: {len(found)} sembol.")
        return results
    return None


def fallback():
    print("[3] Bilinen BIST sembolleri kullaniliyor (fallback)...")
    results = {}
    for sym, name in KNOWN.items():
        results[f"{sym}.IS"] = name
    print(f"   Fallback: {len(KNOWN)} sembol.")
    return results


def main():
    result = try_kap()
    if result is None or len(result) < 50:
        time.sleep(1)
        result = try_bigpara_canli()

    fb = fallback()
    if result is None or len(result) < 50:
        result = fb
    else:
        # Merge: add any symbols in fallback that KAP/bigpara missed
        for k, v in fb.items():
            if k not in result:
                result[k] = v

    data = dict(sorted(result.items()))
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nToplam {len(data)} sembol kaydedildi -> {OUTPUT}")
    sample = list(data.items())[:3]
    print(f"Ornek: {sample}")


if __name__ == "__main__":
    main()
