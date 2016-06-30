from PySide.QtGui import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QListWidget
from PySide import QtGui, QtCore

class HiddenMessageDialog(QDialog):
   
    msgList = None 

    def __init__(self, hiddenLifeline, parent = None):
        super(HiddenMessageDialog, self).__init__(parent)

        self.msgList = hiddenLifeline
        layout = QVBoxLayout(self)

        listTitle = QLabel('Hidden Messages')
        layout.addWidget(listTitle)

        self.listHiddenMessages = QListWidget()
        self.listHiddenMessages.setFixedWidth(400)
        self.listHiddenMessages.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        for text in self.msgList:
            item = QtGui.QListWidgetItem(text)
            self.listHiddenMessages.addItem(item)

        layout.addWidget(self.listHiddenMessages)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.button(QDialogButtonBox.Ok).setText('Show')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def getSelectedItems(msgList, parent = None):
        dialog = HiddenMessageDialog(msgList,parent)
        result = dialog.exec_()
        return (result, [str(x.text()) for x in dialog.listHiddenMessages.selectedItems()])

