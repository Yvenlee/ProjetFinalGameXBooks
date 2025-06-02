import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from database.database_manager import initialize_database

def main():
    initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
