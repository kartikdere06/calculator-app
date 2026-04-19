import math
import re
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.history_file = Path(__file__).with_name("history.txt")
        self.memory_value = 0.0
        self.grand_total = 0.0
        self.ans_value = 0.0
        self.last_operator = None
        self.last_operand = None
        self.last_was_result = False
        self.theme_mode = "dark"
        self.scientific_mode = True
        self.binary_operators = {"+", "-", "*", "/", "^"}

        self.setWindowTitle("Color Calculator")
        self.resize(480, 760)
        self.setMinimumSize(420, 680)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setMinimumHeight(72)
        self.display.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.display.setPlaceholderText("0")

        self.status_label = QLabel("ANS: 0    MEM: 0    GT: 0")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(12)
        root_layout.addWidget(self.display)
        root_layout.addWidget(self.status_label)

        history_header = QHBoxLayout()
        history_title = QLabel("Calculation History")
        history_title.setObjectName("sectionTitle")
        history_header.addWidget(history_title)
        history_header.addStretch()

        self.theme_button = QPushButton("Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        history_header.addWidget(self.theme_button)

        self.scientific_button = QPushButton("Scientific: ON")
        self.scientific_button.clicked.connect(self.toggle_scientific_mode)
        history_header.addWidget(self.scientific_button)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        history_header.addWidget(self.clear_history_button)
        root_layout.addLayout(history_header)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(160)
        self.history_list.itemClicked.connect(self.use_history_item)
        root_layout.addWidget(self.history_list)

        grid = QGridLayout()
        grid.setSpacing(10)

        buttons = [
            ("MC", 0, 0), ("MR", 0, 1), ("MS", 0, 2), ("GT", 0, 3), ("Back", 0, 4),
            ("sin", 1, 0), ("cos", 1, 1), ("tan", 1, 2), ("√", 1, 3), ("^", 1, 4),
            ("(", 2, 0), (")", 2, 1), ("%", 2, 2), ("±", 2, 3), ("C", 2, 4),
            ("7", 3, 0), ("8", 3, 1), ("9", 3, 2), ("/", 3, 3), ("*", 3, 4),
            ("4", 4, 0), ("5", 4, 1), ("6", 4, 2), ("-", 4, 3), ("+", 4, 4),
            ("1", 5, 0), ("2", 5, 1), ("3", 5, 2), ("=", 5, 3, 1, 2),
            ("0", 6, 0, 1, 2), (".", 6, 2), ("00", 6, 3), ("Mode", 6, 4),
        ]

        for definition in buttons:
            if len(definition) == 3:
                text, row, col = definition
                row_span, col_span = 1, 1
            else:
                text, row, col, row_span, col_span = definition

            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.setMinimumHeight(56)
            button.clicked.connect(lambda checked=False, t=text: self.on_button_click(t))
            button.setProperty("kind", self.button_kind(text))
            if text in {"MC", "MR", "MS", "ANS", "sin", "cos", "tan", "âˆš", "^", "(", ")", "Â±"}:
                button.setProperty("scientific", True)
            grid.addWidget(button, row, col, row_span, col_span)

        root_layout.addLayout(grid)
        self.setLayout(root_layout)

        self.load_history()
        self.apply_theme()
        self.apply_scientific_mode()
        self.update_status()

    def button_kind(self, text):
        if text in {"=", "Mode"}:
            return "accent"
        if text in {"C", "Back", "MC", "MR", "MS", "GT", "ANS"}:
            return "utility"
        if text in {"+", "-", "*", "/", "^", "%", "√", "sin", "cos", "tan", "±"}:
            return "operator"
        return "number"

    def on_button_click(self, text):
        if text == "Mode":
            self.toggle_theme()
            return

        if text == "C":
            self.clear_display()
            return

        if text == "Back":
            self.backspace()
            return

        if text == "=":
            self.evaluate_current_expression()
            return

        if text == "%":
            self.apply_percent()
            return

        if text == "±":
            self.toggle_sign()
            return

        if text == "√":
            self.insert_function("sqrt(")
            return

        if text in {"sin", "cos", "tan"}:
            self.insert_function(f"{text}(")
            return

        if text == "ANS":
            self.insert_token(self.format_number(self.ans_value))
            return

        if text == "GT":
            self.display.setText(self.format_number(self.grand_total))
            self.last_was_result = True
            return

        if text == "MS":
            self.store_memory()
            return

        if text == "MR":
            self.insert_token(self.format_number(self.memory_value))
            return

        if text == "MC":
            self.memory_value = 0.0
            self.update_status()
            return

        self.insert_token(text)

    def clear_display(self):
        self.display.clear()
        self.last_was_result = False
        self.last_operator = None
        self.last_operand = None
        self.update_status()

    def backspace(self):
        if self.last_was_result or self.display.text() == "Error":
            self.display.clear()
            self.last_was_result = False
            return
        self.display.setText(self.display.text()[:-1])

    def insert_function(self, function_text):
        current_text = self.prepare_for_input(function_text)
        self.display.setText(current_text + function_text)

    def insert_token(self, token):
        current_text = self.prepare_for_input(token)

        if token == "00":
            if not current_text or current_text[-1] in self.binary_operators or current_text[-1] == "(":
                token = "0"

        if token in self.binary_operators:
            if not current_text:
                if token != "-":
                    return
            elif current_text[-1] in self.binary_operators:
                current_text = current_text[:-1]
            elif current_text[-1] == "(" and token != "-":
                return

        if token == "." and self.current_number_has_decimal(current_text):
            return

        if token == ")" and self.count_open_parentheses(current_text) <= 0:
            return

        if token == "(" and current_text and (current_text[-1].isdigit() or current_text[-1] == ")"):
            current_text += "*"

        if token in {"ANS"}:
            token = self.format_number(self.ans_value)

        self.display.setText(current_text + token)

    def prepare_for_input(self, token):
        current_text = self.display.text()

        if current_text == "Error":
            current_text = ""

        if self.last_was_result:
            if token in self.binary_operators or token == ")" or token == "%":
                current_text = self.display.text()
            else:
                current_text = ""
                self.last_operator = None
                self.last_operand = None
            self.last_was_result = False

        return current_text

    def current_number_has_decimal(self, text):
        last_number = re.split(r"[+\-*/^()]", text)[-1]
        return "." in last_number

    def count_open_parentheses(self, text):
        return text.count("(") - text.count(")")

    def apply_percent(self):
        current_text = self.display.text()
        if not current_text or current_text == "Error":
            return

        if current_text[-1] in self.binary_operators:
            prefix = current_text[:-1]
            seed_match = re.search(r"(-?\d+(?:\.\d+)?)$", prefix)
            if not seed_match:
                return
            number_text = seed_match.group(1)
            seed_value = float(number_text)
            operator = current_text[-1]

            if self.scientific_mode:
                if operator in {"+", "-"}:
                    percent_value = seed_value * seed_value / 100
                elif operator == "*":
                    percent_value = seed_value / 100
                elif operator == "/":
                    percent_value = seed_value * seed_value / 100
                else:
                    percent_value = seed_value / 100
            else:
                percent_value = seed_value / 100

            updated_text = current_text + self.format_number(percent_value)
            self.display.setText(updated_text)
            self.last_was_result = False
            return

        match = re.search(r"(-?\d+(?:\.\d+)?)$", current_text)
        if not match:
            return

        number_text = match.group(1)
        percent_value = float(number_text) / 100
        prefix = current_text[:match.start(1)]
        base_value, operator = self.extract_percent_base(prefix)

        if base_value is not None and operator in {"+", "-"}:
            percent_value = base_value * percent_value

        updated_text = prefix + self.format_number(percent_value)
        self.display.setText(updated_text)
        self.last_was_result = False

    def toggle_sign(self):
        current_text = self.display.text()
        if not current_text or current_text == "Error":
            self.display.setText("-")
            self.last_was_result = False
            return

        match = re.search(r"(-?\d+(?:\.\d+)?)$", current_text)
        if match:
            number_text = match.group(1)
            toggled = self.format_number(-float(number_text))
            updated_text = current_text[:match.start(1)] + toggled
            self.display.setText(updated_text)
            self.last_was_result = False
        elif self.last_was_result:
            self.display.setText(self.format_number(-self.safe_float(current_text)))
            self.last_was_result = True

    def store_memory(self):
        current_text = self.display.text()
        if not current_text or current_text == "Error":
            self.memory_value = 0.0
        else:
            try:
                self.memory_value = float(self.evaluate_expression(current_text))
            except Exception:
                return
        self.update_status()

    def evaluate_current_expression(self):
        try:
            expression = self.display.text()
            if not expression:
                return

            expression_to_store = expression

            if expression[-1] in self.binary_operators:
                if self.last_operator is None or self.last_operand is None:
                    return
                expression = expression + self.last_operand
                expression_to_store = expression

            if self.last_was_result and self.last_operator and self.last_operand:
                expression = f"{expression}{self.last_operator}{self.last_operand}"
                expression_to_store = expression
            else:
                operator, operand = self.extract_last_operation(expression)
                if operator and operand:
                    self.last_operator = operator
                    self.last_operand = operand

            result = self.evaluate_expression(expression)
            self.ans_value = result
            self.grand_total += result
            formatted_result = self.format_number(result)
            self.display.setText(formatted_result)
            self.add_to_history(expression_to_store, formatted_result)
            self.last_was_result = True
            self.update_status()
        except Exception:
            self.display.setText("Error")
            self.last_was_result = False
            self.last_operator = None
            self.last_operand = None

    def evaluate_expression(self, expression):
        translated = self.translate_expression(expression)
        allowed_names = {
            "sin": lambda value: math.sin(math.radians(value)),
            "cos": lambda value: math.cos(math.radians(value)),
            "tan": lambda value: math.tan(math.radians(value)),
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
            "ans": self.ans_value,
        }
        return eval(translated, {"__builtins__": {}}, allowed_names)

    def translate_expression(self, expression):
        translated = expression.replace("^", "**")
        translated = translated.replace("√", "sqrt")
        translated = re.sub(r"(?<![A-Za-z])ANS", "ans", translated)
        translated = re.sub(r"(\d)([A-Za-z(])", r"\1*\2", translated)
        translated = re.sub(r"(\))(\d|[A-Za-z])", r"\1*\2", translated)
        translated = re.sub(r"([A-Za-z])(\d)", r"\1*\2", translated)
        return translated

    def extract_last_operation(self, expression):
        match = re.search(r"([+\-*/^])(-?\d+(?:\.\d+)?)\)?$", expression)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def extract_percent_base(self, prefix):
        stripped_prefix = prefix.rstrip()
        if not stripped_prefix:
            return None, None

        operator_match = re.search(r"([+\-*/^])\s*$", stripped_prefix)
        if not operator_match:
            return None, None

        operator = operator_match.group(1)
        left_expression = stripped_prefix[:operator_match.start(1)].strip()
        if not left_expression:
            return None, operator

        try:
            base_value = float(self.evaluate_expression(left_expression))
        except Exception:
            return None, operator

        return base_value, operator

    def add_to_history(self, expression, result):
        entry = f"{expression} = {result}"
        self.history_list.insertItem(0, entry)
        self.save_history()

    def clear_history(self):
        self.history_list.clear()
        self.save_history()

    def use_history_item(self, item):
        entry = item.text()
        if " = " not in entry:
            return
        result = entry.split(" = ", 1)[1]
        self.display.setText(result)
        try:
            self.ans_value = float(result)
        except ValueError:
            pass
        self.last_was_result = True
        self.update_status()

    def load_history(self):
        if not self.history_file.exists():
            return
        for line in self.history_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self.history_list.addItem(line.strip())

    def save_history(self):
        entries = [self.history_list.item(index).text() for index in range(self.history_list.count())]
        self.history_file.write_text("\n".join(entries), encoding="utf-8")

    def update_status(self):
        self.status_label.setText(
            f"ANS: {self.format_number(self.ans_value)}    MEM: {self.format_number(self.memory_value)}    GT: {self.format_number(self.grand_total)}"
        )

    def toggle_scientific_mode(self):
        self.scientific_mode = not self.scientific_mode
        self.apply_scientific_mode()

    def apply_scientific_mode(self):
        self.scientific_button.setText(
            "Scientific: ON" if self.scientific_mode else "Scientific: OFF"
        )
        for button in self.findChildren(QPushButton):
            if button.property("scientific"):
                button.setVisible(self.scientific_mode)
        self.adjustSize()

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        if self.theme_mode == "dark":
            self.theme_button.setText("Light Mode")
            self.setStyleSheet(
                """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f172a, stop:0.35 #172554, stop:0.7 #1d4ed8, stop:1 #0f766e);
                    color: #eef2ff;
                    font-family: "Segoe UI";
                }
                QLineEdit {
                    background-color: rgba(15, 23, 42, 0.88);
                    border: 2px solid #38bdf8;
                    border-radius: 18px;
                    color: #f8fafc;
                    padding: 14px 16px;
                }
                QLabel#sectionTitle {
                    font-size: 18px;
                    font-weight: 700;
                    color: #fef3c7;
                }
                QLabel {
                    color: #dbeafe;
                    font-size: 13px;
                }
                QListWidget {
                    background-color: rgba(15, 23, 42, 0.72);
                    border: 1px solid #67e8f9;
                    border-radius: 16px;
                    padding: 8px;
                    color: #ecfeff;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 10px;
                }
                QListWidget::item:selected {
                    background-color: rgba(34, 197, 94, 0.25);
                }
                QPushButton {
                    border: none;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: 700;
                    padding: 12px;
                }
                QPushButton[kind="number"] {
                    background-color: rgba(255, 255, 255, 0.16);
                    color: #f8fafc;
                }
                QPushButton[kind="operator"] {
                    background-color: rgba(251, 191, 36, 0.9);
                    color: #1f2937;
                }
                QPushButton[kind="utility"] {
                    background-color: rgba(244, 114, 182, 0.88);
                    color: #fff7ed;
                }
                QPushButton[kind="accent"] {
                    background-color: rgba(34, 197, 94, 0.95);
                    color: #052e16;
                }
                QPushButton:hover {
                    border: 2px solid rgba(255, 255, 255, 0.35);
                }
                """
            )
        else:
            self.theme_button.setText("Dark Mode")
            self.setStyleSheet(
                """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #fff7ed, stop:0.35 #fde68a, stop:0.7 #f9a8d4, stop:1 #bfdbfe);
                    color: #1f2937;
                    font-family: "Segoe UI";
                }
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.86);
                    border: 2px solid #fb7185;
                    border-radius: 18px;
                    color: #111827;
                    padding: 14px 16px;
                }
                QLabel#sectionTitle {
                    font-size: 18px;
                    font-weight: 700;
                    color: #7c2d12;
                }
                QLabel {
                    color: #334155;
                    font-size: 13px;
                }
                QListWidget {
                    background-color: rgba(255, 255, 255, 0.78);
                    border: 1px solid #f97316;
                    border-radius: 16px;
                    padding: 8px;
                    color: #1e293b;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 10px;
                }
                QListWidget::item:selected {
                    background-color: rgba(56, 189, 248, 0.24);
                }
                QPushButton {
                    border: none;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: 700;
                    padding: 12px;
                }
                QPushButton[kind="number"] {
                    background-color: rgba(255, 255, 255, 0.72);
                    color: #0f172a;
                }
                QPushButton[kind="operator"] {
                    background-color: rgba(56, 189, 248, 0.92);
                    color: #082f49;
                }
                QPushButton[kind="utility"] {
                    background-color: rgba(251, 146, 60, 0.92);
                    color: #431407;
                }
                QPushButton[kind="accent"] {
                    background-color: rgba(236, 72, 153, 0.92);
                    color: #500724;
                }
                QPushButton:hover {
                    border: 2px solid rgba(15, 23, 42, 0.18);
                }
                """
            )

    def format_number(self, value):
        if isinstance(value, str):
            return value
        if math.isclose(value, int(value), rel_tol=0, abs_tol=1e-10):
            return str(int(value))
        return f"{value:.10f}".rstrip("0").rstrip(".")

    def safe_float(self, text):
        try:
            return float(text)
        except ValueError:
            return 0.0

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        text = event.text()

        if key in {Qt.Key.Key_Enter, Qt.Key.Key_Return}:
            self.on_button_click("=")
            return
        if key == Qt.Key.Key_Backspace:
            self.on_button_click("Back")
            return
        if key == Qt.Key.Key_Delete or key == Qt.Key.Key_Escape:
            self.on_button_click("C")
            return

        keyboard_map = {
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            ".": ".",
            "(": "(",
            ")": ")",
            "^": "^",
        }

        if text.isdigit():
            self.on_button_click(text)
            return
        if text in keyboard_map:
            self.on_button_click(keyboard_map[text])
            return

        if text.lower() == "s":
            self.on_button_click("sin")
            return
        if text.lower() == "c":
            self.on_button_click("cos")
            return
        if text.lower() == "t":
            self.on_button_click("tan")
            return
        if text.lower() == "r":
            self.on_button_click("√")
            return
        if text.lower() == "m":
            self.on_button_click("MR")
            return
        if text.lower() == "a":
            self.on_button_click("ANS")
            return

        super().keyPressEvent(event)


app = QApplication(sys.argv)
window = Calculator()
window.show()
sys.exit(app.exec())
