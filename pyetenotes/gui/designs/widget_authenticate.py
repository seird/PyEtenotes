# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyetenotes/gui/designs\widget_authenticate.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(274, 214)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 8, 0, 1, 2)
        self.line_password = QtWidgets.QLineEdit(Dialog)
        self.line_password.setMinimumSize(QtCore.QSize(250, 0))
        self.line_password.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.line_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.line_password.setObjectName("line_password")
        self.gridLayout.addWidget(self.line_password, 3, 0, 1, 1)
        self.line_username = QtWidgets.QLineEdit(Dialog)
        self.line_username.setMinimumSize(QtCore.QSize(250, 0))
        self.line_username.setObjectName("line_username")
        self.gridLayout.addWidget(self.line_username, 1, 0, 1, 1)
        self.line_url = QtWidgets.QLineEdit(Dialog)
        self.line_url.setMinimumSize(QtCore.QSize(200, 0))
        self.line_url.setObjectName("line_url")
        self.gridLayout.addWidget(self.line_url, 5, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
        self.cb_stay_logged_in = QtWidgets.QCheckBox(Dialog)
        self.cb_stay_logged_in.setObjectName("cb_stay_logged_in")
        self.gridLayout.addWidget(self.cb_stay_logged_in, 6, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.line_username, self.line_password)
        Dialog.setTabOrder(self.line_password, self.line_url)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_3.setText(_translate("Dialog", "Server url:"))
        self.label_2.setText(_translate("Dialog", "Password:"))
        self.label.setText(_translate("Dialog", "Username:"))
        self.line_url.setPlaceholderText(_translate("Dialog", "e.g. https://api.etebase.com (optional)"))
        self.cb_stay_logged_in.setText(_translate("Dialog", "Stay logged in"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
