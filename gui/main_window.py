import os
import re
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QAction,
    QMessageBox, QTextEdit, QLabel, QTabWidget, QColorDialog,
    QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import requests
from gui.plot_canvas import PlotCanvas
from data.data_fetcher import fetch_json_data
from database.database_manager import initialize_database, clear_database, insert_data, fetch_data
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PIL import Image, ImageOps
from io import BytesIO

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application de Gestion de Jeux")
        self.setGeometry(100, 100, 900, 700)
        self.background_color = "#f0f0f0"
        self.foreground_color = "#333"
        self.font_size = 12
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.central_widget.setLayout(self.layout)

        self.update_stylesheet()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "Accueil")

        self.options_tab = QWidget()
        self.setup_options_tab()
        self.tabs.addTab(self.options_tab, "Options")

        self.json_tab = QWidget()
        self.setup_json_tab()
        self.tabs.addTab(self.json_tab, "Contenu JSON")

        self.books_tab = QWidget()
        self.setup_books_tab()
        self.tabs.addTab(self.books_tab, "Livres")

    def update_stylesheet(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.background_color};
            }}
            QPushButton {{
                background-color: #4CAF50;
                color: {self.foreground_color};
                border: none;
                padding: 12px;
                font-size: {self.font_size}px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QTextEdit {{
                background-color: white;
                color: {self.foreground_color};
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: {self.font_size}px;
                padding: 10px;
            }}
            QLabel {{
                font-size: {self.font_size}px;
                color: {self.foreground_color};
                font-weight: bold;
            }}
        """)

    def setup_main_tab(self):
        layout = QVBoxLayout()

        self.stats_label = QLabel("Statistiques générales :")
        layout.addWidget(self.stats_label)

        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setFont(QFont("Courier", self.font_size))
        self.stats_display.setFixedHeight(100)
        layout.addWidget(self.stats_display)

        self.plot_canvas = PlotCanvas(self, width=5, height=4)
        layout.addWidget(self.plot_canvas)

        self.fetch_btn = QPushButton("Obtenir des données")
        self.fetch_btn.setFont(QFont("Arial", self.font_size))
        self.fetch_btn.clicked.connect(self.fetch_data_from_url)
        layout.addWidget(self.fetch_btn)

        self.clear_btn = QPushButton("Effacer la base de données")
        self.clear_btn.setFont(QFont("Arial", self.font_size))
        self.clear_btn.clicked.connect(self.clear_database)
        layout.addWidget(self.clear_btn)

        self.plot_btn = QPushButton("Afficher les statistiques")
        self.plot_btn.setFont(QFont("Arial", self.font_size))
        self.plot_btn.clicked.connect(self.plot_data)
        layout.addWidget(self.plot_btn)

        self.main_tab.setLayout(layout)

    def setup_options_tab(self):
        layout = QVBoxLayout()

        self.bg_color_btn = QPushButton("Changer la couleur de fond")
        self.bg_color_btn.setFont(QFont("Arial", self.font_size))
        self.bg_color_btn.clicked.connect(self.change_background_color)
        layout.addWidget(self.bg_color_btn)

        self.fg_color_btn = QPushButton("Changer la couleur de texte")
        self.fg_color_btn.setFont(QFont("Arial", self.font_size))
        self.fg_color_btn.clicked.connect(self.change_foreground_color)
        layout.addWidget(self.fg_color_btn)

        self.invert_colors_btn = QPushButton("Inverser les couleurs")
        self.invert_colors_btn.setFont(QFont("Arial", self.font_size))
        self.invert_colors_btn.clicked.connect(self.invert_colors)
        layout.addWidget(self.invert_colors_btn)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(size) for size in range(8, 21)])
        self.font_size_combo.setCurrentText(str(self.font_size))
        self.font_size_combo.setFont(QFont("Arial", self.font_size))
        self.font_size_combo.currentIndexChanged.connect(self.change_font_size)
        layout.addWidget(QLabel("Taille de la police:"))
        layout.addWidget(self.font_size_combo)

        self.options_tab.setLayout(layout)

    def setup_json_tab(self):
        layout = QVBoxLayout()
        self.json_text_viewer = QTextEdit()
        self.json_text_viewer.setReadOnly(True)
        self.json_text_viewer.setFont(QFont("Courier", self.font_size))
        layout.addWidget(self.json_text_viewer)
        self.json_tab.setLayout(layout)

    def setup_books_tab(self):
        layout = QVBoxLayout()

        self.download_book_btn = QPushButton("Télécharger le livre")
        self.download_book_btn.clicked.connect(self.download_book)
        layout.addWidget(self.download_book_btn)

        self.book_display = QTextEdit()
        self.book_display.setReadOnly(True)
        layout.addWidget(self.book_display)

        self.analyze_btn = QPushButton("Analyser les paragraphes")
        self.analyze_btn.clicked.connect(self.analyze_paragraphs)
        layout.addWidget(self.analyze_btn)

        self.book_plot = FigureCanvas(plt.Figure(figsize=(5, 3)))
        layout.addWidget(self.book_plot)

        self.image_btn = QPushButton("Télécharger et modifier les images")
        self.image_btn.clicked.connect(self.process_images)
        layout.addWidget(self.image_btn)

        self.books_tab.setLayout(layout)

    def change_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = color.name()
            self.update_stylesheet()

    def change_foreground_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.foreground_color = color.name()
            self.update_stylesheet()

    def invert_colors(self):
        self.background_color, self.foreground_color = self.foreground_color, self.background_color
        self.update_stylesheet()

    def change_font_size(self, index):
        self.font_size = int(self.font_size_combo.currentText())
        self.update_stylesheet()
        self.stats_display.setFont(QFont("Courier", self.font_size))
        self.json_text_viewer.setFont(QFont("Courier", self.font_size))

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Fichier")

        clear_action = QAction("Effacer la base de données", self)
        clear_action.triggered.connect(self.clear_database)
        file_menu.addAction(clear_action)

        fetch_action = QAction("Obtenir des données", self)
        fetch_action.triggered.connect(self.fetch_data_from_url)
        file_menu.addAction(fetch_action)

    def fetch_data_from_url(self):
        url = "https://gist.githubusercontent.com/Yvenlee/1b028353e059f28a8d00768a2d3791fc/raw/b4f0310ade47261a518c77308900a16a1b53a516/games_cleaned.json"
        try:
            data = fetch_json_data(url)
            insert_data(data)

            if isinstance(data, list):
                preview = json.dumps(data[:5], indent=2)
                full = json.dumps(data, indent=2)
            elif isinstance(data, dict):
                preview = json.dumps(dict(list(data.items())[:5]), indent=2)
                full = json.dumps(data, indent=2)
            else:
                preview = full = str(data)

            self.json_text_viewer.setPlainText(full)

            QMessageBox.information(self, "Succès", "Données téléchargées et stockées avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des données :\n{e}")

    def clear_database(self):
        clear_database()
        self.stats_display.clear()
        self.plot_canvas.ax.clear()
        self.plot_canvas.draw()
        self.json_text_viewer.clear()
        QMessageBox.information(self, "Succès", "Base de données effacée avec succès.")

    def plot_data(self):
        data = fetch_data()
        if not data:
            QMessageBox.warning(self, "Avertissement", "Aucune donnée disponible pour les statistiques.")
            return

        game_stats = {}
        for item in data:
            game_name = item[1]
            hours_played = item[3]
            game_stats.setdefault(game_name, {'total_hours': 0})
            game_stats[game_name]['total_hours'] += hours_played

        game_names = list(game_stats.keys())
        total_hours = [stats['total_hours'] for stats in game_stats.values()]

        total_hours_all = sum(total_hours)
        avg_hours = total_hours_all / len(total_hours) if total_hours else 0
        most_played = max(game_stats.items(), key=lambda x: x[1]['total_hours'])

        stats_text = (
            f"Total des jeux : {len(game_stats)}\n"
            f"Total d'heures jouées : {total_hours_all}\n"
            f"Heures moyennes par jeu : {avg_hours:.2f}\n"
            f"Jeu le plus joué : {most_played[0]} ({most_played[1]['total_hours']} heures)"
        )
        self.stats_display.setPlainText(stats_text)

        self.plot_canvas.ax.clear()
        self.plot_canvas.ax.bar(game_names, total_hours, color='#1f77b4')
        self.plot_canvas.ax.set_xlabel('Nom du Jeu', fontsize=self.font_size)
        self.plot_canvas.ax.set_ylabel('Heures Jouées', fontsize=self.font_size)
        self.plot_canvas.ax.set_title('Total des Heures Jouées par Jeu', fontsize=self.font_size)
        self.plot_canvas.ax.tick_params(axis='x', rotation=45)
        self.plot_canvas.draw()

    def download_book(self):
        try:
            url = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
            response = requests.get(url)
            response.raise_for_status()
            self.book_text = response.text

            title = re.search(r"Title:\s*(.*)", self.book_text)
            author = re.search(r"Author:\s*(.*)", self.book_text)

       
            chapter_start = re.search(r"^CHAPTER\s+([IVXLC\d]+)", self.book_text, re.MULTILINE)
            if not chapter_start:
                raise ValueError("Chapitre 1 non trouvé")

            start_pos = chapter_start.start()

            chapter_2 = re.search(r"^CHAPTER\s+([IVXLC\d]+)", self.book_text[start_pos + 10:], re.MULTILINE)
            if chapter_2:
                end_pos = start_pos + 10 + chapter_2.start()
                chapter_text = self.book_text[start_pos:end_pos]
            else:
                chapter_text = self.book_text[start_pos:start_pos + 4000]

            self.chapter1 = chapter_text

            self.book_display.setPlainText(
                f"Titre: {title.group(1) if title else 'N/A'}\n"
                f"Auteur: {author.group(1) if author else 'N/A'}\n\n"
                + chapter_text
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


    def analyze_paragraphs(self):
        if not hasattr(self, 'chapter1'):
            QMessageBox.warning(self, "Avertissement", "Téléchargez d'abord un livre.")
            return

        paragraphs = [p.strip() for p in self.chapter1.split('\n\n') if p.strip()]
        word_counts = [len(p.split()) for p in paragraphs]
        rounded_counts = [round(wc, -1) for wc in word_counts]

        distribution = {}
        for count in rounded_counts:
            distribution[count] = distribution.get(count, 0) + 1

        ax = self.book_plot.figure.subplots()
        ax.clear()
        ax.bar(distribution.keys(), distribution.values(), color="#c7254e")
        ax.set_title("Distribution des longueurs de paragraphes (Chapitre 1)")
        ax.set_xlabel("Nombre de mots (arrondi à la dizaine)")
        ax.set_ylabel("Nombre de paragraphes")
        self.book_plot.draw()

    def process_images(self):
        try:
            img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Thomson-PP02.jpg/250px-Thomson-PP02.jpg"
            response = requests.get(img_url)
            response.raise_for_status()
            img1 = Image.open(BytesIO(response.content))

            img1 = ImageOps.fit(img1, (300, 400))
            
            logo_path = "assets/jasmin.png"
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.rotate(45, expand=True)
            logo = ImageOps.fit(logo, (100, 100))

            img1.paste(logo, (10, 10), logo)
            output_path = "output/composite_image.png"
            os.makedirs("output", exist_ok=True)
            img1.save(output_path)

            QMessageBox.information(self, "Image traitée", f"Image sauvegardée : {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur image", str(e))
