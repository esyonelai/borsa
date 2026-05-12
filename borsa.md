Sen finansal mühendislik ve tam yığın (full-stack) yazılım uzmanısın. Python Streamlit kullanarak localhost'ta çalışacak, **'Global Makro ve BIST Strateji Terminali'** kodlamanı istiyorum.

### 🧩 1. AKILLI ARAMA VE VERİ ENTEGRASYONU
- Kullanıcı şirket adını yazdığında (Örn: 'Türk Hava', 'Ereğli', 'Kazatomprom') ilgili sembolleri (THYAO.IS, EREGL.IS, KAP.L vb.) getiren açılır liste (Autocomplete/Selectbox) ekle.
- `yfinance` kullanarak Borsa İstanbul, Dünya Borsaları (S&P500, Nasdaq) ve Kripto verilerini çek.

### 📈 2. GELİŞMİŞ TEKNİK ANALİZ
- Plotly ile etkileşimli Mum Grafikleri oluştur.
- Göstergeler: EMA 20, 50, 200, RSI, MACD, Bollinger Bantları ve otomatik Fibonacci seviyeleri.
- Grafik üzerinde tek tıkla **TL / USD / KZT (Tenge)** bazlı görünüm arası geçiş sağla.

### 📰 3. ANLIK HABER & KAP İSTİHBARATI
- Seçilen hisseyle ilgili en güncel KAP haberlerini ve sektörel haberleri çeken canlı bir akış oluştur.
- Haberleri AI (Duygu Analizi) ile 'Pozitif/Negatif' olarak etiketle.

### 🌍 4. KÜRESEL RADAR & MAKRO VERİLER
- S&P 500, Nasdaq, DXY (Dolar Endeksi), Brent Petrol, Demir-Çelik ve Bakır fiyatlarını takip et.
- Altın Bölümü: ONS Altın, Gram Altın ve Yabancı Altın ETF'lerini takip et.
- FED ve TCMB faiz kararı tarihlerini içeren bir ekonomik takvim ekle.

### 💱 5. PARA BİRİMİ VE KORELASYON MASASI
- USD/TRY, USD/KZT ve TRY/KZT çapraz kurlarını anlık takip et.
- Bu kurların BIST ile olan ilişkisini gösteren bir Isı Haritası (Heatmap) oluştur.

### 🏦 6. FONLAR VE AKILLI PARA TAKİBİ
- TEFAS fon performanslarını listele.
- Hisse bazında yabancı takas oranlarını ve büyük fonların giriş-çıkışlarını gösteren tablolar ekle.

### 🛡️ 7. RİSK YÖNETİMİ VE PSİKOLOJİK GÜNLÜK
- **Risk Hesabı:** Toplam sermayenin %2'sini riske atacak şekilde stop-loss seviyesine göre kaç 'Lot' alınması gerektiğini hesaplayan araç.
- **Yatırımcı Günlüğü:** Her işlemin nedenini, giriş fiyatını, o anki duygu durumunu (Korku/Açgözlülük) ve sonucunu kaydeden, verileri bir CSV dosyasına saklayan modül.

### 🎨 8. TASARIM VE ARAYÜZ
- Profesyonel 'Dark Mode' (Karanlık Tema) tasarımı kullan.
- Sidebar (Kenar Çubuğu) üzerinden hisse araması ve risk hesaplaması yapılabilsin.

**Lütfen bu sistemi tek bir `app.py` dosyası olarak, modüler, hatasız ve açıklama satırları eklenmiş şekilde kodla.**