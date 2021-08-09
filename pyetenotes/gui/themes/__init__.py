from PyQt5 import QtGui, QtWidgets


def set_theme(app: QtWidgets.QMainWindow, theme: str):
    if theme == "darkgreen":
        from .darkgreen import DarkGreenPalette
        # app.setStyleSheet("")
        app.setPalette(DarkGreenPalette())
    elif theme == "lightgreen":
        from .lightgreen import LightGreenPalette
        # app.setStyleSheet("")
        app.setPalette(LightGreenPalette())
    elif theme == "default":
        app.setStyleSheet("")
        app.setPalette(QtGui.QPalette())
