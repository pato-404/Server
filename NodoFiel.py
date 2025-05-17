import sys
import threading
import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QListWidget,
    QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QDialogButtonBox, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

CONFIG_FILE = "config.json"
LOGS_DIR = "logs"

# HANDLERS
class CustomStaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self._custom_directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        return

class CustomSimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        response_text = f"Hola desde servidor en puerto {self.server.server_port}"
        self.wfile.write(response_text.encode())

        if hasattr(self.server, 'callback'):
            message = f"GET {self.path} desde {self.client_address[0]}:{self.client_address[1]}"
            self.server.callback(message)

    def log_message(self, format, *args):
        return

class HttpServerThread(threading.Thread):
    def __init__(self, port, message_callback, server_name, mode, static_dir=None):
        super().__init__()
        self.port = port
        self.message_callback = message_callback
        self.server_name = server_name
        self.mode = mode
        self.static_dir = static_dir

        if mode == "static":
            handler_class = lambda *args, **kwargs: CustomStaticHandler(*args, directory=static_dir, **kwargs)
        else:
            handler_class = CustomSimpleHandler

        self.httpd = HTTPServer(('0.0.0.0', port), handler_class)
        self.httpd.callback = message_callback
        self.httpd.server_name = server_name
        self.daemon = True

    def run(self):
        try:
            self.httpd.serve_forever()
        except Exception:
            pass

    def stop(self):
        self.httpd.shutdown()

class Communicate(QObject):
    new_message = pyqtSignal(str, int, str)

class NewServerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuevo Servidor HTTP")
        self.setFixedSize(400, 200)

        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        layout.addRow("Nombre del servidor:", self.name_input)

        self.port_input = QLineEdit()
        layout.addRow("Puerto:", self.port_input)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Servidor simple (texto fijo)", "Servidor estático (archivos)"])
        layout.addRow("Tipo de servidor:", self.mode_combo)

        self.dir_button = QPushButton("Seleccionar carpeta raíz (solo para estático)")
        self.dir_button.setEnabled(False)
        layout.addRow(self.dir_button)

        self.dir_label = QLabel("<ninguna>")
        layout.addRow("Carpeta raíz:", self.dir_label)

        self.dir_button.clicked.connect(self.select_directory)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.static_dir = None

    def on_mode_changed(self, index):
        self.dir_button.setEnabled(index == 1)
        if index != 1:
            self.static_dir = None
            self.dir_label.setText("<ninguna>")

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta raíz")
        if dir_path:
            self.static_dir = dir_path
            self.dir_label.setText(dir_path)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'port': self.port_input.text().strip(),
            'mode': "static" if self.mode_combo.currentIndex() == 1 else "simple",
            'static_dir': self.static_dir
        }

