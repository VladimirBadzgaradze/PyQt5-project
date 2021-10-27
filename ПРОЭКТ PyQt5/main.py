import sys

from PIL import Image

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3


events_lst = []


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


class ClassDialog(QDialog):
    def __init__(self, parent=None):
        super(ClassDialog, self).__init__(parent)
        global events_lst
        uic.loadUi('UI/base.ui', self)
        self.lst = events_lst
        self.id = []
        self.max = 0
        self.con = sqlite3.connect("base.db")
        self.init()
        self.update_result()
        self.add_btn.clicked.connect(self.add)
        self.del_btn.clicked.connect(self.delete)
        self.take_btn.clicked.connect(self.take)

    def update_result(self):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        que = "SELECT * FROM tab"  # ID, Name
        result = cur.execute(que).fetchall()
        self.max = len(result)
        if result:
            # Заполнили размеры таблицы
            self.TW.setRowCount(len(result))
            self.TW.setColumnCount(len(result[0]))
            self.TW.setHorizontalHeaderLabels(['ID', 'Name', 'Picture'])

            # Заполнили таблицу полученными элементами
            for i, elem in enumerate(result):
                self.id.append(elem[0])
                for j, val in enumerate(elem):
                    if j in [0, 1]:
                        self.TW.setItem(i, j, QTableWidgetItem(str(val)))
                    elif j == 2:
                        with open('img.jpg', 'wb') as file:
                            file.write(val)
                        item = QTableWidgetItem()
                        self.TW.setItem(i, j, item)
                        item.setIcon(QIcon("img.jpg"))
                        self.TW.setIconSize(QSize(50, 50))

    def init(self):
        self.setWindowTitle('Base')
        self.setStyleSheet("#Form{background-color:White}")
        self.setGeometry(500, 200, 1000, 700)

    def add(self):
        global events_lst
        name, ok_pressed = QInputDialog.getText(self, 'Get name', 'Name your project', QLineEdit.Normal, "")
        id_, ok_pressed2 = QInputDialog.getInt(self, 'Get id', 'id your project', 1, 1, 999, 1)

        if ok_pressed and ok_pressed2:
            cur = self.con.cursor()
            cur.execute("INSERT INTO tab VALUES(?, ?, ?);", [id_, name, events_lst])
            self.con.commit()
            self.update_result()

    def delete(self):
        val, ok_pressed = QInputDialog.getInt(self, 'Get ID project', 'ID project  to delete', 1, 1, 999, 1)
        if ok_pressed and val in self.id:
            cur = self.con.cursor()
            cur.execute("DELETE FROM tab WHERE ID=" + str(val))
            self.con.commit()
            self.update_result()

    def take(self):
        global events_lst
        val, ok_pressed = QInputDialog.getInt(self, 'Get ID project', 'ID project  to open', 1, 1, 999, 1)
        if ok_pressed:
            cur = self.con.cursor()
            res = cur.execute("SELECT Code FROM tab WHERE ID=" + str(val)).fetchall()
            events_lst = res[0][0]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.file_name = ''
        self.pixels = []
        self.x_img, self.y_img = 0, 0

        self.events = []
        self.pop_events = []

        self.point = None
        self.tool = 'marker'
        self.alpha = 100
        self.thick = 5
        self.color = '#000000'
        self.style = 'SolidLine'
        self.fill = None

        self.x = 160
        self.y = 140
        self.width = 1500
        self.height = 800

        self.mouse_pos0 = None
        self.mouse_pos1 = None

        uic.loadUi('UI/main.ui', self)
        self.init_ui()

        for i in self.color_group.buttons():
            i.setStyleSheet(f"background-color : #{i.objectName()[4:]}")
            i.clicked.connect(self.set_color)

        for i in self.tool_group.buttons():
            i.clicked.connect(self.set_tool)

        self.clear_btn.clicked.connect(self.clear)

        self.left_btn.clicked.connect(self.btnpress)
        self.right_btn.clicked.connect(self.btnpress)

        self.btn_person_color.clicked.connect(self.set_person_color)

        self.thick_slider.valueChanged[int].connect(self.set_thick)
        self.alpha_slider.valueChanged[int].connect(self.set_alpha)

        self.comboBox_line.currentTextChanged.connect(self.set_line_style)

        self.btn_fill.stateChanged.connect(self.set_fill_color)
        self.btn_color_fill.clicked.connect(self.set_fill_color_btn)

        self.menu_click = False
        self.menu_btn.clicked.connect(self.menu_bar)

        self.save_as_btn.clicked.connect(self.save_as)
        self.open_btn.clicked.connect(self.open)
        self.save_btn.clicked.connect(self.save)
        self.base_btn.clicked.connect(self.base)

    def menu_bar(self):
        self.menu_click = not self.menu_click
        if self.menu_click:
            self.save_as_btn.setVisible(True)
            self.save_btn.setVisible(True)
            self.open_btn.setVisible(True)
            self.base_btn.setVisible(True)
            self.menu_btn.setIcon(QIcon('images/menu2.png'))
            self.menu_btn.setIconSize(QSize(91, 91))
        else:
            self.save_as_btn.setVisible(False)
            self.save_btn.setVisible(False)
            self.open_btn.setVisible(False)
            self.base_btn.setVisible(False)
            self.menu_btn.setIcon(QIcon('images/menu1.png'))
            self.menu_btn.setIconSize(QSize(91, 91))

    def base(self):
        # открываем новое окно
        global events_lst
        im = self.label.pixmap()
        im.save('img.jpg')
        with open('img.jpg', 'rb') as file:
            blob_data = file.read()
        events_lst = blob_data
        dialog = ClassDialog(self)
        dialog.exec_()
        with open('img.jpg', 'wb') as file:
            file.write(events_lst)
        im = Image.open('img.jpg')
        w, h = im.size
        im.save('img.jpg')
        self.label.setPixmap(QPixmap('img.jpg'))
        self.label.setGeometry(self.x, self.y, w, h)
        self.update()

    def save_as(self):
        filename = QFileDialog.getSaveFileName(None, 'Save Image', 'C:\\', "Image files (*.jpg *.png)")
        if filename:
            if filename[0].count('.') == 1 and filename[0][filename[0].index('.') + 1:] in ['jpg', 'png']:
                im = self.label.pixmap()
                im.save(filename[0])
            elif filename != ('', ''):
                valid = QMessageBox.question(
                    self, 'Ошибка сохранения', "Пересохранить?",
                    QMessageBox.Yes, QMessageBox.No)
                if valid == QMessageBox.Yes:
                    self.save_as()

    def save(self):
        if not self.file_name:
            self.save_as()
        else:
            im = self.label.pixmap()
            im.save(self.file_name)

    def open(self):
        filename = QFileDialog.getOpenFileName(None, 'Open Image', 'C:\\', "Image files (*.jpg *.png)")
        self.file_name = filename[0]
        img = Image.open(filename[0]).resize((self.width, self.height)).convert('RGB')
        img.save('img.jpg')
        self.pixels = img.load()
        self.x_img, self.y_img = img.size
        self.label.setPixmap(QPixmap('img.jpg'))
        self.setWindowTitle(f'Graphic editor {filename[0]}')
        self.events = list()
        self.pop_events = list()
        self.update()

    def mousePressEvent(self, event):
        if self.tool in ['marker', 'stylus', 'brush']:
            self.move_point(event)
            self.mouseMoveEvent(event)
        elif self.tool == 'line':
            self.move_line(event)
            self.mouseMoveEvent(event, event.x(), event.y())
        elif self.tool in ['rectangle', 'circle']:
            self.move_rect(event)
            self.mouseMoveEvent(event, event.x(), event.y())
        # Вызов перерисовки виджета
        self.update()

    def mouseMoveEvent(self, event, *p):
        if self.tool in ['marker', 'stylus', 'brush', 'rubber']:
            self.move_point(event)
        elif self.tool == 'line' and self.point:
            pass
        elif self.tool in ['rectangle', 'circle'] and self.point:
            pass
        self.update()

    def mouseReleaseEvent(self, event):
        if self.tool in ['marker', 'stylus', 'brush', 'rubber']:
            self.events.append([None])
        elif self.tool == 'line':
            self.move_line(event)
        elif self.tool in ['rectangle', 'circle']:
            self.move_rect(event)
        self.point = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.selected_color.setStyleSheet(f"background-color : {self.color}")

    def draw(self):
        qp = QPainter(self.label.pixmap())
        qp.begin(self)
        for i in range(len(self.events)):
            if self.events[i][0] == 'Point':
                n = QColor(self.events[i][1][0], self.events[i][1][1],
                           self.events[i][1][2], self.events[i][2])
                qp.setPen(QPen(n, self.events[i][3]))
                qp.drawPoint(self.events[i][4])
                try:
                    if self.events[i + 1][0] == 'Point':
                        n = QColor(self.events[i + 1][1][0], self.events[i + 1][1][1],
                                   self.events[i + 1][1][2], self.events[i + 1][2])
                        qp.setPen(QPen(n, self.events[i + 1][3]))
                        qp.drawLine(self.events[i][4], self.events[i + 1][4])
                except IndexError:
                    pass
            elif self.events[i][0] == 'Line':
                n = QColor(self.events[i][1][0], self.events[i][1][1],
                           self.events[i][1][2], self.events[i][2])
                qp.setPen(QPen(n, self.events[i][3], self.events[i][6]))
                qp.drawLine(self.events[i][4][0], self.events[i][4][1], self.events[i][5][0], self.events[i][5][1])
            elif self.events[i][0] == 'Rectangle':
                p = QColor(self.events[i][1][0], self.events[i][1][1],
                           self.events[i][1][2], self.events[i][2])
                qp.setPen(QPen(p, self.events[i][3], self.events[i][7]))
                if self.events[i][6]:
                    b = QColor(self.events[i][6][0], self.events[i][6][1],
                               self.events[i][6][2], self.events[i][2])
                    qp.setBrush(b)
                    qp.drawRect(self.events[i][4][0], self.events[i][4][1], self.events[i][5][0] - self.events[i][4][0],
                                self.events[i][5][1] - self.events[i][4][1])
                else:
                    qp.drawLine(self.events[i][4][0], self.events[i][4][1], self.events[i][5][0], self.events[i][4][1])
                    qp.drawLine(self.events[i][4][0], self.events[i][4][1], self.events[i][4][0], self.events[i][5][1])
                    qp.drawLine(self.events[i][5][0], self.events[i][4][1], self.events[i][5][0], self.events[i][5][1])
                    qp.drawLine(self.events[i][4][0], self.events[i][5][1], self.events[i][5][0], self.events[i][5][1])
            elif self.events[i][0] == 'Circle':
                p = QColor(self.events[i][1][0], self.events[i][1][1],
                           self.events[i][1][2], self.events[i][2])
                qp.setPen(QPen(p, self.events[i][3], self.events[i][7]))
                if self.events[i][6]:
                    b = QColor(self.events[i][6][0], self.events[i][6][1],
                               self.events[i][6][2], self.events[i][2])
                    qp.setBrush(b)
                qp.drawEllipse(self.events[i][4][0], self.events[i][4][1], self.events[i][5][0] - self.events[i][4][0],
                               self.events[i][5][1] - self.events[i][4][1])
        qp.end()

    def move_line(self, event):
        if not self.mouse_pos0:
            self.mouse_pos0 = event.x(), event.y()
        else:
            self.events.append(['Line',
                                tuple(int(self.color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)),
                                round(255 / 100 * self.alpha),
                                self.thick,
                                (self.mouse_pos0[0] - self.x, self.mouse_pos0[1] - self.y),
                                (event.x() - self.x, event.y() - self.y),
                                self.line_style()])
            self.mouse_pos0 = None
            self.events.append([None])
            self.draw()

    def move_rect(self, event):
        if not self.mouse_pos0:
            self.mouse_pos0 = event.x(), event.y()
        else:
            if self.tool == 'rectangle':
                t = 'Rectangle'
            elif self.tool == 'circle':
                t = 'Circle'
            self.events.append([t,
                                tuple(int(self.color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)),
                                round(255 / 100 * self.alpha),
                                self.thick,
                                (self.mouse_pos0[0] - self.x, self.mouse_pos0[1] - self.y),
                                (event.x() - self.x, event.y() - self.y),
                                tuple(int(self.fill.lstrip('#')[i:i + 2], 16)
                                      for i in (0, 2, 4)) if self.fill else self.fill,
                                self.line_style()])
            self.mouse_pos0 = None
            self.events.append([None])
            self.draw()

    def line_style(self):
        stl = None
        if self.style == 'SolidLine':
            stl = Qt.SolidLine
        elif self.style == 'DashLine':
            stl = Qt.DashLine
        elif self.style == 'DotLine':
            stl = Qt.DotLine
        elif self.style == 'DashDotLine':
            stl = Qt.DashDotLine
        return stl

    def move_point(self, event):
        self.point = event.pos()
        if event.x() in [i for i in range(self.x - 200, self.x + self.width + 200)] and \
                event.y() in [i for i in range(self.y - 200, self.y + self.height + 200)]:
            self.events.append(['Point', tuple(int(self.color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)),
                                round(255 / 100 * self.alpha),
                                self.thick, event.pos() - QPoint(self.x, self.y),
                                event.x() - self.x, event.y() - self.y])
            self.draw()

    def keyPressEvent(self, e):
        # отработать символ внутри поля ввода
        k = e.key()
        super().keyPressEvent(e)
        self.press(k)

    def btnpress(self):
        k = None
        if self.sender().objectName() == 'left_btn':
            k = 16777234
        elif self.sender().objectName() == 'right_btn':
            k = 16777236
        self.press(k)

    def press(self, k):
        try:
            if k == 16777234:
                n = -1
                x = self.events[-1]
                while x == [None]:
                    n -= 1
                    x = self.events[n]
                self.events[n][1] = (255, 255, 255)
                self.pop_events.append(x)
            elif k == 16777236:
                x = self.pop_events.pop()
                self.events.append(x)
            elif k == 16777216:
                sys.exit()
            self.update()
            self.draw()
        except IndexError:
            pass

    def init_ui(self):
        self.showMaximized()
        self.setWindowTitle('Graphic editor')
        self.setStyleSheet("#Form{background-color:DarkKhaki}")
        app.setWindowIcon(QIcon('images/ico.ico'))
        self.comboBox_line.addItems(['SolidLine', 'DashLine', 'DotLine', 'DashDotLine'])
        self.btn_fill.setVisible(False)
        self.btn_color_fill.setVisible(False)
        self.comboBox_line.setVisible(False)
        self.save_as_btn.setVisible(False)
        self.save_btn.setVisible(False)
        self.open_btn.setVisible(False)
        self.base_btn.setVisible(False)
        self.set_img_on_buttons()
        self.size_holst()

    def set_color(self):
        self.color = f'#{self.sender().objectName()[4:]}'
        self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        self.btn_person_color.setStyleSheet("QWidget { background-color: %s }"
                                            % None)

    def set_person_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.sender().setStyleSheet("QWidget { background-color: %s }"
                                        % color.name())
            self.color = color.name()
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")

    def set_fill_color(self, state):
        if state == Qt.Checked:
            color = QColorDialog.getColor()
            if color.isValid():
                self.fill = color.name()
            self.btn_color_fill.setStyleSheet("QWidget { background-color: %s }"
                                              % self.fill)
        else:
            self.fill = None
            self.btn_color_fill.setStyleSheet("QWidget { background-color: %s }" % self.fill)

    def set_fill_color_btn(self):
        if self.fill:
            color = QColorDialog.getColor()
            if color.isValid():
                self.btn_color_fill.setStyleSheet("QWidget { background-color: %s }"
                                                  % color.name())
                self.fill = color.name()

    def set_thick(self, value):
        self.thick = value
        self.value_thick_label.setText(str(value) + 'px')
        self.is_used_label_px.setText(str(value) + 'px')

    def set_alpha(self, value):
        self.alpha = value
        self.value_alpha_label.setText(str(value) + '%')
        self.is_used_label_alpha.setText(str(value) + '%')

    def set_line_style(self):
        self.style = self.comboBox_line.currentText()

    def set_tool(self):
        self.tool = self.sender().objectName()
        self.is_used_label_tool.setText(self.tool)
        if self.tool == 'marker':
            self.thick_slider.setValue(5)
            self.set_thick(5)
            self.alpha_slider.setValue(100)
            self.set_alpha(100)
            self.color = '#000000'
            self.btn_fill.setVisible(False)
            self.btn_color_fill.setVisible(False)
            self.comboBox_line.setVisible(False)
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        elif self.tool == 'stylus':
            self.thick_slider.setValue(1)
            self.set_thick(1)
            self.alpha_slider.setValue(100)
            self.set_alpha(100)
            self.color = '#0000ff'
            self.btn_fill.setVisible(False)
            self.btn_color_fill.setVisible(False)
            self.comboBox_line.setVisible(False)
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        elif self.tool == 'brush':
            self.thick_slider.setValue(3)
            self.set_thick(3)
            self.alpha_slider.setValue(75)
            self.set_alpha(75)
            self.color = '#101241'
            self.btn_fill.setVisible(False)
            self.btn_color_fill.setVisible(False)
            self.comboBox_line.setVisible(False)
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        elif self.tool == 'rubber':
            self.thick_slider.setValue(10)
            self.set_thick(10)
            self.alpha_slider.setValue(100)
            self.set_alpha(100)
            self.color = '#ffffff'
            self.btn_fill.setVisible(False)
            self.btn_color_fill.setVisible(False)
            self.comboBox_line.setVisible(False)
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        elif self.tool == 'line':
            self.thick_slider.setValue(self.thick)
            self.set_thick(self.thick)
            self.alpha_slider.setValue(self.alpha)
            self.set_alpha(self.alpha)
            self.color = self.color
            self.btn_fill.setVisible(False)
            self.btn_color_fill.setVisible(False)
            self.comboBox_line.setVisible(True)
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        elif self.tool in ['rectangle', 'circle']:
            self.thick_slider.setValue(self.thick)
            self.set_thick(self.thick)
            self.alpha_slider.setValue(self.alpha)
            self.set_alpha(self.alpha)
            self.color = self.color
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
            self.btn_fill.setVisible(True)
            self.btn_color_fill.setVisible(True)
            self.comboBox_line.setVisible(True)

    def size_holst(self):
        width = self.size().width()
        height = self.size().height()
        w, ok_pressed = QInputDialog.getInt(
            self, "Введите значение", "Ширина холста?",
            1500, 100, width - self.x, 10)
        if ok_pressed:
            self.width = w
        h, ok_pressed = QInputDialog.getInt(
            self, "Введите значение", "Высота холста?",
            800, 100, height - self.y, 10)
        if ok_pressed:
            self.height = h
        im = Image.open('img.jpg').resize((self.width, self.height))
        pix = im.load()
        w, h = im.size
        for i in range(w):
            for j in range(h):
                pix[i, j] = 255, 255, 255
        im.save('img.jpg')
        self.label.setPixmap(QPixmap('img.jpg'))
        self.label.setGeometry(self.x, self.y, self.width, self.height)

    def clear(self):
        self.events = list()
        self.pop_events = list()
        self.pixels = list()
        self.x_img, self.y_img = 0, 0
        self.file_name = ''
        im = Image.open('img.jpg').resize((self.width, self.height))
        pix = im.load()
        w, h = im.size
        for i in range(w):
            for j in range(h):
                pix[i, j] = 255, 255, 255
        im.save('img.jpg')
        self.label.setPixmap(QPixmap('img.jpg'))
        self.label.setGeometry(self.x, self.y, self.width, self.height)
        self.update()
        self.draw()

    def set_img_on_buttons(self):
        self.marker.setIcon(QIcon('images/marker.png'))
        self.marker.setIconSize(QSize(61, 61))
        self.stylus.setIcon(QIcon('images/stylus.png'))
        self.stylus.setIconSize(QSize(61, 61))
        self.brush.setIcon(QIcon('images/brush.png'))
        self.brush.setIconSize(QSize(61, 61))
        self.clear_btn.setIcon(QIcon('images/clear.png'))
        self.clear_btn.setIconSize(QSize(61, 61))
        self.rubber.setIcon(QIcon('images/rubber.png'))
        self.rubber.setIconSize(QSize(61, 61))
        self.line.setIcon(QIcon('images/line.png'))
        self.line.setIconSize(QSize(61, 61))
        self.rectangle.setIcon(QIcon('images/rectangle.png'))
        self.rectangle.setIconSize(QSize(61, 61))
        self.circle.setIcon(QIcon('images/circle.png'))
        self.circle.setIconSize(QSize(61, 61))
        self.menu_btn.setIcon(QIcon('images/menu1.png'))
        self.menu_btn.setIconSize(QSize(91, 91))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    screen = QApplication.primaryScreen()
    sys.excepthook = except_hook
    sys.exit(app.exec())
