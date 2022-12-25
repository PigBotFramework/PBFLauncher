import sys
import traceback, time, random, requests, hmac, math, datetime, pytz, threading, sqlite3, os
from urllib.request import urlopen
from io import BytesIO
from path import path
# from PIL import Image, ImageFont, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
from apscheduler.schedulers.blocking import BlockingScheduler
from googletrans import Translator as googleTranslator
from imageutils.build_image import BuildImage, Text2Image
# from main import myWin

sys.path.append(path("plugins"))
googleTranslatorIns = googleTranslator()
# requests处理
s = requests.session()
s.keep_alive = False
requests.adapters.DEFAULT_RETRIES = 5
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}

commandListener = []
commandPluginsList = {}
messagelist = []
commandlist = []
messageListenerList = []
metaEventListenerList = []
requestListenerList = []
noticeListenerList = []
pluginsList = []

def varsInit(commandPluginsListVar, commandlistVar, messageListenerListVar, metaEventListenerListVar, requestListenerListVar, noticeListenerListVar, pluginsListVar):
    global commandPluginsList, commandlist, messageListenerList, metaEventListenerList, requestListenerList, noticeListenerList, pluginsList
    commandPluginsList = commandPluginsListVar
    commandlist = commandlistVar
    messageListenerList = messageListenerListVar
    metaEventListenerList = metaEventListenerListVar
    requestListenerList = requestListenerListVar
    noticeListenerList = noticeListenerListVar
    pluginsList = pluginsListVar

class ThreadWRV(threading.Thread):
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    
    def join(self):
        super().join()
        return self._return

