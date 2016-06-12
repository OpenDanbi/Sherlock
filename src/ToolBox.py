from PySide import QtCore, QtGui
from PySide.QtGui import QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QGroupBox, QCheckBox, QLineEdit, QInputDialog

import ClusterDialog

class ToolBox(QVBoxLayout):

    sig = QtCore.Signal(object)

    def __init__(self,parentQWidget = None):
        QVBoxLayout.__init__(self)

        self.sig.connect(self.addThreadList)

        self.searchHLayout = QHBoxLayout()
        self.editTextSearch = QTextEdit('hello')
        self.editTextSearch.setFixedSize(100,30)
        self.buttonSearch = QPushButton('Search')
        self.buttonSearch.setFixedSize(100,30)
        self.buttonSearch.clicked.connect(self.searchMsg)
        self.searchHLayout.addWidget(self.editTextSearch)
        self.searchHLayout.addWidget(self.buttonSearch)
        self.addLayout(self.searchHLayout)
        self.browseHLayout = QHBoxLayout()
        self.searchCursor = QLabel('2/2')
        self.buttonLookUp = QPushButton('\u21e7')  #Arrow up
        self.buttonLookUp.clicked.connect(self.moveToPrev)
        self.buttonLookDown = QPushButton('\u21e9') #Arrow down
        self.buttonLookDown.clicked.connect(self.moveToNext)
        self.browseHLayout.addWidget(self.buttonLookUp)
        self.browseHLayout.addWidget(self.searchCursor)
        self.browseHLayout.addWidget(self.buttonLookDown)
        self.addLayout(self.browseHLayout)
        self.buttonShowAll = QPushButton('Show All')
        self.buttonShowAll.clicked.connect(self.notifyShowAll)
        self.addWidget(self.buttonShowAll)
        self.buttonCapture = QPushButton('Capture')
        self.buttonCapture.clicked.connect(self.notifyCapture)
        self.addWidget(self.buttonCapture)
        self.msgRcv = []
        self.msgInfo = QLabel()
        self.groupBoxMessageInfo = QGroupBox("Message Info.")
        self.groupBoxMessageInfo.setStyleSheet("QGroupBox {border: 1px solid gray; border-radius: 9px; margin-top: 0.5em} QGroupBox::title {subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;")
        vbox = QVBoxLayout()
        vbox.addWidget(self.msgInfo)
        self.buttonSrcView = QPushButton('view code')
        self.buttonSrcView.clicked.connect(self.openSourceViewer)
        vbox.addWidget(self.buttonSrcView)
        self.buttonHide = QPushButton('Hide')
        self.buttonHide.clicked.connect(self.notifyHide)
        vbox.addWidget(self.buttonHide)
        self.buttonHideAllMsg = QPushButton('Hide All')
        self.buttonHideAllMsg.clicked.connect(self.hideAllMsgNamedAsSelected)
        vbox.addWidget(self.buttonHideAllMsg)
        self.groupBoxMessageInfo.setLayout(vbox)
        self.checkHideCircular = QCheckBox('Hide Circular Messages')
        self.checkHideCircular.setCheckState(QtCore.Qt.Unchecked)
        self.checkHideCircular.stateChanged.connect(self.changeHideCircularMessage)
        self.addWidget(self.checkHideCircular)
        self.buttonGroupName = QPushButton('Group')
        self.buttonGroupName.clicked.connect(self.addGroupName)
        self.addWidget(self.buttonGroupName)
        self.listGroupName = QListWidget()
        self.listGroupName.setFixedWidth(200)
        self.addWidget(self.listGroupName)

        self.addWidget(self.groupBoxMessageInfo)

    def setMsgInfoMessage(self,msg):
        self.strMessage = msg

    def addGroupName(self):
        response, cluster_name = ClusterDialog.ClusterDialog.getClusterName(self.diagramView.getLifeLines())
        
        print("cluster name is %s" % cluster_name)
        if self.diagramView.createCluster(cluster_name):
            item = QtGui.QListWidgetItem(cluster_name)
            self.listGroupName.addItem(item)
        else:
            pass

    def changeHideCircularMessage(self,state):
        if state == QtCore.Qt.Unchecked:
            self.diagramView.hideCircularChanged(False)
        elif state == QtCore.Qt.Checked:
            self.diagramView.hideCircularChanged(True)
    
    def setMsgInfoModule(self,module):
        self.strModule = module

    def updateSearchStatus(self,curr,number):
        self.searchCursor.setText("%d/%d" % (curr,number))

    def connectSourceViewer(self,viewer):
        self.srcViewer = viewer

    def openSourceViewer(self):
        self.srcViewer.openViewer(self.strModule,self.strMessage)

    def setMessageInfo(self,info):
        self.msgInfo.setText(info)

    def setAvailable(self,threads):
        self.sig.emit(threads)

    def toggleThreadDisplay(self,item):
        print(self.listThread.currentRow())
        if item.isSelected():
            print(item.text() + "  is selected")
        else:
            print(item.text() + "  is not selected")
        self.diagramView.showThread(self.listThread.currentRow(),item.isSelected())

    def hideAllMsgNamedAsSelected(self):
        self.diagramView.hideAllMessageSelected()

    def addThreadList(self,threads):
        self.listThread = QListWidget()
        self.listThread.setFixedWidth(200)
        self.listThread.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        QtCore.QObject.connect(self.listThread, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.toggleThreadDisplay)
        self.addWidget(self.listThread)

        for id in threads:
            item = QtGui.QListWidgetItem(id)
            self.listThread.addItem(item)

    def connectController(self,controller):
        self.controller = controller
        self.connect(controller,QtCore.SIGNAL('setAvailable()'),self.setAvailable)
       
    def connectDiagramView(self,view):
        self.diagramView = view
 
    def disconnectMsgRcv(self,receiver):
        print("Implement this method !!! disconnectMsgRcv")

    def connectMsgRcv(self,receiver):
        self.msgRcv.append(receiver)

    def notifyHide(self):
        for rcv in self.msgRcv:
            rcv.activateHide(True)

    def notifyShowAll(self):
        for rcv in self.msgRcv:
            rcv.resetAllLifelines()

    def notifyCapture(self):
        for rcv in self.msgRcv:
            rcv.activateCapture(True)
    
    def moveToPrev(self):
        for rcv in self.msgRcv:
            rcv.moveToPrev()
        
    def moveToNext(self):
        for rcv in self.msgRcv:
            rcv.moveToNext()

    def searchMsg(self):
        str = self.editTextSearch.toPlainText()
        for rcv in self.msgRcv:
            rcv.searchMessage(str)
