from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QScrollArea, QProgressBar,
                              QTextEdit)
from PyQt6.QtCore import Qt

from ..theme import COMMON_SYMBOLS


class AIKararMotoruPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Başlık
        baslik = QLabel("🤖 AI Karar Destek Motoru")
        baslik.setStyleSheet("font-size: 20px; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(baslik)

        # Sinyal kartı
        self.signal_card = QFrame()
        self.signal_card.setObjectName("metricCard")
        self.signal_card.setStyleSheet("""
            QFrame#metricCard {
                background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.05);
                border-left: 4px solid #ffeb3b; border-radius: 16px; padding: 20px;
            }
        """)
        sig_layout = QVBoxLayout(self.signal_card)
        self.signal_label = QLabel("⚠️ NÖTR")
        self.signal_label.setStyleSheet("font-size: 30px; font-weight: 700; color: #ffeb3b;")
        self.signal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig_layout.addWidget(self.signal_label)
        self.signal_detail = QLabel("Skor: %50 | Henüz analiz yapılmadı")
        self.signal_detail.setStyleSheet("font-size: 16px; color: #94a3b8;")
        self.signal_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig_layout.addWidget(self.signal_detail)
        layout.addWidget(self.signal_card)

        # Modül skorları
        layout.addWidget(self._modul_skorlari())

        # Çalıştır butonu
        self.run_btn = QPushButton("🚀 Ajanları Paralel Çalıştır (asyncio.gather)")
        self.run_btn.clicked.connect(self._on_run)
        layout.addWidget(self.run_btn)

        # Chain-of-Thought expander benzeri
        self.cot_area = QTextEdit()
        self.cot_area.setReadOnly(True)
        self.cot_area.setMaximumHeight(150)
        self.cot_area.setPlaceholderText("🧠 Ajan Düşünce Zinciti burada görünecek...")
        layout.addWidget(self.cot_area)

        layout.addStretch()

        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0, 0, 0, 0)
        main_l.addWidget(scroll)

    def _modul_skorlari(self):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        self.module_cards = {}
        for label, key, color in [
            ("Teknik Analiz", "technical", "#ffeb3b"),
            ("Temel Analiz", "fundamental", "#4ade80"),
            ("Duygu Analizi", "sentiment", "#ce93d8"),
            ("Fon Akışı", "flow", "#38bdf8"),
            ("Makro Radar", "macro", "#f97316"),
        ]:
            card = QFrame()
            card.setObjectName("metricCard")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(8, 6, 8, 6)
            cl.setSpacing(2)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 600;")
            cl.addWidget(lbl)
            val = QLabel("%—")
            val.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc;")
            cl.addWidget(val)
            pb = QProgressBar()
            pb.setFixedHeight(4)
            pb.setValue(0)
            cl.addWidget(pb)
            l.addWidget(card)
            self.module_cards[key] = (val, pb)
        return w

    def _on_run(self):
        from ...core.engine import HedgeFundManagerAgent
        sym = self.main._current_symbol
        df = self.main.data
        vade = self.main._current_vade
        if df is None or df.empty:
            return
        self.cot_area.append("🚀 Çoklu-Ajan analizi başlatılıyor...")
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Senkron fallback kullan
            loop.close()
            mgr = HedgeFundManagerAgent(sym, df, vade)
            sonuc = mgr.run_parallel()
            self.main.update_agent_memory(sonuc)
            self.cot_area.append("✅ Konsensüs oluşturuldu!")
        except:
            self.cot_area.append("🔴 Hata oluştu.")

    def refresh(self):
        mem = self.main.agent_memory
        final_score = mem.get("final_score", 50)
        signal = mem.get("signal", "⚠️ BEKLE")

        if final_score >= 75: color = "#4ade80"
        elif final_score >= 60: color = "#22c55e"
        elif final_score >= 40: color = "#fbbf24"
        elif final_score >= 25: color = "#ef4444"
        else: color = "#dc2626"

        self.signal_label.setText(signal)
        self.signal_label.setStyleSheet(f"font-size: 30px; font-weight: 700; color: {color};")
        self.signal_detail.setText(f"Skor: %{final_score:.0f} | {'Güncel' if mem else 'Henüz analiz yapılmadı'}")
        self.signal_card.setStyleSheet(f"""
            QFrame#metricCard {{
                background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.05);
                border-left: 4px solid {color}; border-radius: 16px; padding: 20px;
            }}
        """)

        # Modül skorları (DecisionEngine ile)
        from ...core.engine import DecisionEngine
        df = self.main.data
        sym = self.main._current_symbol
        if df is not None and not df.empty:
            try:
                engine = DecisionEngine(sym, df)
                report = engine.get_report()
                for key, (val_lbl, pb) in self.module_cards.items():
                    skor = report.get("Detay", {}).get(key, 50)
                    val_lbl.setText(f"%{skor:.1f}")
                    pb.setValue(int(skor))
            except:
                pass
