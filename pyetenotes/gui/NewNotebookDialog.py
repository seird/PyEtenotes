from PyQt5 import QtCore, QtGui, QtWidgets

from ..utils import center_widget
from .designs.widget_new_notebook import Ui_Dialog


class NewNotebookDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super(NewNotebookDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Add a new notebook")
        self.line_name.setFocus()
        self.update_color(QtGui.QColor(QtCore.Qt.blue).name())
        self.line_description.setPlaceholderText("(Optional)")
        center_widget(parent, self)
        self.link_callbacks()

    def update_color(self, color_name: str):
        self.color_name = color_name
        self.label_color.setStyleSheet(f"QLabel {{ background-color : {self.color_name} }}")
        self.label_color.setToolTip(self.color_name)

    def pick_color(self, *args):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color_name), self)
        if color.isValid():
            self.update_color(color.name())

    def link_callbacks(self):
        self.pb_color.clicked.connect(self.pick_color)
        self.label_color.mousePressEvent = self.pick_color
