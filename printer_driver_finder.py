# -*- coding: utf-8 -*-
# Printer Driver Finder
# جميع الحقوق محفوظة © khalid aldawish 2025

import sys
import usb.core
import usb.util
import webbrowser
import socket
import threading

from PyQt5.QtWidgets import (
    QApplication, QSplashScreen, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QLabel, QProgressBar, QMenuBar, QAction, QDialog, QTextEdit, QLineEdit, QCheckBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap

# --------- الترجمة ---------
translations = {
    'en': {
        'title': "Printer Driver Finder",
        'search': "Search for Printers",
        'usb': "USB",
        'network': "Network",
        'snmp': "SNMP",
        'mdns': "Bonjour/mDNS",
        'printer_name': "Printer Name",
        'driver_name': "Driver Name",
        'driver_id': "Driver ID",
        'download': "Download",
        'no_printers': "No printers found.",
        'found': "Found {n} printer(s).",
        'loading': "Loading...",
        'lang': "Language",
        'no_usb_printers': "No USB printers detected.\nTry connecting a printer and click again.",
        'no_network_printers': "No Network printers detected.",
        'searching': "Searching for printers...",
        'search_usb': "USB Only",
        'search_network': "Network Only",
        'search_both': "USB & Network",
        'about': "About",
        'about_text': "Printer Driver Finder\nVersion 1.0.0\n\nDeveloped by: khalid aldawish\n\n- Detects printers via USB, Network, SNMP, Bonjour/mDNS\n- Supports English and Arabic\n- Direct search for drivers\n- Progress bar for scan\n- Advanced search options\n\n© 2025 khalid aldawish. All rights reserved.",
        'refresh': "Refresh",
        'history': "History",
        'clear_history': "Clear History",
        'copied': "Copied to clipboard.",
        'advanced': "Advanced",
        'ip_range': "IP Range",
        'protocols': "Protocols",
        'search_by_model': "Search by Model",
        'manufacturer': "Manufacturer",
        'search': "Search",
        'close': "Close",
        'invalid_range': "Invalid IP range.",
        'searching_mdns': "Searching via mDNS...",
        'searching_snmp': "Searching via SNMP...",
        'searching_network': "Searching via Network...",
        'searching_usb': "Searching via USB...",
        'filter': "Filter",
    },
    'ar': {
        'title': "باحث تعريفات الطابعات",
        'search': "بحث عن الطابعات",
        'usb': "USB",
        'network': "الشبكة",
        'snmp': "SNMP",
        'mdns': "Bonjour/mDNS",
        'printer_name': "اسم الطابعة",
        'driver_name': "اسم التعريف",
        'driver_id': "رقم التعريف",
        'download': "تحميل",
        'no_printers': "لم يتم العثور على أي طابعة.",
        'found': "تم العثور على {n} طابعة.",
        'loading': "جاري التحميل...",
        'lang': "اللغة",
        'no_usb_printers': "لم يتم اكتشاف أي طابعة USB.\nحاول توصيل طابعة واضغط مرة أخرى.",
        'no_network_printers': "لم يتم اكتشاف أي طابعة عبر الشبكة.",
        'searching': "جاري البحث عن الطابعات...",
        'search_usb': "USB فقط",
        'search_network': "الشبكة فقط",
        'search_both': "USB + الشبكة",
        'about': "حول البرنامج",
        'about_text': "باحث تعريفات الطابعات\nالإصدار 1.0.0\n\nتطوير: خالد الدويش\n\n- كشف الطابعات عبر USB والشبكة و SNMP و mDNS\n- يدعم العربية والإنجليزية\n- بحث مباشر عن التعاريف\n- شريط تقدم للفحص\n- خيارات بحث متقدمة\n\n© 2025 خالد الدويش. جميع الحقوق محفوظة.",
        'refresh': "تحديث",
        'history': "السجل",
        'clear_history': "مسح السجل",
        'copied': "تم النسخ إلى الحافظة.",
        'advanced': "خيارات متقدمة",
        'ip_range': "نطاق IP",
        'protocols': "البروتوكولات",
        'search_by_model': "بحث بالاسم أو الموديل",
        'manufacturer': "الشركة",
        'search': "بحث",
        'close': "إغلاق",
        'invalid_range': "نطاق IP غير صالح.",
        'searching_mdns': "جاري البحث عبر mDNS...",
        'searching_snmp': "جاري البحث عبر SNMP...",
        'searching_network': "جاري البحث عبر الشبكة...",
        'searching_usb': "جاري البحث عبر USB...",
        'filter': "تصفية",
    }
}

HISTORY_FILE = "printer_history.txt"

def save_to_history(entry):
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception:
        return []

def clear_history():
    try:
        open(HISTORY_FILE, "w").close()
    except Exception:
        pass

def safe_usb_string(device, idx):
    try:
        return usb.util.get_string(device, idx)
    except Exception:
        return None

def get_printer_name_from_usb(device):
    manufacturer = safe_usb_string(device, getattr(device, 'iManufacturer', 0)) or f"Vendor:{hex(getattr(device, 'idVendor', 0))}"
    product = safe_usb_string(device, getattr(device, 'iProduct', 0)) or f"Product:{hex(getattr(device, 'idProduct', 0))}"
    return f"{manufacturer} {product}".strip()

def find_usb_printers_safe():
    printers = []
    try:
        devices = list(usb.core.find(find_all=True))
    except Exception:
        devices = []
    seen = set()
    for device in devices:
        try:
            if getattr(device, 'bDeviceClass', 0) == 7:
                pass
            else:
                has_printer_if = False
                try:
                    for cfg in device:
                        if getattr(cfg, 'bInterfaceClass', 0) == 7:
                            has_printer_if = True
                            break
                except Exception:
                    pass
                if not has_printer_if:
                    continue
            printer_name = get_printer_name_from_usb(device)
            driver_name = f"{printer_name} Driver"
            driver_id = f"{hex(getattr(device, 'idVendor', 0))}:{hex(getattr(device, 'idProduct', 0))}"
            search_q = f"{printer_name} printer driver"
            download_url = f"https://www.google.com/search?q={search_q.replace(' ', '+')}"
            if (printer_name, driver_id) in seen:
                continue
            seen.add((printer_name, driver_id))
            printers.append({
                "printer_name": printer_name,
                "driver_name": driver_name,
                "driver_id": driver_id,
                "download_url": download_url,
                "type": "usb"
            })
        except Exception:
            continue
    return printers

def snmp_get_printer_info(ip):
    try:
        from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
    except ImportError:
        return None
    oids = [
        ('1.3.6.1.2.1.1.1.0', 'Description'),
        ('1.3.6.1.2.1.25.3.2.1.3.1', 'Model'),
        ('1.3.6.1.2.1.43.5.1.1.16.1', 'Product'),
    ]
    info = {}
    for oid, name in oids:
        try:
            iterator = getCmd(SnmpEngine(),
                            CommunityData('public', mpModel=0),
                            UdpTransportTarget((ip, 161), timeout=1, retries=0),
                            ContextData(),
                            ObjectType(ObjectIdentity(oid)))
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            if errorIndication or errorStatus:
                continue
            for varBind in varBinds:
                info[name] = str(varBind[1])
        except Exception:
            continue
    return info if info else None

class SNMPScanner(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    def __init__(self, ip_range):
        super().__init__()
        self.ip_range = ip_range

    def scan(self):
        printers = []
        total = self.ip_range[1] - self.ip_range[0] + 1
        for idx, i in enumerate(range(self.ip_range[0], self.ip_range[1] + 1)):
            ip = f"{self.ip_range[2]}.{i}"
            info = snmp_get_printer_info(ip)
            if info:
                printers.append({
                    "printer_name": info.get('Description', f"SNMP Printer ({ip})"),
                    "driver_name": info.get('Model', "Generic SNMP Printer"),
                    "driver_id": ip,
                    "download_url": f"https://www.google.com/search?q=printer+driver+{ip}",
                    "type": "snmp"
                })
            self.progress.emit(int((idx+1)/total*100))
        self.finished.emit(printers)

def mdns_search(timeout=2):
    try:
        from zeroconf import Zeroconf, ServiceBrowser
    except ImportError:
        return []
    import time
    class PrinterListener:
        def __init__(self):
            self.found = []
        def add_service(self, zeroconf, type, name):
            info = zeroconf.get_service_info(type, name)
            if info and info.addresses:
                ip = ".".join(str(b) for b in info.addresses[0])
                self.found.append({
                    "printer_name": info.name,
                    "driver_name": "mDNS Printer",
                    "driver_id": ip,
                    "download_url": f"https://www.google.com/search?q=printer+driver+{ip}",
                    "type": "mdns"
                })
    zeroconf = Zeroconf()
    listener = PrinterListener()
    browser = ServiceBrowser(zeroconf, "_ipp._tcp.local.", listener)
    time.sleep(timeout)
    zeroconf.close()
    return listener.found

class MDNSScanner(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    def __init__(self, timeout=2):
        super().__init__()
        self.timeout = timeout
    def scan(self):
        printers = mdns_search(timeout=self.timeout)
        self.progress.emit(100)
        self.finished.emit(printers)

class NetworkScanner(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    def __init__(self, ip_range):
        super().__init__()
        self.ip_range = ip_range

    def scan(self):
        printers = []
        total = self.ip_range[1] - self.ip_range[0] + 1
        for idx, i in enumerate(range(self.ip_range[0], self.ip_range[1] + 1)):
            ip = f"{self.ip_range[2]}.{i}"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.12)
                result = sock.connect_ex((ip, 9100))
                if result == 0:
                    printers.append({
                        "printer_name": f"Network Printer ({ip})",
                        "driver_name": f"Generic Network Printer Driver",
                        "driver_id": ip,
                        "download_url": f"https://www.google.com/search?q=network+printer+driver+{ip}",
                        "type": "network"
                    })
                sock.close()
            except Exception:
                pass
            self.progress.emit(int((idx+1)/total*100))
        self.finished.emit(printers)

class AboutDialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)

class HistoryDialog(QDialog):
    def __init__(self, history, lang, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translations[lang]['history'])
        self.resize(500, 300)
        self.lang = lang
        layout = QVBoxLayout(self)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setText("\n".join(history) if history else translations[lang]['no_printers'])
        layout.addWidget(self.text)
        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copy" if lang == "en" else "نسخ")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.clear_btn = QPushButton(translations[lang]['clear_history'])
        self.clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text.toPlainText())
        QMessageBox.information(self, "Info", translations[self.lang]['copied'])

    def clear_history(self):
        clear_history()
        self.text.setText(translations[self.lang]['no_printers'])

class AdvancedDialog(QDialog):
    def __init__(self, lang, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translations[lang]['advanced'])
        self.resize(350, 250)
        self.lang = lang
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.ip_prefix = QLineEdit("192.168.1")
        self.ip_start = QSpinBox()
        self.ip_start.setRange(1, 254)
        self.ip_start.setValue(1)
        self.ip_end = QSpinBox()
        self.ip_end.setRange(1, 254)
        self.ip_end.setValue(254)
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel(translations[lang]['ip_range']))
        ip_layout.addWidget(self.ip_prefix)
        ip_layout.addWidget(self.ip_start)
        ip_layout.addWidget(QLabel("-"))
        ip_layout.addWidget(self.ip_end)
        form.addRow(translations[lang]['ip_range'] + ":", ip_layout)
        self.chk_usb = QCheckBox(translations[lang]['usb'])
        self.chk_network = QCheckBox(translations[lang]['network'])
        self.chk_snmp = QCheckBox(translations[lang]['snmp'])
        self.chk_mdns = QCheckBox(translations[lang]['mdns'])
        self.chk_usb.setChecked(True)
        self.chk_network.setChecked(True)
        proto_layout = QHBoxLayout()
        proto_layout.addWidget(self.chk_usb)
        proto_layout.addWidget(self.chk_network)
        proto_layout.addWidget(self.chk_snmp)
        proto_layout.addWidget(self.chk_mdns)
        form.addRow(translations[lang]['protocols'] + ":", proto_layout)
        self.model_search = QLineEdit()
        form.addRow(translations[lang]['search_by_model'] + ":", self.model_search)
        layout.addLayout(form)
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton(translations[lang]['search'])
        self.btn_close = QPushButton(translations[lang]['close'])
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_close.clicked.connect(self.reject)

    def get_options(self):
        prefix = self.ip_prefix.text().strip()
        start = self.ip_start.value()
        end = self.ip_end.value()
        try:
            parts = prefix.split('.')
            if len(parts) != 3 or not all(0 <= int(p) <= 255 for p in parts):
                raise ValueError("Invalid IP prefix")
            if start > end:
                start, end = end, start
            ip_range = (start, end, prefix)
        except Exception:
            ip_range = (1, 254, "192.168.1")
        protocols = {
            'usb': self.chk_usb.isChecked(),
            'network': self.chk_network.isChecked(),
            'snmp': self.chk_snmp.isChecked(),
            'mdns': self.chk_mdns.isChecked(),
        }
        model = self.model_search.text().strip()
        return ip_range, protocols, model

