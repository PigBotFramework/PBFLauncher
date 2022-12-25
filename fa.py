from fastapi import FastAPI, Header, Request
from typing import Union
from path import path
import uvicorn, traceback, time, requests, sys, os, json
from bot import bot, varsInit
from urllib.request import urlopen
# 解决“Max retries exceeded with url”问题
s = requests.session()
s.keep_alive = False
requests.adapters.DEFAULT_RETRIES = 5
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}

description = '''
> PigBotFramework is built on FastApi, all APIs are listed below and provide query parameters  
**Notice: 以下接口默认使用1000处理器，其他处理器用法相同**
'''
app = FastAPI(
    title="PigBotFramework API",
    description=description,
    version="4.1.0",
    contact={
        "name": "xzyStudio",
        "url": "https://xzy.center",
        "email": "gingmzmzx@gmail.com",
    },
)

@app.post("/")
async def post_data(request: Request, X_Signature: Union[str, None] = Header(default=None)):
    """机器人事件上报接口"""
    try:
        # botIns.CrashReport("New post data", "FastApi")
        # sha1校验防伪上报
        params = request.query_params
        botIns.CrashReport(params.get("uuid"), "uuis")
        botPswd = botIns.GetPswd(params.get("uuid"))
        if botPswd == params.get("pswd"):
            sig = 1
            received_sig = 1
        else:
            sig = botIns.encryption(await request.body(), botPswd)
            received_sig = X_Signature[len('sha1='):] if X_Signature else False
        if sig == received_sig:
            se = await request.json()
            bot().requestInit(se, params.get("uuid"))
        else:
            return {"code":403}
    except Exception as e:
        return traceback.format_exc()

@app.post("/status")
@app.get("/status")
async def webstatus():
    """获取处理器状态"""
    return json.dumps({"code":200}, ensure_ascii=False)

@app.get("/overview")
@app.post("/overview")
async def weboverview(uuid:str):
    """获取机器人GOCQ数据概览"""
    try:
        botSettings = botIns.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid))[0]
        
        # 尝试请求gocq获取gocq信息
        try:
            gocq = CallApi("get_version_info", {}, ob=botSettings, timeout=5).get("data")
            if gocq.get('app_name') != "go-cqhttp":
                return str(json.dumps({'code':502}))
        except Exception as e:
            print(e)
            return str(json.dumps({'code':502}))
        
        data = {'code':200,'go-cqhttp':gocq,'time':time.time()}
        # 获取各项数据
        # 1. 群聊列表
        groupList = CallApi('get_group_list', {}, ob=botSettings).get('data')
        data['groupCount'] = len(groupList)
        # 2. 好友列表
        friendList = CallApi('get_friend_list', {}, ob=botSettings).get('data')
        data['friendCount'] = len(friendList)
        # 3. 网络信息
        network = CallApi('get_status', {}, ob=botSettings).get('data')
        data['network'] = network.get('stat')
        
        return json.dumps(data)
    except Exception as e:
        return traceback.format_exc()
    
@app.get("/getFriendAndGroupList")
async def webgetFriendAndGroupList(pswd:str, uuid:str):
    """获取机器人好友和群聊列表"""
    try:
        if pswd == botIns.GetPswd(uuid):
            groupList = CallApi('get_group_list', {}, uuid).get('data')
            friendList = CallApi('get_friend_list', {}, uuid).get('data')
            return json.dumps({'friendList':friendList,'groupList':groupList})
        else:
            return 'Password error.'
    except Exception as e:
        return traceback.format_exc()

@app.get("/getFriendList")
async def webgetFriendList(pswd:str, uuid:str):
    """获取机器人好友列表"""
    if pswd == botIns.GetPswd(uuid):
        return json.dumps(CallApi('get_friend_list', {}, uuid).get('data'))
    else:
        return 'Password error.'

@app.get("/kickUser")
async def webkickUser(pswd:str, uuid:str, gid:int, uid:int):
    """踢出某人"""
    if pswd == botIns.GetPswd(uuid):
        data = CallApi('set_group_kick', {'group_id':gid,'user_id':uid}, uuid)
        if data['status'] == 'ok':
            return 'OK.'
        else:
            return 'failed.'
    else:
        return 'Password error.'

@app.get("/banUser")
async def webBanUser(pswd:str, uuid:str, uid:int, gid:int, duration:int):
    """禁言某人"""
    if pswd == botIns.GetPswd(uuid):
        CallApi('set_group_ban', {'group_id':gid,'user_id':uid,'duration':duration}, uuid)
        return 'OK.'
    else:
        return 'Password error.'

@app.get("/delete_msg")
async def webDeleteMsg(pswd:str, uuid:str, message_id:str):
    """撤回消息"""
    if pswd == botIns.GetPswd(uuid):
        CallApi('delete_msg', {'message_id':message_id}, uuid)
        # commonx('DELETE FROM `botChat` WHERE `mid`="{0}"'.format(mid))
        return 'OK.'
    else:
        return 'Password error.'

@app.get("/getGroupHistory")
async def webGetGroupHistory(uuid:str, group_id:int):
    """获取群聊聊天记录"""
    try:
        return json.dumps(CallApi('get_group_msg_history', {'group_id':group_id}, uuid))
    except Exception as e:
        return traceback.format_exc()

