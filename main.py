import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QGridLayout


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setGeometry(200, 200, 300, 400)

        self.display = QLineEdit()
        self.display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.display)

        grid = QGridLayout()
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("=", 3, 2), ("+", 3, 3),
            ("C", 4, 0)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.clicked.connect(lambda checked=False, t=text: self.on_button_click(t))
            grid.addWidget(button, row, col)

        layout.addLayout(grid)
        self.setLayout(layout)

    def on_button_click(self, text):
        if text == "C":
            self.display.clear()
        elif text == "=":
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except Exception:
                self.display.setText("Error")
        else:
            self.display.setText(self.display.text() + text)


app = QApplication(sys.argv)
window = Calculator()
window.show()
sys.exit(app.exec())
