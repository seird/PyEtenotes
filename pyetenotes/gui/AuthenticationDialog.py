from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

from ..etesync import Notebook
from .designs.widget_authenticate import Ui_Dialog


class AuthenticationDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, username: str = None, password: str = None, server_url: str = None, stay_logged_in: bool = True):
        super(AuthenticationDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Authenticate")
        self.line_username.setFocus()
        self.cb_stay_logged_in.setChecked(stay_logged_in)

        if username:
            self.line_username.setText(username)
        if password:
            self.line_password.setText(password)
        if server_url:
            self.line_url.setText(server_url)
