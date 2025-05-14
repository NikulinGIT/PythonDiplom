import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QListWidget, QFileDialog


class TextEditorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Text Editor with Versions")
        self.setGeometry(300, 100, 600, 400)

        self.initUI()

    def initUI(self):
        # Создаем основной лэйаут
        layout = QVBoxLayout()

        # Создаем Tab Widget для двух вкладок
        self.tabs = QTabWidget()
        self.tab1 = QWidget()  # Вкладка для ввода текста
        self.tab2 = QWidget()  # Вкладка для отображения версий

        # Вкладка 1: Ввод текста
        self.text_input = QTextEdit(self)
        self.save_button = QPushButton("Сохранить скрипт", self)
        self.load_button = QPushButton("Загрузить скрипты", self)

        # Сигналы кнопок
        self.save_button.clicked.connect(self.save_text)
        self.load_button.clicked.connect(self.load_text)

        tab1_layout = QVBoxLayout()
        tab1_layout.addWidget(self.text_input)
        tab1_layout.addWidget(self.save_button)
        tab1_layout.addWidget(self.load_button)

        self.tab1.setLayout(tab1_layout)

        # Вкладка 2: Список версий текста
        self.version_list = QListWidget(self)
        self.delete_button = QPushButton("Удалить выбранную версию", self)

        # Сигнал для удаления
        self.delete_button.clicked.connect(self.delete_version)

        tab2_layout = QVBoxLayout()
        tab2_layout.addWidget(self.version_list)
        tab2_layout.addWidget(self.delete_button)

        self.tab2.setLayout(tab2_layout)

        # Добавляем вкладки в основной виджет
        self.tabs.addTab(self.tab1, "Избранные скрипты")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # Список для хранения версий текста
        self.text_versions = []

    def save_text(self):
        """Сохраняем текст в список версий и файл."""
        text = self.text_input.toPlainText()
        if text:
            # Сохраняем в список и в список виджета
            self.text_versions.append(text)
            self.version_list.addItem(text)

            # Открываем диалог для выбора пути сохранения
            file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить текст в файл", "", "Text Files (*.txt);;All Files (*)")
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as file:file.write(text)

    def load_text(self):
        """Загружаем текст из файла."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                text = file.read()
                self.text_input.setPlainText(text)

    def delete_version(self):
        """Удаляем выбранную версию текста из списка."""
        selected_item = self.version_list.currentItem()
        if selected_item:
            row = self.version_list.row(selected_item)
            del self.text_versions[row]
            self.version_list.takeItem(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextEditorApp()
    window.show()
    sys.exit(app.exec_())
