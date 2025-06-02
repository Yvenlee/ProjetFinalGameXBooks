from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QAction, QMessageBox
from PyQt5.QtCore import Qt
from .plot_canvas import PlotCanvas
from data.data_fetcher import fetch_json_data
from database.database_manager import initialize_database, clear_database, insert_data, fetch_data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application de Gestion de Jeux")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.plot_canvas = PlotCanvas(self, width=5, height=4)
        self.layout.addWidget(self.plot_canvas)

        self.fetch_btn = QPushButton("Obtenir des données")
        self.fetch_btn.clicked.connect(self.fetch_data)
        self.layout.addWidget(self.fetch_btn)

        self.clear_btn = QPushButton("Effacer la base de données")
        self.clear_btn.clicked.connect(self.clear_database)
        self.layout.addWidget(self.clear_btn)

        self.plot_btn = QPushButton("Afficher le graphique")
        self.plot_btn.clicked.connect(self.plot_data)
        self.layout.addWidget(self.plot_btn)

        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Fichier")

        clear_action = QAction("Effacer la base de données", self)
        clear_action.triggered.connect(self.clear_database)
        file_menu.addAction(clear_action)

        fetch_action = QAction("Obtenir des données", self)
        fetch_action.triggered.connect(self.fetch_data)
        file_menu.addAction(fetch_action)

    def fetch_data(self):
        try:
            url = "URL_TO_YOUR_JSON_DATA"  # Remplacez par l'URL de votre fichier JSON
            data = fetch_json_data(url)
            insert_data(data)
            QMessageBox.information(self, "Succès", "Données téléchargées et stockées avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def clear_database(self):
        clear_database()
        QMessageBox.information(self, "Succès", "Base de données effacée avec succès.")

    def plot_data(self):
        data = fetch_data()
        if not data:
            QMessageBox.warning(self, "Avertissement", "Aucune donnée disponible pour le graphique.")
            return

        names = [item[1] for item in data]
        sizes = [item[2] for item in data]

        self.plot_canvas.ax.clear()
        self.plot_canvas.ax.bar(names, sizes)
        self.plot_canvas.ax.set_title("Taille des Jeux")
        self.plot_canvas.ax.set_xlabel("Nom du Jeu")
        self.plot_canvas.ax.set_ylabel("Taille")
        self.plot_canvas.draw()
