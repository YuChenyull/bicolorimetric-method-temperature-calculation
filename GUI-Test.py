#!/usr/bin/python3
# -*- coding: utf-8 -*-

'火焰温度图像处理'

__author__ = 'YuChenyu'


#确保CV2能够被打包
import ctypes
try:
    temp=ctypes.windll.LoadLibrary( 'opencv_ffmpeg401.dll' )
except:
    pass

#调用PyQt5编写程序GUI界面
from PyQt5.QtWidgets import (QMainWindow,QLabel,QProgressBar,QWidget,QToolButton, 
QAction, QFileDialog, QApplication,QPushButton,QInputDialog,qApp)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

#调用系统模块
import sys
import os
import time
import math

#调用PIL模块的图像、滤波器模块
from PIL import Image,ImageFilter

#调用NumPy进行数据计算
import numpy as np

#调用Matplotlib画图
import matplotlib.pyplot as plt
import matplotlib.font_manager

#字体管理,用雅黑允许输入中文
myfont = matplotlib.font_manager.FontProperties(fname='Fonts/msyh.ttc')

#调用OpenCV进行视频分割
import cv2


#比色法温度计算函数
def tempcalc(r,g,b):
    #阈值分割
    gamma = 0.299*r + 0.587*g + 0.114*b
    if gamma <= 20:
        return 0
    #RB双色消除不符合辐射规律的点
    if(r <= b):
        r,b = b,r
    if(r == 0):
        r = r+1
    if(b == 0):
        b = b+1
    x = r
    x2 = x*x
    x3 = x2*x
    x4 = x3*x
    CALC = Msg.fa4*x4+Msg.fa3*x3+Msg.fa2*x2+Msg.fa1*x + Msg.fb + Msg.BB
    
    answer = int(Msg.A/(math.log(r/b,math.e)+CALC))
    if answer >= 1800:
        answer = 1800
    return answer 

#读取图片RGB值函数
def returnrgb(Path):
    img = Image.open(Path)
    img = medianfiltering(img,3)
    rows,cols = img.size
    img=np.array(img)#图像转变为数组
    return img[int(rows/2),int(cols/2)]

#视频分割函数（单幅图像时不引用该函数）
def save_img(videopath):
    
    if(os.path.exists('videocache')):
        pass
    else:
        os.mkdir('videocache')
        
    vc = cv2.VideoCapture(videopath)
    totalFrameNumber = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    c=0
    rval=vc.isOpened()

    while rval:
        c = c + 1
        rval, frame = vc.read()
        if rval:
            size = frame.shape
            progress=c*100/totalFrameNumber
            cv2.imwrite('videocache\\'+str(c) + '.jpg', frame)
            v.statusBar().showMessage('当前分割进度%.2f%%，请稍等'%progress)
            v.pbar.setValue(int(progress))
            cv2.waitKey(1)
        else:
            break
    vc.release()
    v.pbar.setValue(100)

#图像平均函数
def imgavg(start,num):
    image=np.array([0,0,0])
    img=[0 for i in range(num)]
    for i in range(num):
        img[i]=cv2.imread('videocache/'+str(i+1)+'.jpg')
        img[i]=img[i].astype(np.float32)
        image=image+img[i]
    image=image/num
    image=image.astype(np.uint8)
    cv2.imwrite('average.jpg',image)
        
#中值滤波函数
def medianfiltering(img,time=9):
    afterfiltering=img.filter(ImageFilter.MedianFilter(time))
    return afterfiltering
  
#图像分割函数
def cutimg(img,cutsizelist):
    cutsizelist = [int(i) for i in cutsizelist]#将每个元素转变格式为整数
    cropped=img.crop(cutsizelist)
    return cropped

#图像显示函数
def showimg(img):
    plt.imshow(img)
    plt.show()

    
#用来传递参数的信号类
class Message(object):
    pass

