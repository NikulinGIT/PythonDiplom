import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QMenu, QInputDialog, QAction, QTabWidget, QWidget,
    QVBoxLayout, QPushButton, QHBoxLayout,QFileDialog
)
from PyQt5.QtCore import Qt, QPoint
import os
import sqlite3
import unittest
from PyQt5.QtWidgets import QApplication, QTableWidget
import csv
import pandas as pd


app = QApplication([])  # Обязателен для создания виджетов в тестах

class TestTableWidget(unittest.TestCase):
    def setUp(self):
        # Создание приложения PyQt для тестирования
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()

        # Создание таблицы и заполнение данными
        self.table_widget = QTableWidget(self.window)
        self.table_widget.setRowCount(3)  # 3 строки
        self.table_widget.setColumnCount(3)  # 3 столбца
        self.table_widget.setHorizontalHeaderLabels(["Имя", "Возраст", "профессия"])

        data = [
            ["Аня", "27", "врач"],
            ["Катя", "44", "учитель"],
            ["Саня", "65", "космонавт"]
        ]
        for row in range(len(data)):
            for col in range(len(data[row])):
                self.table_widget.setItem(row, col, QTableWidgetItem(data[row][col]))

    def test_table_creation(self):
        """Проверка, что таблица была создана с правильными размерами"""
        self.assertEqual(self.table_widget.rowCount(), 3, "Количество строк должно быть 3")
        self.assertEqual(self.table_widget.columnCount(), 3, "Количество столбцов должно быть 3")

    def test_table_data(self):
        """Проверка, что таблица правильно наполнилась данными"""
        expected_data = [
            ["Аня", "27", "врач"],
            ["Катя", "44", "учитель"],
            ["Саня", "65", "космонавт"]
        ]

        for row in range(3):
            for col in range(3):
                item = self.table_widget.item(row, col)
                self.assertEqual(item.text(), expected_data[row][col], f"Неверное значение в ячейке {row},{col}")
    def test_delete_cell(self):
        """Проверка удаления содержимого ячейки"""
        # До удаления содержимого ячейки, она должна быть заполнена
        cell_item = self.table_widget.item(0, 0)
        self.assertEqual(cell_item.text(), "Аня", "Содержимое ячейки должно быть 'Аня'")

        # Удаляем содержимое ячейки (0, 0)
        self.table_widget.setItem(0, 0, None)

        # После удаления содержимого, ячейка должна быть пустой
        cell_item = self.table_widget.item(0, 0)
        self.assertIsNone(cell_item, "Ячейка должна быть пустой")

