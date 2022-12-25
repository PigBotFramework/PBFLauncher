import gc, sys, os, requests, json, shutil, time, datetime, pytz, traceback, path, psutil, fa
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo
from PyQt5 import QtCore, QtGui, QtWidgets
from system_hotkey import SystemHotkey
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QMessageBox, QDialog, QAction, QMenu, QSystemTrayIcon, QVBoxLayout, QToolButton
from PyQt5.QtCore import QThread, pyqtSignal, QStringListModel, QUrl
from uvicorn.supervisors import Multiprocess, ChangeReload
from uvicorn.server import Server
from ui.Ui_form import Ui_Form
from ui.Ui_pluginDialog import Ui_pluginDialog
from ui.Ui_updateDialog import Ui_updateDialog
from ui.titleWindow import TitleWindow
from ui.Ui_debug import Ui_debugDialog
from ui.Ui_noticeDialog import Ui_noticeDialog
from qt_material import apply_stylesheet
from bot import bot

__version__ = "1.1.3"

class debugDialog(QDialog, Ui_debugDialog):
    def __init__(self, parent=None):
        super(debugDialog,self).__init__(parent)
        self.setupUi(self)
        self.execBtn.clicked.connect(self.execPlugins)
    
    def execPlugins(self):
        func = self.exec.text()
        add = self.textEdit.toPlainText()
        if add:
            exec(add)
        try:
            if self.threadBox.isChecked():
                botIns.execPluginThread(func)
                self.textBrowser.setText("Thread无返回值")
            else:
                self.textBrowser.setText(botIns.execPlugin(func))
        except Exception as e:
            self.textBrowser.setText(traceback.format_exc())
        self.exec.setText("")

class PluginDialog(QDialog, Ui_pluginDialog):
    plugin = None

    def __init__(self, plugin, parent=None):
        super(PluginDialog,self).__init__(parent)
        self.setupUi(self)
        self.plugin = plugin
        self.PluginName.setText(plugin.get("name"))
        self.PluginVersion.setText(plugin.get("version"))
        self.PluginAuthor.setText(plugin.get("author"))
        self.PluginDes.setText(plugin.get("description"))
        self.cancelBtn.clicked.connect(self.close)
        self.installBtn.clicked.connect(self.install)
        self.openBtn.clicked.connect(self.open)
    
    def open(self):
        try:
            path = "./plugins/{}".format(self.plugin.get("cwd"))
            if not os.path.exists(path):
                QMessageBox.warning(self, "打开插件失败", "该插件尚未安装")
                return 
            exec("from {0}.ui import main as Ui_{0}_Main".format(self.plugin.get('cwd')))
            exec("Ui_{}_Main(self)".format(self.plugin.get('cwd')))
        except Exception as e:
            QMessageBox.warning(self, "打开插件失败", "该插件没有提供UI界面或代码有BUG\n报错信息如下：\n{}".format(e))
    
    def install(self):
        self.cancelBtn.setEnabled(False)
        self.installBtn.setText('Processing')
        path = "./plugins/{}".format(self.plugin.get("cwd"))
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        # 拉取远程代码
        try:
            clone_repo=Repo.clone_from('https://github.com/PigBotFrameworkPlugins/{}'.format(self.plugin.get("cwd")), path) 
            remote = clone_repo.remote()
            QMessageBox.information(self, "安装成功", "该插件安装/升级成功！")
            self.close()
        except Exception as e:
            shutil.rmtree(path)
            QMessageBox.warning(self, "插件安装失败", "执行Git Clone时失败\n{}".format(e))
            self.close()

class UpdateDialog(QDialog, Ui_updateDialog):
    def __init__(self, data, parent=None):
        super(UpdateDialog,self).__init__(parent)
        self.setupUi(self)
        print(data)
        self.versionBtn.setText(data.get("version"))
        self.nameBtn.setText(data.get("name"))
        self.timeBtn.setText(data.get("time"))
        self.descriptionBtn.setText(data.get("description"))
        self.cancelBtn.clicked.connect(self.close)
        self.installBtn.clicked.connect(self.install)
    
    def install(self):
        pass

class NoticeDialog(QDialog, Ui_noticeDialog):
    def __init__(self, parent=None):
        super(NoticeDialog,self).__init__(parent)
        self.setupUi(self)
        data = requests.get("https://qb.xzy.center/pbfl/notice")
        self.textBrowser.setText(data.content.decode())

