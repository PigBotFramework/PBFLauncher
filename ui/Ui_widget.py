from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QStyleOption, QStyle
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import pyqtSignal


# 定义标题栏
class MyWidget(QtWidgets.QWidget):
    signal_resize = pyqtSignal(int)
    signal_move = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.setObjectName('widget_status')
        self.db = 0
        self.m_flag = False

    # 重写paintEvent 否则不能使用样式表定义外观
    def paintEvent(self, evt):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        # 反锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.db = 1
        self.signal_resize.emit(self.db)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_position = event.pos()
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move_pos = QMouseEvent.globalPos() - self.m_position
            self.move_pos = str(self.move_pos)
            QMouseEvent.accept()
            # 判断鼠标位置切换鼠标手势
            self.signal_move.emit(1, self.move_pos)

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