#Msg是Message的一个类
Msg=Message()
Msg.lbcs = 3#默认滤波参数3
Msg.texthigh = 1300#默认高温为1300
Msg.textlow = 900#默认有效温度900
Msg.imgflag = 0#图片打开有效位置0
Msg.videoflag = 0#视频打开有效位置0
Msg.cutflag = 0#视频切割有效位置0
Msg.fa1 = -0.8514988528771257
Msg.fa2 = 0.007770962883027608
Msg.fa3 = -2.9824213008869194e-05
Msg.fa4 = 4.112641645792059e-08
Msg.fb = 39.506469454314335
Msg.ffa1 = -0.004945755380001099
Msg.ffa2 = 0.0003572448037209888
Msg.ffa3 = -3.614249575967717e-06
Msg.ffa4 = 9.876346847371055e-09
Msg.ffb = 6.75440195601941
#标定导入成功位置0
Msg.Calibration1flag = 0
Msg.Calibration2flag = 0
Msg.Calibration3flag = 0
Msg.Calibration4flag = 0
Msg.Calibration5flag = 0
Msg.Calibration6flag = 0
Msg.tempset = 0

Msg.A = 12460.85585
Msg.BB = 2.369484563
#GUI类-主窗口
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        #工具栏
        self.VideoAct = QAction(QIcon('ico/video.ico'), '视频处理模块', self)
        self.VideoAct.setStatusTip('进入视频处理模块')

        self.CalibrationAct = QAction(QIcon('ico/Calibration.ico'), '标定模块', self)
        self.CalibrationAct.setStatusTip('进入标定模块')
        
        toolbar = self.addToolBar('Tools')
        toolbar.addAction(self.VideoAct)
        toolbar.addAction(self.CalibrationAct)

        #创建状态栏
        self.statusBar()

        #创建进度条并设为不可见
        
        self.pbar = QProgressBar(self)
        #参数是从左上取点，长度和高度
        self.pbar.setGeometry(150, 240, 200, 25)
        self.pbar.setVisible(False)

        #第一个菜单栏
        openFile = QAction(QIcon('ico/open.ico'), '打开图片', self)
        openFile.setShortcut('Ctrl+P')
        openFile.setStatusTip('打开一个图片文件')
        openFile.triggered.connect(self.FileOpen)

        openVideo = QAction(QIcon('ico/openvideo.ico'),'选择视频', self)
        openVideo.setShortcut('Ctrl+V')
        openVideo.setStatusTip('打开一个视频文件')
        openVideo.triggered.connect(self.VideoOpen)


        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')
        fileMenu.addAction(openFile)
        fileMenu.addAction(openVideo)
        

        #第二个菜单栏
        showFile = QAction(QIcon('ico/show.ico'),'原图',self)
        showFile.setShortcut('Ctrl+Q')
        showFile.setStatusTip('查看已经打开的文件的原图')
        showFile.triggered.connect(self.FileShow)
        
        checklb = QAction(QIcon('ico/lb.ico'), '滤波结果', self)
        checklb.setStatusTip('查看中值滤波的结果')
        checklb.triggered.connect(self.zzlb)

        checkjq = QAction(QIcon('ico/jq.ico'), '截取结果', self)
        checkjq.setStatusTip('查看图像截取的结果')
        checkjq.triggered.connect(self.txjq)

        checklbjq = QAction(QIcon('ico/lbjq.ico'), '预处理结果', self)
        checklbjq.setStatusTip('查看图像预处理的结果')
        checklbjq.triggered.connect(self.lbjq)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&查看')
        fileMenu.addAction(showFile)
        fileMenu.addAction(checklb)
        fileMenu.addAction(checkjq)
        fileMenu.addAction(checklbjq)

        #第三个菜单栏
        self.VideoMenu = QAction(QIcon('ico/video.ico'), '视频处理模块', self)
        self.VideoMenu.setStatusTip('进入视频处理模块')

        self.Calibration = QAction(QIcon('ico/Calibration.ico'), '标定模块', self)
        self.Calibration.setStatusTip('进入标定模块')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&模块')
        fileMenu.addAction(self.VideoMenu)
        fileMenu.addAction(self.Calibration)


        #第四个菜单栏
        self.openHelp = QAction(QIcon('ico/help.ico'), '帮助', self)
        self.openHelp.setShortcut('F1')
        self.openHelp.setStatusTip('如需帮助，请按此')
        

        helpMenu = menubar.addMenu('&帮助')
        helpMenu.addAction(self.openHelp)

        #滤波相关
        self.lbbtn = QPushButton('滤波参数', self)
        self.lbbtn.move(20, 80)
        self.lbbtn.clicked.connect(self.lbcs)

        
        self.label1=QLabel(self)
        self.label1.setText("滤波参数为默认值9")
        self.label1.adjustSize()
        self.label1.move(180,88)

        #图像切割相关
        self.lbbtn = QPushButton('截取参数', self)
        self.lbbtn.move(20, 120)
        self.lbbtn.clicked.connect(self.jqcs)

        
        self.label2=QLabel(self)
        self.label2.setText("截取参数尚未设定")
        self.label2.adjustSize()
        self.label2.move(180,128)

        #阈值设定
        self.lbbtn = QPushButton('温度阈值设定', self)
        self.lbbtn.move(20, 160)
        self.lbbtn.clicked.connect(self.yzsd)


        self.label3=QLabel(self)
        self.label3.setText("默认值，高温阈值1300K，有效温度阈值900K")
        self.label3.adjustSize()
        self.label3.move(180,168)
        
        #输出结果
        self.outbtn = QPushButton('输出结果',self)
        self.outbtn.move(20,200)
        self.outbtn.clicked.connect(self.out)

        self.label4=QLabel(self)
        self.label4.setText("等待分析")
        self.label4.adjustSize()
        self.label4.move(180,208)


        #主窗口初始化
        self.statusBar().showMessage('程序就绪，请操作。如需帮助，请按F1')
        self.setGeometry(300, 300, 550, 300)
        self.setWindowTitle('锅炉火焰图像处理软件')
        self.setWindowIcon(QIcon('ico/main.ico'))
        self.show()
        

    #打开图片
    def FileOpen(self):

        fname = QFileDialog.getOpenFileName(self, '打开一张图片', '/home')
        self.statusBar().showMessage('打开图片的路径'+fname[0])
        filetype=fname[0].split('.')[-1].lower()
        
        if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
            Msg.fname=fname[0]
            Msg.imgflag=1
            img = Image.open(fname[0])
            rows,cols=img.size
            self.label2.setText("截取参数默认为图片大小"+str(rows)+'*'+str(cols))
            self.label2.adjustSize()
            Msg.cutinfo=[0,0,rows,cols]
            
           
        else:
            self.statusBar().showMessage(fname[0]+'不是一个图片文件，请重试')

    #打开视频
    def VideoOpen(self):
        fname = QFileDialog.getOpenFileName(self, '打开一个视频文件', '/home')
        self.statusBar().showMessage('选取视频的路径'+fname[0])
        filetype=fname[0].split('.')[-1].lower()

        if (filetype=='avi' or filetype=='rmvb' or filetype=='mov' or filetype=='rm' or filetype=='mkv' or filetype=='mp4'):
            Msg.vname=fname[0]
            Msg.videoflag=1
        else:
            self.statusBar().showMessage(fname[0]+'不是一个视频文件，请重试')

    #显示原图
    def FileShow(self):
        if(Msg.imgflag == 1):
            img=Image.open(Msg.fname)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有读取图片')
            
    #设置滤波参数    
    def lbcs(self):
        text, ok = QInputDialog.getText(self, '输入滤波参数', '输入滤波参数:')

        if (ok and int(text)%2!=0):
            self.label1.setText('滤波参数是：'+str(text))
            Msg.lbcs=int(text)
            self.statusBar().showMessage('滤波参数是：'+text)
        else:
            self.label1.setText('输入的滤波参数为一个偶数，滤波参数为'+str(Msg.lbcs))
            self.label1.adjustSize()
            
    #中值滤波结果显示
    def zzlb(self):
        if(Msg.imgflag==1):
            img=Image.open(Msg.fname)
            img=medianfiltering(img,Msg.lbcs)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有读取图片')
            
    #截取参数设置
    def jqcs(self):
        textl, ok = QInputDialog.getText(self, '输入截取点左', '输入截取参数left:')
        Msg.textl=textl
        textu, ok = QInputDialog.getText(self, '输入截取参数上', '输入截取参数top:')
        Msg.textu=textu
        textr, ok = QInputDialog.getText(self, '输入截取参数右', '输入截取参数right:')
        Msg.textr=textr
        textd, ok = QInputDialog.getText(self, '输入截取参数下', '输入截取参数bottom:')
        Msg.textd=textd
        self.label2.setText('截取部分的左上角坐标为('+textl+','+textu+'),右下角坐标为('+textr+','+textd+')')
        self.label2.adjustSize()
        Msg.cutinfo=[Msg.textl,Msg.textu,Msg.textr,Msg.textd]
        Msg.cutinfo=[int(i)for i in Msg.cutinfo]

    #截取结果显示
    def txjq(self):
        if(Msg.imgflag==1):
            img=Image.open(Msg.fname)
            img=cutimg(img,Msg.cutinfo)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有读取图片')

    #预处理结果
    def lbjq(self):
        if (Msg.imgflag==1):
            img=Image.open(Msg.fname)
            img=medianfiltering(img,Msg.lbcs)
            img=cutimg(img,Msg.cutinfo)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有读取图片')

    #阈值设定
    def yzsd(self):
        texthigh, ok = QInputDialog.getText(self, '输入高温阈值', '输入高温阈值:')
        Msg.texthigh=int(texthigh)
        textlow, ok = QInputDialog.getText(self, '输入有效温度阈值', '输入有效温度阈值:')
        Msg.textlow=int(textlow)
        self.label3.setText('高温区阈值为'+texthigh+'K，有效温度阈值为'+textlow+'K')
        self.label3.adjustSize()

    #图像处理
    def out(self):
        self.statusBar().showMessage('开始处理图像……')
        if (Msg.imgflag==1):
            highdot=0
            lowdot=0
            img=Image.open(Msg.fname)
            img=cutimg(img,Msg.cutinfo)
            img=medianfiltering(img,Msg.lbcs)
            self.statusBar().showMessage('图像预处理成功……正在生成热力图……')
            
            
            img=np.array(img)#图像转变为数组，三维
            rows,cols,dims=img.shape#新图像的大小数据
            temp=[[0 for c in range(cols)]for c in range(rows)]#建立一个和图像等大的二维数组存储温度信号
            
            #显示进度条
            self.pbar.setVisible(True)
            for i in range(rows):
                progress = i*100/rows
                self.statusBar().showMessage('温度计算中，已完成%.2f%%'%progress)
                self.pbar.setValue(int(progress))
    
                for j in range(cols):
                    temp[i][j]=int(tempcalc(int(img[i,j,0]),int(img[i,j,1]),int(img[i,j,2])))#温度变换算法
                    
                    
            self.statusBar().showMessage('温度计算完成！正在分析温度场信息')
            
            self.pbar.setValue(100)
            
            
            #隐藏进度条
            self.pbar.setVisible(False)
            
            for i in range(rows):
                for j in range(cols):
                    if ((temp[i][j])>=Msg.texthigh):
                        highdot=highdot+1
                    if ((temp[i][j])>=Msg.textlow):
                        lowdot=lowdot+1
            hpercent=highdot*100/(rows*cols)
            lpercent=lowdot*100/(rows*cols)
            self.statusBar().showMessage('热力图生成成功！')

            self.label4.setText('温度分析完成！')
            self.label4.adjustSize()

        
            picture=np.array(temp)

            maxtemp = picture.max()
            mintemp = picture.min()
            avetemp = picture.mean()
            

            
            plt.figure('温度热力图')
            plt.title('温度热力图',fontproperties = myfont)
            plt.xlabel('最高温度：%dK 最低温度：%dK 平均温度：%.2fK\n 高温面积率：%.2f%% 有效面积率：%.2f%%'%(maxtemp,mintemp,avetemp,hpercent,lpercent) , fontproperties=myfont)
            plt.imshow(picture,cmap='jet')
            plt.colorbar()
            plt.show()

        else:
            self.statusBar().showMessage('还没有读取图片')
 
        
        
