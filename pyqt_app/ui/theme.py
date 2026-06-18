BLOOMBERG_QSS = """
/* === GENEL === */
QMainWindow, QWidget {
    background-color: #0b1120;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Outfit', sans-serif;
    font-size: 12px;
}

/* === SOL NAVIGASYON === */
QFrame#navPanel {
    background-color: #0F172A;
    border-right: 1px solid #1e293b;
}
QPushButton#navBtn {
    background: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#navBtn:hover {
    background: rgba(255,255,255,0.06);
    color: #e2e8f0;
}
QPushButton#navBtn:checked {
    background: rgba(56,189,248,0.12);
    color: #38bdf8;
    font-weight: 600;
    border-left: 3px solid #ff5722;
}

/* === ÜST ÇUBUK === */
QFrame#topBar {
    background-color: #0F172A;
    border-bottom: 1px solid #1e293b;
    padding: 4px 12px;
}
QLabel#topBarLabel {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
QLabel#tickerLabel {
    color: #f8fafc;
    font-size: 26px;
    font-weight: 700;
}
QLabel#changeLabel {
    font-size: 15px;
    font-weight: 600;
}

/* === METRİK KARTLARI === */
QFrame#metricCard {
    background: rgba(30,41,59,0.4);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px 16px;
}
QLabel#metricTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
QLabel#metricValue {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
}
QLabel#metricDelta {
    font-size: 12px;
    font-weight: 600;
}

/* === KONSENSÜS WIDGET === */
QFrame#consWidget {
    background: #0F172A;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 10px;
}
QLabel#consTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
QLabel#consScore {
    font-size: 22px;
    font-weight: 700;
}

/* === KONSENSÜS PANELİ (ortak) === */
QFrame#consensusPanel {
    border-radius: 12px;
    padding: 12px 16px;
}
QLabel#panelTitle {
    color: #94a3b8;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.4px;
}
QLabel#panelScore {
    font-size: 28px;
    font-weight: 700;
}
QLabel#panelSignal {
    font-size: 18px;
    font-weight: 700;
}

/* === BUTONLAR === */
QPushButton {
    background: rgba(255,255,255,0.06);
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    color: white;
    border: none;
}
QPushButton:pressed {
    background: #1e40af;
}

/* === SELECT / COMBOBOX === */
QComboBox {
    background: rgba(255,255,255,0.06);
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 20px;
}
QComboBox:hover { border-color: #38bdf8; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: none; border: solid #94a3b8; border-width: 0 2px 2px 0; padding: 3px; transform: rotate(45deg); }
QComboBox QAbstractItemView {
    background: #1e293b; color: #e2e8f0; border: 1px solid #334155;
    selection-background-color: #334155; outline: none;
}

/* === TAB WIDGET === */
QTabWidget::pane {
    background: transparent;
    border: none;
}
QTabBar::tab {
    background: transparent;
    color: #64748b;
    border: none;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}
QTabBar::tab:hover { color: #e2e8f0; }
QTabBar::tab:selected { color: #38bdf8; border-bottom: 2px solid #38bdf8; }

/* === KAYDIRMA ÇUBUĞU === */
QScrollBar:vertical {
    background: rgba(0,0,0,0.1);
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.2); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* === PROGRESS BAR === */
QProgressBar {
    background: rgba(255,255,255,0.05);
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 0px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #3b82f6);
    border-radius: 4px;
}

/* === SPIN BOX === */
QSpinBox, QDoubleSpinBox {
    background: rgba(255,255,255,0.06);
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}

/* === SPLITTER === */
QSplitter::handle {
    background: #1e293b;
    width: 1px;
}

/* === STATUS BAR === */
QStatusBar {
    background: #0F172A;
    border-top: 1px solid #1e293b;
    color: #64748b;
    font-size: 11px;
}

/* === TABLO === */
QTableWidget, QTableView {
    background: #0F172A;
    color: #e2e8f0;
    border: 1px solid #1e293b;
    gridline-color: #1e293b;
    selection-background-color: rgba(56,189,248,0.15);
}
QHeaderView::section {
    background: #1e293b;
    color: #94a3b8;
    border: none;
    padding: 6px 10px;
    font-weight: 600;
    font-size: 11px;
}

/* === TEXT EDIT === */
QTextEdit, QPlainTextEdit {
    background: #0F172A;
    color: #e2e8f0;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 6px;
    font-size: 12px;
    selection-background-color: rgba(56,189,248,0.3);
}

/* === CHECKBOX === */
QCheckBox {
    color: #cbd5e1;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #475569;
}
QCheckBox::indicator:checked {
    background: #38bdf8;
    border-color: #38bdf8;
}

/* === LİSTE === */
QListWidget {
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-size: 12px;
    outline: none;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
}
QListWidget::item:hover {
    background: rgba(255,255,255,0.05);
}
QListWidget::item:selected {
    background: rgba(56,189,248,0.15);
    color: #38bdf8;
}
"""

COMMON_SYMBOLS = {
    "THYAO.IS": "Türk Hava Yolları", "EREGL.IS": "Ereğli Demir Çelik",
    "AKBNK.IS": "Akbank", "GARAN.IS": "Garanti BBVA", "ISCTR.IS": "İş Bankası C",
    "KCHOL.IS": "Koç Holding", "SAHOL.IS": "Sabancı Holding", "TUPRS.IS": "Tüpraş",
    "ASELS.IS": "Aselsan", "SASA.IS": "SASA Polyester", "BTC-USD": "Bitcoin",
    "GC=F": "Altın (Ons)", "USDTRY=X": "USD/TRY", "USDKZT=X": "USD/KZT",
    "^GSPC": "S&P 500",
}

VADE_SECENEKLERI = ["KISA", "ORTA", "UZUN"]
