from BotServer.BotFunction.InterfaceFunction import *
from ApiServer.ApiMainServer import ApiMainServer
from BotServer.BotFunction.JudgeFuncion import *
import Config.ConfigServer as Cs
import re


class HappyFunction:
    def __init__(self, wcf):
        """
        娱乐功能
        :param wcf:
        """
        self.wcf = wcf
        self.Ams = ApiMainServer()
        configData = Cs.returnConfigData()
        self.picKeyWords = configData['functionKeyWord']['picWord']
        self.videoKeyWords = configData['functionKeyWord']['videoWord']
        self.fishKeyWords = configData['functionKeyWord']['fishWord']
        self.kfcKeyWords = configData['functionKeyWord']['kfcWord']
        self.dogKeyWords = configData['functionKeyWord']['dogWord']
        # 段子触发关键词
        self.duanziKeyWords = configData['functionKeyWord']['duanziWord']
        # 股票触发关键词
        self.stockKeyWords = configData['functionKeyWord']['stockWord']
        self.shortPlayWords = configData['functionKeyWord']['shortPlayWords']
        self.morningPageKeyWords = configData['functionKeyWord']['morningPageWord']
        self.eveningPageKeyWords = configData['functionKeyWord']['eveningPageWord']
        self.helpKeyWords = configData['functionKeyWord']['helpMenu']
        self.emoHelpKeyWords = configData['emoConfig']['emoHelp']
        self.emoKeyWords = configData['emoConfig']['emoKeyWord']
        self.emoOneKeyWordsData = configData['emoConfig']['onePicEmo']
        self.emoTwoKeyWordsData = configData['emoConfig']['twoPicEwo']
        self.emoRandomKeyWords = configData['emoConfig']['emoRandomKeyWord']
        self.taLuoWords = configData['functionKeyWord']['taLuoWords']
        self.musicWords = configData['functionKeyWord']['musicWords']
        # 自定义回复关键词字典
        self.customKeyWords = configData['customKeyWord']


    def mainHandle(self, message):
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        atUserLists, noAtMsg = getAtData(self.wcf, message)
        senderName = self.wcf.get_alias_in_chatroom(sender, roomId)
        avatarPathList = []
        if msgType == 1:
            # 美女图片
            if judgeEqualListWord(content, self.picKeyWords):
                picPath = self.Ams.getGirlPic()
                if not picPath:
                    self.wcf.send_text(
                        f'@{senderName} 美女图片接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_image(picPath, receiver=roomId)
            # 美女视频
            elif judgeEqualListWord(content, self.videoKeyWords):
                videoPath = self.Ams.getGirlVideo()
                if not videoPath:
                    self.wcf.send_text(
                        f'@{senderName} 美女视频接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_file(videoPath, receiver=roomId)

            # 摸鱼日历
            elif judgeEqualListWord(content, self.fishKeyWords):
                fishPath = self.Ams.getFish()
                if not fishPath:
                    self.wcf.send_text(
                        f'@{senderName} 摸鱼日历接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_file(fishPath, receiver=roomId)

            # 疯狂星期四
            elif judgeEqualListWord(content, self.kfcKeyWords):
                kfcText = self.Ams.getKfc()
                if not kfcText:
                    self.wcf.send_text(
                        f'@{senderName} KFC疯狂星期四接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{senderName} {kfcText}',
                    receiver=roomId, aters=sender)

            # 段子
            elif judgeEqualListWord(content, self.duanziKeyWords):
                duanziText = self.Ams.getDuanZi()
                if not duanziText:
                    self.wcf.send_text(
                        f'@{senderName} 段子接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{senderName} {duanziText}',
                    receiver=roomId, aters=sender)
            
            # 股票
            elif any(kw in content for kw in self.stockKeyWords):
                # 正则提取股票代码
                match = re.match(r'股票[\s　]*(?P<symbol>\w+)', content, flags=re.UNICODE)
                
                if not match:
                    self.wcf.send_text(f'@{senderName} 格式错误，正确示例：股票 QQQ', receiver=roomId, aters=sender)
                    return
                
                symbol = match.group('symbol').upper()  # 统一转为大写
                op(f'[DEBUG] 识别到股票代码: {symbol}')  # 日志记录
                
                stock_info = self.Ams.getStock(symbol)
                
                if stock_info:
                    response = f'@{senderName} 💰最新行情\n{stock_info}'
                else:
                    response = f'@{senderName} 查询失败，可能原因：\n1.非交易时段\n2.代码无效\n3.系统限流'
                    
                self.wcf.send_text(response, receiver=roomId, aters=sender)
            
            # 舔狗日记
            elif judgeEqualListWord(content, self.dogKeyWords):
                dogText = self.Ams.getDog()
                if not dogText:
                    self.wcf.send_text(
                        f'@{senderName} 舔狗日记接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{senderName} {dogText}',
                    receiver=roomId, aters=sender)
            # 早报
            elif judgeEqualListWord(content, self.morningPageKeyWords):
                morningPage = self.Ams.getMorningNews()
                if not morningPage:
                    self.wcf.send_text(
                        f'@{senderName} 早报接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(morningPage, receiver=roomId)
            # 晚报
            elif judgeEqualListWord(content, self.eveningPageKeyWords):
                eveningPage = self.Ams.getEveningNews()
                if not eveningPage:
                    self.wcf.send_text(
                        f'@{senderName} 晚报接口出现错误, 请联系超管查看控制台输出日志 ~~~',
                        receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(eveningPage, receiver=roomId)
            # 短剧搜索
            elif judgeSplitAllEqualWord(content, self.shortPlayWords):
                playName = content.split(' ')[-1]
                content = self.Ams.getShortPlay(playName)
                if content:
                    self.wcf.send_text(f'@{senderName}\n{content}', receiver=roomId, aters=sender)
            # 抖音视频解析
            elif judgeInWord(content, '复制打开抖音'):
                videoPath = self.Ams.getVideoAnalysis(content)
                if videoPath:
                    self.wcf.send_file(path=videoPath, receiver=roomId)
            # 点歌
            elif judgeSplitAllEqualWord(content, self.musicWords):
                musicName = content.split(' ')[-1]
                musicHexData = self.Ams.getMusic(musicName)
                if not musicHexData:
                    self.wcf.send_text(f'@{senderName} 点歌接口出现错误, 请稍后再试 ~~~', receiver=roomId, aters=sender)
                    return
                data = self.wcf.query_sql('MSG0.db', "SELECT * FROM MSG where type = 49  limit 1")
                self.wcf.query_sql('MSG0.db',
                                   f"UPDATE MSG SET  CompressContent = x'{musicHexData}', BytesExtra=x'',type=49,SubType=3,IsSender=0,TalkerId=2 WHERE MsgSvrID={data[0]['MsgSvrID']}")
                self.wcf.forward_msg(data[0]["MsgSvrID"], roomId)
            # 塔罗牌
            elif judgeEqualListWord(content, self.taLuoWords):
                content, picPath = self.Ams.getTaLuo()
                if content and picPath:
                    self.wcf.send_image(path=picPath, receiver=roomId)
                    self.wcf.send_text(f'@{senderName}\n\n{content}', receiver=roomId, aters=sender)
                else:
                    self.wcf.send_text(f'@{senderName}\n塔罗牌占卜接口出现错误, 请联系超管查看控制台输出 ~~~', receiver=roomId, aters=sender)

            # 随机表情
            elif judgeEqualListWord(content, self.emoRandomKeyWords):
                avatarPathList.append(getUserPicUrl(self.wcf, sender))
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情包功能 不@制作表情
            elif not atUserLists and judgeSplitAllEqualWord(content, self.emoKeyWords):
                avatarPathList.append(getUserPicUrl(self.wcf, sender))
                emoMeme = self.emoOneKeyWordsData.get(content.split(' ')[-1])
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList, emoMeme)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情包功能 @制作对方表情
            elif atUserLists and judgeSplitAllEqualWord(noAtMsg, self.emoKeyWords):
                for atUser in atUserLists:
                    avatarPathList.append(getUserPicUrl(self.wcf, atUser))
                    break
                emoMeme = self.emoOneKeyWordsData.get(noAtMsg.split(' ')[-1])
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList, emoMeme)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 表情包功能 @对方制作双人表情
            elif atUserLists and judgeEqualListWord(noAtMsg, self.emoTwoKeyWordsData.keys()):
                avatarPathList.append(getUserPicUrl(self.wcf, sender))
                avatarPathList.append(getUserPicUrl(self.wcf, atUserLists[0]))
                emoMeme = self.emoTwoKeyWordsData.get(noAtMsg.split(' ')[-1])
                emoPath, sizeBool = self.Ams.getEmoticon(avatarPathList, emoMeme)
                if not emoPath:
                    return
                if sizeBool:
                    self.wcf.send_emotion(path=emoPath, receiver=roomId)
                else:
                    self.wcf.send_image(path=emoPath, receiver=roomId)
            # 自定义回复
            elif judgeEqualListWord(content, self.customKeyWords.keys()):
                for keyWord in self.customKeyWords.keys():
                    if judgeEqualWord(content, keyWord):
                        replyMsgLists = self.customKeyWords.get(keyWord)
                        for replyMsg in replyMsgLists:
                            self.wcf.send_text(replyMsg, receiver=roomId)
            # 表情菜单
            elif judgeEqualListWord(content, self.emoHelpKeyWords):
                msg = '【单人表情】使用方法: \n表情 表情选项\n@某人 表情选项\n单人表情选项如下: \n'
                for oneEmoKey in self.emoOneKeyWordsData.keys():
                    msg += oneEmoKey + '\n'
                msg += '【双人表情】使用方法: \n表情选项@某人 \n双人表情选项如下\n'
                for twoEmoKey in self.emoTwoKeyWordsData.keys():
                    msg += twoEmoKey + '\n'
                self.wcf.send_text(f'@{senderName}\n{msg}', receiver=roomId, aters=sender)
            # 帮助菜单
            elif judgeEqualListWord(content, self.helpKeyWords):
                helpMsg = '[爱心]=== NGCBot菜单 ===[爱心]\n'
                helpMsg += '【一、积分功能】\n1.1、Ai画图(@机器人 画一张xxxx)\n1.2、Ai对话(@机器人即可)\n1.3、IP溯源(溯源 ip)\n1.4、IP威胁查询(ip查询 ip)\n1.5、CMD5查询(md5查询 xxx)\n1.6、签到(签到)\n1.7、积分查询(积分查询)\n\n'
                helpMsg += '【二、娱乐功能】\n2.1、美女图片(图片)\n2.2、美女视频(视频)\n2.3、摸鱼日历(摸鱼日历)\n2.4、舔狗日记(舔我)\n2.5、早报(早报)\n2.6、晚报(晚报)\n2.6、表情列表(表情列表)\n2.7、随机表情(随机表情, 有几率报错)\n'
                helpMsg += '[爱心]=== NGCBot菜单 ===[爱心]\n'
                self.wcf.send_text(f'@{senderName}\n{helpMsg}', receiver=roomId, aters=sender)
        elif msgType == 49:
            # 视频号解析
            objectId, objectNonceId = getWechatVideoData(content)
            if objectId and objectNonceId:
                msg = self.Ams.getWechatVideo(objectId, objectNonceId)
                if msg:
                    self.wcf.send_text(f'@{senderName}\n{msg}', receiver=roomId, aters=sender)