class bot:
    args = None
    messageType = 'qn'
    botSettings = None
    userCoin = None
    userInfo = None
    pluginsList = []
    se = {}
    message = None
    ocrImage = None
    isGlobalBanned = None
    uuid = None
    runningProgram = "BOT"
    groupSettings = None
    
    sql_config = "SELECT * FROM `botSettings` WHERE `uuid` = '{0}' and {1}"
    sql_coinlist = "SELECT * FROM `botCoin` WHERE `uuid` = '{0}' and {1}"
    sql_quanjing = "SELECT * FROM `botQuanping` WHERE {0}"
    sql_keywordListSql = "SELECT * FROM `botKeyword` WHERE `uuid` = '{0}' and `state`=0"
    
    weijin = None
    rclOb = None
    kwrlist = None
    settingName = None
    commandmode = []
    # pluginsList = self.getPluginsList()
    
    def __init__(self):
        pass
    
    def WriteCommandListener(self, func=None, args=None, step=1, sendTime=time.time()):
        global commandListener
        num = self.findObject("uid", self.se.get('user_id'), commandListener).get('num')
        if num == -1:
            if step == None:
                step = 1
            commandListener.append({
                "func": func,
                "step": step,
                "args": args,
                "time": sendTime,
                "uid": self.se.get('user_id'),
                "gid": self.se.get('group_id')
            })
        else:
            if func != None:
                commandListener[num]['func'] = func
            if args != None:
                commandListener[num]['args'] = args
            if step != None and step != 1 and step != '1':
                commandListener[num]['step'] = step
            else:
                commandListener[num]['step'] = int(commandListener[num]['step']) + 1
            commandListener[num]['time'] = sendTime
        
    def ReadCommandListener(self):
        if self.rclOb == None:
            return self.findObject("uid", self.se.get('user_id'), commandListener).get('object')
        else:
            return self.rclOb
        
    def RemoveCommandListener(self):
        global commandListener
        
        num = self.findObject("uid", self.se.get('user_id'), commandListener).get('num')
        if num == -1:
            return False
        else:
            commandListener.pop(num)
            return True
    
    def requestInit(self, se, uuid):
        self.se = se
        self.message = se.get('message')
        try:
            if se.get('meta_event_type') == 'heartbeat':
                print('忽略心跳事件')
                return None
            
            # 不处理其他机器人的消息
            if se.get('user_id'):
                if self.selectx('SELECT * FROM `botBotconfig` WHERE `myselfqn`={0}'.format(se.get('user_id'))):
                    return None
                
            #入站第二步：初始化各项
            self.weijin = self.selectx("SELECT * FROM `botWeijin` WHERE `state`=0 or `state`=3;")
            self.kwrlist = self.selectx("SELECT * FROM `botReplace`")
            self.settingName = self.selectx("SELECT * FROM `botSettingName`")
            
            self.args = se.get("message").split(' ') if se.get('message') else None # 初始化参数
            self.messageType = 'cid' if se.get('channel_id') else 'qn' # 消息来源（频道或群组）
            self.botSettings = self.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid)) # 机器人实例设置
            self.groupSettings = self.GetConfig(uuid, self.messageType, se.get('group_id'), self.sql_config) if se.get('group_id') else None # 加载群聊设置
            if se.get('user_id'):
                self.userCoin = self.GetConfig(uuid, self.messageType, se.get('user_id'), self.sql_coinlist) # 初始化好感度
            if self.userCoin != None:
                try:
                    self.userInfo = self.userCoin[0]
                    self.userCoin = self.userInfo.get('value')
                    if not self.userCoin:
                        self.userCoin = -1
                except Exception as e:
                    self.userInfo = self.userCoin
                    self.userCoin = self.userInfo.get('value')
            else:
                self.userCoin = -1
                self.userInfo = None
                
            self.pluginsList = self.selectx('SELECT * FROM `botPlugins` WHERE `uuid` = "{0}"'.format(uuid)) # 插件列表
            if se.get('user_id'):
                self.isGlobalBanned = self.GetConfig(None, self.messageType, se.get('user_id'), self.sql_quanjing) if self.messageType != 'cid' else None
            self.uuid = uuid
            
            if self.groupSettings:
                try:
                    self.groupSettings = self.groupSettings[0]
                except Exception as e:
                    pass
            
            if self.botSettings:
                try:
                    self.botSettings = self.botSettings[0]
                except Exception as e:
                    pass
            
            if not self.groupSettings: # 初始化群聊设置
                if se.get("group_id"):
                    self.GroupInit()
                    return None
            
            print(self.groupSettings)
            print(self.botSettings)
            
            # 入站第三步：分发处理
            if self.isGlobalBanned == None:
                if se.get('channel_id') != None or self.se.get('group_id') == None:
                    self.start()
                elif self.groupSettings.get('power'):
                    self.start()
                else:
                    if self.message == '开机':
                        if se.get('sender').get('role') != 'member' or se.get('user_id') == self.botSettings.get('owner') or se.get('user_id') == self.botSettings.get('second_owner'):
                            sql = 'UPDATE `botSettings` SET `power`=1 WHERE `qn`='+str(se.get('group_id'))
                            self.commonx(sql)
                            self.send('{0}-开机成功！'.format(self.botSettings.get('name')))
                        else:
                            self.send('[CQ:face,id=151] 就你？先拿到管理员再说吧！')
                    elif self.message:
                        if ('[CQ:at,qq='+str(self.botSettings.get('myselfqn'))+']' in self.message) or (self.botSettings.get('name') in self.message) or ('机器人' in self.message):
                            self.send('{0}还没有开机哦~\n发送“开机”可以开启机器人！'.format(self.botSettings.get('name')))
                    self.checkWeijin(0)
        
        except Exception as e: # 出错了
            msg = '在处理群：{0} 用户：{1} 的消息时出现异常！\n{2}\n'.format(se.get('group_id'), se.get('user_id'), traceback.format_exc())
            self.CrashReport(msg)
    
    def GetPswd(self, uuid):
        if not uuid:
            return 'Please give a non-empty string as a uuid.'
        botOb = self.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid))
        if not botOb:
            return 'Cannot find the right secret. Is the uuid right?'
        else:
            return botOb[0].get('secret')
            
    def GetConfig(self, uuid, key, value, template, sql=None):
        if sql == None:
            sql = '`{0}`="{1}"'.format(key, value) if isinstance(value, str) else '`{0}`={1}'.format(key, value)
        sql = template.format(uuid, sql) if uuid else template.format(sql)
        ob = self.selectx(sql)
        return None if not ob else ob
    
    def encryption(self, data, secret):
        key = secret.encode('utf-8')
        obj = hmac.new(key, msg=data, digestmod='sha1')
        return obj.hexdigest()
        
    def selectx(self, sqlstr):
        conn = sqlite3.connect(path('data.db'))
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        cursor = c.execute(sqlstr)
        data = cursor.fetchall()
        conn.close()
        ret = []
        for i in data:
            ret.append(dict(i))
        return ret
    
    def commonx(self, sqlstr):
        conn = sqlite3.connect(path('data.db'))
        c = conn.cursor()
        c.execute(sqlstr)
        conn.commit()
        conn.close()
        
    def sendRawMessage(self, content):
        if self.se.get('group_id') == None:
            data = self.CallApi('send_msg', {'user_id':self.se.get('user_id'),'message':content})
        else:
            data = self.CallApi('send_msg', {'group_id':self.se.get('group_id'),'message':content})
        return data
    
    def sendChannel(self, content):
        data = self.CallApi('send_guild_channel_msg', {'guild_id':self.se.get('guild_id'),'channel_id':self.se.get('channel_id'),'message':content})
        return data

    def sendInsertStr(self, content):
        sendStr = 'abcdefghijklmnopqrstuvwxyz'
        if '[CQ:' not in content:
            for i in range(math.floor(len(content)/15)):
                pos = random.randint(0, len(content))
                content = content[:pos] + sendStr[random.randint(0, 25)] + content[pos:]
        return content

    def send(self, content, coinFlag=True, insertStrFlag=True, retryFlag=True, translateFlag=True):
        uid = self.se.get("user_id")
        gid = self.se.get("group_id")
        uuid = self.uuid
        botSettings = self.botSettings
        groupSettings = self.groupSettings
        content = str(content)
        
        # 随机好感度
        if random.randint(1, botSettings.get('coinPercent')) == 1 and coinFlag:
            userCoin = self.addCoin()
            if userCoin != False:
                content += '\n\n『谢谢陪我聊天，好感度加{0}』'.format(userCoin)
        
        # 插入字符和翻译
        if "[" in content and "]" in content:
            content = content.replace("\n", "[\n]").replace("face54", "[face54]")
            newcon = ""
            for i in content.split("["):
                if "]" in i:
                    i = i.split("]")
                    newcon += "[{0}]".format(i.pop(0))
                    for l in i:
                        if l:
                            l = self.translator(l, to_lang=groupSettings.get('translateLang')) if translateFlag and groupSettings.get('translateLang') != "zh" else l
                            l = self.sendInsertStr(l) if insertStrFlag and groupSettings.get('translateLang') == "zh" else l
                        newcon += str(l)
                else:
                    if i:
                        i = self.translator(i, to_lang=groupSettings.get('translateLang')) if translateFlag and groupSettings.get('translateLang') != "zh" else i
                        i = self.sendInsertStr(i) if insertStrFlag and groupSettings.get('translateLang') == "zh" else i
                    newcon += str(i)
            content = newcon
            content = content.replace("[\n]", "\n").replace("[|", "").replace("|]", "").replace("[face54]", "[CQ:face,id=54]")
        else:
            content = self.translator(content, to_lang=groupSettings.get('translateLang')) if translateFlag and groupSettings.get('translateLang') != "zh" else content
            content = self.sendInsertStr(content) if insertStrFlag and groupSettings.get('translateLang') == "zh" else content
        
        # 频道消息
        if self.se.get('channel_id') != None:
            return self.sendChannel(content)
        
        dataa = self.sendRawMessage(content)
        try:
            if dataa.get('status') == 'failed' and self.se.get('post_type') == 'message':
                mid = None
                if retryFlag:
                    self.sendRawMessage('消息发送失败，尝试转图片发送...')
                    self.message = content
                    self.se['user_id'] = botSettings.get('myselfqn')
                    self.se['sender']['nickname'] = botSettings.get('name')
                    return self.sendImage()
            else:
                mid = dataa.get('data').get('message_id')
                return mid
        except Exception as e:
            pass

    def SendOld(self, uid, content, gid=None):
        # 随机插入字符
        # content = sendInsertStr(content)
        
        if gid == None:
            dataa = self.CallApi('send_msg', {'user_id':uid,'message':content})
        else:
            dataa = self.CallApi('send_msg', {'group_id':gid,'message':content})
        if dataa.get('status') != 'failed':
            mid = dataa.get('data').get('message_id')
        else:
            mid = None
        return mid
        
    def CrashReport(self, message, title='异常报告', level="info", sendFlag=False):
        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        ctime = now.strftime("%Y-%m-%d %H:%M:%S")
        str = "[{0}] [{1}/{2}/{3}] [{4}] {5}\n".format(ctime, self.runningProgram, level, self.uuid, title, message)
        print(str)
        # myWin.textBrowser.append(str)
        fileName = now.strftime("logs/%Y-%m-%d.log")
        f = open(path(fileName), "a")
        f.write(str)
        f.close()
        if sendFlag:
            self.SendOld(self.botSettings.get('owner'), '[CQ:face,id=189] '+str(title)+'\n'+str(message), self.botSettings.get('CrashReport'))
    
    def CallApi(self, api, parms={}):
        botSettings = self.botSettings
        return requests.post(url='{0}/{1}?access_token={2}'.format(botSettings.get('httpurl'), api, botSettings.get('secret')), json=parms).json()
        
    def weijinWhileFunc(self, message):
        for l in self.weijin:
            i = l.get('content')
            if i in message and i != '' and (l.get("qn") == 0 or l.get("qn") == self.se.get("group_id")):
                return i
        return False
    
    def checkWeijin(self, weijinFlag):
        se = self.se
        uid = se.get('user_id')
        gid = se.get('group_id')
        message = self.message
        
        if message == None:
            return False
        
        messageReplace = message.replace(' ','')
        i = self.weijinWhileFunc(messageReplace)
        if i != False:
            if weijinFlag == 1 and gid != None and self.se.get("sender").get("role") == "member":
                self.send('[CQ:face,id=151] {0}不喜欢您使用（{1}）这种词语哦，请换一种表达方式吧！'.format(self.botSettings.get('name'), i))
                self.delCoin()
                self.CallApi('delete_msg', {'message_id':self.se.get('message_id')})
                
            # 如果辱骂机器人则骂回去
            if ('[CQ:at,qq='+str(self.botSettings.get('myselfqn'))+']' in messageReplace) or (self.botSettings.get('name') in messageReplace) or ('猪比' in messageReplace) or ('猪逼' in messageReplace) or ('猪鼻' in messageReplace) or ('机器人' in messageReplace) or (gid == None):
                repeatnum = self.botSettings.get('yiyan')
                while repeatnum > 0:
                    self.delCoin()
                    dataa = requests.get(url=self.botSettings.get('duiapi'))
                    dataa.enconding = "utf-8"
                    if repeatnum == self.botSettings.get('yiyan'):
                        replymsg = '[CQ:reply,id='+str(se.get('message_id'))+'] 你骂我？好啊\n'+str(dataa.text)
                    else:
                        replymsg = dataa.text
                    self.send(replymsg)
                    repeatnum -= 1
        
            # break 
            return True
    
    def GroupInit(self):
        gid = self.se.get('group_id')
        self.CrashReport(gid, "groupinit")
        if gid == None:
            return 
        sql = 'INSERT INTO `botSettings` (`qn`, `replyPercent`, `autoAcceptGroup`, `recallFlag`, `admin`, `decrease`, `increase`, `AntiswipeScreen`, `increase_notice`, `weijinCheck`, `keywordReply`, `power`, `uuid`) VALUES ({0}, 100, 1, 1, 1, 1, 1, 10, "欢迎入群！（请管理自定义入群欢迎内容）", 0, 1, {2}, "{1}");'.format(gid, self.uuid, self.botSettings.get('defaultPower'))
        self.commonx(sql)
        if self.botSettings.get('defaultPower'):
            self.send('[CQ:face,id=189] 机器人已初始化，发送“菜单”可以查看全部指令\n发送“群聊设置”可以查看本群的初始设置\n 如果不会使用机器人请发送“新手教程”查看教程！')
        else:
            self.send('[CQ:face,id=189] 机器人已初始化，当前已关机，发送“开机”可以开启机器人\n开机后，发送“菜单”可以查看指令！')
        
    def checkCoin(self):
        for i in self.coinlist:
            if str(self.se.get('user_id')) == str(i.get(self.messageType)):
                return i.get('value')
        return -1

    def addCoin(self, value=None):
        if value == None:
            value=random.randint(self.botSettings.get('lowRandomCoin'), self.botSettings.get('highRandomCoin'))
        
        uid = self.se.get('user_id')
        
        if self.userCoin == -1:
            return 0
        if self.userCoin == False:
            return False
        
        try:
            self.commonx('UPDATE `botCoin` SET `value`='+str(int(self.userCoin)+int(value))+' WHERE `qn`='+str(uid))
        except Exception as e:
            pass
        return value
    
    def delCoin(self, value=None):
        if value == None:
            value = random.randint(self.botSettings.get('lowRandomCoin'), self.botSettings.get('highRandomCoin'))
        
        uid = self.se.get('user_id')
        
        if self.userCoin == -1:
            return 0
        if self.userCoin == False:
            return False
        
        try:
            self.commonx('UPDATE `botCoin` SET `value`='+str(int(self.userCoin)-int(value))+' WHERE `qn`='+str(uid))
        except Exception as e:
            pass
        return value

    def getCQValue(self, key, message):
        return self.findObject('key', key, self.getCQArr(message)).get('object').get('value')

    def getCQArr(self, message):
        # message = message.replace('[', '').replace(']', '')
        message1 = message.split('[')
        message2 = message1[1].split(']')
        message = message2[0]
        message = message.split(',')
        arr = []
        for i in message:
            if i == message[0]:
                continue
            message1 = i.split('=')
            arr.append({"key":message1[0], "value":message1[1]})
        return arr

    # commandmode专用
    def findObject1(self, content):
        for l in self.commandmode:
            if content == l.get('name'):
                return l
        return -1

    # 查找键值对并返回对象
    def findObject(self, key, value, ob):
        num = 0
        for i in ob:
            if str(i.get(str(key))) == str(value):
                return {"num":num,"object":i}
            num += 1
        return {"num":-1,"object":404}
    
    # 查找键值对并返回在数组中的下标
    def getNumByObject(self, key, value, ob):
        num = 0
        for i in ob:
            if i.get(str(key)) == value:
                return num
            num += 1
        return -1
    
    def generate_code(self, num):
        '''generate_code方法主要用于生成指定长度的验证码，有一个num函数,需要传递一个int类型的数值,其return返回结果为num'''
        #定义字符串
        str1= "23456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        #循环num次生成num长度的字符串
        code =''
        for i in range(num):
            index = random.randint(0,len(str1)-1)
            code += str1[index]
        return code
    
    def openFile(self, path):
        with open(path, 'r') as f:
            return f.read()
        
    def writeFile(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def reply(self):
        uid = self.se.get('user_id')
        gid = self.se.get('group_id')
        message = self.message
        
        dataa = requests.get(url='http://ruyi.ai/v1/message?q={0}&app_key=2405d0e8-3cf0-4bb1-bb4f-c528ec7e8f5f&user_id=61492'.format(message))
        datajson = dataa.json()
        # print(datajson)
        try:
            message = datajson['result']['intents'][0]['result']['text'].replace('海知工程师', 'xzy')
            if '哈哈，说话跟绕口令似的~ 好长好长呀' not in message and '啊呀，你慢点说慢点说，太长了我记不住啦' not in message and '你喝口水再继续说嘛，我有点儿跟不上呢' not in message and '问题太长啦，我不得不插嘴啦~' not in message:
                if random.randint(0,5) == 3:
                    self.send("[CQ:tts,text='"+str(message)+"']")
                else:
                    self.send(message)
        except Exception as e:
            pass
    
    # 注意！本函数需要使用 imageutils
    def sendImage(self):
        userid = self.se.get('user_id')
        name = self.se.get('sender').get('nickname')
        texts = self.message
        
        def load_image(path: str):
            return BuildImage.open(path("resources/images/" + path)).convert("RGBA")
        
        # 获取头像
        url = "http://q1.qlogo.cn/g?b=qq&nk="+str(userid)+"&s=640"
        image_bytes = urlopen(url).read()
        # internal data file
        data_stream = BytesIO(image_bytes)
        # open as a PIL image object
        #以一个PIL图像对象打开
        img = BuildImage.open(data_stream).convert("RGBA").square().circle().resize((100, 100))
    
        name_img = Text2Image.from_text(name, 25, fill="#868894").to_image()
        name_w, name_h = name_img.size
        if name_w >= 700:
            raise ValueError("名字太长啦！")
    
        corner1 = load_image("my_friend/corner1.png")
        corner2 = load_image("my_friend/corner2.png")
        corner3 = load_image("my_friend/corner3.png")
        corner4 = load_image("my_friend/corner4.png")
        label = load_image("my_friend/label.png")
    
        def make_dialog(text: str) -> BuildImage:
            text_img = Text2Image.from_text(text, 40).wrap(700).to_image()
            text_w, text_h = text_img.size
            box_w = max(text_w, name_w + 15) + 140
            box_h = max(text_h + 103, 150)
            box = BuildImage.new("RGBA", (box_w, box_h))
            box.paste(corner1, (0, 0))
            box.paste(corner2, (0, box_h - 75))
            box.paste(corner3, (text_w + 70, 0))
            box.paste(corner4, (text_w + 70, box_h - 75))
            box.paste(BuildImage.new("RGBA", (text_w, box_h - 40), "white"), (70, 20))
            box.paste(BuildImage.new("RGBA", (text_w + 88, box_h - 150), "white"), (27, 75))
            box.paste(text_img, (70, 16 + (box_h - 40 - text_h) // 2), alpha=True)
        
            dialog = BuildImage.new("RGBA", (box.width + 130, box.height + 60), "#eaedf4")
            dialog.paste(img, (20, 20), alpha=True)
            dialog.paste(box, (130, 60), alpha=True)
            dialog.paste(label, (160, 25))
            dialog.paste(name_img, (260, 22 + (35 - name_h) // 2), alpha=True)
            return dialog
        dialogs = [make_dialog(texts)]
        frame_w = max((dialog.width for dialog in dialogs))
        frame_h = sum((dialog.height for dialog in dialogs))
        frame = BuildImage.new("RGBA", (frame_w, frame_h), "#eaedf4")
        current_h = 0
        for dialog in dialogs:
            frame.paste(dialog, (0, current_h))
            current_h += dialog.height
        self.sendRawMessage('[CQ:image,file=https://resourcesqqbot.xzy.center/createimg/{0}]'.format(frame.save_jpg()))
    
    def chushihuacd(self):
        for i in commandlist:
            if self.findObject1(i.get('mode')) == -1 and i.get('isHide') != 1:
                if '.' in i.get('eval'):
                    cwd = i.get('eval').split('.')[0]
                else:
                    cwd = ''
                self.commandmode.append({'name':i.get('mode'),'cwd':cwd})
    
    def cd3(self):
        uid = self.se.get('user_id')
        gid = self.se.get('group_id')
        mode = self.message
        
        message = '[CQ:face,id=151]{0}-菜单：[|{1}|]'.format(self.botSettings.get('name'), mode)
        for i in commandlist:
            if i.get('promise') != 'xzy' and i.get('mode') == mode:
                if i.get('isHide') == 0:
                    message += '\n[CQ:face,id=54] [|'+str(i.get('content'))+'|]\n用法：[|'+str(i.get('usage'))+'|]\n解释：'+str(i.get('description'))+'\n权限：'
                    if i.get('promise') == 'admin' or i.get('promise') == 'ao':
                        message += '管理员'
                    elif i.get('promise') == 'owner':
                        message += '我的主人'
                    elif i.get('promise') == 'anyone':
                        message += '任何人'
                    elif i.get('promise') == 'ro':
                        message += '真正的主人'
                elif i.get('isHide') == 2:
                    message += '\n[CQ:face,id=54] [|'+str(i.get('usage'))+'|]'
        message += '\n\n[ {0} POWERED BY PIGBOTFRAMEWORK ]'.format(self.botSettings.get('name'))
            
        self.send(message)

    def KeywordExcept(self, replyKey, message):
        if ('$1' in replyKey) and ('$2' in replyKey):
            replyKey = replyKey.split('$1')[1]
            replyKey = replyKey.split('$2')[0]
            if ',' in replyKey:
                replyKey = replyKey.split(',')
                for i in replyKey:
                    if i in message:
                        return 1
            elif replyKey in message:
                return 1
        else:
            return 0
    
    def KeywordReplace(self, replyContent):
        uid = self.se.get('user_id')
        gid = self.se.get('group_id')
        se = self.se
        coin = self.userCoin
        
        if coin == -1:
            coin = '用户未注册！'
        for i in self.kwrlist:
            if i.get('key') in replyContent:
                replyContent = replyContent.replace(i.get('key'), str(eval(i.get('value'))))
        return replyContent
    
    def KeywordOr(self, replyKey, message):
        if '|' in replyKey:
            splitKey = replyKey.split('|')
            for sk in splitKey:
                if sk in message:
                    return 1
                elif '&amp;' in sk:
                    if self.KeywordAnd(sk, message):
                        return 1
            return 0
        elif '&amp;' in replyKey:
            return self.KeywordAnd(replyKey, message)
        else:
            return 0
    
    def KeywordAnd(self, replyKey, message):
        if '&amp;' in replyKey:
            msgandflag = 0
            msgand = replyKey.split('&amp;')
            for msgandi in msgand:
                if msgandi not in message:
                    return 0
            return 1
        else:
            return 0
    
    def sendKeyword(self, replyContent):
        uid = self.se.get('user_id')
        gid = self.se.get('group_id')
        se = self.se
        coin = self.userCoin
        
        replyContent = self.KeywordReplace(replyContent)
        if ('|' in replyContent) and ('|]' not in replyContent) and ('[|' not in replyContent):
            replyContentList = replyContent.split('|')
            for rcl in replyContentList:
                self.send(rcl)
        else:
            self.send(replyContent)
    
    def translator(self, text, from_lang="zh", to_lang="en"):
        if from_lang == to_lang or not text.lstrip().rstrip():
            return text
        self.CrashReport("from_lang: {0}\tto_lang: {1}\ntext: {2}".format(from_lang, to_lang, text), "translator")
        try:
            return googleTranslatorIns.translate(text, dest=to_lang).text
        except Exception:
            return text
    
    def execPluginThread(self, func):
        twrv = threading.Thread(target=self.execPlugin,args=(func,))
        twrv.start()
    
    def execPlugin(self, func):
        exec('from {0}.main import {0} as {0}'.format(func.split('.')[0]))
        loc = locals()
        exec('{0}Cla = {0}()'.format(func.split('.')[0]))
        for i in dir(self):
            if i[0:2] != '__' and callable(eval('self.'+str(i))) == False:
                exec('{1}Cla.{0} = self.{0}'.format(i, func.split('.')[0]))
        exec('{0}Cla.runningProgram = "{0}"'.format(func.split('.')[0]))
        exec('resData = {0}Cla.{1}'.format(func.split('.')[0], func.split('.')[1]))
        return loc['resData']
        
    def checkPromiseAndRun(self, i, echoFlag=False, senderFlag=False):
        uid = self.se.get('user_id')
        gid = self.se.get('group_id')
        se = self.se
        botSettings = self.botSettings
        evalFunc = i.get('eval')
        
        if gid:
            commandCustom = self.selectx('SELECT * FROM `botPromise` WHERE `uuid`="{0}" and `gid`={1} and `command`="{2}"'.format(self.uuid, gid, i.get('content').lstrip(' ')))
        else:
            commandCustom = None
        if commandCustom:
            promise = commandCustom[0].get('promise')
        else:
            promise = i.get('promise')
        
        if promise == 'anyone':
            return self.execPluginThread(evalFunc)
        elif promise == 'owner':
            if uid == botSettings.get('owner') or uid == botSettings.get('second_owner'):
                return self.execPluginThread(evalFunc)
            elif echoFlag == True:
                self.send('[CQ:face,id=151] 你不是我的主人，哼ꉂ(ˊᗜˋ*)')
        elif promise == 'ro':
            if uid == botSettings.get('owner'):
                return self.execPluginThread(evalFunc)
            elif echoFlag == True:
                self.send('[CQ:face,id=151] 你不是我真正的主人，哼ꉂ(ˊᗜˋ*)')
        
        if senderFlag == True:
            if promise == 'admin':
                if se.get('sender').get('role') != 'member':
                    return self.execPluginThread(evalFunc)
                elif echoFlag == True:
                    self.send('[CQ:face,id=151] 就你？先拿到管理员再说吧！')
            elif promise == 'ao':
                if se.get('sender').get('role') != 'member' or uid == botSettings.get('owner') or uid == botSettings.get('second_owner'):
                    return self.execPluginThread(evalFunc)
                elif echoFlag == True:
                    self.send('[CQ:face,id=151] 就你？先拿到管理员再说吧！')
    
    def start(self):
        userCoin = self.userCoin
        se = self.se
        gid = se.get('group_id')
        cid = se.get('channel_id')
        uid = se.get('user_id')
        message = se.get('message')
        settings = self.groupSettings
        uuid = self.uuid
        botSettings = self.botSettings
            
        if se.get('post_type') == 'notice':
            # 群通知
            for i in noticeListenerList:
                self.checkPromiseAndRun(i)
        
        elif se.get('post_type') == 'request':
            # 请求
            for i in requestListenerList:
                self.checkPromiseAndRun(i)
        
        elif se.get('post_type') == 'meta_event':
            for i in metaEventListenerList:
                self.checkPromiseAndRun(i)
        
        elif se.get('channel_id') == None and gid != None:
            for i in messageListenerList:
                self.checkPromiseAndRun(i)
                
            # 以下是还未来得及移走的
            # 上报消息
            # reportMessage(se)
            
            # 防刷屏
            mlob = self.findObject('qn', gid, messagelist)
            mlo = mlob.get('object')
            if mlo == 404:
                messagelist.append({'qn':gid, 'uid':uid, 'times':1})
            else:
                arrnum = mlob.get('num')
                if mlo.get('uid') == uid:
                    if mlo.get('times') >= int(settings.get('AntiswipeScreen')):
                        messagelist[arrnum]['times'] = 1
                        if se.get('sender').get('role') == "member":
                            datajson = self.CallApi('set_group_ban', {"group_id":gid,"user_id":uid,"duration":600})
                            if datajson['status'] != 'ok':
                                self.send('[CQ:face,id=151] 检测到刷屏，但禁言失败！')
                            else:
                                self.send('[CQ:face,id=54] 检测到刷屏，已禁言！')
                    else:
                        messagelist[arrnum]['times'] += 1
                    # 禁言警告
                    if mlo.get('times') == int(settings.get('AntiswipeScreen'))-1 and se.get('sender').get('role') == "member":
                        self.send('刷屏禁言警告！\n请不要连续发消息超过设定数量！')
                else:
                    messagelist[arrnum]['times'] = 1
                    messagelist[arrnum]['uid'] = uid
            
            # 功能函数
            self.bot()
        
        else:
            for i in messageListenerList:
                self.checkPromiseAndRun(i)
            
            self.bot()
        
        return 'OK'
    
    def keywordPair(self, replyKey, message):
        if self.KeywordExcept(replyKey, message):
            return False
        if ('$1' in replyKey) and ('$2' in replyKey):
            replyKey = replyKey.split('$1')[0] + replyKey.split('$2')[1]
        if self.KeywordOr(replyKey, message) or replyKey in message:
            return True
        return False
    
    def bot(self):
        global commandPluginsList
        userCoin = self.userCoin if self.userCoin else -1
        se = self.se
        gid = se.get('group_id')
        cid = se.get('channel_id')
        uid = se.get('user_id')
        message = se.get('message')
        settings = self.groupSettings
        uuid = self.uuid
        botSettings = self.botSettings
        
        if uid != botSettings.get('owner') and se.get('channel_id') == None and gid == None and botSettings.get("reportPrivate"):
            self.SendOld(botSettings.get('owner'), '[CQ:face,id=151] 主人，有人跟我说话话\n内容：'+str(message)+'\n回复请对我说：\n\n回复|'+str(se.get('user_id'))+'|'+str(se.get('message_id'))+'|<回复内容>')
            if uid != botSettings.get('second_owner'):
                self.SendOld(botSettings.get('second_owner'), '[CQ:face,id=151] 副主人，有人跟我说话话\n内容：'+str(message)+'\n回复请对我说：\n\n回复|'+str(se.get('user_id'))+'|'+str(se.get('message_id'))+'|<回复内容>')
                # self.send('请尽量在群中使用机器人，否则因为风控，机器人可能无法向你发送消息')
        
        if '[CQ:at,qq='+str(botSettings.get('owner'))+']' in message and botSettings.get("reportAt"):
            self.SendOld(botSettings.get('owner'), '[CQ:face,id=151] 主人，有人艾特你awa\n消息内容：'+str(message)+'\n来自群：'+str(gid)+'\n来自用户：'+str(uid))
            
        if '[CQ:at,qq='+str(botSettings.get('second_owner'))+']' in message and botSettings.get("reportAt"):
            self.SendOld(botSettings.get('second_owner'), '[CQ:face,id=151]副主人，有人艾特你awa\n消息内容：'+str(message)+'\n来自群：'+str(gid)+'\n来自用户：'+str(uid))
        
        if ('[CQ:at,qq='+str(botSettings.get('myselfqn'))+']' in message) and (userCoin == -1):
            self.send('[CQ:reply,id='+str(se.get('message_id'))+'] '+str(botSettings.get('name'))+'想起来你还没有注册哦~\n发送“注册”可以让机器人认识你啦QAQ')
        
        if '[CQ:image,' in message:
            try:
                dataa = self.CallApi('ocr_image', {'image':self.getCQValue('file', message)})
                message = ' '
                datajson = dataa.get('data').get('texts')
                for i in datajson:
                    message += i.get('text')
                # CrashReport(message, '图片OCR内容')
            except Exception as e:
                pass
        
        try:
            if gid != None:
                if settings.get('increase_verify') != 0:
                    if self.execPlugin('basic.getVerifyStatus()') == True and '人机验证 ' not in message:
                        self.CallApi('delete_msg', {'message_id':self.se.get('message_id')})
        except Exception as e:
            self.CrashReport(settings, e)
            pass
        
        # 指令监听器
        self.rclOb = self.ReadCommandListener()
        if self.rclOb != 404:
            if message == '退出':
                self.RemoveCommandListener()
                return self.send('退出！')
            else:
                self.execPlugin(self.rclOb.get('func'))
                return True
        # 指令
        atStr = '[CQ:at,qq='+str(botSettings.get('myselfqn'))+'] '
        if message[0:len(atStr)] == atStr:
            message = message.replace(atStr, '', 1)
        
        for l in self.pluginsList:
            if commandPluginsList.get(l.get('path')) == None:
                continue
            for i in commandPluginsList.get(l.get('path')):
                # 识别指令
                lengthmx = len(i.get('content'))
                if self.message[0:lengthmx] == i.get('content'):
                    # 提示<>
                    for args in self.args:
                        if '>' in args or '<' in args:
                            self.send('温馨提示，指令列表中的<>符号请忽略！')
                            break
                    self.message = self.message.replace(i.get('content'), '', 1).replace('  ', ' ').lstrip(' ')
                    self.ocrImage = message
                    self.se['message'] = self.message
                    self.checkPromiseAndRun(i, True, True)
                    return 
                # 检测
                if self.message[0:3] == "/风车":
                    self.send("请注意“/风车”是一个表情，而不是指令的一部分！")
                # 检测
                lengthmx = len(i.get('content').lstrip().rstrip())
                if self.message[0:lengthmx] == i.get('content').lstrip().rstrip():
                    self.send("请注意指令每一部分之间有一个空格！！！")
        
        if self.message[0:10] == '[CQ:reply,' and '撤回' in message:
            if uid == botSettings.get('owner') or uid == botSettings.get('second_owner') or se.get('sender').get('role') != 'member':
                self.CallApi('delete_msg', {'message_id':self.getCQValue('id', message)})
                self.CallApi('delete_msg', {'message_id':self.se.get('message_id')})
                return 
            else:
                self.send('[CQ:face,id=151] 就你？先拿到管理员再说吧！')
        
        # 违禁词检查
        if settings != None:
            weijinFlag = 1 if settings.get('weijinCheck') else 0
        else:
            weijinFlag = 1
        if self.checkWeijin(weijinFlag) == True:
            return 'OK.'
        
        # 关键词回复
        if settings != None:
            kwFlag = 1 if settings.get('keywordReply') else 0
        else:
            kwFlag = 1
        if kwFlag:
            keywordlist = self.selectx(self.sql_keywordListSql.format(uuid))
            for i in keywordlist:
                replyFlag = False
                if userCoin >= i.get('coin') and (i.get("qn") == 0 or gid == i.get("qn")):
                    replyFlag = True
                if replyFlag == True:
                    replyKey = self.KeywordReplace(i.get('key'))
                    if self.keywordPair(replyKey, message):
                        self.sendKeyword(i.get('value'))
        
        # 分类菜单
        if len(self.commandmode) == 0:
            self.chushihuacd()
        
        for i in self.commandmode:
            if message == i.get('name'):
                self.cd3()
        
        replyFlag = True
        randnum = random.randint(0, int(settings.get("MC_random")))
        if randnum == 3:
            if self.execPlugin("mc.mobsComing()"):
                replyFlag = False
        elif randnum == 4:
            if self.execPlugin("mc.save()"):
                replyFlag = False
        if replyFlag:
            # 回复  
            if gid != None or cid != None:
                if gid != None:
                    randnum = settings.get('replyPercent')
                elif cid != None:
                    randnum = 100
                rand = random.randint(1, randnum)
                if (rand == 1) or ('[CQ:at,qq='+str(botSettings.get('myselfqn'))+']' in message):
                    self.message = self.se['message'] = self.message.replace('[CQ:at,qq='+str(botSettings.get('myselfqn'))+']', "")
                    self.reply()
            else:
                self.reply()
