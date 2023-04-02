import sqlite3
import sys
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QMainWindow, QLabel, QWidget, QApplication, QPushButton
from PyQt5 import QtCore, QtGui
from Miniphotoshop import Ui_Miniphotoshop


class Ui_Registration(object):

    def Miniphotoshop(self):
        self.window2 = QMainWindow()
        self.ui = Ui_Miniphotoshop()
        self.ui.setupUi(self.window2)
        self.window2.show()
        Registration.close()

    def erorr(self, text, warning='ОШИБКА!!!'):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle(warning)
        error_dialog.setText(text)
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        error_dialog.exec_()

    def registr(self):
        user_name = self.login.text().strip()
        user_password = self.password.text().strip()
        start_main = False
        if user_name == '' or user_password == '':
            self.erorr('Логин или пароль не может быть пустой')
        else:
            Flag = False
            while not Flag:
                with sqlite3.connect('data.db') as db:
                    cur = db.cursor()
                    data = cur.execute("""SELECT user, password FROM users WHERE user=?""",
                                       (user_name,)).fetchall()
                    if data:
                        for el in data:
                            if user_password != el[1]:
                                self.erorr('Неверный пароль, попробуйте снова')
                                Flag = True
                            else:
                                Flag = True
                                start_main = True
                    else:
                        Flag = True
                        start_main = False
                        cur.execute("""INSERT INTO users(user, password) VALUES(?, ?)""",
                                    (user_name, user_password))
                if start_main:
                    self.Miniphotoshop()

    def setupUi(self, Registration):
        Registration.setObjectName("Registration")
        Registration.resize(300, 181)
        self.centralwidget = QWidget(Registration)
        self.centralwidget.setObjectName("centralwidget")
        self.login = QLineEdit(self.centralwidget)
        self.login.setGeometry(QtCore.QRect(90, 50, 113, 20))
        self.login.setObjectName("login")
        self.password = QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(90, 90, 113, 20))
        self.password.setObjectName("password")
        self.password.setEchoMode(QLineEdit.Password)
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 0, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.login_text = QLabel(self.centralwidget)
        self.login_text.setGeometry(QtCore.QRect(20, 50, 41, 21))
        self.login_text.setObjectName("login_text")
        self.password_text = QLabel(self.centralwidget)
        self.password_text.setGeometry(QtCore.QRect(20, 90, 41, 21))
        self.password_text.setObjectName("password_text")
        self.registr_btn = QPushButton(self.centralwidget)
        self.registr_btn.setGeometry(QtCore.QRect(90, 130, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.registr_btn.setFont(font)
        self.registr_btn.setObjectName("registr_btn")
        self.registr_btn.clicked.connect(self.registr)
        Registration.setCentralWidget(self.centralwidget)

        self.retranslateUi(Registration)
        QtCore.QMetaObject.connectSlotsByName(Registration)

    def retranslateUi(self, Registration):
        _translate = QtCore.QCoreApplication.translate
        Registration.setWindowTitle(_translate("Registration", "Регистрация"))
        self.label.setText(_translate("Registration", "Регистрация"))
        self.login_text.setText(_translate("Registration", "Логин:"))
        self.password_text.setText(_translate("Registration", "Пароль:"))
        self.registr_btn.setText(_translate("Registration", "Войти"))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Registration = QMainWindow()
    ui = Ui_Registration()
    ui.setupUi(Registration)
    Registration.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