@app.get("/sendMessage")
async def webSendMessage(pswd:str, uuid:str, uid:int, gid:int, message:str):
    """发送消息"""
    if pswd == botIns.GetPswd(uuid):
        SendOld(uuid, uid, message, gid)
        return 'OK.'
    else:
        return 'Password error.'

@app.get("/getGroupList")
async def getGroupList(uuid:str):
    """获取某机器人群聊列表"""
    return json.dumps(CallApi('get_group_list', {}, uuid))

@app.get("/MCServer")
async def MCServer(msg:str, uuid:str, qn:int):
    """MC服务器消息同步"""
    print('服务器消息：')
    msg = msg[2:-1]
    
    if msg != '' and '[Server] <' not in msg:
        msg = '[CQ:face,id=151] 服务器消息：'+str(msg)
        if 'logged in with entityid' in msg:
            msg1 = msg[0:msg.find('logged in with entityid')-1]
            msg = msg1 + '进入了游戏'
        
        SendOld(uuid, None, msg, qn)
    
    return '200 OK.'

@app.get('/getGroupMemberList')
async def webGetGroupMemberList(uuid:str, gid:int):
    """获取群聊成员列表"""
    return json.dumps(CallApi('get_group_member_list', {'group_id':gid}, uuid))

@app.get('/getPluginsData')
async def webgetPluginsData():
    """刷新插件数据"""
    return json.dumps(pluginsData, ensure_ascii=False)

@app.get("/reloadPlugins")
async def webreloadPlugins():
    '''刷新插件及指令列表'''
    return reloadPlugins()

def reloadPlugins():
    global pluginsData, commandPluginsList, commandlist, noticeListenerList, requestListenerList, metaEventListenerList, messageListenerList
    commandlist = []
    pluginsData = []
    commandPluginsList = {}
    pluginsList = getPluginsList()
    
    # 引入
    for i in pluginsList:
        try:
            # 只能使用exec函数引入
            '''
            moduleName = 'plugins.{0}.main'.format(i)
            print(moduleName in sys.modules)
            if moduleName not in sys.modules:
                exec('import plugins.{0}.main as {0}'.format(i))
            '''
            
            # 加载json
            clist = json.loads(openFile(path('plugins/{0}/commands.json'.format(i))))
            if not commandPluginsList.get(i):
                commandPluginsList[i] = []
            commandPluginsList[i] += clist
            for l in clist:
                if l.get('type') == "command":
                    commandlist.append(l)
                elif l.get('type') == "message":
                    messageListenerList.append(l)
                elif l.get('type') == "notice":
                    noticeListenerList.append(l)
                elif l.get('type') == "request":
                    requestListenerList.append(l)
                elif l.get('type') == "meta_event":
                    metaEventListenerList.append(l)
                else:
                    # CrashReport(yamldata.get('self').get('defaultUuid'), '无效的指令TYPE：{0}'.format(i), '无效的指令TYPE')
                    pass
            
            clist = json.loads(openFile(path('plugins/{0}/data.json'.format(i))))
            clist['cwd'] = i
            pluginsData.append(clist)
        except Exception as e:
            msg = traceback.format_exc()
            # CrashReport('在引入插件 {0} 时遇到错误：\n{1}'.format(i, msg), '插件警告⚠', uuid=yamldata.get('self').get('defaultUuid'))
            print(msg)
            pluginsList.remove(i)
    
    varsInit(commandPluginsList, commandlist, messageListenerList, metaEventListenerList, requestListenerList, noticeListenerList, pluginsList)
    return json.dumps({"code":200}, ensure_ascii=False)

def getPluginsList():
    # 生成插件列表
    # global pluginsList
    pluginsList = os.listdir('plugins')
    for dbtype in pluginsList[::]:
        if os.path.isfile(os.path.join('plugins',dbtype)):
            pluginsList.remove(dbtype)
    return pluginsList

def openFile(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def CallApi(api, parms, uuid=None, httpurl=None, access_token=None, ob=None, timeout=10):
    if ob != None:
        httpurl = ob.get("httpurl")
        access_token = ob.get("secret")
    elif httpurl != None and access_token != None:
        pass
    elif uuid != None:
        ob = botIns.selectx('SELECT * FROM `botBotconfig` WHERE `uuid`="{0}";'.format(uuid))[0]
        httpurl = ob.get("httpurl")
        access_token = ob.get("secret")
    
    data = requests.post(url='{0}/{1}?access_token={2}'.format(httpurl, api, access_token), json=parms, timeout=timeout)
    return data.json()

def SendOld(uuid, uid, content, gid=None):
    if gid == None:
        dataa = CallApi('send_msg', {'user_id':uid,'message':content}, uuid)
    else:
        dataa = CallApi('send_msg', {'group_id':gid,'message':content}, uuid)
    if dataa.get('status') != 'failed':
        mid = dataa.get('data').get('message_id')
    else:
        mid = None
    return mid


# -------------------全局变量-----------------
commandListener = []
pluginsData = []
commandPluginsList = {}
messagelist = []
commandlist = []
messageListenerList = []
metaEventListenerList = []
requestListenerList = []
noticeListenerList = []
pluginsList = getPluginsList()
botIns = bot()
reloadPlugins()

# -------------------启动-----------------
def run(port, host):
    uvicorn.run(app="fa:app",  host=host, port=port)