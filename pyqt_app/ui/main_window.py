import asyncio
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QComboBox, QStackedWidget,
                              QFrame, QSplitter, QApplication, QProgressBar,
                              QButtonGroup)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from .theme import BLOOMBERG_QSS, COMMON_SYMBOLS, VADE_SECENEKLERI
from .pages.ana_sayfa import AnaSayfaPage
from .pages.al_sat_sartlari import AlSatSartlariPage
from .pages.ai_karar_motoru import AIKararMotoruPage


class AgentWorker(QThread):
    """Ajanları arka planda async çalıştırır (UI donmasın diye)."""
    finished = pyqtSignal(dict)

    def __init__(self, symbol, data, horizon):
        super().__init__()
        self.symbol = symbol
        self.data = data
        self.horizon = horizon

    def run(self):
        from ..core.engine import HedgeFundManagerAgent
        mgr = HedgeFundManagerAgent(self.symbol, self.data, self.horizon)
        result = mgr.run_parallel()
        self.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bloomberg Terminal — BIST & Global Makro")
        self.setMinimumSize(1400, 850)
        self.data = None
        self.agent_memory = {}
        self._current_symbol = "THYAO.IS"
        self._current_vade = "ORTA"

        # Merkezi widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Üst çubuk
        self.top_bar = self._build_top_bar()
        main_layout.addWidget(self.top_bar)

        # Alt gövde: sol navigasyon + sayfalar
        body = QSplitter(Qt.Orientation.Horizontal)
        body.setHandleWidth(1)
        main_layout.addWidget(body, 1)

        # Sol navigasyon
        nav_frame = QFrame()
        nav_frame.setObjectName("navPanel")
        nav_frame.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(6, 8, 6, 8)
        nav_layout.setSpacing(2)

        nav_label = QLabel("MENÜ")
        nav_label.setObjectName("topBarLabel")
        nav_layout.addWidget(nav_label)

        self.nav_btns = QButtonGroup(self)
        self.nav_btns.setExclusive(True)
        nav_items = [
            ("🏠 Ana Sayfa", "ana_sayfa"),
            ("📋 Al-Sat Şartları", "al_sat"),
            ("🤖 AI Karar Motoru", "ai_karar"),
        ]
        self.nav_pages = {}
        for label, key in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav_btns.addButton(btn, len(self.nav_pages))
            nav_layout.addWidget(btn)
            self.nav_pages[key] = btn

        nav_layout.addStretch()

        # Vade seçici
        vade_label = QLabel("VADE")
        vade_label.setObjectName("topBarLabel")
        vade_label.setStyleSheet("margin-top: 12px;")
        nav_layout.addWidget(vade_label)
        self.vade_combo = QComboBox()
        self.vade_combo.addItems(VADE_SECENEKLERI)
        self.vade_combo.setCurrentText("ORTA")
        self.vade_combo.currentTextChanged.connect(self._on_vade_changed)
        nav_layout.addWidget(self.vade_combo)

        body.addWidget(nav_frame)

        # Sayfalar (stacked)
        self.stacked = QStackedWidget()
        self.ana_sayfa = AnaSayfaPage(self)
        self.al_sat_page = AlSatSartlariPage()
        self.ai_karar_page = AIKararMotoruPage(self)

        self.stacked.addWidget(self.ana_sayfa)     # 0
        self.stacked.addWidget(self.al_sat_page)    # 1
        self.stacked.addWidget(self.ai_karar_page)  # 2

        body.addWidget(self.stacked)
        body.setStretchFactor(0, 0)
        body.setStretchFactor(1, 1)

        # Navigasyon olayları
        self.nav_btns.idClicked.connect(self._on_nav_clicked)
        self.nav_btns.button(0).setChecked(True)

        # Stil
        self.setStyleSheet(BLOOMBERG_QSS)

        # İlk veri yükleme
        QTimer.singleShot(100, self._initial_load)

    def _build_top_bar(self):
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(48)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 4, 12, 4)

        self.ticker_label = QLabel("THYAO.IS")
        self.ticker_label.setObjectName("tickerLabel")
        layout.addWidget(self.ticker_label)

        self.price_label = QLabel("0.00")
        self.price_label.setObjectName("tickerLabel")
        self.price_label.setStyleSheet("font-size: 20px; color: #94a3b8;")
        layout.addWidget(self.price_label)

        self.change_label = QLabel("")
        self.change_label.setObjectName("changeLabel")
        layout.addWidget(self.change_label)

        layout.addStretch()

        # Sembol seçici
        self.symbol_combo = QComboBox()
        self.symbol_combo.setMinimumWidth(220)
        for sym, name in COMMON_SYMBOLS.items():
            self.symbol_combo.addItem(f"{sym} — {name}", sym)
        self.symbol_combo.currentIndexChanged.connect(self._on_symbol_changed)
        layout.addWidget(self.symbol_combo)

        # Ajan durum çubuğu
        self.agent_bar = self._build_agent_bar()
        layout.addWidget(self.agent_bar)

        return bar

    def _build_agent_bar(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(6)

        self.agent_labels = {}
        self.agent_progress = {}
        for key, label, color in [
            ("ai", "🧠 AI", "#58a6ff"),
            ("teknik", "📡 Teknik", "#ffeb3b"),
            ("balina", "🐋 Balina", "#00e5ff"),
            ("duygu", "🌍 Duygu", "#ce93d8"),
        ]:
            c = QWidget()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(1)
            lbl = QLabel(label)
            lbl.setObjectName("topBarLabel")
            lbl.setStyleSheet(f"color: {color}; font-size: 10px;")
            cl.addWidget(lbl)
            pb = QProgressBar()
            pb.setFixedSize(60, 4)
            pb.setValue(0)
            cl.addWidget(pb)
            layout.addWidget(c)
            self.agent_labels[key] = lbl
            self.agent_progress[key] = pb

        return widget

    def _on_symbol_changed(self, idx):
        sym = self.symbol_combo.currentData()
        if sym:
            self._current_symbol = sym
            self.ticker_label.setText(sym)
            self._load_data()

    def _on_vade_changed(self, vade):
        self._current_vade = vade

    def _on_nav_clicked(self, idx):
        self.stacked.setCurrentIndex(idx)

    def _initial_load(self):
        self._load_data()

    def _load_data(self):
        """Arka planda veri çek + UI'ı güncelle."""
        import yfinance as yf
        import pandas as pd
        sym = self._current_symbol
        try:
            df = yf.download(sym, period="1y", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            self.data = df
            # Fiyat güncelle
            if not df.empty:
                close = df['Close'].iloc[-1]
                prev = df['Close'].iloc[0]
                chg = ((close / prev) - 1) * 100
                self.price_label.setText(f"{close:.4f}")
                sig = "+" if chg >= 0 else ""
                color = "#4ade80" if chg >= 0 else "#ef4444"
                self.change_label.setText(f"({sig}{chg:.2f}%)")
                self.change_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {color};")
        except:
            self.data = pd.DataFrame()
            self.price_label.setText("—")
            self.change_label.setText("")

        # Sayfaları güncelle
        self.ana_sayfa.refresh()
        self.ai_karar_page.refresh()

    def update_agent_memory(self, memory: dict):
        self.agent_memory = memory
        # Agent bar'ı güncelle
        labels_map = {
            "ai": ("final_score", "🧠 AI"),
            "teknik": ("technical_score", "📡 Teknik"),
            "balina": ("whale_score", "🐋 Balina"),
            "duygu": ("sentiment_score", "🌍 Duygu"),
        }
        for key, (field, label) in labels_map.items():
            score = memory.get(field)
            if score is not None:
                pct = max(0, min(100, int(score)))
                self.agent_labels[key].setText(f"{label} %{pct}")
                self.agent_progress[key].setValue(pct)
            else:
                self.agent_labels[key].setText(label)
                self.agent_progress[key].setValue(0)

        # Sayfaları da güncelle
        self.ana_sayfa.refresh()
        self.ai_karar_page.refresh()
