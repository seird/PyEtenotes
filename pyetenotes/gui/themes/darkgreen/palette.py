from PyQt5 import QtGui


class DarkGreenPalette(QtGui.QPalette):
    def __init__(self):
        super(DarkGreenPalette, self).__init__()

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Window, QtGui.QColor(0x3B3B3D))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QColor(0x404042))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QColor(0x424242))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.WindowText, QtGui.QColor(0xCACBCE))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, QtGui.QColor(0xC8C8C6))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor(0x707070))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(0xCACBCE))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Text, QtGui.QColor(0xC8C8C6))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(0x707070))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, QtGui.QColor(0x7D7D82))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, QtGui.QColor(0x87888C))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, QtGui.QColor(0x737373))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.BrightText, QtGui.QColor(0x252627))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, QtGui.QColor(0x2D2D2F))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, QtGui.QColor(0x333333))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(0x27272A))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Base, QtGui.QColor(0x2A2A2D))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QColor(0x343437))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, QtGui.QColor(0x2C2C30))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, QtGui.QColor(0x2B2B2F))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, QtGui.QColor(0x36363A))

        self.setColor(QtGui.QPalette.All, QtGui.QPalette.ToolTipBase, QtGui.QColor(0x2D532D))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.ToolTipText, QtGui.QColor(0xBFBFBF))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(0x28282B))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Button, QtGui.QColor(0x28282B))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, QtGui.QColor(0x2B2A2A))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, QtGui.QColor(0xB9B9BE))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, QtGui.QColor(0x9E9FA5))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor(0x73747E))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.Highlight, QtGui.QColor(0x2D532D))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, QtGui.QColor(0x354637))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, QtGui.QColor(0x293D29))

        self.setColor(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, QtGui.QColor(0xCCCCCC))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText, QtGui.QColor(0xCECECE))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, QtGui.QColor(0x707070))

        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Light, QtGui.QColor(0x414145))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Midlight, QtGui.QColor(0x39393C))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Mid, QtGui.QColor(0x2F2F32))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Dark, QtGui.QColor(0x202022))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Shadow, QtGui.QColor(0x19191A))

        self.setColor(QtGui.QPalette.All, QtGui.QPalette.Link, QtGui.QColor(0x68B668))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Link, QtGui.QColor(0x74A474))
        self.setColor(QtGui.QPalette.All, QtGui.QPalette.LinkVisited, QtGui.QColor(0x75B875))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.LinkVisited, QtGui.QColor(0x77A677))
