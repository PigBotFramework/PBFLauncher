import path, os, requests, sys

def download(url, pathToFile):
    try:
        data = requests.get(url).content
        f = open(path.path(pathToFile), "wb")
        f.write(data)
        f.close()
    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        import MainWindow
        QMessageBox.warning(MainWindow.myWin, "发生错误", "请关闭系统代理并重新启动本程序！\n请关闭系统代理并重新启动本程序！\n请关闭系统代理并重新启动本程序！\n猪比运行发生错误，请将下列错误信息提交给开发者：\n{}".format(str(e)))
        sys.exit()

path.makeSurePathExists("resources/")
path.makeSurePathExists("plugins/")
path.makeSurePathExists("logs/")
if not os.path.exists(path.path("data.db")):
    print("data.db is not exists, downloading...")
    download("https://qb.xzy.center/pbfl/DlDB", "data.db")
if not os.path.exists(path.path("icon.jpg")):
    print("icon.jpg is not exists, downloading...")
    download("https://qb.xzy.center/pbfl/DlIcon", "icon.jpg")


import MainWindow
MainWindow.run()