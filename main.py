"""
 * @brief python的包管理器
 * @author 党智腾
 * mail 642212607@qq.com
 * WeChat dangzhiteng
 * @date 2018-08-26
 * @version V 1.0
"""

import os
import sys
import time
import requests
import threading
import qdarkstyle
from threading import Thread
from PyQt5.QtWidgets import (QWidget, QApplication, QTableWidgetItem, QPushButton, QAbstractItemView, 
                             QHeaderView, QPushButton, QProgressBar, QHBoxLayout, QMessageBox, QStyle)
from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QIcon
from Ui_MainWindow import Ui_MainWindow
# pip install --upgrade 包名
__myPackage__ = []
__pyPiPackage__ = []

class UpdateProgress(QProgressBar):
    startUpdateSignal = pyqtSignal(QPoint)
    def __init__(self, parent=None):
        super(UpdateProgress, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(2)
        self.progress = QProgressBar()
        self.updateBtn = QPushButton(QIcon(QApplication.style().standardIcon(QStyle.SP_MediaPlay)), '')
        # self.updateBtn.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        # self.progress.setStyleSheet('background-color: transparents')
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.updateBtn)
        self.setLayout(self.layout)

        self.updateBtn.clicked.connect(self.update)
    def update(self):
        self.startUpdateSignal.emit(QPoint(self.updateBtn.frameGeometry().x(), self.updateBtn.frameGeometry().y()))
        # timer = threading.Thread(target=self.temp)
        # timer.start()
    # def temp(self):
      #   while True:
        #     self.progress.setValue(self.progress.value() + 2)
          #   time.sleep(1)

class MainWindow(QWidget, Ui_MainWindow):
    myModulesNum = 0
    checkOver = pyqtSignal(dict)
    notFind = pyqtSignal()
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.myPackTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.myPackTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.myPackTable.horizontalHeader().setMinimumSectionSize(200)

        myModules = os.popen('pip list').read().split('\n')[2:-1]
        self.myModulesNum = len(myModules)
        self.updateProcess = list(range(self.myModulesNum))
        self.myPackTable.setRowCount(self.myModulesNum)
        for i in range(self.myModulesNum):
            name = myModules[i].split()[0]
            version = myModules[i].split()[1]
            self.myPackTable.setItem(i, 0, QTableWidgetItem(name))
            self.myPackTable.setItem(i, 1, QTableWidgetItem(version))
            self.updateProcess[i] = UpdateProgress()
            self.updateProcess[i].startUpdateSignal.connect(self.checkAndUpdate)
            self.myPackTable.setCellWidget(i, 3, self.updateProcess[i])
            self.myPackTable.setCellWidget(i, 4, QPushButton("Uninstall"))
        # 连接信号和槽
        self.myPackTable.cellClicked.connect(self.updatePackage)
        self.checkOver.connect(self.updateVersion)
        self.notFind.connect(self.showWarning)
        # 检查最新版本
        latest = Thread(target=self.showLatest, name='CheckLatest')
        latest.start()

    # 检查更新线程
    def showLatest(self):
        latestVersion = os.popen('pip list --outdated').read().split('\n')[2:-1]
        myPack = dict()
        for item in latestVersion:
            temp = item.split()
            myPack[temp[0]] = temp[2]
        self.checkOver.emit(myPack)

    # 检查完毕 显示可更新版本
    def updateVersion(self, myPack):  
        for i in range(self.myModulesNum):
            curName = self.myPackTable.item(i, 0).text()
            if curName in myPack:
                self.myPackTable.setItem(i, 2, QTableWidgetItem(myPack[curName]))

    # 开启加载模块详细信息线程
    def updatePackage(self, row, col):
        loadInfoThread = Thread(target=self.loadInfo, args=(row,col))
        loadInfoThread.start()

    # 加载模块详细信息线程
    def loadInfo(self, row, col):
        packName = self.myPackTable.item(row, 0).text()
        info = os.popen('pip show %s' % packName).read().split('\n')[:-1]
        packInfo = dict()
        for item in info:
            temp = item.split(':')
            packInfo[temp[0]] = temp[1]
            if temp[0] == 'Location':
                packInfo[temp[0]] += temp[2]
        self.nameLabel.setText(packInfo['Name'])
        self.versionLabel.setText(packInfo['Version'])
        self.summaryLabel.setText(packInfo['Summary'])
        self.homePageLabel.setText(packInfo['Home-page'])
        self.authorLabel.setText(packInfo['Author'])
        self.authorEmailLabel.setText(packInfo['Author-email'])
        self.licenseLabel.setText(packInfo['License'])
        self.locationLabel.setText(packInfo['Location'])
        self.requiresLabel.setText(packInfo['Requires'])
        self.requiresByLabel.setText(packInfo['Required-by'])
    
    def showWarning(self):
        QMessageBox.warning(self, 'warning', 'No new version was detected!')
    
    def checkAndUpdate(self, pos):
        print(pos)
        item = self.myPackTable.indexAt(pos)
        row = item.row()
        col = item.column()
        print(row, col)
        if col == 3:
            if self.myPackTable.item(row, 2) is None:
                self.notFind.emit()
                print('你在点什么鬼')
            else:
                print('updating')
                # self.progressPushButton.progress.setValue(50)
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # pyPiHtml = requests.get('http://')
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())