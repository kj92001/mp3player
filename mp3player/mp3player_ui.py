# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mp3player.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QLabel, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QScrollBar, QSizePolicy,
    QSlider, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(782, 442)
        MainWindow.setStyleSheet(u"QWidget {\n"
"    background: rgb(30, 30, 30);\n"
"}\n"
"\n"
"QPushButton {\n"
"    color: rgb(255, 255, 255);\n"
"    font-size: 12pt;\n"
"    font-weight: bold;\n"
"}\n"
"QLabel{\n"
"	color:rgb(255,255,255);\n"
"}\n"
"\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lblCover = QLabel(self.centralwidget)
        self.lblCover.setObjectName(u"lblCover")
        self.lblCover.setMinimumSize(QSize(400, 380))
        self.lblCover.setFrameShape(QFrame.Shape.Box)
        self.lblCover.setPixmap(QPixmap(u"logo.svg"))
        self.lblCover.setScaledContents(True)

        self.verticalLayout.addWidget(self.lblCover)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnPrev = QPushButton(self.centralwidget)
        self.btnPrev.setObjectName(u"btnPrev")

        self.horizontalLayout.addWidget(self.btnPrev)

        self.btnPlay = QPushButton(self.centralwidget)
        self.btnPlay.setObjectName(u"btnPlay")

        self.horizontalLayout.addWidget(self.btnPlay)

        self.btnStop = QPushButton(self.centralwidget)
        self.btnStop.setObjectName(u"btnStop")

        self.horizontalLayout.addWidget(self.btnStop)

        self.btnPause = QPushButton(self.centralwidget)
        self.btnPause.setObjectName(u"btnPause")

        self.horizontalLayout.addWidget(self.btnPause)

        self.btnNext = QPushButton(self.centralwidget)
        self.btnNext.setObjectName(u"btnNext")
        self.btnNext.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.btnNext)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listAndScrollLayout = QHBoxLayout()
        self.listAndScrollLayout.setObjectName(u"listAndScrollLayout")
        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setStyleSheet(u"/* QListWidget \uc804\uccb4 \ubc30\uacbd \ubc0f \uae30\ubcf8 \uae00\uc790 \uc0c9\uc0c1 */\n"
"QListWidget {\n"
"    background-color: #121212; /* \uc644\uc804 \ube14\ub799 \ub610\ub294 \uc5b4\ub450\uc6b4 \ud68c\uc0c9 */\n"
"    border: 1px solid #333333;\n"
"    padding: 5px;\n"
"}\n"
"\n"
"/* \uac1c\ubcc4 \uc544\uc774\ud15c\uc758 \uae30\ubcf8 \uae00\uc790 \uc0c9\uc0c1 \ubc0f \uc5ec\ubc31 */\n"
"QListWidget::item {\n"
"    color: #FFFFFF; /* \uae00\uc790\uc0c9 \ud654\uc774\ud2b8 */\n"
"    padding: 8px;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"/* \ub9c8\uc6b0\uc2a4\ub97c \uc62c\ub838\uc744 \ub54c (Hover) */\n"
"QListWidget::item:hover {\n"
"    background-color: #2C2C2C; /* \uc57d\uac04 \ubc1d\uc740 \ud68c\uc0c9 */\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* \uc120\ud0dd(\ud074\ub9ad)\ub418\uc5c8\uc744 \ub54c (Selected) */\n"
"QListWidget::item:selected {\n"
"    background-color: #0078D4; /* \ud3ec\uc778\ud2b8 \ube14\ub8e8 \uce7c\ub77c (\ucde8\ud5a5\uc5d0 \ub9de\uac8c \uc218\uc815 \uac00\ub2a5) */\n"
""
                        "    color: #FFFFFF;\n"
"}\n"
"\n"
"/* \uc120\ud0dd\ub41c \uc0c1\ud0dc\uc5d0\uc11c \ub9c8\uc6b0\uc2a4\ub97c \uc62c\ub824\ub3c4 \uc0c9\uc0c1 \uc720\uc9c0 */\n"
"QListWidget::item:selected:hover {\n"
"    background-color: #006CBE;\n"
"}\n"
"")
        self.listWidget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.listWidget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.listWidget.setResizeMode(QListView.ResizeMode.Adjust)

        self.listAndScrollLayout.addWidget(self.listWidget)

        self.verticalScrollBar = QScrollBar(self.centralwidget)
        self.verticalScrollBar.setObjectName(u"verticalScrollBar")
        self.verticalScrollBar.setOrientation(Qt.Orientation.Vertical)

        self.listAndScrollLayout.addWidget(self.verticalScrollBar)


        self.verticalLayout_2.addLayout(self.listAndScrollLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btnDelete = QPushButton(self.centralwidget)
        self.btnDelete.setObjectName(u"btnDelete")

        self.horizontalLayout_2.addWidget(self.btnDelete)

        self.btnFullDelete = QPushButton(self.centralwidget)
        self.btnFullDelete.setObjectName(u"btnFullDelete")

        self.horizontalLayout_2.addWidget(self.btnFullDelete)

        self.btnOpenDir = QPushButton(self.centralwidget)
        self.btnOpenDir.setObjectName(u"btnOpenDir")

        self.horizontalLayout_2.addWidget(self.btnOpenDir)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.setObjectName(u"sliderLayout")
        self.lblTime = QLabel(self.centralwidget)
        self.lblTime.setObjectName(u"lblTime")
        self.lblTime.setMinimumSize(QSize(90, 0))

        self.sliderLayout.addWidget(self.lblTime)

        self.sliderProgress = QSlider(self.centralwidget)
        self.sliderProgress.setObjectName(u"sliderProgress")
        self.sliderProgress.setOrientation(Qt.Orientation.Horizontal)

        self.sliderLayout.addWidget(self.sliderProgress)


        self.verticalLayout_2.addLayout(self.sliderLayout)

        self.volumeLayout = QHBoxLayout()
        self.volumeLayout.setObjectName(u"volumeLayout")
        self.lblVolume = QLabel(self.centralwidget)
        self.lblVolume.setObjectName(u"lblVolume")
        self.lblVolume.setMinimumSize(QSize(90, 0))

        self.volumeLayout.addWidget(self.lblVolume)

        self.sliderVolume = QSlider(self.centralwidget)
        self.sliderVolume.setObjectName(u"sliderVolume")
        self.sliderVolume.setMaximum(100)
        self.sliderVolume.setValue(70)
        self.sliderVolume.setOrientation(Qt.Orientation.Horizontal)

        self.volumeLayout.addWidget(self.sliderVolume)


        self.verticalLayout_2.addLayout(self.volumeLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.rightWidgetContainer = QWidget(self.centralwidget)
        self.rightWidgetContainer.setObjectName(u"rightWidgetContainer")
        self.lblTitle = QLabel(self.rightWidgetContainer)
        self.lblTitle.setObjectName(u"lblTitle")
        self.lblTitle.setGeometry(QRect(0, 5, 38, 18))
        self.lblTitle.setWordWrap(True)
        self.lblArtist = QLabel(self.rightWidgetContainer)
        self.lblArtist.setObjectName(u"lblArtist")
        self.lblArtist.setGeometry(QRect(0, 29, 45, 18))
        self.lblArtist.setWordWrap(True)

        self.horizontalLayout_3.addWidget(self.rightWidgetContainer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mp3 Player", None))
        self.lblCover.setText("")
        self.btnPrev.setText(QCoreApplication.translate("MainWindow", u"\uc774\uc804", None))
        self.btnPlay.setText(QCoreApplication.translate("MainWindow", u"\uc7ac\uc0dd", None))
        self.btnStop.setText(QCoreApplication.translate("MainWindow", u"\uc815\uc9c0", None))
        self.btnPause.setText(QCoreApplication.translate("MainWindow", u"\uc77c\uc2dc\uc815\uc9c0", None))
        self.btnNext.setText(QCoreApplication.translate("MainWindow", u"\ub2e4\uc74c", None))
        self.btnDelete.setText(QCoreApplication.translate("MainWindow", u"\uc0ad\uc81c", None))
        self.btnFullDelete.setText(QCoreApplication.translate("MainWindow", u"\uc804\uccb4\uc0ad\uc81c", None))
        self.btnOpenDir.setText(QCoreApplication.translate("MainWindow", u"\ud3f4\ub354 \uc704\uce58 \uc5f4\uae30", None))
        self.lblTime.setText(QCoreApplication.translate("MainWindow", u"00:00 / 00:00", None))
        self.lblVolume.setText(QCoreApplication.translate("MainWindow", u"\ubcfc\ub968", None))
        self.lblTitle.setText(QCoreApplication.translate("MainWindow", u"Title: ", None))
        self.lblArtist.setText(QCoreApplication.translate("MainWindow", u"Artist: ", None))
    # retranslateUi

