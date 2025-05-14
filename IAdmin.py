from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QMenu, QAction, QMessageBox,
    QVBoxLayout, QSplitter, QTabWidget, QHBoxLayout, QFileDialog,QInputDialog,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QPushButton, QApplication,QGraphicsPixmapItem,QSpacerItem, QSizePolicy
    )
import console
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,QIcon
import sys
import additionalfunctons as addfun
import Icon_modul as icon
import os
import sqlite3
import  NetworkScanner as ns
import fast_buttons as fb
import tables
import subprocess
import unittest
import test


class Work_space(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)  # контейнер для окна Work_space
        '''Работа с вкладками'''
        self.tab_widget = QTabWidget(self)  # Создаем QTabWidget для вкладок
        self.tab_widget.setTabBar(addfun.EditableTabBar())
        self.tab_counter = 1  # Счётчик вкладок

        layout.addWidget(self.tab_widget)  # собираем Widget в контейнер
        buttom_plus = QPushButton()
        buttom_plus.setIcon(QIcon("files/plus.png"))
        buttom_plus.setIconSize(buttom_plus.sizeHint())  # подгоняет размер иконки под кнопку
        buttom_plus.setFixedSize(50, 50)  # зафиксировать размер кнопки

        buttom_minus = QPushButton()
        buttom_minus.setIcon(QIcon("files/minus.png"))
        buttom_minus.setIconSize(buttom_minus.sizeHint())  # подгоняет размер иконки под кнопку
        buttom_minus.setFixedSize(50, 50)  # зафиксировать размер кнопки

        buttom_plus.clicked.connect(self.zoom_in)
        buttom_minus.clicked.connect(self.zoom_out)

        # Layout для кнопок

        button_scale_layout = QHBoxLayout()
        button_scale_layout.addWidget(buttom_plus)
        button_scale_layout.addWidget(buttom_minus)
        button_scale_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(button_scale_layout)

        buttom_layout = QHBoxLayout(self)  # кнопка "Быстрое сканирование оборудования"
        update_button = QPushButton("Архив оборудования")  # кнопка "Полное сканирование оборудования"
        update_button.setFixedSize(250, 20)
        update_button.clicked.connect(self.archive_icon_image)

        fast_button = QPushButton("Быстрое сканирование оборудования")  # кнопка "Полное сканирование оборудования"
        fast_button.setFixedSize(250, 20)
        fast_button.clicked.connect(self.update_icon_image)

        test_button = QPushButton("Тестирование сканирование оборудования")  # кнопка "Полное сканирование оборудования"
        test_button.setFixedSize(250, 20)
        test_button.clicked.connect(lambda : self.test_update_icon_image())

        buttom_layout.addWidget(fast_button)
        buttom_layout.addWidget(test_button)
        buttom_layout.addWidget(update_button)

        layout.addLayout(buttom_layout)  # Потом кнопки в строку
        self.setLayout(layout)

    '''меню при нажатии правой кнопки мыши'''
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)  # Создаем контекстное меню

        '''Добавляем действия в контекстное меню'''
        action1 = QAction("Добавить вкладку", self)
        action1.triggered.connect(self.add_tab)
        context_menu.addAction(action1)

        action2 = QAction("Удалить вкладку", self)
        action2.triggered.connect(self.remove_tab)
        context_menu.addAction(action2)

        if self.tab_counter > 1:
            action3 = QAction("Добавить фоновое изображение", self)
            tab_index = self.tab_widget.currentIndex()
            action3.triggered.connect(lambda: self.add_Fon())
            context_menu.addAction(action3)

            action4 = QAction("Добавить устройство", self)
            tab_index = self.tab_widget.currentIndex()
            action4.triggered.connect(lambda: self.add_icon_image("", "","",True))
            context_menu.addAction(action4)

        # Показываем контекстное меню в позиции правого клика
        context_menu.exec_(event.globalPos())

    '''добавление вкладки '''
    def add_tab(self):
        # Создаем новый Widget для новой вкладки
        tab_activ = QWidget()
        self.tab_widget.addTab(tab_activ, f"Вкладка {self.tab_counter}")
        self.tab_counter += 1

        self.tab_layout = QVBoxLayout(tab_activ)  # Компоновщик для вкладки
        scene = QGraphicsScene()
        view = QGraphicsView(scene)
        view = addfun.AutoResizingGraphicsView(scene)
        self.tab_layout .addWidget(view)

    '''удаление вкладки '''
    def remove_tab(self):
        # Удаляем вкладку по индексу (последнюю вкладку)
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)
            self.tab_counter -= 1

    '''установить фоновое изображение '''
    def add_Fon(self):
      try:
        current_widget = self.tab_widget.currentWidget()
        # Найдём QGraphicsView внутри текущей вкладки
        graphics_view = current_widget.findChild(QGraphicsView)
        if graphics_view:
            current_scene = graphics_view.scene()
            filename, _ = QFileDialog.getOpenFileName(
                None, "Выбрать файл", "", "Все файлы (*);;Текстовые файлы (*.txt)"
            )

            self.background  = QGraphicsPixmapItem(QPixmap(filename))
            self.background .setZValue(-1)
            current_scene.addItem(self.background )


      except:print('error')

    def zoom_in(self):
       try:
         current_widget = self.tab_widget.currentWidget()
         # Найдём QGraphicsView внутри текущей вкладки
         graphics_view = current_widget.findChild(QGraphicsView)
         if graphics_view:
            current_scene = graphics_view.scene()
            items = current_scene.items(Qt.AscendingOrder)
            background_item = items[-1] if items else None
            current_scale = background_item.scale()
            new_scale = current_scale * 1.1
            background_item.setScale(new_scale)
       except:QMessageBox.warning(None, "Предупреждение", "Необходимо добавить фоновое изображение")

    def zoom_out(self):
       try:
         current_widget = self.tab_widget.currentWidget()
         # Найдём QGraphicsView внутри текущей вкладки
         graphics_view = current_widget.findChild(QGraphicsView)
         if graphics_view:
            current_scene = graphics_view.scene()
            items = current_scene.items(Qt.AscendingOrder)
            background_item = items[-1] if items else None
            current_scale = background_item.scale()
            new_scale = current_scale / 1.1
            background_item.setScale(new_scale)
       except:QMessageBox.warning(None, "Предупреждение", "Необходимо добавить фоновое изображение")

    def change_image(self):
        # Изменить картинку (предположим, загрузка нового изображения)
        filename, _ = QFileDialog.getOpenFileName(None, "Выбрать файл", "", "Все файлы (*);;Текстовые файлы (*.txt)")
        pixmap = QPixmap(filename)
        if not pixmap.isNull():
            self.background.setPixmap(pixmap)  # Меняем картинку
            self.background.setScale(1.0)  # Сбрасываем масштаб
            self.background.setPos(0, 0)  # Сбрасываем позицию

    def update_icon_image(self):
        try:
            current_file = os.path.realpath(__file__)
            current_directory = os.path.dirname(current_file)
            system_icon = {
                "Windows": f"{current_directory}\\units\\computer.png",
                "Android": f"{current_directory}\\units\\phone.png",
                "Linux": f"{current_directory}\\units\\other.png",
                "routerOS": f"{current_directory}\\units\\wifi.png"
            }
            rez_scan = ns.NetworkScanner()
            rez_scan.scan_network_fast()
            rez_scan.create_graph()
            data = []
            self.position = 10
            conn = sqlite3.connect('Device_parametres.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM devices')
            cap_devices = cursor.fetchall()

            list_param=[]

            # Выводим результат
            for text in cap_devices:
                name_ip = text[1]
                addr_icon = system_icon[text[2]]
                list_param=(addr_icon, name_ip, (self.position, self.position))
                self.position = self.position + 10
                print(list_param)
                data.append(list_param)
            print(data)
            for i in data:
                self.add_icon_image(i[0], i[1], i[2], False)
        except:QMessageBox.warning(None, "Предупреждение", "Необходимо добавить вкладку")

    def test_update_icon_image(self):
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        data = [
            (f"{current_directory}\\units\\wifi.png", "Модуль 1", (10, 10)),
            (f"{current_directory}\\units\\computer.png", "Модуль 2", (30, 20)),
            (f"{current_directory}\\units\\other.png", "Модуль 3", (20, 35)),
            (f"{current_directory}\\units\\phone.png", "Модуль 4", (20, 35)),
        ]
        for i in data:
            self.add_icon_image(i[0], i[1], i[2], False)

        current_widget = self.tab_widget.currentWidget()
        graphics_view = current_widget.findChild(QGraphicsView)
        i = 0
        if graphics_view:
            current_scene = graphics_view.scene()
            items = current_scene.items()
            for item in items:
                if isinstance(item, QGraphicsPixmapItem):
                    image = item.pixmap()
                    this_image = image.toImage()
                    format = this_image.format()
                    if format: i = i + 1
            # Создаём и настраиваем тест

            # Создаём и настраиваем тест
            tst = test.GraphicsTest(methodName='test_graphics_item_count')
            tst.num_img = i

            suite = unittest.TestSuite()
            suite.addTest(tst)

            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            if result.wasSuccessful():
               print("✅ Успешно: на сцене 4 изображения")
            else:
               print("❌ Ошибка: тест провален")

    '''добавить устроройство '''
    def archive_icon_image(self):
      try:
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        system_icon = {
            "Windows": f"{current_directory}\\units\\computer.png",
            "Android": f"{current_directory}\\units\\phone.png",
            "Linux": f"{current_directory}\\units\\other.png",
            "routerOS": f"{current_directory}\\units\\wifi.png"
        }

        data = []
        self.position = 10
        conn = sqlite3.connect('Device_parametres.db')
        cursor = conn.cursor()
        data = []
        try:
            cursor.execute('SELECT * FROM hand_devices')
            cap_devices = cursor.fetchall()
            list_param = []
            # Выводим результат
            for text in cap_devices:
                name_ip = text[1]
                addr_icon = system_icon[text[2]]
                list_param = (addr_icon, name_ip, (self.position, self.position))
                self.position = self.position + 10
                print(list_param)
                data.append(list_param)
            print(data)
            for i in data:
                self.add_icon_image(i[0], i[1], i[2], False)
        except:
            print('hand_devices is empty')
      except:QMessageBox.warning(None, "Предупреждение", "Необходимо добавить вкладку")


    '''добавить устроройство '''
    def add_icon_image(self,filename,name,pos,act):
        try:
           self.items = []
           current_file = os.path.realpath(__file__)
           current_directory = os.path.dirname(current_file)
           if act:
              filename, _ = QFileDialog.getOpenFileName(None, "Выбрать файл", f"{current_directory}\\units", "Все файлы (*);;Текстовые файлы (*.txt)" )
              name="Модуль 1"
              pos=(10, 10)
           data = [(filename, name,pos)]
           current_widget = self.tab_widget.currentWidget()
           # Найдём QGraphicsView внутри текущей вкладки
           graphics_view = current_widget.findChild(QGraphicsView)
           if graphics_view:
               current_scene = graphics_view.scene()
               for img_path, text, pos in data:
                  icon_frame = icon.FramedImage(img_path, text)
                  icon_frame.setPos(*pos)
                  icon_frame.setFlag(QGraphicsRectItem.ItemIsSelectable)
                  icon_frame.setFlag(QGraphicsRectItem.ItemIsFocusable)
                  current_scene.addItem(icon_frame)
                  self.items.append(icon_frame)
        except:QMessageBox.warning(None, "Предупреждение", "Необходимо добавить вкладку")

    def capture_tab(self):
        current_widget = self.tab_widget.currentWidget()
        pixmap = current_widget.grab()  # Снимок содержимого текущей вкладки
        text,ok = QInputDialog.getText(None, 'Переименование', 'Введите новое имя:',text="screenshot.png")
        folder = QFileDialog.getExistingDirectory(None, "Выберите папку для сохранения")
        if ok:pixmap.save(folder+'/'+text)
        print("Скриншот сохранён как screenshot.png")