#帮助窗口        
class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        
        self.setFixedSize(300, 300)
        self.setWindowTitle('帮助')
        self.setWindowIcon(QIcon('ico/help.ico'))
        self.label1=QLabel(self)
        self.label1.setText("  对视频的处理需要先将视频分割，分割\n成图像后可选择合并或不合并再手动处理。")
        self.label1.adjustSize()
        self.label1.move(40,40)
        
    def handle_click(self):
        self.show()


#标定模块        
class CalibrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    #响应事件
    def handle_click(self):
        self.show()

    def initUI(self):
        
        self.statusBar()
        self.resize(700, 300)
        self.setWindowTitle('标定模块')
        self.setWindowIcon(QIcon('ico/Calibration.ico'))


        #导入标定图片菜单栏

        openFile1 = QAction(QIcon('ico/open.ico'), '导入标定图片1', self)
        openFile1.setStatusTip('导入标定图片1')
        openFile1.triggered.connect(self.FileOpen1)

        openFile2 = QAction(QIcon('ico/open.ico'), '导入标定图片2', self)
        openFile2.setStatusTip('导入标定图片2')
        openFile2.triggered.connect(self.FileOpen2)

        openFile3 = QAction(QIcon('ico/open.ico'), '导入标定图片3', self)
        openFile3.setStatusTip('导入标定图片3')
        openFile3.triggered.connect(self.FileOpen3)

        openFile4 = QAction(QIcon('ico/open.ico'), '导入标定图片4', self)
        openFile4.setStatusTip('导入标定图片4')
        openFile4.triggered.connect(self.FileOpen4)

        openFile5 = QAction(QIcon('ico/open.ico'), '导入标定图片5', self)
        openFile5.setStatusTip('导入标定图片5')
        openFile5.triggered.connect(self.FileOpen5)

        openFile6 = QAction(QIcon('ico/open.ico'), '导入标定图片6', self)
        openFile6.setStatusTip('导入标定图片6')
        openFile6.triggered.connect(self.FileOpen6)


        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&导入')
        fileMenu.addAction(openFile1)
        fileMenu.addAction(openFile2)
        fileMenu.addAction(openFile3)
        fileMenu.addAction(openFile4)
        fileMenu.addAction(openFile5)
        fileMenu.addAction(openFile6)

        #显示标定图片菜单栏

        showFile1 = QAction(QIcon('ico/show.ico'), '显示标定图片1', self)
        showFile1.setStatusTip('显示标定图片1')
        showFile1.triggered.connect(self.ShowFile1)

        showFile2 = QAction(QIcon('ico/show.ico'), '显示标定图片2', self)
        showFile2.setStatusTip('显示标定图片2')
        showFile2.triggered.connect(self.ShowFile2)

        showFile3 = QAction(QIcon('ico/show.ico'), '显示标定图片3', self)
        showFile3.setStatusTip('显示标定图片3')
        showFile3.triggered.connect(self.ShowFile3)

        showFile4 = QAction(QIcon('ico/show.ico'), '显示标定图片4', self)
        showFile4.setStatusTip('显示标定图片4')
        showFile4.triggered.connect(self.ShowFile4)

        showFile5 = QAction(QIcon('ico/show.ico'), '显示标定图片5', self)
        showFile5.setStatusTip('显示标定图片5')
        showFile5.triggered.connect(self.ShowFile5)

        showFile6 = QAction(QIcon('ico/show.ico'), '显示标定图片6', self)
        showFile6.setStatusTip('显示标定图片6')
        showFile6.triggered.connect(self.ShowFile6)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&显示')
        fileMenu.addAction(showFile1)
        fileMenu.addAction(showFile2)
        fileMenu.addAction(showFile3)
        fileMenu.addAction(showFile4)
        fileMenu.addAction(showFile5)
        fileMenu.addAction(showFile6)

        #RGB参数读取
        readrgb = QPushButton('读取RGB参数',self)
        readrgb.move(20, 40)
        readrgb.clicked.connect(self.readrgb)

        self.label1=QLabel(self)
        self.label1.setText("RGB参数等待读取")
        self.label1.adjustSize()
        self.label1.move(160,48)

        #温度设置
        tempset = QPushButton('设置温度参数',self)
        tempset.move(20, 100)
        tempset.clicked.connect(self.settemp)

        self.label2=QLabel(self)
        self.label2.setText("温度参数等待设置")
        self.label2.adjustSize()
        self.label2.move(160,108)

        #拟合
        Calibration = QPushButton('开始标定',self)
        Calibration.move(20,200)
        Calibration.clicked.connect(self.Calibration)

        self.label3=QLabel(self)
        self.label3.setText("尚未标定")
        self.label3.adjustSize()
        self.label3.move(160,208)
        
    def readrgb(self):
        if(Msg.Calibration6flag == 1):
            
            R1,G1,B1 = returnrgb(Msg.Calibration1)
            R2,G2,B2 = returnrgb(Msg.Calibration2)
            R3,G3,B3 = returnrgb(Msg.Calibration3)
            R4,G4,B4 = returnrgb(Msg.Calibration4)
            R5,G5,B5 = returnrgb(Msg.Calibration5)
            R6,G6,B6 = returnrgb(Msg.Calibration6)
            
            if B1 == 0:
                B1 = 1
            if B2 == 0:
                B2 = 1
            if B3 == 0:
                B3 = 1
            if B4 == 0:
                B4 = 1
            if B5 == 0:
                B5 = 1
            if B6 == 0:
                B6 = 1

            Msg.R = [R1,R2,R3,R4,R5,R6]
            Msg.G = [G1,G2,G3,G4,G5,G6]
            Msg.B = [B1,B2,B3,B4,B5,B6]
            Msg.RB = [R1/B1,R2/B2,R3/B3,R4/B4,R5/B5,R6/B6]

            self.label1.setText("1:[%d,%d,%d] 2:[%d,%d,%d]\n3:[%d,%d,%d] 4:[%d,%d,%d]\n5:[%d,%d,%d] 6:[%d,%d,%d]"%(R1,G1,B1,R2,G2,B2,R3,G3,B3,R4,G4,B4,R5,G5,B5,R6,G6,B6))
            self.label1.adjustSize()
            
        else:
            self.statusBar().showMessage('请确保所有的标定图片都被导入！')

    def settemp(self):
        temp1, ok = QInputDialog.getText(self, '输入标定图片1的温度（K）', '输入标定图片1的温度（K）')
        Msg.temp1 = int(temp1)
        temp1, ok = QInputDialog.getText(self, '输入标定图片2的温度（K）', '输入标定图片2的温度（K）')
        Msg.temp2 = int(temp1)
        temp1, ok = QInputDialog.getText(self, '输入标定图片3的温度（K）', '输入标定图片3的温度（K）')
        Msg.temp3 = int(temp1)
        temp1, ok = QInputDialog.getText(self, '输入标定图片4的温度（K）', '输入标定图片4的温度（K）')
        Msg.temp4 = int(temp1)
        temp1, ok = QInputDialog.getText(self, '输入标定图片5的温度（K）', '输入标定图片5的温度（K）')
        Msg.temp5=int(temp1)
        temp1, ok = QInputDialog.getText(self, '输入标定图片6的温度（K）', '输入标定图片6的温度（K）')
        Msg.temp6 = int(temp1)
        Msg.tempset = 1
        self.label2.setText("标定图片1温度：%d K\n标定图片2温度：%d K\n标定图片3温度：%d K\n标定图片4温度：%d K\n标定图片5温度：%d K\n标定图片6温度：%d K\n"%(Msg.temp1,Msg.temp2,Msg.temp3,Msg.temp4,Msg.temp5,Msg.temp6))
        self.label2.adjustSize()

    def Calibration(self):
        if(Msg.tempset == 1 and Msg.Calibration6flag == 1):
            f = [0,0,0,0,0,0]
            T = [Msg.temp1,Msg.temp2,Msg.temp3,Msg.temp4,Msg.temp5,Msg.temp6]
            for i in range(6):
                f[i] = Msg.A/T[i] - Msg.BB - math.log(Msg.RB[i],math.e)
            y = np.array(f)
            x = np.array(Msg.R)
            z1 = np.polyfit(x, y, 4)#用4次多项式拟合
            Msg.fa4 , Msg.fa3 , Msg.fa2 , Msg.fa1 , Msg.fb = z1
            print(Msg.fa4 , Msg.fa3 , Msg.fa2 , Msg.fa1 , Msg.fb)
            x = np.array(Msg.B)
            z1 = np.polyfit(x, y, 4)
            Msg.ffa4 , Msg.ffa3 , Msg.ffa2 , Msg.ffa1 , Msg.ffb = z1
            print(Msg.ffa4 , Msg.ffa3 , Msg.ffa2 , Msg.ffa1 , Msg.ffb)
            self.label3.setText('标定成功！')
            self.label3.adjustSize()

    def FileOpen1(self):

        fname = QFileDialog.getOpenFileName(self, '导入标定图片1', '/home')
        filetype=fname[0].split('.')[-1].lower()
        
        if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
            Msg.Calibration1 = fname[0]
            Msg.Calibration1flag = 1
            self.statusBar().showMessage('标定图片1导入成功！')
           
        else:
            self.statusBar().showMessage('文件格式错误！')

    def ShowFile1(self):
        
        if(Msg.Calibration1flag == 1):
            img = Image.open(Msg.Calibration1)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有导入标定图片1')

    def FileOpen2(self):

        if(Msg.Calibration1flag == 1):
            fname = QFileDialog.getOpenFileName(self, '导入标定图片2', '/home')
            filetype=fname[0].split('.')[-1].lower()
        
            if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
                Msg.Calibration2 = fname[0]
                Msg.Calibration2flag = 1
           
            else:
                self.statusBar().showMessage('文件格式错误！')
        else:
            self.statusBar().showMessage('请先导入标定图片1！')

    def ShowFile2(self):
        
        if(Msg.Calibration2flag == 1):
            img = Image.open(Msg.Calibration2)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有导入标定图片2')

    def FileOpen3(self):

        if(Msg.Calibration2flag == 1):
            fname = QFileDialog.getOpenFileName(self, '导入标定图片3', '/home')
            filetype=fname[0].split('.')[-1].lower()
        
            if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
                Msg.Calibration3 = fname[0]
                Msg.Calibration3flag = 1
           
            else:
                self.statusBar().showMessage('文件格式错误！')
        else:
            self.statusBar().showMessage('请先导入标定图片2！')

    def ShowFile3(self):

        if(Msg.Calibration3flag == 1):
            img = Image.open(Msg.Calibration3)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有导入标定图片3')


    def FileOpen4(self):

        if(Msg.Calibration3flag == 1):
            fname = QFileDialog.getOpenFileName(self, '导入标定图片4', '/home')
            filetype=fname[0].split('.')[-1].lower()
        
            if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
                Msg.Calibration4 = fname[0]
                Msg.Calibration4flag = 1
           
            else:
                self.statusBar().showMessage('文件格式错误！')
        else:
            self.statusBar().showMessage('请先导入标定图片3！')

    def ShowFile4(self):
        
        if(Msg.Calibration4flag == 1):
            img = Image.open(Msg.Calibration4)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有导入标定图片4')

    def FileOpen5(self):

        if(Msg.Calibration4flag == 1):
            fname = QFileDialog.getOpenFileName(self, '导入标定图片5', '/home')
            filetype=fname[0].split('.')[-1].lower()
        
            if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
                Msg.Calibration5 = fname[0]
                Msg.Calibration5flag = 1
           
            else:
                self.statusBar().showMessage('文件格式错误！')
        else:
            self.statusBar().showMessage('请先导入标定图片4！')

    def ShowFile5(self):
        
        if(Msg.Calibration5flag == 1):
            img = Image.open(Msg.Calibration5)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有导入标定图片5')

    def FileOpen6(self):

        if(Msg.Calibration5flag == 1):
            fname = QFileDialog.getOpenFileName(self, '导入标定图片6', '/home')
            filetype=fname[0].split('.')[-1].lower()
        
            if (filetype=='png'or filetype=='jpg'or filetype=='jpeg' or filetype=='bmp' ):
                Msg.Calibration6 = fname[0]
                Msg.Calibration6flag = 1
           
            else:
                self.statusBar().showMessage('文件格式错误！')
        else:
            self.statusBar().showMessage('请先导入标定图片5！')

    def ShowFile6(self):
        
        if(Msg.Calibration6flag == 1):
            img = Image.open(Msg.Calibration6)
            showimg(img)
        else:
            self.statusBar().showMessage('还没有导入标定图片6')
            