class TableWidget(QTableWidget):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        for col in range(columns):
            self.setHorizontalHeaderItem(col, QTableWidgetItem(f"Столбец {col + 1}"))

    def open_context_menu(self, position: QPoint):
        index = self.indexAt(position)
        col = index.column() if index.isValid() else -1
        row=index.row() if index.isValid() else -1
        menu = QMenu()

        add_row_action = QAction("Добавить строку", self)
        add_row_action.triggered.connect(self.add_row)
        menu.addAction(add_row_action)

        if col >= 0:
            delete_row_action = QAction("Удалить строку", self)
            delete_row_action.triggered.connect(lambda: self.delete_row(row))
            menu.addAction(delete_row_action)

            add_column_action = QAction("Добавить столбец", self)
            add_column_action.triggered.connect(lambda: self.add_column(col))
            menu.addAction(add_column_action)

            rename_column_action = QAction("Переименовать столбец", self)
            rename_column_action.triggered.connect(lambda: self.rename_column(col))
            menu.addAction(rename_column_action)

            delete_column_action = QAction("Удалить столбец", self)
            delete_column_action.triggered.connect(lambda: self.delete_column(col))
            menu.addAction(delete_column_action)

        menu.exec_(self.viewport().mapToGlobal(position))

    def add_row(self):
        self.insertRow(self.rowCount())
    def delete_row(self,row):
        self.removeRow(row)  # Удалит строку с индексом 1 (вторая строка)

    def add_column(self, after_column):
        self.insertColumn(after_column + 1)
        self.setHorizontalHeaderItem(after_column + 1, QTableWidgetItem(f"Столбец {self.columnCount()}"))

    def rename_column(self, column):
        text, ok = QInputDialog.getText(self, "Переименовать столбец", "Новое имя столбца:")
        if ok and text:
            self.setHorizontalHeaderItem(column, QTableWidgetItem(text))

    def delete_column(self, column):
        self.removeColumn(column)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Динамические вкладки с таблицами")
        self.resize(800, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.add_tab_button = QPushButton("Добавить вкладку")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        button_layout.addWidget(self.add_tab_button)
        self.layout.addLayout(button_layout)

        self.add_tab_button = QPushButton("Добавить результаты сканирования")
        self.add_tab_button.clicked.connect(self.add_scan_tab)
        button_layout.addWidget(self.add_tab_button)
        self.layout.addLayout(button_layout)

        # Вкладки
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab_count = 0  # Счётчик вкладок
        self.add_new_tab()  # Создаем первую вкладку при старте

        buttom_layout = QHBoxLayout(self)  # кнопка "Быстрое сканирование оборудования"
        self.save_button = QPushButton("Сохранить таблицу")
        self.save_button.clicked.connect(self.save_current_table)

        self.update_button= QPushButton("Загрузить таблицу")
        self.update_button.clicked.connect(self.update_current_table)

        buttom_layout.addWidget(self.save_button)
        buttom_layout.addWidget(self.update_button)
        self.layout.addLayout(buttom_layout)

    def add_scan_tab(self):
        conn = sqlite3.connect('Device_parametres.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM devices')
        main_devices = cursor.fetchall()

        list_param = []
        rows=len(main_devices)
        table_devices = TableWidget(rows, 4)
        table_devices.setHorizontalHeaderLabels(["Primary key", "IP", "System", "Activity"])

        widget_devices = QWidget()
        layout = QVBoxLayout(widget_devices)
        layout.addWidget(table_devices)
        row_position = table_devices.rowCount()
        i=0
        first_elements_main_devices = [item[0] for item in main_devices]

        for text in main_devices:
           table_devices.setItem(i, 0, QTableWidgetItem(str(text[0])))
           table_devices.setItem(i, 1, QTableWidgetItem(text[1]))
           table_devices.setItem(i, 2, QTableWidgetItem(text[2]))
           table_devices.setItem(i, 3, QTableWidgetItem(str(text[3])))
           if i<row_position:i=i+1
           else:
               row_position = table_devices.rowCount()
               table_devices.insertRow(row_position)
        self.tab_count += 1
        self.tabs.addTab(widget_devices, f"devices")

        cursor.execute('SELECT * FROM MAC')
        cap_devices = cursor.fetchall()

        list_param = []
        rows = len(cap_devices)
        table_MAC = TableWidget(rows, 3)
        table_MAC.setHorizontalHeaderLabels(["Primary key", "IP", "MAC"])

        widget_MAC = QWidget()
        layout = QVBoxLayout(widget_MAC)
        layout.addWidget(table_MAC)
        row_position = table_MAC.rowCount()
        i = 0
        for text in cap_devices:
            table_MAC.setItem(i, 0, QTableWidgetItem(str(text[0])))
            index_IP = first_elements_main_devices.index(text[1])
            table_MAC.setItem(i, 1, QTableWidgetItem(main_devices[index_IP][1]))
            table_MAC.setItem(i, 2, QTableWidgetItem(str(text[2])))
            if i < row_position:
                i = i + 1
            else:
                row_position = table_devices.rowCount()
                table_devices.insertRow(row_position)
        self.tab_count += 1
        self.tabs.addTab(widget_MAC, f"MAC")

        cursor.execute('SELECT * FROM Ports')
        cap_devices = cursor.fetchall()

        list_param = []
        rows = len(cap_devices)
        table_ports = TableWidget(rows, 3)
        table_ports.setHorizontalHeaderLabels(["Primary key", "IP", "Port"])

        widget_ports = QWidget()
        layout = QVBoxLayout(widget_ports)
        layout.addWidget(table_ports)
        row_position = table_ports.rowCount()
        i = 0
        for text in cap_devices:
            table_ports.setItem(i, 0, QTableWidgetItem(str(text[0])))
            index_IP = first_elements_main_devices.index(text[1])
            table_ports.setItem(i, 1, QTableWidgetItem(main_devices[index_IP][1]))
            table_ports.setItem(i, 2, QTableWidgetItem(str(text[2])))
            if i < row_position:
                i = i + 1
            else:
                row_position = table_ports.rowCount()
                table_ports.insertRow(row_position)
        self.tab_count += 1
        self.tabs.addTab(widget_ports, f"Port")

    def update_current_table(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл для загрузки", "", "CSV Files (*.csv)")
        if path:
          df = pd.read_csv(path)
          column_names = list(df.columns)
          num_rows = df.shape[0]  # Количество строк
          num_cols = df.shape[1]  # Количество столбцов
          table = TableWidget(num_rows, num_cols)
          table.setHorizontalHeaderLabels(column_names)
          widget = QWidget()
          layout = QVBoxLayout(widget)
          layout.addWidget(table)
          row_position = table.rowCount()
          rows_as_lists = df.values.tolist()
          for row in rows_as_lists:
             i = 0
             for column in row:
               table.setItem(i, 0, QTableWidgetItem(str(column)))
               i=i+1
             row_position = table.rowCount()
             table.insertRow(row_position)
          self.tab_count += 1
          filename = os.path.basename(path)
          self.tabs.addTab(widget, filename)
    def save_current_table(self):
        current_widget = self.tabs.currentWidget()
        if not current_widget:
            return

        table = current_widget.findChild(QTableWidget)
        if not table:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Выберите файл для сохранения", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = [table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else ""
                           for col in range(table.columnCount())]
                writer.writerow(headers)

                for row in range(table.rowCount()):
                    row_data = [table.item(row, col).text() if table.item(row, col) else ""
                                for col in range(table.columnCount())]
                    writer.writerow(row_data)
    def add_new_tab(self):
        table = TableWidget(4, 4)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(table)

        self.tab_count += 1
        self.tabs.addTab(widget, f"Вкладка {self.tab_count}")

    def add_rez_tab(self):
       print('po')
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #unittest.main()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