# MAIN APP
class ServerManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administrador de Servidores HTTP")
        self.resize(950, 550)

        os.makedirs(LOGS_DIR, exist_ok=True)
        self.comm = Communicate()
        self.comm.new_message.connect(self.add_message)

        self.servers = {}
        self.messages = {}
        self.port_to_name = {}

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        left_panel = QVBoxLayout()
        layout.addLayout(left_panel, 1)

        self.servers_list = QListWidget()
        self.servers_list.clicked.connect(self.on_server_selected)
        left_panel.addWidget(QLabel("Servidores abiertos"))
        left_panel.addWidget(self.servers_list)

        self.open_button = QPushButton("Abrir servidor")
        self.open_button.clicked.connect(self.open_server_dialog)
        left_panel.addWidget(self.open_button)

        self.close_button = QPushButton("Cerrar servidor seleccionado")
        self.close_button.clicked.connect(self.close_selected_server)
        left_panel.addWidget(self.close_button)

        # NUEVOS BOTONES DE LOGS
        self.export_logs_button = QPushButton("Exportar logs")
        self.export_logs_button.clicked.connect(self.export_logs)
        self.export_logs_button.setEnabled(False)
        left_panel.addWidget(self.export_logs_button)

        self.clear_logs_button = QPushButton("Limpiar logs")
        self.clear_logs_button.clicked.connect(self.clear_logs)
        self.clear_logs_button.setEnabled(False)
        left_panel.addWidget(self.clear_logs_button)

        self.load_logs_button = QPushButton("Cargar logs históricos")
        self.load_logs_button.clicked.connect(self.load_logs_from_file)
        self.load_logs_button.setEnabled(False)
        left_panel.addWidget(self.load_logs_button)

        right_panel = QVBoxLayout()
        layout.addLayout(right_panel, 2)

        self.messages_label = QLabel("Selecciona un servidor para ver mensajes")
        self.messages_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.messages_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar mensaje...")
        self.search_input.textChanged.connect(self.filter_messages)
        right_panel.addWidget(self.search_input)

        self.messages_list = QListWidget()
        right_panel.addWidget(self.messages_list)

        self.current_port = None

        self.load_config()

    def open_server_dialog(self):
        dlg = NewServerDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            name = data['name']
            port_text = data['port']
            mode = data['mode']
            static_dir = data['static_dir']

            if not name or not port_text.isdigit():
                QMessageBox.warning(self, "Error", "Nombre o puerto inválido.")
                return
            port = int(port_text)
            if port in self.servers:
                QMessageBox.warning(self, "Error", f"Ya hay un servidor en puerto {port}.")
                return
            if mode == "static" and not static_dir:
                QMessageBox.warning(self, "Error", "Seleccione una carpeta raíz.")
                return

            try:
                server_thread = HttpServerThread(
                    port,
                    lambda msg: self.comm.new_message.emit(msg, port, name),
                    name,
                    mode,
                    static_dir
                )
                server_thread.start()
                self.servers[port] = server_thread
                self.messages[port] = []
                self.port_to_name[port] = name
                self.servers_list.addItem(f"{name} (Puerto: {port})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el servidor:\n{e}")

    def add_message(self, message, port, name):
        # Añadir fecha y hora al mensaje
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"

        self.messages[port].append(full_message)
        log_path = os.path.join(LOGS_DIR, f"servidor_{port}.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
        if self.current_port == port:
            self.filter_messages()

    def on_server_selected(self):
        selected = self.servers_list.currentItem()
        if not selected:
            self.current_port = None
            self.export_logs_button.setEnabled(False)
            self.clear_logs_button.setEnabled(False)
            self.load_logs_button.setEnabled(False)
            self.messages_label.setText("Selecciona un servidor para ver mensajes")
            self.messages_list.clear()
            return
        try:
            port = int(selected.text().split("Puerto:")[1].strip(" )"))
        except Exception:
            port = None

        self.current_port = port
        self.export_logs_button.setEnabled(True)
        self.clear_logs_button.setEnabled(True)
        self.load_logs_button.setEnabled(True)
        self.messages_label.setText(f"Mensajes del servidor {self.port_to_name.get(port,'')} (Puerto {port})")
        self.filter_messages()

    def filter_messages(self):
        if self.current_port is None:
            self.messages_list.clear()
            return
        search = self.search_input.text().lower()
        self.messages_list.clear()
        for msg in self.messages[self.current_port]:
            if search in msg.lower():
                self.messages_list.addItem(msg)

    def close_selected_server(self):
        if self.current_port is None:
            QMessageBox.warning(self, "Error", "Seleccione un servidor primero.")
            return
        thread = self.servers.get(self.current_port)
        if thread:
            thread.stop()
            thread.join()
            del self.servers[self.current_port]
            del self.messages[self.current_port]
            del self.port_to_name[self.current_port]
            self.current_port = None
            self.servers_list.clear()
            self.messages_list.clear()
            self.search_input.clear()
            self.load_config()
        else:
            QMessageBox.warning(self, "Error", "Servidor no encontrado.")

    def export_logs(self):
        if self.current_port is None:
            QMessageBox.warning(self, "Error", "Seleccione un servidor primero.")
            return
        log_path = os.path.join(LOGS_DIR, f"servidor_{self.current_port}.log")
        if not os.path.exists(log_path):
            QMessageBox.information(self, "Información", "No hay logs para exportar.")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar logs como", f"servidor_{self.current_port}.log", "Archivos de texto (*.log *.txt)")
        if save_path:
            try:
                with open(log_path, "r", encoding="utf-8") as fsrc, open(save_path, "w", encoding="utf-8") as fdst:
                    fdst.write(fsrc.read())
                QMessageBox.information(self, "Éxito", "Logs exportados correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar logs:\n{e}")

    def clear_logs(self):
        if self.current_port is None:
            QMessageBox.warning(self, "Error", "Seleccione un servidor primero.")
            return
        reply = QMessageBox.question(self, "Confirmar", "¿Seguro que quieres limpiar los logs? Esto no se puede deshacer.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            log_path = os.path.join(LOGS_DIR, f"servidor_{self.current_port}.log")
            try:
                open(log_path, "w", encoding="utf-8").close()
                self.messages[self.current_port].clear()
                self.filter_messages()
                QMessageBox.information(self, "Éxito", "Logs limpiados correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudieron limpiar los logs:\n{e}")

    def load_logs_from_file(self):
        if self.current_port is None:
            QMessageBox.warning(self, "Error", "Seleccione un servidor primero.")
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de logs", "", "Archivos de texto (*.log *.txt)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                self.messages[self.current_port] = [line.strip() for line in lines if line.strip()]
                self.filter_messages()
                QMessageBox.information(self, "Éxito", "Logs cargados correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudieron cargar los logs:\n{e}")

    def save_config(self):
        data = {
            "servers": []
        }
        for port, thread in self.servers.items():
            data["servers"].append({
                "name": self.port_to_name.get(port, ""),
                "port": port,
                "mode": thread.mode,
                "static_dir": thread.static_dir
            })
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuración:\n{e}")

    def load_config(self):
        self.servers_list.clear()
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for srv in data.get("servers", []):
                    name = srv.get("name", "Servidor")
                    port = srv.get("port", 0)
                    mode = srv.get("mode", "simple")
                    static_dir = srv.get("static_dir", None)
                    if port in self.servers:
                        continue
                    try:
                        server_thread = HttpServerThread(
                            port,
                            lambda msg, p=port, n=name: self.comm.new_message.emit(msg, p, n),
                            name,
                            mode,
                            static_dir
                        )
                        server_thread.start()
                        self.servers[port] = server_thread
                        self.messages[port] = []
                        self.port_to_name[port] = name
                        self.servers_list.addItem(f"{name} (Puerto: {port})")
                    except Exception:
                        pass
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar la configuración:\n{e}")

    def closeEvent(self, event):
        self.save_config()
        for thread in self.servers.values():
            thread.stop()
            thread.join()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ServerManagerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
