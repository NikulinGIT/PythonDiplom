from PyQt5.QtWidgets import (QTabBar,QLabel,QLineEdit)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import (QMenu,QGraphicsRectItem)
#перетаскивание картинки
class DraggableLabel(QLabel):
    def __init__(self, pixmap):
        super().__init__()
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setFixedSize(pixmap.size())
        self.drag_start_position = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self.drag_start_position:
            # Перемещаем метку относительно текущей позиции
            self.move(self.mapToParent(event.pos() - self.drag_start_position))

#изменение имени вкладки
class EditableTabBar(QTabBar):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.editor = None
    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index < 0:
            return

        # Получаем прямоугольник заголовка вкладки
        tab_rect = self.tabRect(index)

        # Создаем QLineEdit прямо поверх заголовка вкладки
        self.editor = QLineEdit(self)
        self.editor.setText(self.tabText(index))
        self.editor.setGeometry(tab_rect)
        self.editor.setFocus()
        self.editor.selectAll()

        # Обрабатываем завершение редактирования
        self.editor.editingFinished.connect(lambda: self.renameTab(index))
        self.editor.installEventFilter(self)  # Чтобы ловить нажатие Esc
        self.editor.show()

    def renameTab(self, index):
        if self.editor:
            new_name = self.editor.text().strip()
            if new_name:
                self.setTabText(index, new_name)
            self.editor.deleteLater()
            self.editor = None

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            # Отмена редактирования
            self.editor.deleteLater()
            self.editor = None
            return True
        return super().eventFilter(source, event)

class AutoResizingGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setScene(scene)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = self.viewport().size()
        self.scene().setSceneRect(QRectF(0, 0, size.width(), size.height()))

class MyRectItem(QGraphicsRectItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)

    def contextMenuEvent(self, event):
        menu = QMenu()
        action1 = menu.addAction("Действие 1")
        action2 = menu.addAction("Действие 2")
        selected_action = menu.exec_(event.screenPos())

        if selected_action == action1:
            print("Выбрано действие 1")
        elif selected_action == action2:
            print("Выбрано действие 2")