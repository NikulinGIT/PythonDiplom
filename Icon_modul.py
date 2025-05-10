from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QMenu, QGraphicsItemGroup,
    QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem, QInputDialog, QAction
)
from PyQt5.QtGui import QPixmap, QPen, QBrush
from PyQt5.QtCore import QLineF, Qt
from PyQt5.QtWidgets import (QMenu, QAction,QGraphicsView, QGraphicsRectItem, QApplication,QGraphicsPixmapItem)
import requests
import sqlite3
import os
class FramedImage(QGraphicsItemGroup):
    def __init__(self, pixmap_path, label_text):
        super().__init__()

        # Рамка
        self.rect = QGraphicsRectItem(0, 0, 120, 100)
        self.rect.setBrush(QBrush(Qt.white))
        self.rect.setPen(QPen(Qt.black, 2))
        self.addToGroup(self.rect)

        # Картинка
        pixmap = QPixmap(pixmap_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image = QGraphicsPixmapItem(pixmap)
        self.image.setPos(10, 10)
        self.addToGroup(self.image)

        # Подпись
        label_eth_text, ok = QInputDialog.getText(None, 'Переименование', 'Введите имя:', text=label_text)
        self.label = QGraphicsTextItem(label_eth_text)
        self.label.setDefaultTextColor(Qt.black)
        self.label.setPos(20, 72)
        self.addToGroup(self.label)

        # Включаем перемещение
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.line_update_callback = None

        conn = sqlite3.connect('Device_parametres.db')
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        # Создаем основную таблицу devices
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS hand_devices (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL unique,
                                System TEXT,
                                Activity INTEGER
                            )
                            ''')

        filename = os.path.basename(pixmap_path)
        filename_dict = {
            "computer.png": "Windows",
            "phone.png": 'Android',
            "other.png": "Linux",
            "wifi.png": "routerOS"
        }
        try:cursor.execute("INSERT INTO hand_devices (name, System, Activity) VALUES (?, ?, ?)", (label_eth_text, filename_dict[filename], 0))
        except:pass

        conn.commit()
        conn.close()
        # Начальные состояния флажков
        self.List_flag_option = []
    def contextMenuEvent(self, event):

        # Создаем контекстное меню
        menu = QMenu()
        # Добавляем действия в меню
        action1 = menu.addAction("Переименовать устройство")
        recent_menu = QMenu("Построить/удалить связь", menu)
        action3 = menu.addAction("Сделать шлюзом")
        action4 = menu.addAction("Удалить устройство")
        action2 = menu.addAction('Удалить все связи элемента')
        # Добавляем подменю в "Файл"

        # Подключаем действия к их обработчикам
        action1.triggered.connect(self.change_name)
        action3.triggered.connect(self.make_gateway)
        action4.triggered.connect(self.delete_device)
        action2.triggered.connect(self.delete_links)
        view = QApplication.focusWidget()
        scene = view.scene()
        self.list_items = scene.items()
        active_item = scene.focusItem()
        self.list_addr=[]# список имен элементов
        List_frames=[]#список имен item
        list_action=[]#список элементов во вкладке
        self.list_check=[]#список активных элементов
        List_lines=[]#список связей
        List_itemslines=[]
        i=0
        my_addr=''

        for item in self.list_items:
            if item==active_item:my_addr = self.list_items[i-3].toPlainText() # получаем активное имя
            #if isinstance(item, QGraphicsTextItem):
            if isinstance(item, FramedImage):
                List_frames.append(item) # получаем список имен item
                self.list_addr.append(self.list_items[i-3].toPlainText()) # получаем список имен элементов
                self.list_check.append(False)
            if isinstance(item,LineConnector):
                List_itemslines.append(item)
                List_lines.append(item.collidingItems()) # получаем список линий
            i = i + 1

        list_active_FrameImage=[]
        #print(List_itemslines)
        for i in List_itemslines: # проходка по линиям
            #print(i.collidingItems())
            for k in i.collidingItems(): # разбиваем линию на элементы
                if active_item is k: # если активный элемент есть в списке
                    #print(i.collidingItems())
                    for l in i.collidingItems():
                        #print(List_frames)
                        for j in List_frames: # находим элементы, связанные с линиями
                            if l is j:
                                list_active_FrameImage.append(j)
                                #print(l)
                                print('')

        print(list_active_FrameImage)

        checkmark = ("✓")
        k=0
        print(List_frames)
        active_item = scene.focusItem()
        for i in List_frames:
            flag_active=False
            print(active_item)
            if len(list_active_FrameImage)==0:name_addr=self.list_addr[k]
            else:
               print(list_active_FrameImage)
               for cur_unit in list_active_FrameImage:
                  if cur_unit == i:
                    flag_active=True
            if flag_active: name_addr=checkmark+' '+self.list_addr[k]
            else:name_addr=self.list_addr[k]

            list_action.append(QAction(name_addr, recent_menu))
            list_action[-1].setCheckable(True)
            this_action=self.function_collection(list_action[-1],active_item,List_lines,i,List_itemslines,List_frames)
            if my_addr != self.list_addr[k]:recent_menu.addAction(this_action)
            k=k+1
        print('!!!')

        menu.addMenu(recent_menu)
        menu.exec_(event.screenPos()) # Отображаем меню в позиции курсора

    def function_collection(self,this_action,active_item,List_lines,frame,List_itemslines,List_frames):
       try:
        if active_item is frame:
            #print('eq')
            this_action.setChecked(False)
            this_action.toggled.connect(lambda state: self.make_link(active_item, frame))
        else:
           #print('noteq')
           print(' ')
           i = 0
           #print(List_itemslines)
           while i < len(List_itemslines):
              list_active_FrameImage=[]
              #print(i)
              k = 0
              flag_active_line='0'
              while k < len(List_lines[i]):
                 for j in List_frames:
                    if (List_lines[i][k] is j):list_active_FrameImage.append(List_lines[i][k])
                 k=k+1
              #print(list_active_FrameImage)
              #print(frame)
              if len(list_active_FrameImage)==0:
                  view = QApplication.focusWidget()
                  current_scene = view.scene()
                  current_scene.removeItem(List_itemslines[i])
              else:
                for FrameIm in list_active_FrameImage:
                  if (FrameIm is frame):flag_active_line='1'
                if flag_active_line=='1':
                   print(flag_active_line)
                elif flag_active_line=='0':
                  print(flag_active_line)
                  this_action.setChecked(False)
                  this_action.toggled.connect(lambda state: self.make_link(active_item, frame))
              i=i+1
           if len(List_itemslines)==0:
               this_action.setChecked(False)
               this_action.toggled.connect(lambda state: self.make_link(active_item, frame))
       except:print('err')
       return this_action

    def make_link(self,active_item,frame):
       view = QApplication.focusWidget()
       if isinstance(view, QGraphicsView):
           current_scene = view.scene()
           line = LineConnector(active_item, frame)
           line.setZValue(-0.5)
           current_scene.addItem(line)

    def delete_links(self):
        view = QApplication.focusWidget()
        current_scene = view.scene()
        active_item = current_scene.focusItem()
        for item in self.list_items:
            if isinstance(item, LineConnector):
                k = 0
                list_itemsline=item.collidingItems()
                while k < len(list_itemsline):
                    if list_itemsline[k]==active_item:current_scene.removeItem(item)
                    k=k+1

    def change_name(self):
        try:
            view = QApplication.focusWidget()
            if isinstance(view, QGraphicsView):
                scene = view.scene()
                active_item = scene.selectedItems()
                items = active_item[0].childItems()
                for item in items:
                    if isinstance(item, QGraphicsTextItem):
                        text, ok = QInputDialog.getText(None, 'Переименование', 'Введите новое имя:',
                                                        text=item.toPlainText())
                        if ok:
                            old_name=item.toPlainText()
                            item.setPlainText(text)
                            conn = sqlite3.connect('Device_parametres.db')
                            cursor = conn.cursor()
                            conn.execute("PRAGMA foreign_keys = ON")
                            cursor.execute("UPDATE hand_devices SET name = ? WHERE name = ?", (text, old_name))
                            conn.commit()
                            conn.close()
        except:pass

    def make_gateway(self):
        try:
            view = QApplication.focusWidget()
            if isinstance(view, QGraphicsView):
                scene = view.scene()
                active_item = scene.selectedItems()
                active_item = active_item[0]
                items = active_item.childItems()
                for item in items:
                    if isinstance(item, QGraphicsRectItem):
                        item.setRect(0, 40, 120, 100)
                    if isinstance(item, QGraphicsPixmapItem):
                        item.setPos(10, 50)
                    if isinstance(item, QGraphicsTextItem):
                        item.setPos(20, 112)
                ip = requests.get('https://api.ipify.org').text
                label_eth_text, ok = QInputDialog.getText(None, 'Переименование', 'Введите новое имя:',text=ip)
                if ok:
                    label_eth = QGraphicsTextItem(label_eth_text, active_item)
                    label_eth.setDefaultTextColor(Qt.black)
                    label_eth.setPos(35, 10)
                line_eth = QGraphicsLineItem(QLineF(30, 0, 30, 38), active_item)
                line_eth.setPen(QPen(Qt.red, 3))  # Цвет и толщина
        except:pass

    def delete_device(self):
        view = QApplication.focusWidget()
        if isinstance(view, QGraphicsView):
            scene = view.scene()
            delete_item = scene.focusItem()
            # элемент с фокусом
            try:
               active_item = scene.selectedItems()
               items = active_item[0].childItems()
               for item in items:
                   if isinstance(item, QGraphicsTextItem):
                      old_name = item.toPlainText()
                      conn = sqlite3.connect('Device_parametres.db')
                      cursor = conn.cursor()
                      cursor.execute("DELETE FROM hand_devices WHERE name = ?", (old_name,))
                      conn.commit()
                      conn.close()
            except:print('error database')
            scene.removeItem(delete_item)


class LineConnector(QGraphicsLineItem):
    def __init__(self, item1, item2):
        super().__init__()
        self.item1 = item1
        self.item2 = item2
        self.setPen(QPen(Qt.blue, 2))
        self.update_position()

        self.item1.line_update_callback = self.update_position
        self.item2.line_update_callback = self.update_position

    def update_position(self):
        p1 = self.item1.sceneBoundingRect().center()
        p2 = self.item2.sceneBoundingRect().center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

