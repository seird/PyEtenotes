from PyQt5 import QtGui


class LightGreenPalette(QtGui.QPalette):
    def __init__(self):
        super(LightGreenPalette, self).__init__()
        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Window, QtGui.QColor(0xF7F7F7))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QColor(0xFCFCFC))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QColor(0xEDEDED))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.WindowText, QtGui.QColor(0x1D1D20))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, QtGui.QColor(0x252528))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(0x8C8C92))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(0x1D1D20))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Text, QtGui.QColor(0x252528))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(0x8C8C92))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, QtGui.QColor(0x71727D))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, QtGui.QColor(0x878893))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, QtGui.QColor(0xA3A4AC))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.BrightText, QtGui.QColor(0xF3F3F4))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, QtGui.QColor(0xEAEAEB))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, QtGui.QColor(0xE4E5E7))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(0xF9F9F9))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Base, QtGui.QColor(0xFCFCFC))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QColor(0xEFEFF2))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, QtGui.QColor(0xECF3E8))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, QtGui.QColor(0xF1F6EE))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, QtGui.QColor(0xE1E9DD))

        self.setColor(QtGui.QPalette.All, QtGui.QPalette.ToolTipBase, QtGui.QColor(0x4D7F1A))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.ToolTipText, QtGui.QColor(0xF9F9F9))

        # self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(0xD4D5DD))
        # self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Button, QtGui.QColor(0xDCDCE0))
        # self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, QtGui.QColor(0xE5E5E6))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, QtGui.QColor(0x181A18))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, QtGui.QColor(0x454A54))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(0x97979B))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Highlight, QtGui.QColor(0x507F1F))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, QtGui.QColor(0xA6BE8E))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, QtGui.QColor(0xC3D5B4))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, QtGui.QColor(0xFFFFFF))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText, QtGui.QColor(0x252528))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, QtGui.QColor(0x8C8C92))

        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Light, QtGui.QColor(0xF9F9F9))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Midlight, QtGui.QColor(0xE9E9EB))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Mid, QtGui.QColor(0xC9C9CF))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Dark, QtGui.QColor(0xBBBBC2))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Shadow, QtGui.QColor(0x6C6D79))

        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Link, QtGui.QColor(0x4B7B19))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Link, QtGui.QColor(0x4F6935))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.LinkVisited, QtGui.QColor(0x507826))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.LinkVisited, QtGui.QColor(0x506935))
