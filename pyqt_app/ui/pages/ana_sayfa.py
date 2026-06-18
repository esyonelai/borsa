from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QScrollArea, QGridLayout,
                              QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import yfinance as yf
import pandas as pd

from ..theme import COMMON_SYMBOLS


class MetricCard(QFrame):
    """Bloomberg tarzı tek metrik kartı."""

    def __init__(self, title, value, delta="", parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self.setFixedWidth(180)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("metricTitle")
        layout.addWidget(title_lbl)
        self.val_lbl = QLabel(value)
        self.val_lbl.setObjectName("metricValue")
        layout.addWidget(self.val_lbl)
        self.delta_lbl = QLabel(delta)
        self.delta_lbl.setObjectName("metricDelta")
        layout.addWidget(self.delta_lbl)

    def set_values(self, value, delta=""):
        self.val_lbl.setText(value)
        self.delta_lbl.setText(delta)


class KonsensusWidget(QFrame):
    """Tek bir ajan için 3-sütun widget'ı."""

    def __init__(self, title, score, items, score_color="#fbbf24", parent=None):
        super().__init__(parent)
        self.setObjectName("consWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("consTitle")
        layout.addWidget(title_lbl)

        self.score_lbl = QLabel(f"%{score:.0f}" if isinstance(score, (int, float)) else "%—")
        self.score_lbl.setObjectName("consScore")
        self.score_lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {score_color}; margin: 2px 0;")
        layout.addWidget(self.score_lbl)

        for text in items:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #cbd5e1; font-size: 11px; line-height: 1.6;")
            layout.addWidget(lbl)

        layout.addStretch()

    def update_score(self, score, score_color):
        self.score_lbl.setText(f"%{score:.0f}" if isinstance(score, (int, float)) else "%—")
        self.score_lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {score_color}; margin: 2px 0;")


class AnaSayfaPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.dashboard = None
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

        # Bloomberg kartı
        self.card_widget = QWidget()
        card_layout = QHBoxLayout(self.card_widget)
        card_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_lbl = QLabel("TH")
        self.logo_lbl.setStyleSheet("background: #1f2937; border-radius: 8px; padding: 12px; font-size: 32px; font-weight: 700; color: #e2e8f0; min-width: 60px; min-height: 60px;")
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.logo_lbl)

        info_w = QWidget()
        info_l = QVBoxLayout(info_w)
        info_l.setContentsMargins(12, 0, 0, 0)
        self.name_lbl = QLabel("THYAO.IS")
        self.name_lbl.setStyleSheet("font-size: 12px; color: #8b949e;")
        info_l.addWidget(self.name_lbl)
        self.price_lbl = QLabel("0.00")
        self.price_lbl.setStyleSheet("font-size: 30px; font-weight: 700; color: #f0f6fc;")
        info_l.addWidget(self.price_lbl)
        self.change_lbl = QLabel("")
        self.change_lbl.setStyleSheet("font-size: 16px; font-weight: 600;")
        info_l.addWidget(self.change_lbl)
        card_layout.addWidget(info_w)
        card_layout.addStretch()
        layout.addWidget(self.card_widget)

        # Ayraç
        layout.addWidget(self._hr())

        # 3 sütunlu konsensüs widget alanı
        self.consensus_row = QWidget()
        self.consensus_layout = QHBoxLayout(self.consensus_row)
        self.consensus_layout.setContentsMargins(0, 0, 0, 0)
        self.consensus_layout.setSpacing(8)
        layout.addWidget(self.consensus_row)

        # Konsensüs paneli (ortak skor)
        self.consensus_panel = QFrame()
        self.consensus_panel.setObjectName("consensusPanel")
        self.cp_layout = QHBoxLayout(self.consensus_panel)
        self.cp_layout.setContentsMargins(16, 12, 16, 12)
        self.cp_layout.setSpacing(20)
        layout.addWidget(self.consensus_panel)

        # Buton
        self.run_btn = QPushButton("🚀 Ajanları Paralel Çalıştır (asyncio.gather)")
        self.run_btn.clicked.connect(self._on_run_agents)
        layout.addWidget(self.run_btn)

        # Piyasa metrikleri
        layout.addWidget(self._hr())
        market_row = QWidget()
        market_l = QHBoxLayout(market_row)
        market_l.setContentsMargins(0, 0, 0, 0)
        self.market_cards = {}
        for sym in ["USDTRY=X", "USDKZT=X", "GC=F", "BTC-USD", "^GSPC"]:
            card = MetricCard(COMMON_SYMBOLS.get(sym, sym), "—")
            self.market_cards[sym] = card
            market_l.addWidget(card)
        market_l.addStretch()
        layout.addWidget(market_row)

        layout.addStretch()

        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Piyasa verileri timer
        self.market_timer = QTimer()
        self.market_timer.timeout.connect(self._update_market_data)
        self.market_timer.start(60000)

    def _hr(self):
        h = QFrame()
        h.setFrameShape(QFrame.Shape.HLine)
        h.setStyleSheet("color: #1e293b; margin: 4px 0;")
        return h

    def _on_run_agents(self):
        from ...core.engine import ConsensusDashboard
        sym = self.main._current_symbol
        df = self.main.data
        if df is None or df.empty:
            return
        vade = self.main._current_vade
        self.dashboard = ConsensusDashboard(sym, df, vade)

        # Arka planda çalıştır
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            sonuc = loop.run_until_complete(self.dashboard.run_async())
            loop.close()
            self.main.update_agent_memory(sonuc)
        except:
            from ...core.engine import HedgeFundManagerAgent
            mgr = HedgeFundManagerAgent(sym, df, vade)
            sonuc = mgr.run_parallel()
            self.main.update_agent_memory(sonuc)

    def refresh(self):
        """Ana sayfayı güncelle."""
        mem = self.main.agent_memory
        sym = self.main._current_symbol
        df = self.main.data

        # Bloomberg kartı
        sym_clean = sym.replace(".IS", "")
        self.logo_lbl.setText(sym_clean[:2])
        self.name_lbl.setText(COMMON_SYMBOLS.get(sym, sym))

        if df is not None and not df.empty:
            close = df['Close'].iloc[-1]
            prev = df['Close'].iloc[0]
            chg = ((close / prev) - 1) * 100
            self.price_lbl.setText(f"{close:.4f}")
            sig = "+" if chg >= 0 else ""
            color = "#4ade80" if chg >= 0 else "#ef4444"
            self.change_lbl.setText(f"({sig}{chg:.2f}%)")
            self.change_lbl.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {color};")
        else:
            self.price_lbl.setText("—")
            self.change_lbl.setText("")

        # Konsensüs widget'ları (3 sütun)
        self._clear_layout(self.consensus_layout)
        t_skor = mem.get("technical_score")
        w_skor = mem.get("whale_score")
        s_skor = mem.get("sentiment_score")

        t_col = "#4ade80" if t_skor and t_skor >= 60 else "#ef4444" if t_skor and t_skor <= 30 else "#fbbf24"
        w_col = "#38bdf8" if w_skor and w_skor >= 60 else "#ef4444" if w_skor and w_skor <= 30 else "#fbbf24"
        s_col = "#fbbf24" if s_skor and s_skor >= 60 else "#ef4444" if s_skor and s_skor <= 30 else "#94a3b8"

        from ...core.engine import detect_divergence
        divs = []
        if df is not None and not df.empty:
            try: divs = detect_divergence(df)
            except: pass

        tech_items = []
        if divs:
            for d in divs[:1]:
                tech_items.append(f"🔍 Uyumsuzluk: {d[2][:50]}")
        else:
            tech_items.append("✅ RSI uyumsuzluk yok")

        if df is not None and not df.empty:
            try:
                close = df['Close'].squeeze().astype(float)
                ema50 = ta.trend.ema_indicator(close, window=50).iloc[-1] if hasattr(__import__('ta'), 'trend') else None
            except:
                pass

        # Basit widget'lar
        w1 = KonsensusWidget("🟢 TEKNİK MOMENTUM", t_skor or 0, tech_items, t_col)
        w2 = KonsensusWidget("🔵 BALİNA & TAKAS", w_skor or 0, [
            f"🏦 Kurum Kararlılığı: %{mem.get('whale_score', 0):.0f}",
            "📋 Emir Defteri: —",
        ], w_col)
        w3 = KonsensusWidget("🟡 MAKRO DUYGU", s_skor or 0, [
            f"📰 Haber Duyarlılığı: %{mem.get('sentiment_score', 0):.0f}",
            "🌐 Sosyal Medya: —",
        ], s_col)

        self.consensus_layout.addWidget(w1)
        self.consensus_layout.addWidget(w2)
        self.consensus_layout.addWidget(w3)

        # Konsensüs paneli
        self._update_consensus_panel(mem)

    def _update_consensus_panel(self, mem):
        # Mevcut etiketleri temizle
        for i in reversed(range(self.cp_layout.count())):
            w = self.cp_layout.itemAt(i).widget()
            if w: w.deleteLater()

        final_score = mem.get("final_score", 50)
        signal = mem.get("signal", "⚠️ BEKLE")
        horizon = self.main._current_vade
        exec_time = mem.get("execution_time", "—")

        if final_score >= 75: color = "#4ade80"; bg = "rgba(74,222,128,0.08)"
        elif final_score >= 60: color = "#22c55e"; bg = "rgba(34,197,94,0.06)"
        elif final_score >= 40: color = "#fbbf24"; bg = "rgba(251,191,36,0.06)"
        elif final_score >= 25: color = "#ef4444"; bg = "rgba(239,68,68,0.08)"
        else: color = "#dc2626"; bg = "rgba(220,38,38,0.1)"

        self.consensus_panel.setStyleSheet(f"""
            QFrame#consensusPanel {{ background: {bg}; border: 1px solid {color}40; border-left: 4px solid {color}; border-radius: 12px; padding: 12px 16px; }}
            QLabel#panelTitle {{ color: #94a3b8; font-size: 10px; font-weight: 500; letter-spacing: 0.4px; }}
            QLabel#panelScore {{ font-size: 28px; font-weight: 700; color: {color}; }}
            QLabel#panelSignal {{ font-size: 18px; font-weight: 700; color: {color}; }}
        """)

        def panel_section(title, value):
            w = QWidget()
            l = QVBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            t = QLabel(title)
            t.setObjectName("panelTitle")
            l.addWidget(t)
            v = QLabel(value)
            v.setObjectName("panelScore")
            l.addWidget(v)
            return w

        self.cp_layout.addWidget(panel_section("ORTAK KONSENSÜS SKORU", f"%{final_score:.0f}"))
        sep1 = QFrame(); sep1.setFrameShape(QFrame.Shape.VLine); sep1.setStyleSheet("color: #1e293b;")
        self.cp_layout.addWidget(sep1)
        self.cp_layout.addWidget(panel_section("📢 SİSTEM SİNYALİ", signal))
        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.VLine); sep2.setStyleSheet("color: #1e293b;")
        self.cp_layout.addWidget(sep2)
        self.cp_layout.addWidget(panel_section("📅 VADE", horizon))
        sep3 = QFrame(); sep3.setFrameShape(QFrame.Shape.VLine); sep3.setStyleSheet("color: #1e293b;")
        self.cp_layout.addWidget(sep3)
        self.cp_layout.addWidget(panel_section("⏱ SÜRE", f"{exec_time}s"))
        self.cp_layout.addStretch()

    def _update_market_data(self):
        try:
            fx = yf.download(["USDTRY=X", "USDKZT=X", "GC=F", "BTC-USD", "^GSPC"], period="2d", progress=False)['Close']
            if isinstance(fx.columns, pd.MultiIndex): fx.columns = fx.columns.get_level_values(0)
            for sym, card in self.market_cards.items():
                if sym in fx.columns and len(fx) > 0:
                    val = fx[sym].iloc[-1]
                    fmt = f"{val:.4f}" if "USD" in sym else f"${val:,.2f}" if sym != "BTC-USD" else f"${val:,.0f}"
                    card.set_values(fmt)
        except:
            pass

    def _clear_layout(self, layout):
        while layout.count():
            w = layout.takeAt(0).widget()
            if w: w.deleteLater()
