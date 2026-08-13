from tools.tools import ListFilesTool,ReadFileTool,WriteFileTool
import uuid
import os
from dotenv import load_dotenv
load_dotenv() # 读取当前目录下.env文件

system_prompt=f"""
##role:
你是一个专业的手机顾问 AI，职责是利用工具帮助用户查询、对比和获取手机信息。

##task:
    1.利用工具查询用户想要了解或者对比的手机信息。
    2.根据用户的问题以及查询到的信息进行回复。
    3.将回答记录到本地record路径下，文件名为用户问题相关分析报告。

##info:
手机信息路径为:PhoneParameter
"""
api_key = os.getenv("API_KEY")
base_url = os.getenv("API_URL")
model = os.getenv("MODEL_NAME")


from lkl_ai.model.glm import glm
qwen3_model = glm(api_key=api_key,
                    base_url=base_url,
                    model=model,
                    )
from lkl_ai.agent import Agent
phone_pilot_agent=Agent(
                        system_prompt=system_prompt,
                        tools=[ListFilesTool,ReadFileTool,WriteFileTool],
                        model=qwen3_model
                        )