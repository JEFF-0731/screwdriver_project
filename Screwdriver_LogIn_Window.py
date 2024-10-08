# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Screwdriver_LogIn_Window.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Screwdriver_LogIn_Form(object):
    def setupUi(self, Screwdriver_LogIn_Form):
        Screwdriver_LogIn_Form.setObjectName("Screwdriver_LogIn_Form")
        Screwdriver_LogIn_Form.resize(543, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Screwdriver_LogIn_Form.sizePolicy().hasHeightForWidth())
        Screwdriver_LogIn_Form.setSizePolicy(sizePolicy)
        Screwdriver_LogIn_Form.setMinimumSize(QtCore.QSize(543, 400))
        Screwdriver_LogIn_Form.setMaximumSize(QtCore.QSize(543, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("UI_Logo/Lancer Small Logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Screwdriver_LogIn_Form.setWindowIcon(icon)
        Screwdriver_LogIn_Form.setStyleSheet("background: \'white\';")
        self.label_LogIn = QtWidgets.QLabel(Screwdriver_LogIn_Form)
        self.label_LogIn.setGeometry(QtCore.QRect(81, 29, 371, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_LogIn.sizePolicy().hasHeightForWidth())
        self.label_LogIn.setSizePolicy(sizePolicy)
        self.label_LogIn.setMinimumSize(QtCore.QSize(371, 61))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(36)
        self.label_LogIn.setFont(font)
        self.label_LogIn.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_LogIn.setAlignment(QtCore.Qt.AlignCenter)
        self.label_LogIn.setObjectName("label_LogIn")
        self.lineEdit_username = QtWidgets.QLineEdit(Screwdriver_LogIn_Form)
        self.lineEdit_username.setGeometry(QtCore.QRect(81, 116, 380, 71))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_username.sizePolicy().hasHeightForWidth())
        self.lineEdit_username.setSizePolicy(sizePolicy)
        self.lineEdit_username.setMinimumSize(QtCore.QSize(301, 71))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(33)
        self.lineEdit_username.setFont(font)
        self.lineEdit_username.setStyleSheet("QLineEdit {\n"
"        border:1px solid #000;\n"
"        border-radius: 10px;\n"
"    }\n"
"QLineEdit:focus {\n"
"        \n"
"        background:#e8ecef;\n"
"    }")
        self.lineEdit_username.setInputMask("")
        self.lineEdit_username.setFrame(True)
        self.lineEdit_username.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.lineEdit_username.setClearButtonEnabled(False)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.lineEdit_password = QtWidgets.QLineEdit(Screwdriver_LogIn_Form)
        self.lineEdit_password.setGeometry(QtCore.QRect(81, 213, 380, 71))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_password.sizePolicy().hasHeightForWidth())
        self.lineEdit_password.setSizePolicy(sizePolicy)
        self.lineEdit_password.setMinimumSize(QtCore.QSize(301, 71))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(33)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setStyleSheet("QLineEdit {\n"
"        border:1px solid #000;\n"
"        border-radius: 10px;\n"
"    }\n"
"QLineEdit:focus {\n"
"        \n"
"        background:#e8ecef;\n"
"    }")
        self.lineEdit_password.setInputMask("")
        self.lineEdit_password.setFrame(True)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.pushButton_login = QtWidgets.QPushButton(Screwdriver_LogIn_Form)
        self.pushButton_login.setGeometry(QtCore.QRect(81, 310, 371, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_login.sizePolicy().hasHeightForWidth())
        self.pushButton_login.setSizePolicy(sizePolicy)
        self.pushButton_login.setMinimumSize(QtCore.QSize(371, 61))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(20)
        self.pushButton_login.setFont(font)
        self.pushButton_login.setStyleSheet("QPushButton {\n"
"    background-color: #e8ecef;\n"
"    border-radius: 20px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #95949a;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #e8ecef;\n"
"}\n"
"\n"
"#pushButton_login {\n"
"    border-radius: 30px;\n"
"}")
        self.pushButton_login.setObjectName("pushButton_login")

        self.retranslateUi(Screwdriver_LogIn_Form)
        QtCore.QMetaObject.connectSlotsByName(Screwdriver_LogIn_Form)

    def retranslateUi(self, Screwdriver_LogIn_Form):
        _translate = QtCore.QCoreApplication.translate
        Screwdriver_LogIn_Form.setWindowTitle(_translate("Screwdriver_LogIn_Form", "Engineer Mode Log In"))
        self.label_LogIn.setText(_translate("Screwdriver_LogIn_Form", "Log In"))
        self.lineEdit_username.setPlaceholderText(_translate("Screwdriver_LogIn_Form", "Username"))
        self.lineEdit_password.setPlaceholderText(_translate("Screwdriver_LogIn_Form", "Password"))
        self.pushButton_login.setText(_translate("Screwdriver_LogIn_Form", "Log In"))