#视频处理模块        
class VideoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        

        self.setWindowTitle('视频处理模块')
        self.setWindowIcon(QIcon('ico/video.ico'))

        self.setFixedSize(400, 300)
        
        #创建进度条并设为不可见
        
        self.pbar = QProgressBar(self)
        #参数是从左上取点，长度和高度
        self.pbar.setGeometry(50, 140, 300, 25)
        self.pbar.setVisible(False)

        #视频切割
        self.videobtn = QPushButton('视频切割',self)
        self.videobtn.move(150,60)
        self.videobtn.clicked.connect(self.videocut)


        #多帧合成
        self.fusionbtn = QPushButton('多帧合成',self)
        self.fusionbtn.move(150,100)
        self.fusionbtn.clicked.connect(self.fusion)

        #第一个菜单栏
        openVideo = QAction(QIcon('ico/openvideo.ico'),'选择视频', self)
        openVideo.setShortcut('Ctrl+V')
        openVideo.setStatusTip('打开一个视频文件')
        openVideo.triggered.connect(self.VideoOpen)

        openFolder = QAction(QIcon('ico/folder.ico'),'视频文件夹', self)
        openFolder.setStatusTip('打开视频分割文件夹')
        openFolder.triggered.connect(self.FolderOpen)


        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')
        fileMenu.addAction(openVideo)
        fileMenu.addAction(openFolder)

    #打开文件夹
    def FolderOpen(self):
        if(Msg.cutflag==1):
            os.system("start explorer videocache")
        else:
            self.statusBar().showMessage('本次程序运行时并没有分割过视频，请尝试再运行一次分割。')

    #视频切割
    def videocut(self):
        if(Msg.videoflag==1):
            self.statusBar().showMessage('正在分割视频中……请稍等')
            self.pbar.setVisible(True)
            save_img(Msg.vname)
            self.statusBar().showMessage('视频分割成功，请在程序目录下/videocache文件中查看！')
            Msg.cutflag=1
            self.pbar.setVisible(False)
        else:
            self.statusBar().showMessage('还没有读取视频')

    #多帧合成       
    def fusion(self):
        if(Msg.cutflag==1):
            textstart, ok = QInputDialog.getText(self, '输入初始图像编号', '输入初始图像编号:')
            textnum, ok = QInputDialog.getText(self, '输入平均的图像张数', '输入平均图像张数:')
            Msg.fusionstart=int(textstart)
            Msg.fusionnum=int(textnum)
            self.statusBar().showMessage('正在合成图像中……请稍等')
            imgavg(Msg.fusionstart,Msg.fusionnum)
            self.statusBar().showMessage('图像合成成功，请在程序目录下average.jpg查看')
        else:
            self.statusBar().showMessage('本次程序运行时并没有分割过视频，请尝试再运行一次分割。')

    #打开视频
    def VideoOpen(self):
        fname = QFileDialog.getOpenFileName(self, '打开一个视频文件', '/home')
        self.statusBar().showMessage('选取视频的路径'+fname[0])
        filetype=fname[0].split('.')[-1].lower()

        if (filetype=='avi' or filetype=='rmvb' or filetype=='mov' or filetype=='rm' or filetype=='mkv' or filetype=='mp4'):
            Msg.vname=fname[0]
            Msg.videoflag=1
        else:
            self.statusBar().showMessage(fname[0]+'不是一个视频文件，请重试')

    def handle_click(self):
        self.show()

        

            
if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
        # 创建QSplashScreen对象实例
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap("ico/load.jpg"))
        # 显示画面
    splash.show()
        # 显示信息
    #splash.showMessage("启动中...", QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom, QtCore.Qt.white)
    time.sleep(3)
    ui = MainWindow()
    h = HelpWindow()
    v = VideoWindow()
    c = CalibrationWindow()
    ui.show()
        # 当主界面显示后销毁启动画面
    splash.finish(ui)
    ui.VideoAct.triggered.connect(v.handle_click)
    ui.openHelp.triggered.connect(h.handle_click)
    ui.VideoMenu.triggered.connect(v.handle_click)
    ui.CalibrationAct.triggered.connect(c.handle_click)
    ui.Calibration.triggered.connect(c.handle_click)
    sys.exit(app.exec_())


