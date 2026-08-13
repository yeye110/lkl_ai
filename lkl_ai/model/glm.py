import os
from dotenv import load_dotenv
import requests
import json
from json_repair import repair_json

from lkl_ai.context import Context
load_dotenv()


class glm():
    def __init__(self,base_url,api_key,model):
        self.url=base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model=model

    def request(self,messages):

        data={
            "model": self.model,
            "messages": messages
        }
        try:
            # 1. 发送请求
            print(data)
            response = requests.post(self.url, json=data, headers=self.headers)
            # 2. 解析 JSON 响应
            resp_json = response.json()
            # 3. 提取模型返回的 content
            # print(f"大模型初始返回:\n{json.dumps(resp_json, ensure_ascii=False, indent=2)}")
            
            content = resp_json["choices"][0]["message"]["content"]
            print(content)
            return content
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False


