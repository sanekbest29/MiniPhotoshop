import sys
import sqlite3
import torch
from torchvision import transforms
from os import listdir, remove, path
from PIL import Image, ImageFilter
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox, QColorDialog

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Miniphotoshop(object):
    def vers(self):
        self.max_version += 1
        self.version += 1
        self.original_img.save(f'versions\\vers{self.version}.png')
        with sqlite3.connect('data.db') as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO versions(version) VALUES(?)""",
                        (f'versions\\vers{self.version}.png',))

    def get_file(self):
        if self.warning:
            self.erorr('Ваше изображение будет сжато до разрешения 640x360', 'ПРЕДУПРЕЖДЕНИЕ')
            self.warning = False
        self.fname = QFileDialog.getOpenFileName(None, 'Выбрать картинку', '',
                                                 'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]
        if self.fname:
            self.original_img = Image.open(self.fname)
            self.original_img = self.original_img.convert('RGBA')
            self.canvas()
            self.vers()
            self.max_version += 1
            self.version += 1

    def save_file(self):
        if self.get_image:
            filePath, _ = QFileDialog.getSaveFileName(None, "Save Image", "",
                                                      "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
            if filePath == "":
                return
            self.original_img.save(filePath)

    def empty_canvas(self):
        if self.getSizeX.text().isdigit() and self.getSizeY.text().isdigit():
            if int(self.getSizeX.text()) == 0 or int(self.getSizeY.text()) == 0:
                self.erorr('Число должно быть только положительным и не равным 0')
            else:
                self.original_img = Image.new("RGBA", (int(self.getSizeX.text()), int(self.getSizeY.text())),
                                              (255, 255, 255))
                self.canvas(True)
        else:
            self.erorr('Тут должно быть только число')

    def canvas(self, status=False):
        if not status:
            self.im2 = self.original_img.resize((640, 360))
        else:
            self.im2 = self.original_img
        transp = int(self.alpha.value())
        self.im2.putalpha(transp)
        self.im2.save('new1.png')
        self.update_canvas()

    def update_canvas(self):
        self.pixmap = QPixmap('new1.png')
        self.image.setPixmap(self.pixmap)
        self.get_image = True

    def change_alpha(self):
        transp = int(self.alpha.value())
        if self.fname:
            self.original_img.putalpha(transp)
            self.original_img.save(self.new_img)
            self.vers()
            self.canvas()

    def erorr(self, text, warning='ОШИБКА!!!'):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle(warning)
        error_dialog.setText(text)
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        error_dialog.exec_()

    def clear(self):
        dir = 'versions'
        for f in listdir(dir):
            remove(path.join(dir, f))

        with sqlite3.connect('data.db') as db:
            cur = db.cursor()
            comand = """DELETE FROM versions"""
            cur.execute(comand)
            comand = """UPDATE sqlite_sequence
                        SET seq = '0'
                        WHERE name = 'versions'"""
            cur.execute(comand)

    def black_white(self):
        if self.get_image:
            pixels = self.original_img.load()
            x, y = self.original_img.size
            for i in range(x):
                for j in range(y):
                    r, g, b, alpha = pixels[i, j]
                    bw = (r + g + b) // 3
                    pixels[i, j] = bw, bw, bw, alpha
            self.original_img.save(self.new_img)
            self.vers()
            self.canvas()
        else:
            self.erorr('вы не выбрали изображение')

    def negative(self):
        if self.get_image:
            pixels = self.original_img.load()
            x, y = self.original_img.size
            for i in range(x):
                for j in range(y):
                    r, g, b, alpha = pixels[i, j]
                    pixels[i, j] = 255 - r, 255 - g, 255 - b, alpha
            self.original_img.save(self.new_img)
            self.vers()
            self.canvas()
        else:
            self.erorr('вы не выбрали изображение')

    def blur(self):
        if self.get_image:
            radius, ok_pressed = QInputDialog.getInt(
                None, "Размытие", "введите радиус размытия",
                1, 0, 100, 1)
            if ok_pressed:
                img = Image.open('new.png')
                self.original_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
                self.original_img.save(self.new_img)
                self.vers()
                self.canvas()
        else:
            self.erorr('вы не выбрали изображение')

    def contour_image(self):
        if self.get_image:
            img = Image.open('new.png')
            self.original_img = img.filter(ImageFilter.CONTOUR)
            self.original_img.save('new.png')
            self.vers()
            self.canvas()
        else:
            self.erorr('вы не выбрали изображение')

    def glitch(self):
        if self.get_image:
            delta, ok_pressed = QInputDialog.getInt(
                None, "Глитч", "введите длинну сдвига",
                1, 0, 100, 1)

            if ok_pressed:
                im = Image.open('new.png')
                x1, y1 = im.size
                self.original_img = Image.new('RGBA', (x1, y1), (0, 0, 0))
                pixels = im.load()
                pixels2 = self.original_img.load()
                for x in range(x1):
                    for y in range(y1):
                        if x >= delta:
                            g, b, alpha = pixels[x, y][1:]
                            r = pixels[x - delta, y][0]
                            pixels2[x, y] = r, g, b
                        else:
                            g, b, alpha = pixels[x, y][1:]
                            pixels2[x, y] = 0, g, b
                self.original_img.save("new.png")
                self.vers()
                self.canvas()
        else:
            self.erorr('Вы не выбрали изображение')

    def emboss(self):
        if self.get_image:
            img = Image.open('new.png')
            self.original_img = img.filter(ImageFilter.EMBOSS)
            self.original_img.save("new.png")
            self.vers()
            self.canvas()
        else:
            self.erorr('Вы не выбрали изображение')

    def sharpen(self):
        if self.get_image:
            img = Image.open('new.png')
            self.original_img = img.filter(ImageFilter.SHARPEN)
            self.original_img.save("new.png")
            self.vers()
            self.canvas()
        else:
            self.erorr('Вы не выбрали изображение')

    def delete_canvas(self):
        self.pixmap = QPixmap('')
        self.image.setPixmap(self.pixmap)
        self.get_image = False
        self.fname = None

    def undo(self):
        if self.get_image:
            if self.version >= 1:
                self.version -= 1
                with sqlite3.connect('data.db') as db:
                    cur = db.cursor()
                    result = cur.execute("""SELECT version FROM versions 
                    WHERE id = ?""", (f'{self.version}',))
                for el in result:
                    self.original_img = Image.open(el[0])
                    pixels = self.original_img.load()
                    *_, alpha = pixels[1, 1]
                    self.alpha.setValue(alpha)
                    self.original_img.save("new.png")
                    self.canvas()
            else:
                self.get_image = False
                self.pixmap = QPixmap('')
                self.image.setPixmap(self.pixmap)
                self.fname = None
        else:
            self.erorr('Вы не выбрали изображение')

    def redo(self):
        if self.get_image:
            if self.max_version == self.version:
                self.erorr('Вы достигли последней версии изображения')
            else:
                self.version += 1
                with sqlite3.connect('data.db') as db:
                    cur = db.cursor()
                    result = cur.execute("""SELECT version FROM versions 
                            WHERE id = ?""", (f'{self.version}',))
                for el in result:
                    self.original_img = Image.open(el[0])
                    pixels = self.original_img.load()
                    *_, alpha = pixels[1, 1]
                    self.alpha.setValue(alpha)
                    self.original_img.save("new.png")
                    self.canvas()
        else:
            self.erorr('Вы не выбрали изображение')

    def rotate_img(self):
        if self.get_image:
            self.original_img = self.original_img.rotate(90, expand=True)
            self.original_img.save("new.png")
            self.canvas()
            self.vers()
        else:
            self.erorr('Вы не выбрали изображение')

    def reverse_rotate_img(self):
        if self.get_image:
            self.original_img = self.original_img.rotate(-90, expand=True)

            self.original_img.save("new.png")
            self.canvas()
            self.vers()
        else:
            self.erorr('Вы не выбрали изображение')

    def mirrow(self):
        if self.get_image:
            self.original_img = self.original_img.transpose(Image.FLIP_LEFT_RIGHT)

            self.original_img.save("new.png")
            self.canvas()
            self.vers()
        else:
            self.erorr('Вы не выбрали изображение')

    def remove_background(self):
        if self.get_image:
            model = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_resnet50', pretrained=True)

            model.eval()

            input_image = self.original_img.convert("RGB")
            preprocess = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            input_tensor = preprocess(input_image)
            input_batch = input_tensor.unsqueeze(0)

            with torch.no_grad():
                output = model(input_batch)['out'][0]
            output_predictions = output.argmax(0)

            palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])
            colors = torch.as_tensor([i for i in range(21)])[:, None] * palette
            colors = (colors % 255).numpy().astype("uint8")

            r = Image.fromarray(output_predictions.byte().cpu().numpy()).resize(input_image.size)
            r.putpalette(colors)
            rgb_image = r.convert('RGB')
            x, y = r.size
            pixels2 = rgb_image.load()
            pixels = self.original_img.load()
            for i in range(x):
                for j in range(y):
                    r, g, b = pixels2[i, j]
                    if (r, g, b) == (0, 0, 0):
                        pixels[i, j] = 255, 255, 255, int(self.alpha.value())
            self.original_img.save('new.png')
            self.vers()
            self.canvas()
        else:
            self.erorr('Вы не выбрали изображение')

    def original_color(self):
        self.color1 = QColorDialog.getColor()

    def replaced_color(self):
        self.color2 = QColorDialog.getColor()

    def replace_color(self):
        if self.get_image:
            if self.color1 and self.color2:
                pixels = self.original_img.load()
                x, y = self.original_img.size
                for i in range(x):
                    for j in range(y):
                        if self.color1.getRgb() == pixels[i, j]:
                            pixels[i, j] = self.color2.getRgb()
                self.original_img.save('new.png')
                self.vers()
                self.canvas()
            else:
                self.erorr('Вы не выбрали цвет')
        else:
            self.erorr('Вы не выбрали изображение')

    def setupUi(self, Miniphotoshop):
        Miniphotoshop.setObjectName("Miniphotoshop")
        Miniphotoshop.resize(940, 637)
        Miniphotoshop.setStyleSheet("alternate-background-color: rgb(204, 13, 195);")
        self.centralwidget = QtWidgets.QWidget(Miniphotoshop)
        self.centralwidget.setObjectName("centralwidget")
        self.getFile_btn = QtWidgets.QPushButton(self.centralwidget)
        self.getFile_btn.setGeometry(QtCore.QRect(30, 10, 101, 23))
        self.getFile_btn.setObjectName("getFile_btn")
        self.saveFile_btn = QtWidgets.QPushButton(self.centralwidget)
        self.saveFile_btn.setGeometry(QtCore.QRect(30, 40, 101, 23))
        self.saveFile_btn.setObjectName("saveFile_btn")
        self.getSizeX = QtWidgets.QLineEdit(self.centralwidget)
        self.getSizeX.setGeometry(QtCore.QRect(30, 170, 113, 20))
        self.getSizeX.setInputMask("")
        self.getSizeX.setObjectName("getSizeX")
        self.getSizeY = QtWidgets.QLineEdit(self.centralwidget)
        self.getSizeY.setGeometry(QtCore.QRect(30, 200, 113, 20))
        self.getSizeY.setObjectName("getSizeY")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 170, 16, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 200, 16, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.image = QtWidgets.QLabel(self.centralwidget)
        self.image.setGeometry(QtCore.QRect(290, 10, 640, 360))
        self.image.setStyleSheet("border-color: rgb(219, 35, 255);")
        self.image.setText("")
        self.image.setObjectName("image")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(50, 270, 47, 13))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(50, 470, 71, 16))
        self.label_6.setObjectName("label_6")
        self.alpha = QtWidgets.QSlider(self.centralwidget)
        self.alpha.setGeometry(QtCore.QRect(190, 40, 22, 160))
        self.alpha.setMaximum(255)
        self.alpha.setProperty("value", 255)
        self.alpha.setOrientation(QtCore.Qt.Vertical)
        self.alpha.setObjectName("alpha")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(140, 10, 151, 21))
        self.label_7.setObjectName("label_7")
        self.empty_btn = QtWidgets.QPushButton(self.centralwidget)
        self.empty_btn.setGeometry(QtCore.QRect(20, 140, 131, 23))
        self.empty_btn.setObjectName("empty_btn")
        self.cb_btn = QtWidgets.QPushButton(self.centralwidget)
        self.cb_btn.setGeometry(QtCore.QRect(10, 290, 81, 31))
        self.cb_btn.setObjectName("cb_btn")
        self.negative_btn = QtWidgets.QPushButton(self.centralwidget)
        self.negative_btn.setGeometry(QtCore.QRect(10, 320, 81, 31))
        self.negative_btn.setObjectName("negative_btn")
        self.emboss_btn = QtWidgets.QPushButton(self.centralwidget)
        self.emboss_btn.setGeometry(QtCore.QRect(90, 350, 81, 31))
        self.emboss_btn.setObjectName("emboss_btn")
        self.blur_btn = QtWidgets.QPushButton(self.centralwidget)
        self.blur_btn.setGeometry(QtCore.QRect(10, 350, 81, 31))
        self.blur_btn.setObjectName("blur_btn")
        self.glitch_btn = QtWidgets.QPushButton(self.centralwidget)
        self.glitch_btn.setGeometry(QtCore.QRect(90, 320, 81, 31))
        self.glitch_btn.setObjectName("glitch_btn")
        self.contour_btn = QtWidgets.QPushButton(self.centralwidget)
        self.contour_btn.setGeometry(QtCore.QRect(90, 290, 101, 31))
        self.contour_btn.setObjectName("contour_btn")
        self.delete_btn = QtWidgets.QPushButton(self.centralwidget)
        self.delete_btn.setGeometry(QtCore.QRect(30, 70, 101, 31))
        self.delete_btn.setObjectName("delete_btn")
        self.sharpen_btn = QtWidgets.QPushButton(self.centralwidget)
        self.sharpen_btn.setGeometry(QtCore.QRect(10, 380, 161, 31))
        self.sharpen_btn.setObjectName("sharpen_btn")
        self.undo_btn = QtWidgets.QPushButton(self.centralwidget)
        self.undo_btn.setGeometry(QtCore.QRect(580, 420, 161, 31))
        self.undo_btn.setObjectName("undo_btn")
        self.redo_btn = QtWidgets.QPushButton(self.centralwidget)
        self.redo_btn.setGeometry(QtCore.QRect(740, 420, 171, 31))
        self.redo_btn.setObjectName("redo_btn")
        self.background_btn = QtWidgets.QPushButton(self.centralwidget)
        self.background_btn.setGeometry(QtCore.QRect(10, 410, 161, 31))
        self.background_btn.setObjectName("background_btn")
        self.revers_rotate_btn = QtWidgets.QPushButton(self.centralwidget)
        self.revers_rotate_btn.setGeometry(QtCore.QRect(4, 490, 91, 31))
        self.revers_rotate_btn.setObjectName("revers_rotate_btn")
        self.rotate_btn = QtWidgets.QPushButton(self.centralwidget)
        self.rotate_btn.setGeometry(QtCore.QRect(100, 490, 91, 31))
        self.rotate_btn.setObjectName("rotate_btn")
        self.mirror_btn = QtWidgets.QPushButton(self.centralwidget)
        self.mirror_btn.setGeometry(QtCore.QRect(4, 522, 91, 31))
        self.mirror_btn.setObjectName("mirror_btn")
        self.replace_color_btn = QtWidgets.QPushButton(self.centralwidget)
        self.replace_color_btn.setGeometry(QtCore.QRect(390, 560, 91, 31))
        self.replace_color_btn.setObjectName("replace_color_btn")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(400, 430, 71, 16))
        self.label_3.setObjectName("label_3")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(400, 500, 61, 16))
        self.label_10.setObjectName("label_10")
        self.original_color_btn = QtWidgets.QPushButton(self.centralwidget)
        self.original_color_btn.setGeometry(QtCore.QRect(310, 500, 75, 23))
        self.original_color_btn.setObjectName("original_color_btn")
        self.replaced_color_btn = QtWidgets.QPushButton(self.centralwidget)
        self.replaced_color_btn.setGeometry(QtCore.QRect(480, 500, 75, 23))
        self.replaced_color_btn.setObjectName("replaced_color_btn")
        Miniphotoshop.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Miniphotoshop)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 940, 21))
        self.menubar.setObjectName("menubar")
        Miniphotoshop.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Miniphotoshop)
        self.statusbar.setObjectName("statusbar")
        Miniphotoshop.setStatusBar(self.statusbar)

        self.retranslateUi(Miniphotoshop)
        QtCore.QMetaObject.connectSlotsByName(Miniphotoshop)

        self.warning = True
        self.fname = ''
        self.current = "orig.jpg"
        self.new_img = 'new.png'
        self.pixmap = QPixmap(self.current)
        self.image.setPixmap(self.pixmap)
        self.get_image = False

        self.color1 = None
        self.color2 = None

        self.max_version = 0
        self.version = 0

        self.clear()

        self.getFile_btn.clicked.connect(self.get_file)
        self.alpha.valueChanged.connect(self.change_alpha)
        self.empty_btn.clicked.connect(self.empty_canvas)
        self.saveFile_btn.clicked.connect(self.save_file)
        self.cb_btn.clicked.connect(self.black_white)
        self.negative_btn.clicked.connect(self.negative)
        self.blur_btn.clicked.connect(self.blur)
        self.contour_btn.clicked.connect(self.contour_image)
        self.glitch_btn.clicked.connect(self.glitch)
        self.emboss_btn.clicked.connect(self.emboss)
        self.sharpen_btn.clicked.connect(self.sharpen)
        self.delete_btn.clicked.connect(self.delete_canvas)
        self.undo_btn.clicked.connect(self.undo)
        self.redo_btn.clicked.connect(self.redo)
        self.background_btn.clicked.connect(self.remove_background)
        self.revers_rotate_btn.clicked.connect(self.reverse_rotate_img)
        self.rotate_btn.clicked.connect(self.rotate_img)
        self.mirror_btn.clicked.connect(self.mirrow)
        self.original_color_btn.clicked.connect(self.original_color)
        self.replaced_color_btn.clicked.connect(self.replaced_color)
        self.replace_color_btn.clicked.connect(self.replace_color)

    def retranslateUi(self, Miniphotoshop):
        _translate = QtCore.QCoreApplication.translate
        Miniphotoshop.setWindowTitle(_translate("Miniphotoshop", "MainWindow"))
        self.getFile_btn.setText(_translate("Miniphotoshop", "Выбрать файл"))
        self.saveFile_btn.setText(_translate("Miniphotoshop", "Сохранить файл"))
        self.label.setText(_translate("Miniphotoshop", "X:"))
        self.label_2.setText(_translate("Miniphotoshop", "Y:"))
        self.label_5.setText(_translate("Miniphotoshop", "Фильтры"))
        self.label_6.setText(_translate("Miniphotoshop", "Инструменты"))
        self.label_7.setText(_translate("Miniphotoshop", "Управление прозрачностью"))
        self.empty_btn.setText(_translate("Miniphotoshop", "Создать пустой холст"))
        self.cb_btn.setText(_translate("Miniphotoshop", "ЧБ"))
        self.negative_btn.setText(_translate("Miniphotoshop", "Негатив"))
        self.emboss_btn.setText(_translate("Miniphotoshop", "Тиснение"))
        self.blur_btn.setText(_translate("Miniphotoshop", "Блюр"))
        self.glitch_btn.setText(_translate("Miniphotoshop", "Глитч"))
        self.contour_btn.setText(_translate("Miniphotoshop", "Выделить контур"))
        self.delete_btn.setText(_translate("Miniphotoshop", "Удалить"))
        self.sharpen_btn.setText(_translate("Miniphotoshop", "Повышение резкости"))
        self.undo_btn.setText(_translate("Miniphotoshop", "отменить последние дейсвие"))
        self.redo_btn.setText(_translate("Miniphotoshop", "повторить последние дейсвие"))
        self.background_btn.setText(_translate("Miniphotoshop", "Удалить фон"))
        self.revers_rotate_btn.setText(_translate("Miniphotoshop", "Поворот на -90°"))
        self.rotate_btn.setText(_translate("Miniphotoshop", "Поворот на 90°"))
        self.mirror_btn.setText(_translate("Miniphotoshop", "Отзеркалить"))
        self.replace_color_btn.setText(_translate("Miniphotoshop", "Заменить"))
        self.label_3.setText(_translate("Miniphotoshop", "Замена цвета"))
        self.label_10.setText(_translate("Miniphotoshop", "заменить на:"))
        self.original_color_btn.setText(_translate("Miniphotoshop", "цвет1"))
        self.replaced_color_btn.setText(_translate("Miniphotoshop", "цвет2"))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Miniphotoshop = QtWidgets.QMainWindow()
    ui = Ui_Miniphotoshop()
    ui.setupUi(Miniphotoshop)
    Miniphotoshop.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
