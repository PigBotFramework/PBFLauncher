# 注意
**本地版内核为v3某版本，介于v3版本接口混乱，性能落后，开发方式落后，该版本已经停止更新与维护，请移步新的[v4版本](https://github.com/PigBotFramework/v4)！**

---

# PBFLauncher
PBF本地版

# 介绍
由于[PBF](https://github.com/PigBotFramework/main)之前闭源并且部署起来比较麻烦，推出了适合本地运行的版本，即：PBFL

# 运行
直接下载最新Release中的exe打开即可

# 优点
- 无需依赖
- 开箱即用
- 占用低
- 使用sqlite数据库，无需额外部署
- 设置全面
- 界面美观
- 可自定义性高
- 兼容原版PBF的插件

# 部署
如果你想进行开发工作，需要在本地部署
- 克隆源码
- `pip install -r rms.txt` 安装依赖
- `python main.py` 运行

# 打包
```bash
pip install pyinstaller
pyinstaller main.spec
```
