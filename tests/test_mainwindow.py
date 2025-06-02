import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

import sys

app = QApplication(sys.argv)

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    @patch('data.data_fetcher.fetch_json_data')
    @patch('database.database_manager.insert_data')
    def test_fetch_data_from_url(self, mock_insert, mock_fetch):
        mock_fetch.return_value = [{"id": 1, "game": "Test Game", "platform": "PC", "hours_played": 10}]
        self.window.fetch_data_from_url()

        mock_fetch.assert_called_once()
        mock_insert.assert_called_once()
        self.assertIn("Test Game", self.window.json_text_viewer.toPlainText())

    @patch('database.database_manager.clear_database')
    def test_clear_database(self, mock_clear):
        self.window.stats_display.setPlainText("Texte de test")
        self.window.json_text_viewer.setPlainText("Données JSON")
        self.window.clear_database()

        self.assertEqual(self.window.stats_display.toPlainText(), "")
        self.assertEqual(self.window.json_text_viewer.toPlainText(), "")
        mock_clear.assert_called_once()

    @patch('database.database_manager.fetch_data')
    def test_plot_data_empty(self, mock_fetch):
        mock_fetch.return_value = []
        self.window.plot_data()

    @patch('database.database_manager.fetch_data')
    def test_plot_data_filled(self, mock_fetch):
        mock_fetch.return_value = [
            (1, "Game A", "PC", 10),
            (2, "Game B", "PC", 5),
            (3, "Game A", "PC", 7)
        ]
        self.window.plot_data()

        text = self.window.stats_display.toPlainText()
        self.assertIn("Game A", text)
        self.assertIn("Total d'heures jouées", text)

if __name__ == '__main__':
    unittest.main()