class MainWindow(QMainWindow):
    def __init__(self,NetworkScanner_class_instance):
        super().__init__()
        self.setWindowTitle("IAdmin")
        self.resize(1000, 800)
        self.NetworkScanner=NetworkScanner_class_instance
        # Центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # ===== Вложенный вертикальный сплиттер =====
        vertical_splitter = QSplitter(Qt.Vertical)
        console_app=console.EmbeddedCMD()
        vertical_splitter.addWidget(console_app)
        fast_text=fb.TextEditorApp()
        vertical_splitter.addWidget(fast_text)
        table_tab=tables.MainWindow()
        vertical_splitter.addWidget(table_tab)
        # vertical_splitter.setSizes([300, 300])  # Пропорции
        # ===== Основной горизонтальный сплиттер =====
        work_space = Work_space()
        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.addWidget(work_space)  # Слева список

        horizontal_splitter.addWidget(vertical_splitter)  # Справа вложенный сплиттер
        horizontal_splitter.setSizes([1800, 800])

        # Добавляем в layout
        layout.addWidget(horizontal_splitter)
        # Создаём меню-бар
        menubar = self.menuBar()

        # Добавляем меню "Файл"
        file_menu = menubar.addMenu("Файл")

        # Добавляем действия в меню
        open_action = QAction("Сохранить изображение на вкладке", self)
        open_action.triggered.connect(work_space.capture_tab)
        file_menu.addAction(open_action)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        nmap = menubar.addMenu("Nmap")
        nmap_type_scan=nmap.addMenu("Тип сканирования Nmap")

        activ_console = menubar.addMenu("Консоль")
        activ_console_run = QAction("Запуск консоли", self)
        activ_console_run.triggered.connect(lambda: subprocess.Popen('start cmd.exe /k echo Привет из Python!', shell=True))
        activ_console.addAction(activ_console_run)

        # Добавим ещё одно меню — например, "Справка"
        help_menu = menubar.addMenu("Справка")

        self.nmap_type_scan_with_saving = QAction("✓ Запуск Nmap с сохранением состояния", self)
        self.nmap_type_scan_with_saving.triggered.connect(self.set_norm_mode)
        nmap_type_scan.addAction(self.nmap_type_scan_with_saving)
        self.nmap_type_scan_without_saving = QAction("Запуск Nmap без сохранения состояния", self)
        self.nmap_type_scan_without_saving.triggered.connect(self.set_save_mode)
        nmap_type_scan.addAction(self.nmap_type_scan_without_saving)

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def set_norm_mode(self):
        self.NetworkScanner.set_save_mode(True)
        self.nmap_type_scan_with_saving.setText("✓ Запуск Nmap с сохранением состояния")
        self.nmap_type_scan_without_saving.setText("Запуск Nmap без сохранения состояния")

    def set_save_mode(self):
        self.NetworkScanner.set_save_mode(False)
        self.nmap_type_scan_with_saving.setText("Запуск Nmap с сохранением состояния")
        self.nmap_type_scan_without_saving.setText("✓ Запуск Nmap без сохранения состояния")
    def show_about(self):
        QMessageBox.information(self, "О программе", "Пример меню-бара на PyQt.")

# Запуск
app = QApplication(sys.argv)
NetworkScanner_class_instance = ns.NetworkScanner()
window = MainWindow(NetworkScanner_class_instance)
window.show()
sys.exit(app.exec_())