class MainWindow(QMainWindow):
    def __init__(self, lang='en'):
        super().__init__()
        self.lang = lang
        self.tr = translations[self.lang]
        self.setWindowTitle(self.tr['title'])
        self.setGeometry(300, 100, 900, 600)
        self.history = load_history()
        self.network_scanner = None
        self.adv_ip_range = (1, 254, "192.168.1")
        self.adv_protocols = {'usb': True, 'network': True, 'snmp': False, 'mdns': False}
        self.adv_model = ""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        menubar = QMenuBar(self)
        about_action = QAction(self.tr['about'], self)
        about_action.triggered.connect(self.show_about)
        history_action = QAction(self.tr['history'], self)
        history_action.triggered.connect(self.show_history)
        refresh_action = QAction(self.tr['refresh'], self)
        refresh_action.triggered.connect(self.refresh)
        adv_action = QAction(self.tr['advanced'], self)
        adv_action.triggered.connect(self.show_advanced)
        menubar.addAction(about_action)
        menubar.addAction(history_action)
        menubar.addAction(refresh_action)
        menubar.addAction(adv_action)
        self.setMenuBar(menubar)

        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', 'العربية'])
        self.lang_combo.setMaximumWidth(120)
        self.lang_combo.currentIndexChanged.connect(self.switch_language)
        lang_label = QLabel(self.tr['lang'])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        self.layout.addLayout(lang_layout)

        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText(self.tr['filter'])
        self.filter_edit.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(QLabel(self.tr['filter']))
        filter_layout.addWidget(self.filter_edit)
        self.layout.addLayout(filter_layout)

        self.search_btn = QPushButton(self.tr['search'])
        self.search_btn.clicked.connect(self.search_printers)
        self.advanced_btn = QPushButton(self.tr['advanced'])
        self.advanced_btn.clicked.connect(self.show_advanced)
        adv_btn_layout = QHBoxLayout()
        adv_btn_layout.addWidget(self.search_btn)
        adv_btn_layout.addWidget(self.advanced_btn)
        self.layout.addLayout(adv_btn_layout)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.layout.addWidget(self.progress)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            self.tr['printer_name'],
            self.tr['driver_name'],
            self.tr['driver_id'],
            "Type",
            self.tr['download'],
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.status = QLabel("")
        self.layout.addWidget(self.status)

        self.all_printers = []

    def switch_language(self):
        idx = self.lang_combo.currentIndex()
        self.lang = 'ar' if idx == 1 else 'en'
        self.tr = translations[self.lang]
        self.setWindowTitle(self.tr['title'])
        self.search_btn.setText(self.tr['search'])
        self.advanced_btn.setText(self.tr['advanced'])
        self.table.setHorizontalHeaderLabels([
            self.tr['printer_name'],
            self.tr['driver_name'],
            self.tr['driver_id'],
            "Type",
            self.tr['download'],
        ])
        self.status.setText("")
        self.setMenuBar(None)
        menubar = QMenuBar(self)
        about_action = QAction(self.tr['about'], self)
        about_action.triggered.connect(self.show_about)
        history_action = QAction(self.tr['history'], self)
        history_action.triggered.connect(self.show_history)
        refresh_action = QAction(self.tr['refresh'], self)
        refresh_action.triggered.connect(self.refresh)
        adv_action = QAction(self.tr['advanced'], self)
        adv_action.triggered.connect(self.show_advanced)
        menubar.addAction(about_action)
        menubar.addAction(history_action)
        menubar.addAction(refresh_action)
        menubar.addAction(adv_action)
        self.setMenuBar(menubar)
        self.filter_edit.setPlaceholderText(self.tr['filter'])

    def show_advanced(self):
        dlg = AdvancedDialog(self.lang, self)
        if dlg.exec_():
            self.adv_ip_range, self.adv_protocols, self.adv_model = dlg.get_options()

    def search_printers(self):
        self.status.setText(self.tr['searching'])
        self.progress.setVisible(True)
        self.progress.setValue(0)
        QApplication.processEvents()
        self.table.setRowCount(0)
        threads = []
        self.all_printers = []
        count_protocols = sum(self.adv_protocols.values())
        count_finished = [0]  # list to be mutable in closure

        def add_printers(printers):
            self.all_printers += printers
            count_finished[0] += 1
            if count_finished[0] == count_protocols:
                self.progress.setValue(100)
                self.progress.setVisible(False)
                self.display_printers(self.all_printers)
                for p in self.all_printers:
                    entry = f"{p['printer_name']} | {p['driver_name']} | {p['driver_id']} | {p.get('type','-')}"
                    save_to_history(entry)
        def progress_callback(val):
            self.progress.setValue(val)

        if self.adv_protocols.get('usb'):
            self.status.setText(self.tr['searching_usb'])
            QApplication.processEvents()
            def usb_worker():
                printers = find_usb_printers_safe()
                self.progress.setValue(100)
                add_printers(printers)
            t = threading.Thread(target=usb_worker, daemon=True)
            t.start()
            threads.append(t)
        if self.adv_protocols.get('network'):
            self.status.setText(self.tr['searching_network'])
            self.network_scanner = NetworkScanner(self.adv_ip_range)
            self.network_scanner.progress.connect(progress_callback)
            self.network_scanner.finished.connect(add_printers)
            threading.Thread(target=self.network_scanner.scan, daemon=True).start()
        if self.adv_protocols.get('snmp'):
            self.status.setText(self.tr['searching_snmp'])
            self.snmp_scanner = SNMPScanner(self.adv_ip_range)
            self.snmp_scanner.progress.connect(progress_callback)
            self.snmp_scanner.finished.connect(add_printers)
            threading.Thread(target=self.snmp_scanner.scan, daemon=True).start()
        if self.adv_protocols.get('mdns'):
            self.status.setText(self.tr['searching_mdns'])
            self.mdns_scanner = MDNSScanner(timeout=2)
            self.mdns_scanner.progress.connect(progress_callback)
            self.mdns_scanner.finished.connect(add_printers)
            threading.Thread(target=self.mdns_scanner.scan, daemon=True).start()

    def finish_search(self, printers, net_printers):
        self.progress.setValue(100)
        self.progress.setVisible(False)
        all_printers = printers + net_printers
        self.display_printers(all_printers)
        for p in all_printers:
            entry = f"{p['printer_name']} | {p['driver_name']} | {p['driver_id']} | {p.get('type','-')}"
            save_to_history(entry)

    def display_printers(self, printers):
        filter_text = self.filter_edit.text().strip().lower()
        if filter_text:
            filtered = [p for p in printers if filter_text in p["printer_name"].lower() or filter_text in p["driver_name"].lower()]
        else:
            filtered = printers
        if self.adv_model:
            filtered = [p for p in filtered if self.adv_model.lower() in p["printer_name"].lower() or self.adv_model.lower() in p["driver_name"].lower()]
        self.table.setRowCount(0)
        if not filtered:
            QMessageBox.information(self, self.tr['title'], self.tr['no_printers'])
            self.status.setText(self.tr['no_printers'])
            return
        self.table.setRowCount(len(filtered))
        for row, p in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(p["printer_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(p["driver_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(p["driver_id"])))
            ttype = self.tr.get(p.get("type"), p.get("type", ""))
            self.table.setItem(row, 3, QTableWidgetItem(ttype))
            btn = QPushButton(self.tr['download'])
            btn.clicked.connect(lambda _, url=p["download_url"]: self.download_driver(url))
            self.table.setCellWidget(row, 4, btn)
        self.status.setText(self.tr['found'].format(n=len(filtered)))

    def apply_filter(self):
        self.display_printers(self.all_printers)

    def download_driver(self, url):
        webbrowser.open(url)

    def show_about(self):
        dlg = AboutDialog(self.tr['about_text'], self)
        dlg.exec_()

    def show_history(self):
        self.history = load_history()
        dlg = HistoryDialog(self.history, self.lang, self)
        dlg.exec_()

    def refresh(self):
        self.search_printers()

def main():
    app = QApplication(sys.argv)
    # شاشة تحميل بيضاء فقط بدون صورة
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.white)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setFont(splash.font())
    splash.showMessage("Loading... 0%", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    splash.show()
    for i in range(1, 101):
        QTimer.singleShot(i*10, lambda p=i: splash.showMessage(f"Loading... {p}%", Qt.AlignBottom | Qt.AlignCenter, Qt.black))
    def start_main():
        app.main_win = MainWindow()
        app.main_win.show()
        splash.finish(app.main_win)
    QTimer.singleShot(1300, start_main)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()