import os
import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QProgressBar, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtCore import Qt, QTimer, QRectF

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(800, 300)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(30, 30, 740, 50)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 15px;
                background-color: #FFFFFF;
                text-align: center;
                font-size: 24px;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #3b99fc;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.set_rounded_corners(30)

        # Cargar la versión desde version.qp
        self.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        version_text = self.get_version_from_qp()

        self.version_label = QLabel(version_text, self)
        self.version_label.setStyleSheet("color: grey; font-size: 12px;")
        self.version_label.adjustSize()
        self.version_label.move(self.width() - self.version_label.width() - 10,
                                self.height() - self.version_label.height() - 10)

        self.items_to_check = ["config.json", "logs"]
        self.total_checks = len(self.items_to_check)
        self.current_check = 0
        self.progress_value = 0
        self.steps_per_check = 100 // max(self.total_checks, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_timer)

    def set_rounded_corners(self, radius):
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def start(self):
        self.show()
        self.timer.start(20)

    def handle_timer(self):
        if self.progress_value < 100:
            self.progress_value += 1

            if (self.progress_value % self.steps_per_check == 0) and (self.current_check < self.total_checks):
                item_name = self.items_to_check[self.current_check]
                full_path = os.path.join(self.base_dir, item_name)

                if os.path.isfile(full_path):
                    print(f"✔ Archivo encontrado: {item_name}")
                elif os.path.isdir(full_path):
                    print(f"✔ Carpeta encontrada: {item_name}")
                else:
                    print(f"✘ No encontrado: {item_name} - Creando...")

                    if item_name.endswith(".json"):
                        with open(full_path, "w") as f:
                            json.dump({}, f)
                        print(f"Archivo {item_name} creado.")
                    else:
                        os.makedirs(full_path, exist_ok=True)
                        print(f"Carpeta {item_name} creada.")

                self.current_check += 1

            self.progress.setValue(self.progress_value)
        else:
            self.timer.stop()
            self.close()

            # Ejecutar NodoFiel.exe al terminar el splash
            exe_path = os.path.join(self.base_dir, "NodoFiel.exe")
            if os.path.isfile(exe_path):
                print("Ejecutando NodoFiel.exe...")
                os.startfile(exe_path)  # Solo funciona en Windows
            else:
                print("NodoFiel.exe no encontrado.")

    def get_version_from_qp(self):
        qp_path = os.path.join(self.base_dir, "version.qp")
        today = datetime.now().date()

        if os.path.isfile(qp_path):
            try:
                with open(qp_path, "r") as f:
                    data = json.load(f)
                version = data.get("version", "v1.0.0")
                fecha_str = data.get("fecha", "")
                fecha_qp = datetime.strptime(fecha_str, "%Y-%m-%d").date()

                if fecha_qp <= today:
                    return version
                else:
                    return "v1.0.0"
            except Exception as e:
                print(f"Error leyendo version.qp: {e}")
                return "v1.0.0"
        else:
            print("Archivo version.qp no encontrado.")
            return "v1.0.0"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.start()
    sys.exit(app.exec())
