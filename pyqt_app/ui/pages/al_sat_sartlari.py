from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                              QFrame, QSizePolicy)
from PyQt6.QtCore import Qt


class AlSatSartlariPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # Başlık
        baslik = QLabel("📋 Al-Sat Şartları — Ajan Onaylı Karar Rehberi")
        baslik.setStyleSheet("font-size: 20px; font-weight: 700; color: #e2e8f0; margin-bottom: 8px;")
        layout.addWidget(baslik)

        # --- ALIM KOŞULLARI ---
        layout.addWidget(self._kutu(
            "#4ade80",
            "🟩 NE ZAMAN \"AL\" YAPMALISIN? (Alım Koşulları)",
            """
Ajan Konsensüs Panelindeki 3 ana sütunda şu verileri aynı anda (veya en az ikisini güçlü şekilde) gördüğünde alım yönünde pozisyon açabilirsin:

🟢 TEKNİK ANALİZ AJANINDA:
• Hisse fiyatı düşerken RSI veya MACD çizgilerinin yükseldiğini, yani "Pozitif Uyumsuzluk (Bullish Divergence)" saptandığını görüyorsan (Bu, düşüşün bittiğini ve gizli alıcıların geldiğini gösterir).
• Fiyatın EMA 50 hareketli ortalamasının üzerine yerleştiğini ve hacmin son 20 günlük ortalamanın üzerine çıktığını görüyorsan.

🔵 BALİNA & TAKAS AJANINDA:
• "İlk 5 Kurumun Toplama Oranı" (Haftalık/Aylık Delta) pozitif ve yükseliyorsa (Tahta yapıcılar ve büyük fonlar mal topluyor demektir).
• Emir Defteri Alış Baskı Katsayısı (Imbalance Ratio) 1.5x ile 2.0x arasında veya daha üzerindeyse (Kademelerde devasa alım blokları yığılmıştır).

🟡 MAKRO DUYGU AJANINDA:
• Son KAP haberlerinin veya finansal medya taramalarının FinBERT tarafından yüksek oranda "Positive" (Pozitif) etiketlendiğini görüyorsan.

💥 Nihai Tetikleyici: Bu 3 verinin ağırlıklı ortalamasıyla hesaplanan "Ortak Konsensüs Skoru" 85 ve üzerine çıktığında ve sistem 🚀 GÜÇLÜ AL (STRONG BUY) sinyali ürettiğinde alım yapılabilir.
            """.strip()
        ))
        layout.addWidget(self._kutu(
            "#ef4444",
            "🟥 NE ZAMAN \"SAT\" VEYA \"UZAK DUR\" YAPMALISIN? (Satım Koşulları)",
            """
Elindeki hisseyi satıp kâr realize etmek veya riskli bir hisseye hiç bulaşmamak için şu sinyalleri takip etmelisin:

🟢 TEKNİK ANALİZ AJANINDA:
• Fiyat yeni zirveler yaparken RSI indikatörünün daha düşük tepeler yaptığını, yani "Negatif Uyumsuzluk (Bearish Divergence)" oluştuğunu görüyorsan (Bu, yükselişin sahte olduğunu ve gücünün bittiğini söyler).
• RSI değerinin 70 veya 80 üzerine (Aşırı Alım bölgesi) tırmandığını ve fiyatın Bollinger Üst Bandının dışına taştığını görüyorsan.

🔵 BALİNA & TAKAS AJANINDA:
• Fiyat yükselmesine rağmen "İlk 5 Kurum" mal satıyor ve lotlar diğer küçük yatırımcılara dağıtılıyorsa ("Kurumsal Dağıtım / Mal Çakma" evresi).
• Emir defterinde satış kademelerine gizli veya devasa blok satış emirleri yerleştirilmişse.

🟡 MAKRO DUYGU AJANINDA:
• Şirket hakkında negatif haber akışının başlaması, sosyal medyadaki panik/korku endeksinin aniden fırlaması.

💥 Nihai Tetikleyici: Ortak Konsensüs Skoru 50'nin altına gerilediğinde veya sistem ⚠️ RİSKLİ BÖLGE / UZAK DUR (AVOID) uyarısı verdiğinde eldeki varlıklar satılmalı veya yeni alım yapılmamalıdır.
            """.strip()
        ))

        # ALTIN KURAL
        kural_frame = QFrame()
        kural_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(250,204,21,0.06), stop:1 rgba(245,158,11,0.04));
                border: 1px solid rgba(250,204,21,0.2);
                border-left: 4px solid #fbbf24;
                border-radius: 12px;
                padding: 16px 20px;
            }
        """)
        kural_l = QVBoxLayout(kural_frame)
        kural_l.setContentsMargins(16, 14, 16, 14)

        kural_baslik = QLabel("🎯 Yatırım Yaparken Asla Unutmaman Gereken Altın Kural (Kasa Yönetimi)")
        kural_baslik.setStyleSheet("font-size: 15px; font-weight: 700; color: #fbbf24; margin-bottom: 8px;")
        kural_l.addWidget(kural_baslik)

        kural_text = QLabel(
            "Ajanların ne kadar kusursuz çalışırsa çalışsın, piyasada her zaman beklenmedik bir "
            "jeopolitik risk veya küresel kriz (Siyah Kuğu) çıkabilir. Bu yüzden yatırımlarını "
            "şu iki koruma filtresine göre yapmalısın:\n\n"
            "• Vade Filtresi: Eğer sol menüden \"Kısa Vade\" seçtiysen, Duygu ajanını tamamen "
            "göz ardı et; sadece Teknik Uyumsuzluk + Emir Defteri Alış Baskısına bakarak hareket "
            "et. Eğer \"Uzun Vade\" seçtiysen, indikatörleri boş ver; tamamen Balinaların takas "
            "toplama istikrarına ve temel büyüme verilerine odaklan.\n\n"
            "• %10 Sınırı (Risk Yönetimi): Analiz sonucu %100 kusursuz görünse bile, cüzdanındaki "
            "toplam paranın (kasanın) en fazla %10'u ile tek bir hisseye giriş yap. Paranı en az "
            "4-5 farklı ajan onaylı varlığa bölerek riskini minimize et."
        )
        kural_text.setWordWrap(True)
        kural_text.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.7;")
        kural_l.addWidget(kural_text)
        layout.addWidget(kural_frame)

        layout.addStretch()

        scroll.setWidget(container)
        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0, 0, 0, 0)
        main_l.addWidget(scroll)

    def _kutu(self, border_color, baslik, icerik):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #0F172A; border: 1px solid #1e293b;
                border-left: 4px solid {border_color};
                border-radius: 12px; padding: 16px 20px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)

        lbl_baslik = QLabel(baslik)
        lbl_baslik.setStyleSheet(f"font-size: 15px; font-weight: 700; color: #e2e8f0; margin-bottom: 6px;")
        layout.addWidget(lbl_baslik)

        lbl_icerik = QLabel(icerik)
        lbl_icerik.setWordWrap(True)
        lbl_icerik.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.7;")
        layout.addWidget(lbl_icerik)

        return frame
