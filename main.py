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


class Setting(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/setting.ui', self)

        self.con = sqlite3.connect("base.db")

        self.language_words = []
        cur = self.con.cursor()
        res = cur.execute("SELECT val FROM settings WHERE name='language'").fetchall()
        res = res[0][0]
        self.lang = res
        with open(f'txt files/{res}.txt', mode='r', encoding='utf-8') as f_in:
            self.language_words = f_in.readlines()
        self.language_words = list(map(lambda x: x.split('\n')[0], self.language_words))

        self.color_main = None
        self.color_base = None
        self.color_settings = None

        self.lan = None
        self.round = None

        self.init_ui()

        self.save_settings_btn.clicked.connect(self.save_settings)
        self.bg_main_btn.clicked.connect(self.set_color)
        self.bg_base_btn.clicked.connect(self.set_color)
        self.bg_settings_btn.clicked.connect(self.set_color)

        self.CB_language.currentTextChanged.connect(self.set_lan)
        self.CB_round.currentTextChanged.connect(self.set_round)

    def init_ui(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT val FROM settings WHERE name='bg color settings window'").fetchall()

        self.setStyleSheet("#Form{background-color:" + res[0][0] + "}")

        self.setWindowTitle(self.language_words[54])

        self.bg_main.setText(self.language_words[55])
        self.lang_lbl.setText(self.language_words[56])
        self.save_settings_btn.setText(self.language_words[57])
        self.round_lbl.setText(self.language_words[58])
        self.bg_base.setText(self.language_words[59])
        self.bg_settings.setText(self.language_words[60])

        cur = self.con.cursor()
        col = cur.execute("SELECT val FROM settings WHERE name LIKE 'bg color % window'").fetchall()
        self.bg_main_btn.setStyleSheet(f"background-color : {col[0][0]}")
        self.bg_settings_btn.setStyleSheet(f"background-color : {col[1][0]}")
        self.bg_base_btn.setStyleSheet(f"background-color : {col[2][0]}")

        self.color_main = col[0][0]
        self.color_settings = col[1][0]
        self.color_base = col[2][0]

        ln = cur.execute("SELECT val FROM settings WHERE name='language'").fetchall()
        res = None
        if ln[0][0] == 'English':
            res = ['English', 'Russian']
        elif ln[0][0] == 'Russian':
            res = ['Russian', 'English']
        self.CB_language.addItems(res)
        self.lan = ln[0][0]
        bor_rad = cur.execute("SELECT val FROM settings WHERE name='border radius'").fetchall()
        bor_rad = str(bor_rad[0][0])
        res = None
        if bor_rad == '0':
            res = ['0%', '20%', '40%', '60%', '80%', '100%']
        elif bor_rad == '10':
            res = ['20%', '0%', '40%', '60%', '80%', '100%']
        elif bor_rad == '20':
            res = ['40%', '0%', '20%', '60%', '80%', '100%']
        elif bor_rad == '30':
            res = ['60%', '0%', '20%', '40%', '80%', '100%']
        elif bor_rad == '40':
            res = ['80%', '0%', '20%', '40%', '60%', '100%']
        elif bor_rad == '50':
            res = ['100%', '0%', '20%', '40%', '60%', '80%']

        self.CB_round.addItems(res)
        self.round = bor_rad

    def set_round(self):
        self.round = self.CB_round.currentText()[:-1]
        self.setWindowTitle(self.language_words[54] + '*')

    def set_lan(self):
        self.lan = self.CB_language.currentText()
        self.setWindowTitle(self.language_words[54] + '*')

    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.sender().setStyleSheet("QWidget { background-color: %s }"
                                        % color.name())
            if self.sender().objectName() == 'bg_main_btn':
                self.color_main = color.name()
            elif self.sender().objectName() == 'bg_base_btn':
                self.color_base = color.name()
            elif self.sender().objectName() == 'bg_settings_btn':
                self.color_settings = color.name()
            self.setWindowTitle(self.language_words[54] + '*')

    def save_settings(self):
        cur = self.con.cursor()
        sql_color_main = "UPDATE settings SET val=? WHERE name = 'bg color main window'", (self.color_main, )
        sql_color_base = "UPDATE settings SET val=? WHERE name = 'bg color base window'", (self.color_base, )
        sql_color_settings = "UPDATE settings SET val=? WHERE name = 'bg color settings window'", \
                             (self.color_settings, )

        sql_lan = "UPDATE settings SET val=? WHERE name='language'", (self.lan, )
        sql_round = "UPDATE settings SET val=? WHERE name='border radius'", (int(self.round) // 2, )

        cur.execute(*sql_color_main)
        cur.execute(*sql_color_base)
        cur.execute(*sql_color_settings)

        cur.execute(*sql_lan)
        cur.execute(*sql_round)
        self.con.commit()
        self.setWindowTitle(self.language_words[54])
        self.status_label.setText(self.language_words[63])


class Base(QDialog):
    def __init__(self, parent=None):
        super(Base, self).__init__(parent)
        global events_lst
        uic.loadUi('UI/base.ui', self)

        self.lst = events_lst
        self.id = []
        self.max = 0
        self.con = sqlite3.connect("base.db")

        self.language = None
        self.language_words = []
        cur = self.con.cursor()
        res = cur.execute("SELECT val FROM settings WHERE name='language'").fetchall()
        res = res[0][0]
        self.language = res
        with open(f'txt files/{res}.txt', mode='r', encoding='utf-8') as f_in:
            self.language_words = f_in.readlines()
        self.language_words = list(map(lambda x: x.split('\n')[0], self.language_words))

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
            if self.language == 'English':
                self.TW.setHorizontalHeaderLabels(['ID', 'Name', 'Picture'])
            elif self.language == 'Russian':
                self.TW.setHorizontalHeaderLabels(['ID', 'Имя', 'Картина'])

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
        cur = self.con.cursor()
        res = cur.execute("SELECT val FROM settings WHERE name='bg color base window'").fetchall()

        self.setStyleSheet("#Form{background-color:" + res[0][0] + "}")

        self.setWindowTitle(self.language_words[39])

        self.add_btn.setText(self.language_words[61])
        self.del_btn.setText(self.language_words[62])
        self.take_btn.setText(self.language_words[52])

        self.move(500, 200)

    def add(self):
        global events_lst
        name, ok_pressed = QInputDialog.getText(self, self.language_words[47],
                                                self.language_words[48], QLineEdit.Normal, "")
        if ok_pressed:
            id_, ok_pressed2 = QInputDialog.getInt(self, self.language_words[49],
                                                   self.language_words[50], 1, 1, 999, 1)
            if ok_pressed2:
                cur = self.con.cursor()
                cur.execute("INSERT INTO tab VALUES(?, ?, ?);", [id_, name, events_lst])
                self.con.commit()
                self.update_result()

    def delete(self):
        val, ok_pressed = QInputDialog.getInt(self, self.language_words[44], self.language_words[45], 1, 1, 999, 1)
        if ok_pressed and val in self.id:
            cur = self.con.cursor()
            cur.execute("DELETE FROM tab WHERE ID=" + str(val))
            self.con.commit()
            self.update_result()

    def take(self):
        global events_lst
        val, ok_pressed = QInputDialog.getInt(self, self.language_words[44], self.language_words[46], 1, 1, 999, 1)
        if ok_pressed:
            cur = self.con.cursor()
            res = cur.execute("SELECT Code FROM tab WHERE ID=" + str(val)).fetchall()
            events_lst = res[0][0]


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_settings = Setting()
        self.window_base = Base(self)

        self.file_name = ''
        self.x_img, self.y_img = 0, 0

        self.mouse_pressed = False

        self.events = []

        self.con = sqlite3.connect("base.db")

        self.language = None
        self.language_words = []

        cur = self.con.cursor()
        res = cur.execute("SELECT val FROM settings WHERE name='language'").fetchall()
        res = res[0][0]
        self.language = res

        with open(f'txt files/{res}.txt', mode='r', encoding='utf-8') as f_in:
            self.language_words = f_in.readlines()
        self.language_words = list(map(lambda z: z.split('\n')[0], self.language_words))

        self.point = None
        self.tool = self.language_words[0]
        self.alpha = 100
        self.thick = 5
        self.color = '#000000'
        self.style = self.language_words[1]
        self.fill = None

        self.x = 160
        self.y = 145
        self.width = 1500
        self.height = 800

        self.mouse_pos0 = None
        self.mouse_pos1 = None

        uic.loadUi('UI/main.ui', self)
        self.init_ui()

        x = cur.execute("SELECT val FROM settings WHERE name='border radius'").fetchall()
        x = x[0][0]
        for i in self.color_group.buttons():
            i.setStyleSheet(f"background-color : #{i.objectName()[4:]}; border-radius: {round(30 * x / 100)}px;")
            i.clicked.connect(self.set_color)

        for i in self.tool_group.buttons():
            i.clicked.connect(self.set_tool)

        self.clear_btn.clicked.connect(self.clear)

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
        self.window_base.exec()
        self.clear()
        with open('img.jpg', 'wb') as file:
            file.write(events_lst)
        im = Image.open('img.jpg')
        w, h = im.size
        im.save('img.jpg')
        self.label.setPixmap(QPixmap('img.jpg'))
        self.label.setGeometry(self.x, self.y, w, h)
        self.update()

    def save_as(self):
        filename = QFileDialog.getSaveFileName(None, self.language_words[40], 'C:\\', "Image files (*.jpg *.png)")
        if filename:
            if filename[0].count('.') == 1 and filename[0][filename[0].index('.') + 1:] in ['jpg', 'png']:
                im = self.label.pixmap()
                im.save(filename[0])
            elif filename != ('', ''):
                valid = QMessageBox.question(
                    self, self.language_words[41], self.language_words[42],
                    QMessageBox.Yes, QMessageBox.No)
                if valid == QMessageBox.Yes:
                    self.save_as()

    def save(self):
        if not self.file_name:
            self.save_as()
        else:
            im = self.label.pixmap()
            im.save(self.file_name)

    def new(self):
        self.events = list()
        self.x_img, self.y_img = 0, 0
        self.file_name = ''
        self.size_holst()

    def open(self):
        filename = QFileDialog.getOpenFileName(None, self.language_words[43], 'C:\\', "Image files (*.jpg *.png)")
        self.file_name = filename[0]
        if filename[0]:
            img = Image.open(filename[0]).resize((self.width, self.height)).convert('RGB')
            img.save('img.jpg')
            self.x_img, self.y_img = img.size
            self.label.setPixmap(QPixmap('img.jpg'))
            self.setWindowTitle(f'{self.language_words[2]} {filename[0]}')
            self.events = list()
            self.update()

    def mousePressEvent(self, event):
        if self.tool in [self.language_words[0], self.language_words[26],
                         self.language_words[27], self.language_words[28]]:
            self.move_point(event)
            if event.x() in [i for i in range(self.x, self.x + self.width)] and \
                    event.y() in [i for i in range(self.y, self.y + self.height)]:
                self.x_y_label.setText(f'X: {event.x() - self.x}, Y: {event.y() - self.y}.')
        elif self.tool == self.language_words[29]:
            self.move_line(event)
            if event.x() in [i for i in range(self.x, self.x + self.width)] and \
                    event.y() in [i for i in range(self.y, self.y + self.height)]:
                x = u"X\u2081"
                y = u"Y\u2081"
                self.x_y_label.setText(f'{x}: {event.x() - self.x}, {y}: {event.y() - self.y}.')
        elif self.tool in [self.language_words[30], self.language_words[31]]:
            self.move_rect_circle(event)
            if event.x() in [i for i in range(self.x, self.x + self.width)] and \
                    event.y() in [i for i in range(self.y, self.y + self.height)]:
                x = u"X\u2081"
                y = u"Y\u2081"
                self.x_y_label.setText(f'{x}: {event.x() - self.x}, {y}: {event.y() - self.y}.')
        self.mouse_pressed = True
        # Вызов перерисовки виджета
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            if self.tool in [self.language_words[0], self.language_words[26],
                             self.language_words[27], self.language_words[28]]:
                self.move_point(event)
                if event.x() in [i for i in range(self.x, self.x + self.width)] and \
                        event.y() in [i for i in range(self.y, self.y + self.height)]:
                    self.x_y_label.setText(f'X: {event.x() - self.x}, Y: {event.y() - self.y}.')
            elif self.tool in [self.language_words[29], self.language_words[30], self.language_words[31]]:
                if event.x() in [i for i in range(self.x, self.x + self.width)] and \
                        event.y() in [i for i in range(self.y, self.y + self.height)]:
                    x = u"X\u2081"
                    y = u"Y\u2081"
                    x2 = u"X\u2082"
                    y2 = u"Y\u2082"
                    self.x_y_label.setText(
                        f'{x}: {self.mouse_pos0[0] - self.x}, {y}: '
                        f'{self.mouse_pos0[1] - self.y}; {x2}: {event.x() - self.x}, {y2}: {event.y() - self.y}.')
        self.update()

    def mouseReleaseEvent(self, event):
        if self.tool in [self.language_words[0], self.language_words[26],
                         self.language_words[27], self.language_words[28]]:
            self.events.append([None])
        elif self.tool == self.language_words[29]:
            self.move_line(event)
        elif self.tool in [self.language_words[30], self.language_words[31]]:
            self.move_rect_circle(event)
        self.x_y_label.setText('')
        self.point = None
        self.mouse_pressed = False
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.selected_color.setStyleSheet(f"background-color : {self.color}")

    def draw(self):
        qp = QPainter(self.label.pixmap())
        qp.begin(self)
        for i in range(len(self.events)):
            try:
                if self.events[i][0] == 'Point':
                    n = QColor(self.events[i][1][0], self.events[i][1][1],
                               self.events[i][1][2], self.events[i][2])
                    if self.events[i + 1][0] == 'Point':
                        qp.setPen(QPen(QColor(255, 255, 255), self.events[i][3]))
                        qp.drawLine(self.events[i][4], self.events[i + 1][4])
                        qp.setPen(QPen(n, self.events[i][3]))
                        qp.drawLine(self.events[i][4], self.events[i + 1][4])
                        qp.setPen(QPen(QColor(255, 255, 255), self.events[i][3]))
                        qp.drawPoint(self.events[i][4])
                        qp.drawPoint(self.events[i + 1][4])
                        qp.setPen(QPen(QColor(self.events[i][1][0], self.events[i][1][1],
                                              self.events[i][1][2], self.events[i][2]), self.events[i][3]))
                        qp.drawPoint(self.events[i][4])
                        qp.drawPoint(self.events[i + 1][4])
                        self.events.pop(i)
                        self.events.pop(i + 1)
                elif self.events[i][0] == 'Line':
                    n = QColor(self.events[i][1][0], self.events[i][1][1],
                               self.events[i][1][2], self.events[i][2])
                    qp.setPen(QPen(n, self.events[i][3], self.events[i][6]))
                    qp.drawLine(self.events[i][4][0], self.events[i][4][1], self.events[i][5][0], self.events[i][5][1])
                    self.events.pop(i)
                elif self.events[i][0] == 'Rectangle':
                    p = QColor(self.events[i][1][0], self.events[i][1][1],
                               self.events[i][1][2], self.events[i][2])
                    qp.setPen(QPen(p, self.events[i][3], self.events[i][7]))
                    if self.events[i][6]:
                        b = QColor(self.events[i][6][0], self.events[i][6][1],
                                   self.events[i][6][2], self.events[i][2])
                        qp.setBrush(b)
                    else:
                        qp.setBrush(QBrush())
                    qp.drawRect(self.events[i][4][0], self.events[i][4][1], self.events[i][5][0] - self.events[i][4][0],
                                self.events[i][5][1] - self.events[i][4][1])
                    self.events.pop(i)
                elif self.events[i][0] == 'Circle':
                    p = QColor(self.events[i][1][0], self.events[i][1][1],
                               self.events[i][1][2], self.events[i][2])
                    qp.setPen(QPen(p, self.events[i][3], self.events[i][7]))
                    if self.events[i][6]:
                        b = QColor(self.events[i][6][0], self.events[i][6][1],
                                   self.events[i][6][2], self.events[i][2])
                        qp.setBrush(b)
                    else:
                        qp.setBrush(QBrush())
                    qp.drawEllipse(self.events[i][4][0], self.events[i][4][1],
                                   self.events[i][5][0] - self.events[i][4][0],
                                   self.events[i][5][1] - self.events[i][4][1])
                    self.events.pop(i)
            except IndexError:
                pass
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

    def move_rect_circle(self, event):
        if not self.mouse_pos0:
            self.mouse_pos0 = event.x(), event.y()
        else:
            t = None
            if self.tool == 'rectangle' or self.tool == 'прямоугольник':
                t = 'Rectangle'
            elif self.tool == 'circle' or self.tool == 'круг':
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
        if self.style == self.language_words[1]:
            stl = Qt.SolidLine
        elif self.style == self.language_words[3]:
            stl = Qt.DashLine
        elif self.style == self.language_words[4]:
            stl = Qt.DotLine
        elif self.style == self.language_words[5]:
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
        if k == 16777216:
            sys.exit()

    def show_full_screen(self):
        self.showFullScreen()

    def show_max_screen(self):
        self.showMaximized()

    def show_min_screen(self):
        self.showMinimized()

    def init_ui(self):
        self.showMaximized()
        h = self.size().height()
        self.setWindowTitle(self.language_words[2])

        self.btn_fill.setText(self.language_words[32])
        self.tools_label.setText(self.language_words[33])
        self.color_label.setText(self.language_words[34])
        self.personal_color_label.setText(self.language_words[35])
        self.txt_thick_label.setText(self.language_words[36])
        self.txt_alpha_label.setText(self.language_words[37])
        self.is_used_label.setText(self.language_words[38])

        self.save_btn.setText(self.language_words[10])
        self.save_as_btn.setText(self.language_words[11])
        self.open_btn.setText(self.language_words[12])
        self.base_btn.setText(self.language_words[39])

        self.is_used_label_tool.setText(self.tool)

        cur = self.con.cursor()
        res = cur.execute("SELECT val FROM settings WHERE name='bg color main window'").fetchall()

        self.setStyleSheet("#Form{background-color:" + res[0][0] + "}")

        app.setWindowIcon(QIcon('images/ico.ico'))
        self.comboBox_line.addItems([self.language_words[1], self.language_words[3],
                                     self.language_words[4], self.language_words[5]])

        exit_action = QAction(QIcon('images/menu bar/exit.png'), f'&{self.language_words[6]}', self)
        exit_action.setShortcut('esc')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)

        full_screen_action = QAction(QIcon('images/menu bar/full screen.png'), f'&{self.language_words[7]}', self)
        full_screen_action.setShortcut('F11')
        full_screen_action.setStatusTip('Full screen application')
        full_screen_action.triggered.connect(self.show_full_screen)

        max_screen_action = QAction(QIcon('images/menu bar/max screen.png'), f'&{self.language_words[8]}', self)
        max_screen_action.setShortcut('F3')
        max_screen_action.setStatusTip('Max screen application')
        max_screen_action.triggered.connect(self.show_max_screen)

        min_screen_action = QAction(QIcon('images/menu bar/min screen.png'), f'&{self.language_words[9]}', self)
        min_screen_action.setShortcut('Ctrl+-')
        min_screen_action.setStatusTip('Min screen application')
        min_screen_action.triggered.connect(self.show_min_screen)

        save_action = QAction(QIcon('images/menu bar/save.png'), f'&{self.language_words[10]}', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save application')
        save_action.triggered.connect(self.save)

        save_as_action = QAction(QIcon('images/menu bar/save as.jpg'), f'&{self.language_words[11]}', self)
        save_as_action.setShortcut('Shift+Ctrl+S')
        save_as_action.setStatusTip('Save as application')
        save_as_action.triggered.connect(self.save_as)

        open_action = QAction(QIcon('images/menu bar/open.png'), f'&{self.language_words[12]}', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open application')
        open_action.triggered.connect(self.open)

        new_action = QAction(QIcon('images/menu bar/new.jpg'), f'&{self.language_words[13]}', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New application')
        new_action.triggered.connect(self.new)

        setting_action = QAction(QIcon('images/menu bar/settings.jpg'), f'&{self.language_words[14]}', self)
        setting_action.setShortcut('Ctrl+D')
        setting_action.setStatusTip('Settings application')
        setting_action.triggered.connect(self.settings)

        base_action = QAction(QIcon('images/menu bar/base.jpg'), f'&{self.language_words[39]}', self)
        base_action.setShortcut('Ctrl+B')
        base_action.setStatusTip('Settings application')
        base_action.triggered.connect(self.base)

        menu_bar = self.menuBar()

        menu = menu_bar.addMenu(f'&{self.language_words[15]}')
        file = menu_bar.addMenu(f'&{self.language_words[16]}')
        settings = menu_bar.addMenu(f'&{self.language_words[14]}')
        base = menu_bar.addMenu(f'&{self.language_words[39]}')

        menu.addAction(exit_action)
        menu.addAction(full_screen_action)
        menu.addAction(max_screen_action)
        menu.addAction(min_screen_action)

        file.addAction(new_action)
        file.addAction(open_action)
        file.addAction(save_action)
        file.addAction(save_as_action)
        
        settings.addAction(setting_action)

        base.addAction(base_action)

        self.x_y_label.move(0, h - 40)

        self.btn_fill.setVisible(False)
        self.btn_color_fill.setVisible(False)
        self.comboBox_line.setVisible(False)
        self.save_as_btn.setVisible(False)
        self.save_btn.setVisible(False)
        self.open_btn.setVisible(False)
        self.base_btn.setVisible(False)

        self.statusBar().showMessage(self.language_words[18])

        self.git.setText(f'<a href="https://github.com/VladimirBadzgaradze/PyQt5-project">'
                         f'{self.language_words[19]}</a>')
        self.git.setOpenExternalLinks(True)

        self.git_img.setPixmap(QPixmap('images/git.jpg'))

        self.set_img_on_buttons()

        self.statusBar().showMessage(self.language_words[20])

        self.size_holst()

    def settings(self):
        self.window_settings.show()

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
        if self.tool == 'marker':
            if self.language == 'Russian':
                self.tool = self.language_words[0]
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
            if self.language == 'Russian':
                self.tool = self.language_words[26]
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
            if self.language == 'Russian':
                self.tool = self.language_words[27]
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
            if self.language == 'Russian':
                self.tool = self.language_words[28]
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
            if self.language == 'Russian':
                self.tool = self.language_words[29]
            self.thick_slider.setValue(self.thick)
            self.set_thick(self.thick)
            self.alpha_slider.setValue(self.alpha)
            self.set_alpha(self.alpha)
            self.color = self.color
            self.btn_fill.setVisible(False)
            self.btn_color_fill.setVisible(False)
            self.comboBox_line.setVisible(True)
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
        elif self.tool == 'rectangle':
            if self.language == 'Russian':
                self.tool = self.language_words[30]
            self.thick_slider.setValue(self.thick)
            self.set_thick(self.thick)
            self.alpha_slider.setValue(self.alpha)
            self.set_alpha(self.alpha)
            self.color = self.color
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
            self.btn_fill.setVisible(True)
            self.btn_color_fill.setVisible(True)
            self.comboBox_line.setVisible(True)
            if self.language == 'Russian':
                self.btn_color_fill.move(120, 520)
            elif self.language == 'English':
                self.btn_color_fill.move(70, 520)
        elif self.tool == 'circle':
            if self.language == 'Russian':
                self.tool = self.language_words[31]
            self.thick_slider.setValue(self.thick)
            self.set_thick(self.thick)
            self.alpha_slider.setValue(self.alpha)
            self.set_alpha(self.alpha)
            self.color = self.color
            self.selected_color.setStyleSheet(f"background-color : #{self.color}")
            self.btn_fill.setVisible(True)
            self.btn_color_fill.setVisible(True)
            self.comboBox_line.setVisible(True)
            if self.language == 'Russian':
                self.btn_color_fill.move(120, 520)
            elif self.language == 'English':
                self.btn_color_fill.move(70, 520)
        self.is_used_label_tool.setText(self.tool)

    def size_holst(self):
        width = self.size().width()
        height = self.size().height()
        w, ok_pressed = QInputDialog.getInt(
            self, self.language_words[21], self.language_words[22],
            1500, 100, width - self.x, 10)
        if ok_pressed:
            self.width = w
        h, ok_pressed = QInputDialog.getInt(
            self, self.language_words[21], self.language_words[23],
            800, 100, height - self.y - 42, 10)
        if ok_pressed:
            self.height = h

        self.statusBar().showMessage(self.language_words[24])

        im = Image.open('img.jpg').resize((self.width, self.height))
        pix = im.load()
        w, h = im.size
        for i in range(w):
            for j in range(h):
                pix[i, j] = 255, 255, 255
        im.save('img.jpg')
        self.label.setPixmap(QPixmap('img.jpg'))
        self.label.setGeometry(self.x, self.y, self.width, self.height)

        self.statusBar().showMessage(self.language_words[25])

    def clear(self):
        self.events = list()
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
        self.marker.setIcon(QIcon('images/tools/marker.png'))
        self.marker.setIconSize(QSize(61, 61))
        self.stylus.setIcon(QIcon('images/tools/stylus.png'))
        self.stylus.setIconSize(QSize(61, 61))
        self.brush.setIcon(QIcon('images/tools/brush.png'))
        self.brush.setIconSize(QSize(61, 61))
        self.clear_btn.setIcon(QIcon('images/clear.png'))
        self.clear_btn.setIconSize(QSize(61, 61))
        self.rubber.setIcon(QIcon('images/tools/rubber.png'))
        self.rubber.setIconSize(QSize(61, 61))
        self.line.setIcon(QIcon('images/tools/line.png'))
        self.line.setIconSize(QSize(61, 61))
        self.rectangle.setIcon(QIcon('images/tools/rectangle.png'))
        self.rectangle.setIconSize(QSize(61, 61))
        self.circle.setIcon(QIcon('images/tools/circle.png'))
        self.circle.setIconSize(QSize(61, 61))
        self.menu_btn.setIcon(QIcon('images/menu1.png'))
        self.menu_btn.setIconSize(QSize(91, 91))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