class MyMainWindow(QWidget, Ui_Form):
    pluginsListOb = []
    #定义一个热键信号
    sig_keyhot = pyqtSignal(str)

    def __init__(self,parent =None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("./icon.jpg"))
    
    def init(self):
        try:
            self._init()
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.warning(self, "发生错误", "猪比运行发生错误，请将下列错误信息提交给开发者：\n{}".format(str(e)))

    def _init(self):
        botIns.CrashReport("Starting GUI...", "PBFLauncher")
        
        self.openAction = QAction("打开主界面", self)
        self.exitAction = QAction("退出程序", self)
        self.aboutAction = QAction("关于", self)
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.openAction)
        self.trayIconMenu.addAction(self.exitAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.aboutAction)
        self.openAction.triggered.connect(myWin.show)
        self.exitAction.triggered.connect(app.quit)
        self.aboutAction.triggered.connect(self.about)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon(path.path("icon.jpg")))
        self.trayIcon.setToolTip("PBF")
        self.trayIcon.show()

        #2. 设置我们的自定义热键响应函数
        self.sig_keyhot.connect(self.MKey_pressEvent)
        #3. 初始化两个热键
        self.hk_quit,self.hk_show,self.hk_hide = SystemHotkey(), SystemHotkey(), SystemHotkey()
        #4. 绑定快捷键和对应的信号发送函数
        self.hk_quit.register(('control','q'),callback=lambda x:self.send_key_event("quit"))
        self.hk_show.register(('control', 'up'), callback=lambda x:self.send_key_event("show"))
        self.hk_hide.register(('control', 'down'), callback=lambda x:self.send_key_event("hide"))

        self.websiteBtn.clicked.connect(lambda:QDesktopServices.openUrl(QUrl("https://qb.xzy.center")))
        self.portLine.setText("8080")
        self.hostLine.setText("0.0.0.0")
        self.stopBtn.setEnabled(False)
        self.runBtn.clicked.connect(self.run)
        self.stopBtn.clicked.connect(self.stop)
        self.debugBtn.clicked.connect(debugDialog(self).exec_)
        try:
            datalist = json.loads(requests.get("https://qqbot.xzy.center/1000/getPluginsData").json())
            qlist = []
            self.pluginsListOb = datalist
            for i in datalist:
                qlist.append(i.get("name"))
        except Exception as e:
            qlist = ["拉取插件信息失败", "请检查您是否连接到互联网", "请关闭电脑代理", "具体报错信息如下：", str(e)]
        self.setPluginsList(qlist)
        self.pluginsList.clicked.connect(self.clickedlist)

        self.crashThread = CrashThread()
        self.crashThread.start()
        print("crashThread started.")
        
        try:
            data = requests.get("https://qb.xzy.center/pbfl/version").json()
            if data.get("version") != __version__:
                UpdateDialog(data, self).exec_()
            notice = botIns.selectx("SELECT * FROM `pbflConfig` WHERE `key`='notice'")
            if not notice:
                botIns.commonx("INSERT INTO `pbflConfig` (`key`, `value`) VALUES ('notice', '{}');".format(data.get("notice")))
                NoticeDialog(self).exec_()
            elif notice[0].get("value") != data.get("notice"):
                botIns.commonx("UPDATE `pbflConfig` SET `value`='{}' WHERE `key`='notice'".format(data.get("notice")))
                NoticeDialog(self).exec_()
        except Exception as e:
            print(traceback.format_exc())
            QMessageBox.warning(self, "请求更新失败！", str(e))
        
        # botBotconfig
        botData = botIns.selectx("SELECT * FROM `botBotconfig` WHERE `uuid`=123456789")[0]
        tableData = botIns.selectx("SELECT * FROM `botConfiglist`")
        # print(botData)
        #滚动区域的Widget
        vLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        commitButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        commitButton.setGeometry(QtCore.QRect(0, 0, 90, 80))
        commitButton.setText("提交")
        commitButton.clicked.connect(self.commitConfig)
        vLayout.addWidget(commitButton)
        for i in tableData:
            if i.get("key") == 'uuid' or i.get("key") == 'httpurl':
                continue
            
            inputLine = QtWidgets.QLineEdit(str(botData.get(i.get("key"))))
            inputLine.setObjectName("{}Config".format(i.get("key")))
            labelDes = QtWidgets.QLabel(str(i.get("description")))
            labelDes.setGeometry(QtCore.QRect(0, 0, 340, 211))
            labelDes.setMaximumSize(QtCore.QSize(340, 16777215))
            groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
            groupBox.setTitle(str(i.get("name")))
            vLayouts = QVBoxLayout()
            vLayouts.addWidget(inputLine)
            vLayouts.addWidget(labelDes)
            groupBox.setLayout(vLayouts)

            vLayout.addWidget(groupBox)
        self.scrollAreaWidgetContents.setLayout(vLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

    def commitConfig(self):
        tableData = botIns.selectx("SELECT * FROM `botConfiglist`")
        for i in tableData:
            if i.get("key") == 'uuid' or i.get("key") == 'httpurl':
                continue
            lineEdit = self.scrollAreaWidgetContents.findChild(QtWidgets.QLineEdit, "{}Config".format(i.get("key"))).text()
            if i.get("type") == "varchar":
                message = "`{}`='{}'".format(i.get("key"), lineEdit)
            else:
                message = "`{}`={}".format(i.get("key"), lineEdit)
            botIns.commonx("UPDATE `botBotconfig` SET {} WHERE `uuid`='123456789'".format(message))
        QMessageBox.information(self, "保存配置", "配置保存成功！")

    #热键处理函数
    def MKey_pressEvent(self,i_str):
        if i_str == "quit":
            app.quit()
        elif i_str == "show":
            myWin.show()
        elif i_str == "hide":
            myWin.hide()
        
    #热键信号发送函数(将外部信号，转化成qt信号)
    def send_key_event(self,i_str):
        self.sig_keyhot.emit(i_str)

    def about(self):
        QMessageBox.information(self, "About", "关于PBF")

    def setPluginsList(self, qlist):
        slm = QStringListModel()
        slm.setStringList(qlist) #将数据设置到model
        self.pluginsList.setModel(slm) #绑定 listView 和 model

    def clickedlist(self, qModelIndex):
        PluginDialog(self.pluginsListOb[qModelIndex.row()], self).exec_()
        fa.reloadPlugins()

    def stop(self):
        def _exit():
            for obj in gc.get_objects():
                if isinstance(obj, (ChangeReload, Multiprocess, Server)):
                    if isinstance(obj, Server):
                        obj.should_exit = True
                    else:
                        obj.should_exit.set()
        _exit()
        self.thread.stop()
        self.runBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
    
    def run(self):
        self.thread = RunThread(self.hostLine.text(), self.portLine.text())
        self.thread.start()
        self.stopBtn.setEnabled(True)
        self.runBtn.setEnabled(False)

class CrashThread(QThread):
    trigger = pyqtSignal()
    def __init__(self):
        super(CrashThread, self).__init__()

    def __del__(self):
        self.wait()

    def getEndLine(self, name):
        with open(name, 'rb')as f:
            file_size = os.path.getsize(name)
            offset = -100
            # 文件字节大小为0则返回none
            if file_size == 0:
                return ''
            while True:
                # 判断offset是否大于文件字节数,是则读取所有行，并返回最后一行
                if (abs(offset) >= file_size):
                    f.seek(-file_size,2)
                    data = f.readlines()
                    return data[-1]
                #游标移动倒数的字节数位置
                f.seek(offset, 2)
                data = f.readlines()
                # 判断读取到的行数，如果大于1则返回最后一行，否则扩大offset
                if (len(data) > 1):
                    return data[-1]
                else:
                    offset *= 2

    def run(self):
        oldLine = None
        while True:
            try:
                # PSUTIL
                cpuP = psutil.cpu_percent(interval=1)
                memP = psutil.virtual_memory().percent
                myWin.widget_2_sub.cpuBar.setValue(int(cpuP))
                myWin.widget_2_sub.memBar.setValue(int(memP))
                myWin.widget_2_sub.cpuLab.setText("{}%".format(cpuP))
                myWin.widget_2_sub.memLab.setText("{}%".format(memP))

                # CrashReport
                now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                fileName = now.strftime("logs/%Y-%m-%d.log")
                line = self.getEndLine(path.path(fileName))
                if line != oldLine:
                    print("append")
                    # update text browser
                    self.appendText(line.decode())
                    oldLine = line
            except Exception as e:
                try:
                    self.appendText(e)
                except Exception:
                    print(e)
            # time.sleep(1)
    
    def appendText(self, str):
        myWin.widget_2_sub.logTextarea.append(str.rstrip())
        myWin.widget_2_sub.logTextarea.moveCursor(myWin.widget_2_sub.logTextarea.textCursor().End)

class RunThread(QThread):
    trigger = pyqtSignal()
    host = 0
    port = 0
    uvi = None

    def __init__(self, host, port):
        super(RunThread, self).__init__()
        self.host = host
        self.port = port
  
    def __del__(self):
        self.wait()
  
    def run(self):
        fa.run(host=self.host, port=self.port)
    
    def stop(self):
        print("emit")
        self.trigger.emit()

botIns = bot()
app = QApplication(sys.argv)
# setup stylesheet
apply_stylesheet(app, theme='dark_teal.xml')
QApplication.setQuitOnLastWindowClosed(False)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
myWin = TitleWindow(widget_2_sub=MyMainWindow(),icon_path=path.path("icon.jpg"),title='小猪比机器人框架')
myWin.setWindowIcon(QIcon("./icon.jpg"))
myWin.setWindowTitle("小猪比机器人框架")
myWin.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)

def run():
    myWin.widget_2_sub.init()
    myWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()