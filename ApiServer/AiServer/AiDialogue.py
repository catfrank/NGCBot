from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from volcengine.visual.VisualService import VisualService
from sparkai.core.messages import ChatMessage
from tencentcloud.common import credential
import ApiServer.AiServer.sparkPicApi as sPa
import FileCache.FileCacheServer as Fcs
import Config.ConfigServer as Cs
from OutPut.outPut import op
from datetime import datetime
import requests
import base64
import time
import json


class AiDialogue:
    def __init__(self):

        configData = Cs.returnConfigData()
        self.systemAiRole = configData['apiServer']['aiConfig']['systemAiRule']
        self.openAiConfig = {'openAiApi': configData['apiServer']['aiConfig']['openAi']['openAiApi'],
                             'openAiKey': configData['apiServer']['aiConfig']['openAi']['openAiKey'],
                             'openAiModel': configData['apiServer']['aiConfig']['openAi']['openAiModel']
                             }
        self.sparkAiConfig = {'sparkAiApi': configData['apiServer']['aiConfig']['sparkApi']['sparkAiApi'],
                              'sparkAiAppid': configData['apiServer']['aiConfig']['sparkApi']['sparkAiAppid'],
                              'sparkAiSecret': configData['apiServer']['aiConfig']['sparkApi']['sparkAiSecret'],
                              'sparkAiKey': configData['apiServer']['aiConfig']['sparkApi']['sparkAiKey'],
                              'sparkDomain': configData['apiServer']['aiConfig']['sparkApi']['sparkDomain']
                              }
        self.qianfanAiConfig = {
            'qfAccessKey': configData['apiServer']['aiConfig']['qianFan']['qfAccessKey'],
            'qfSecretKey': configData['apiServer']['aiConfig']['qianFan']['qfSecretKey'],
            'qfAppid': configData['apiServer']['aiConfig']['qianFan']['qfAppid'],
            'qfPicAccessKey': configData['apiServer']['aiConfig']['qianFan']['qfPicAccessKey'],
            'qfPicSecretKey': configData['apiServer']['aiConfig']['qianFan']['qfPicSecretKey'],
            'qfPicAppid': configData['apiServer']['aiConfig']['qianFan']['qfPicAppid'],
        }
        self.hunYuanAiConfig = {
            'hunYuanSecretId': configData['apiServer']['aiConfig']['hunYuan']['hunYuanSecretId'],
            'hunYuanSecretKey': configData['apiServer']['aiConfig']['hunYuan']['hunYuanSecretKey'],
            'hunYuanModel': configData['apiServer']['aiConfig']['hunYuan']['hunYuanModel']
        }
        self.kiMiConfig = {
            'kiMiApi': configData['apiServer']['aiConfig']['kiMi']['kiMiApi'],
            'kiMiKey': configData['apiServer']['aiConfig']['kiMi']['kiMiKey'],
            'kiMiModel': configData['apiServer']['aiConfig']['kiMi']['kiMiModel']
        }
        self.bigModelConfig = {
            'bigModelApi': configData['apiServer']['aiConfig']['bigModel']['bigModelApi'],
            'bigModelKey': configData['apiServer']['aiConfig']['bigModel']['bigModelKey'],
            'bigModelModel': configData['apiServer']['aiConfig']['bigModel']['bigModelModel']
        }
        self.deepSeekConfig = {
            'deepSeekApi': configData['apiServer']['aiConfig']['deepSeek']['deepSeekApi'],
            'deepSeekKey': configData['apiServer']['aiConfig']['deepSeek']['deepSeekKey'],
            'deepSeekModel': configData['apiServer']['aiConfig']['deepSeek']['deepSeekModel']
        }
        self.localDeepSeekModelConfig = {
            'localDeepSeekApi': configData['apiServer']['aiConfig']['localDeepSeek']['localDeepSeekApi'],
            'localDeepSeekModel': configData['apiServer']['aiConfig']['localDeepSeek']['localDeepSeekModel']
        }
        self.siliconFlowConfig = {
            'siliconFlowApi': configData['apiServer']['aiConfig']['siliconFlow']['siliconFlowApi'],
            'siliconFlowKey': configData['apiServer']['aiConfig']['siliconFlow']['siliconFlowKey'],
            'siliconFlowModel': configData['apiServer']['aiConfig']['siliconFlow']['siliconFlowModel']
        }
        self.douBaoConfig = {
            'douBaoApi': configData['apiServer']['aiConfig']['douBao']['douBaoApi'],
            'douBaoKey': configData['apiServer']['aiConfig']['douBao']['douBaoKey'],
            'douBaoModel': configData['apiServer']['aiConfig']['douBao']['douBaoModel'],
            'douBaoAk': configData['apiServer']['aiConfig']['douBao']['douBaoAk'],
            'douBaoSk': configData['apiServer']['aiConfig']['douBao']['douBaoSk'],
            'douBaoReqKey': configData['apiServer']['aiConfig']['douBao']['douBaoReqKey'],
            'douBaoPicModelVersion': configData['apiServer']['aiConfig']['douBao']['douBaoPicModelVersion'],
        }

        self.openAiMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.qianFanMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.hunYuanMessages = [{"Role": "system", "Content": f'{self.systemAiRole}'}]
        self.kimiMessages = [{"Role": "system", "Content": f'{self.systemAiRole}'}]
        self.bigModelMessages = [{"role": "system", "Content": f'{self.systemAiRole}'}]
        self.deepSeekMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.siliconFlowMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.douBaoMessages = [{"role": "system", "content": f'{self.systemAiRole}'}]
        self.aiPriority = configData['apiServer']['aiConfig']['aiPriority']
        self.aiPicPriority = configData['apiServer']['aiConfig']['aiPicPriority']

    # 谷歌搜索
    api_key = "AIzaSyCuWEgOeX5fuF4O6nBBChnKPlpPurEk0yE"
    search_engine_id = "2369d51a6b092401e"

    def get_search_results(self, query, api_key, search_engine_id):
        url = "https://customsearch.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": api_key,  # API Key
            "cx": search_engine_id,  # 搜索引擎 ID
            "num": 10  # 获取前5个结果
        }
        response = requests.get(url, params=params)
        results = response.json()

        # 打印完整的 API 响应以调试
        # print("API Response:", results)

        search_results = ""
        if "items" in results:  # Google Custom Search API 返回的结果在 "items" 字段中
            for i, item in enumerate(results["items"]):
                search_results += f"[webpage {i+1} begin]\n{item['snippet']}\n[webpage {i+1} end]\n"
            print("谷歌搜索成功")
        else:
            search_results = "No results found or API request failed."
            print("谷歌搜索失败")
        return search_results

    # 获取当前日期
    def get_current_date(self):
        """
        动态获取当前日期，格式为 YYYY年MM月DD日
        """
        now = datetime.now()
        return now.strftime("%Y年%m月%d日")
    
    def getOpenAi(self, content, messages, needs_search=True):
        op(f'[*]: 正在调用OpenAi对话接口... ...')
        """
        Open Ai对话
        :param OpenAiConfig: OpenAi 配置字典
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        if not self.openAiConfig.get('openAiKey'):
            op(f'[-]: GPT模型未配置, 请检查相关配置!!!')
            return None, []
        # search_answer_zh_template = \
        #     '''
        #     在回答时，请注意以下几点：
        #     - 今天是{cur_date}。
        #     - 并非搜索结果的所有内容都与用户的问题密切相关，你需要结合问题，对搜索结果进行甄别、筛选。
        #     - 对于列举类的问题（如列举所有航班信息），尽量将答案控制在10个要点以内，并告诉用户可以查看搜索来源、获得完整信息。优先提供信息完整、最相关的列举项；如非必要，不要主动告诉用户搜索结果未提供的内容。
        #     - 你需要解读并概括用户的题目要求，选择合适的格式，充分利用搜索结果并抽取重要信息，生成符合用户要求、极具思想深度、富有创造力与专业性的答案。你的创作篇幅需要尽可能延长，对于每一个要点的论述要推测用户的意图，给出尽可能多角度的回答要点，且务必信息量大、论述详尽。
        #     - 如果回答很长，请尽量结构化、分段落总结。如果需要分点作答，尽量控制在5个点以内，并合并相关的内容。
        #     - 对于客观类的问答，如果问题的答案非常简短，可以适当补充一到两句相关信息，以丰富内容。
        #     - 你需要根据用户要求和回答内容选择合适、美观的回答格式，确保可读性强。
        #     - 你的回答应该综合多个相关网页来回答，不能重复引用一个网页。
        #     - 除非用户要求，否则你回答的语言需要和用户提问的语言保持一致。
        #     # 用户消息为：
        #     {question}'''
        # # 如果需要搜索，调用 Google 搜索 API 获取结果
        # if needs_search:
        #     api_key = "AIzaSyCuWEgOeX5fuF4O6nBBChnKPlpPurEk0yE"
        #     search_engine_id = "2369d51a6b092401e"
            
        #     search_results = self.get_search_results(content, api_key, search_engine_id)
        #     cur_date = self.get_current_date()  # 这里可以动态获取当前日期
        #     search_answer_prompt = search_answer_zh_template.format(
        #         search_results=search_results,
        #         cur_date=cur_date,
        #         question=content
        #     )
        #     messages.append({"role": "user", "content": search_answer_prompt})
        # else:
        #     # 如果不需要搜索，直接使用用户输入
        #     messages.append({"role": "user", "content": f'{content}'})
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.openAiConfig.get('openAiModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.openAiConfig.get('openAiKey')}",
        }
        try:
            resp = requests.post(url=self.openAiConfig.get('openAiApi'), headers=headers, json=data, timeout=150)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            # 根据 openAiModel 添加后缀
            model_suffix = self.openAiConfig.get('openAiModel')
            api_text = f"API来自: {model_suffix}"
            assistant_content += f"\n\n{api_text}"
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content.replace('*', '').replace('#', '').replace('`', ''), messages
        except Exception as e:
            op(f'[-]: open ai对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getSparkAi(self, content):
        """
        星火大模型Ai 对话
        :param content: 对话内容
        :return:
        """
        op(f'[*]: 正在调用星火大模型对话接口... ...')
        SparkAppid = self.sparkAiConfig.get('sparkAiAppid')
        SparkSecret = self.sparkAiConfig.get('sparkAiSecret')
        SParkApiKey = self.sparkAiConfig.get('sparkAiKey')
        SParkApi = self.sparkAiConfig.get('sparkAiApi')
        SParkDomain = self.sparkAiConfig.get('sparkDomain')
        try:
            spark = ChatSparkLLM(
                spark_api_url=SParkApi,
                spark_app_id=SparkAppid,
                spark_api_key=SParkApiKey,
                spark_api_secret=SparkSecret,
                spark_llm_domain=SParkDomain,
                streaming=False,
            )
            messages = [ChatMessage(
                role='system',
                content=self.systemAiRole
            ), ChatMessage(
                role="user",
                content=content
            )]
            handler = ChunkPrintHandler()
            sparkObject = spark.generate([messages], callbacks=[handler])
            sparkContent = sparkObject.generations[0][0].text
            # 根据 Model 添加后缀
            model_suffix = self.sparkAiConfig.get('sparkDomain')
            # api_text = f"API来自: {model_suffix}"
            sparkContent += f"\n\nAPI来自: {model_suffix}"
            return sparkContent.replace('*', '').replace('#', '').replace('`', '')
        except Exception as e:
            op(f'[-]: 星火大模型对话接口出现错误, 错误信息: {e}')
            return None

    def getSparkPic(self, content):
        """
        星火大模型 图像生成
        :param content:
        :return:
        """
        op(f'[*]: 正在调用星火大模型图像生成接口... ...')
        try:
            res = sPa.main(content, self.sparkAiConfig.get('sparkAiAppid'), self.sparkAiConfig.get('sparkAiKey'),
                           self.sparkAiConfig.get('sparkAiSecret'))
            savePath = sPa.parser_Message(res)
            return savePath
        except Exception as e:
            op(f'[-]: 星火大模型图像生成出现错误, 错误信息: {e}')
            return None

    def getQianFanAi(self, content, messages):
        """
        千帆模型 Ai对话
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用千帆大模型对话接口... ...')
        messages.append({"role": "user", "content": content})
        if not self.qianfanAiConfig.get('qfAccessKey') or not self.qianfanAiConfig.get('qfSecretKey'):
            op(f'[-]: 千帆大模型未配置, 请检查相关配置!!!')
            return None, []

        def getAccessToken():
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                query = {
                    'grant_type': 'client_credentials',
                    'client_id': self.qianfanAiConfig.get('qfAccessKey'),
                    'client_secret': self.qianfanAiConfig.get('qfSecretKey'),
                }
                resp = requests.post('https://aip.baidubce.com/oauth/2.0/token', headers=headers, data=query)
                access_token = resp.json()['access_token']
                return access_token
            except Exception as e:
                op(f'[-]: 获取千帆模型AccessToken出现错误, 错误信息: {e}')
                return None

        def getAiContent(access_token, messages):
            try:
                url = f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-turbo-8k?access_token={access_token}'
                data = {
                    'messages': messages
                }
                resp = requests.post(url, json=data)
                result = resp.json()['result']
                messages.append({"role": "assistant", "content": result})
                return result, messages
            except Exception as e:
                op(f'[-]: 请求千帆模型AccessToken出现错误, 错误信息: {e}')
                return None, messages

        access_token = getAccessToken()
        if not access_token:
            op(f'[-]: 获取千帆模型AccessToken失败, 请检查千帆配置!!!')
            return None, messages

        aiContent = getAiContent(access_token, messages)
        if len(messages) == 21:
            del messages[1]
            del messages[2]
        return aiContent, messages

    def getQianFanPic(self, content):
        """
        千帆模型生成图片
        :param content:
        :return:
        """
        op(f'[*]: 正在调用千帆模型图片生成接口... ...')

        def getAccessToken():
            try:
                headers = {
                    'Content-Type': 'application/json'
                }
                query = {
                    'grant_type': 'client_credentials',
                    'client_id': self.qianfanAiConfig.get('qfPicAccessKey'),
                    'client_secret': self.qianfanAiConfig.get('qfPicSecretKey'),
                }
                resp = requests.post('https://aip.baidubce.com/oauth/2.0/token', headers=headers, data=query)
                access_token = resp.json()['access_token']
                return access_token
            except Exception as e:
                op(f'[-]: 获取千帆模型AccessToken出现错误, 错误信息: {e}')
                return None

        def getTaskId(content, accessToken):
            try:
                url = f'https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token={accessToken}'
                data = {
                    "prompt": content,
                    "width": 1024,
                    "height": 1024,
                    "image_num": 1,
                }
                resp = requests.post(url, json=data)
                json_data = resp.json()
                task_id = json_data['data']['task_id']
                return task_id
            except Exception as e:
                op(f'[-]: 千帆模型Ai图像生成出现错误, 错误信息: {e}')
                return None

        def getPicUrl(task_id, accessToken):
            try:
                url = f'https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token={accessToken}'
                data = {
                    'task_id': task_id
                }
                resp = requests.post(url, json=data)
                json_data = resp.json()
                if json_data['data']['task_status'] == 'SUCCESS':
                    sub_task_result_list = json_data['data']['sub_task_result_list']
                    final_image_list = sub_task_result_list[0]['final_image_list']
                    img_url = final_image_list[0]['img_url']
                    return img_url
            except Exception as e:
                op(f'[-]: 千帆模型Ai图像生成出现错误, 错误信息: {e}')

        def downloadImg(imgUrl):
            try:
                save_path = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
                resp = requests.get(url=imgUrl)
                imgContent = resp.content
                with open(save_path, mode='wb') as f:
                    f.write(imgContent)
                return save_path
            except Exception as e:
                op(f'[-]: 千帆模型Ai图像下载出现错误, 错误信息: {e}')
                return None

        accessToken = getAccessToken()
        if accessToken:
            task_id = getTaskId(content, accessToken)
            if task_id:
                time.sleep(20)
                imgUrl = getPicUrl(task_id, accessToken)
                if imgUrl:
                    savePath = downloadImg(imgUrl)
                    return savePath
                return None

    def getHunYuanAi(self, content, messages):
        """
        腾讯混元模型 Ai对话接口
        :param content:
        :param messages:
        :return:
        """
        try:
            op(f'[*]: 正在调用混元模型对话接口... ...')
            cred = credential.Credential(self.hunYuanAiConfig.get('hunYuanSecretId'),
                                         self.hunYuanAiConfig.get('hunYuanSecretKey'))
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = hunyuan_client.HunyuanClient(cred, "ap-beijing", clientProfile)
            req = models.ChatCompletionsRequest()
            messages.append({'Role': 'user', 'Content': content})
            params = {
                "Model": self.hunYuanAiConfig.get('hunYuanModel'),
                "Messages": messages,
            }
            req.from_json_string(json.dumps(params))
            Choices = str(client.ChatCompletions(req).Choices[0])
            jsonData = json.loads(Choices)
            Message = jsonData['Message']
            messages.append({'Role': Message['Role'], 'Content': Message['Content']})
            content = Message['Content'].replace('#', '').replace('*', '').replace('`', '')
            # 根据 hunYuanModel 添加后缀
            model_suffix = self.hunYuanAiConfig.get('hunYuanModel')
            api_text = f"\n\nAPI来自: {model_suffix}"
            # assistant_content += f"{api_text}"
            content += api_text
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            if content:
                return content, messages
            return None, []
        except TencentCloudSDKException as e:
            op(f'[-]: 腾讯混元Ai对话接口出现错误, 错误信息: {e}')
            return None, messages

    def getKiMiAi(self, content, messages):
        op(f'[*]: 正在调用kiMi对话接口... ...')
        """
        kiMi Ai对话
        :param OpenAiConfig: kiMi 配置字典
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        if not self.kiMiConfig.get('kiMiKey'):
            op(f'[-]: kiMi模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.kiMiConfig.get('kiMiModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.kiMiConfig.get('kiMiKey')}",
        }
        try:
            resp = requests.post(url=self.kiMiConfig.get('kiMiApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: kiMi对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getBigModel(self, content, messages):
        """
        BigModel
        :param OpenAiConfig: BigModel 配置字典
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用BigModel对话接口... ...')
        if not self.bigModelConfig.get('bigModelKey'):
            op(f'[-]: BigModel模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.bigModelConfig.get('bigModelModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.bigModelConfig.get('bigModelKey')}",
        }
        try:
            resp = requests.post(url=self.bigModelConfig.get('bigModelApi'), headers=headers, json=data, timeout=15)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: BigMode对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getDeepSeek(self, content, messages, needs_search=True):
        """
        deepSeek
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用deepSeek对话接口... ...')
        if not self.deepSeekConfig.get('deepSeekKey'):
            op(f'[-]: deepSeek模型未配置, 请检查相关配置!!!')
            return None, []
        # search_answer_zh_template = \
        #     '''
        #     - 今天是{cur_date}。
        #     - 并非搜索结果的所有内容都与用户的问题密切相关，你需要结合问题，对搜索结果进行甄别、筛选。
        #     - 对于列举类的问题（如列举所有航班信息），尽量将答案控制在10个要点以内，并告诉用户可以查看搜索来源、获得完整信息。优先提供信息完整、最相关的列举项；如非必要，不要主动告诉用户搜索结果未提供的内容。
        #     - 你需要解读并概括用户的题目要求，选择合适的格式，充分利用搜索结果并抽取重要信息，生成符合用户要求、极具思想深度、富有创造力与专业性的答案。你的创作篇幅需要尽可能延长，对于每一个要点的论述要推测用户的意图，给出尽可能多角度的回答要点，且务必信息量大、论述详尽。
        #     - 如果回答很长，请尽量结构化、分段落总结。如果需要分点作答，尽量控制在5个点以内，并合并相关的内容。
        #     - 对于客观类的问答，如果问题的答案非常简短，可以适当补充一到两句相关信息，以丰富内容。
        #     - 你需要根据用户要求和回答内容选择合适、美观的回答格式，确保可读性强。
        #     - 你的回答应该综合多个相关网页来回答，不能重复引用一个网页。
        #     - 除非用户要求，否则你回答的语言需要和用户提问的语言保持一致。
        #     # 用户消息为：
        #     {question}'''
        # # 如果需要搜索，调用 Google 搜索 API 获取结果
        # if needs_search:
        #     api_key = "AIzaSyCuWEgOeX5fuF4O6nBBChnKPlpPurEk0yE"
        #     search_engine_id = "2369d51a6b092401e"
            
        #     search_results = self.get_search_results(content, api_key, search_engine_id)
        #     cur_date = self.get_current_date()  # 这里可以动态获取当前日期
        #     search_answer_prompt = search_answer_zh_template.format(
        #         search_results=search_results,
        #         cur_date=cur_date,
        #         question=content
        #     )
        #     messages.append({"role": "user", "content": search_answer_prompt})
        # else:
        #     # 如果不需要搜索，直接使用用户输入
        #     messages.append({"role": "user", "content": f'{content}'})
        messages.append({"role": "user", "content": f'{content}'})

        data = {
            "model": self.deepSeekConfig.get('deepSeekModel'),
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.deepSeekConfig.get('deepSeekKey')}",
        }
        try:
            resp = requests.post(url=self.deepSeekConfig.get('deepSeekApi'), headers=headers, json=data, timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            # 根据 deepSeekModel 添加后缀
            model_suffix = self.deepSeekConfig.get('deepSeekModel')
            api_text = f"API来自: {model_suffix}"
            assistant_content += f"\n\n{api_text}"
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content.replace('#', '').replace('*', '').replace('`', ''), messages
        except Exception as e:
            op(f'[-]: deepSeek对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getLocalDeepSeek(self, content, messages):
        """
        deepSeek
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用deepSeek本地对话接口... ...')
        if not self.localDeepSeekModelConfig:
            op(f'[-]: deepSeek本地模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.localDeepSeekModelConfig.get('localDeepSeekModel'),
            'messages': messages,
            'stream': False
        }
        try:
            resp = requests.post(url=self.localDeepSeekModelConfig.get('localDeepSeekApi'), json=data)
            jsonData = resp.json()
            print(jsonData)
            assistant_content = jsonData['message']['content'].split('</think>')[-1].strip()
            return assistant_content, []
        except Exception as e:
            op(f'[-]: deepSeek本地对话接口出现错误, 错误信息: {e}')
            return None, []

    def getSiliconFlow(self, content, messages):
        """
        deepSeek
        :param content: 对话内容
        :param messages: 消息列表
        :return:
        """
        op(f'[*]: 正在调用硅基流动对话接口... ...')
        
        if not self.siliconFlowConfig.get('siliconFlowKey'):
            op(f'[-]: deepSeek模型未配置, 请检查相关配置!!!')
            return None, []
        messages.append({"role": "user", "content": f'{content}'})
        data = {
            "model": self.siliconFlowConfig.get('siliconFlowModel'),
            "messages": messages,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.siliconFlowConfig.get('siliconFlowKey')}",
        }
        try:
            resp = requests.post(url=self.siliconFlowConfig.get('siliconFlowApi'), headers=headers, json=data,
                                 timeout=300)
            json_data = resp.json()
            assistant_content = json_data['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            # 根据 Model 添加后缀
            model_suffix = self.siliconFlowConfig.get('siliconFlowModel')
            api_text = f"API来自: {model_suffix}"
            assistant_content += f"\n\n{api_text}"
            
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content.replace('#', '').replace('*', '').replace('`', ''), messages
        except Exception as e:
            op(f'[-]: 硅基对话接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]
        op()

    def getDouBao(self, content, messages):
        """
        豆包文本大模型
        :param content: 对话内容
        :param messages: 对话消息
        :return:
        """
        op(f'[*]: 正在调用豆包文本大模型接口... ...')
        if not self.douBaoConfig.get('douBaoKey'):
            op(f'[-]: 豆包文本大模型接口未配置')
            return None, self.douBaoMessages[0]
        messages.append({"role": "user", "content": f'{content}'})
        headers = {
            "Authorization": f"{self.douBaoConfig.get('douBaoKey')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.douBaoConfig.get('douBaoModel'),
            "messages": messages,
            "stream": False
        }
        try:
            resp = requests.post(self.douBaoConfig.get('douBaoApi'), headers=headers, json=data)
            jsonData = resp.json()
            assistant_content = jsonData.get('choices')[0].get('message').get('content')
            messages.append({"role": "assistant", "content": f"{assistant_content}"})
            if len(messages) == 21:
                del messages[1]
                del messages[2]
            return assistant_content, messages
        except Exception as e:
            op(f'[-]: 豆包文本大模型接口出现错误, 错误信息: {e}')
            return None, [{"role": "system", "content": f'{self.systemAiRole}'}]

    def getDouBaoPic(self, content):
        op(f'[*]: 正在调用豆包文生图模型... ...')
        if not self.douBaoConfig.get('douBaoAk'):
            op(f'[-]: 豆包文生图模型未配置, 请检查相关配置!!!')
            return None
        visual_service = VisualService()
        visual_service.set_ak(self.douBaoConfig.get('douBaoAk'))
        visual_service.set_sk(self.douBaoConfig.get('douBaoSk'))
        data = {
            'req_key': self.douBaoConfig.get('douBaoReqKey'),
            'model_version': self.douBaoConfig.get('douBaoPicModelVersion'),
            'prompt': content,
        }
        try:
            resp = visual_service.cv_process(data)
            binaryDataBase64 = resp.get('data').get('binary_data_base64')[0]
            picPath = Fcs.returnAiPicFolder() + '/' + str(int(time.time() * 1000)) + '.jpg'
            with open(picPath, 'wb') as f:
                f.write(base64.b64decode(binaryDataBase64))
            return picPath
        except Exception as e:
            op(f'[-]: 豆包文生图模型出现错误, 错误信息: {e}')
            return None

    def getAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        result = ''
        for i in range(1, 11):
            aiModule = self.aiPriority.get(i)
            if aiModule == 'hunYuan':
                result, self.hunYuanMessages = self.getHunYuanAi(content, self.hunYuanMessages)
            if aiModule == 'sparkAi':
                result = self.getSparkAi(content)
            if aiModule == 'openAi':
                result, self.openAiMessages = self.getOpenAi(content, self.openAiMessages)
            if aiModule == 'qianFan':
                result, self.qianFanMessages = self.getQianFanAi(content, self.qianFanMessages)
            if aiModule == 'kiMi':
                result, self.kimiMessages = self.getKiMiAi(content, self.kimiMessages)
            if aiModule == 'bigModel':
                result, self.bigModelMessages = self.getBigModel(content, self.bigModelMessages)
            if aiModule == 'deepSeek':
                result, self.deepSeekMessages = self.getDeepSeek(content, self.deepSeekMessages)
            if aiModule == 'localDeepSeek':
                result, self.deepSeekMessages = self.getLocalDeepSeek(content, self.deepSeekMessages)
            if aiModule == 'siliconFlow':
                result, self.siliconFlowMessages = self.getSiliconFlow(content, self.siliconFlowMessages)
            if aiModule == 'douBao':
                result, self.douBaoMessages = self.getDouBao(content, self.douBaoMessages)
            if not result:
                continue
            else:
                break
        return result
    
    def getPicAi(self, content):
        """
        处理优先级
        :param content:
        :return:
        """
        picPath = ''
        for i in range(1, 4):
            aiPicModule = self.aiPicPriority.get(i)
            if aiPicModule == 'sparkAi':
                picPath = self.getSparkPic(content)
            if aiPicModule == 'qianFan':
                picPath = self.getQianFanPic(content)
            if aiPicModule == 'douBao':
                picPath = self.getDouBaoPic(content)
            if not picPath:
                continue
            else:
                break
        return picPath


if __name__ == '__main__':
    messages = []
    Ad = AiDialogue()
    # print(Ad.getPicAi('画一只布尔猫'))
    while 1:
        print(Ad.getAi(input('>> ')))
    # Ad.getAi(1)
    # while 1:
    #     content, messages = Ad.getHunYuanAi(input(), messages)
    #     print(content)
    # Ad.getHunYuanAi('1', [])
    # print(Ad.getQianFanPic('画一只赛博小狗'))
    # print(Ad.getSparkPic('画一只赛博小狗'))

    # print(Ad.getQianFanAi('你是谁', []))
    # print(Ad.getOpenAi())
    # print(Ad.getSparkAi('你是谁'))
    # while 1:
    #     print(Ad.getAi(input('>> ')))
