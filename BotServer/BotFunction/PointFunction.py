from BotServer.BotFunction.InterfaceFunction import *
from ApiServer.ApiMainServer import ApiMainServer
from BotServer.BotFunction.JudgeFuncion import *
from DbServer.DbMainServer import DbMainServer
import Config.ConfigServer as Cs


class PointFunction:
    def __init__(self, wcf):
        """
        积分功能
        :param wcf:
        """
        self.wcf = wcf
        self.Ams = ApiMainServer()
        self.Dms = DbMainServer()
        configData = Cs.returnConfigData()
        self.aiWenKeyWords = configData['functionKeyWord']['aiWenWord']
        self.md5KeyWords = configData['functionKeyWord']['md5Words']
        self.signKeyWord = configData['pointConfig']['sign']['word']
        self.aiPicKeyWords = configData['functionKeyWord']['aiPic']
        self.searchPointKeyWord = configData['pointConfig']['queryPointWord']

    def mainHandle(self, message):
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        atUserLists, noAtMsg = getAtData(self.wcf, message)
        if msgType == 1:
            # 埃文IPV4地址查询
            if judgeSplitAllEqualWord(content, self.aiWenKeyWords):
                ip = content.split(' ')[-1]
                aiWenData = self.Ams.getAiWen(ip)
                if not aiWenData:
                    self.wcf.send_text(
                        f'@{getIdName(self.wcf, sender, roomId)} 埃文IP地址查询接口出现错误, 请联系超管查看控制台输出日志',
                        receiver=roomId, aters=sender)
                    return
                mapsPaths = aiWenData['maps']
                for mapsPath in mapsPaths:
                    self.wcf.send_image(mapsPath, receiver=roomId)
                aiWenMessage = aiWenData['message']
                self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)} 查询结果如下\n{aiWenMessage}',
                                   receiver=roomId, aters=sender)

            # CMD5查询
            # elif judgeSplitAllEqualWord(content, self.md5KeyWords):
            #     ciphertext = content.split(' ')[-1]
            #     plaintext = self.Ams.getCmd5(ciphertext)
            #     if not plaintext:
            #         self.wcf.send_text(
            #             f'@{getIdName(self.wcf, sender, roomId)} MD5解密接口出现错误, 请联系超管查看控制台输出日志',
            #             receiver=roomId, aters=sender)
            #         return
            #     self.wcf.send_text(
            #         f'@{getIdName(self.wcf, sender, roomId)}\n密文: {ciphertext}\n明文: {plaintext}',
            #         receiver=roomId,
            #         aters=sender)
            # 签到口令提示
            # elif judgeEqualWord(content, '签到'):
            #     self.wcf.send_text(
            #         f'@{getIdName(self.wcf, sender, roomId)} 签到失败\n签到口令已改为：{self.signKeyWord}',
            #         receiver=roomId, aters=sender)
            # # 签到
            # elif judgeEqualWord(content, self.signKeyWord):
            #     if not self.Dms.sign(wxId=sender, roomId=roomId):
            #         self.wcf.send_text(
            #             f'@{getIdName(self.wcf, sender, roomId)} 签到失败, 当日已签到！！！\n当前剩余积分: {self.Dms.searchPoint(sender, roomId)}',
            #             receiver=roomId, aters=sender)
            #         return
            #     self.wcf.send_text(
            #         f'@{getIdName(self.wcf, sender, roomId)} 签到成功, 当前剩余积分: {self.Dms.searchPoint(sender, roomId)}',
            #         receiver=roomId, aters=sender)
            # 查询积分
            # elif judgeEqualListWord(content, self.searchPointKeyWord):
            #     userPoint = self.Dms.searchPoint(sender, roomId)
            #     if userPoint == False and not userPoint == 0:
            #         self.wcf.send_text(
            #             f'@{getIdName(self.wcf, sender, roomId)} 积分查询出现错误, 请联系超管查看控制台输出日志',
            #             receiver=roomId, aters=sender)
            #         return
            #     self.wcf.send_text(
            #         f'@{getIdName(self.wcf, sender, roomId)} 当前剩余积分: {self.Dms.searchPoint(sender, roomId)}',
            #         receiver=roomId, aters=sender)
            # Ai对话
            elif judgeAtMe(self.wcf.self_wxid, content, atUserLists) and not judgeOneEqualListWord(noAtMsg,
                                                                                                   self.aiPicKeyWords):
                aiMsg = self.Ams.getAi(noAtMsg)
                if aiMsg:
                    self.wcf.send_text(f'@{getIdName(self.wcf, sender, roomId)} {aiMsg}',
                                       receiver=roomId, aters=sender)
                    return
                self.wcf.send_text(
                    f'@{getIdName(self.wcf, sender, roomId)} Ai对话接口出现错误, 请联系超管查看控制台输出日志',
                    receiver=roomId, aters=sender)
            # Ai画图
            elif judgeSplitAllEqualWord(content, self.aiPicKeyWords):
                aiPicPath = self.Ams.getAiPic(content.split(' ')[-1])
                if aiPicPath:
                    self.wcf.send_image(path=aiPicPath, receiver=roomId)
                    return
                self.wcf.send_text(
                    f'@{getIdName(self.wcf, sender, roomId)} Ai画图接口出现错误, 请联系超管查看控制台输出日志',
                    receiver=roomId, aters=sender)
