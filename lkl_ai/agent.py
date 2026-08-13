from lkl_ai.config.prompt import INSTRUCTION

import uuid

from lkl_ai.context import Message,Context
from lkl_ai.utils import extract_agent_response,extract_tool_info,tools_registry,tool_run



class Agent():
    def __init__(self,
                 session_id=f"sess_{uuid.uuid4().hex[:16]}",
                 user_id=f"user_{uuid.uuid4().hex[:12]}",
                 system_prompt="",
                 tools=[],
                 model=None,
                 ):
        
        self.session_id=session_id
        self.user_id=user_id
        self.instruction = INSTRUCTION
        self.system_prompt=system_prompt
        self.tools_description=[]
        for tool in tools:
            self.tools_description.append(extract_tool_info(tool))  # 生成工具描述(提供给LLM)
        self.TOOLS_REGISTRY = tools_registry(tools)  # 注册工具名
        self.context=Context(
                    session_id=session_id,
                    user_id=user_id,
                    instruction=self.instruction,
                    system_prompt=self.system_prompt,
                    tools=self.tools_description)
        self.model=model
        self.MAX_RETRY=10
        #print(f"初始化的上下文{self.context}")


    def run(self,user_prompt=""):
        print("任务开始:")


        self.context.context_init()
        self.context.add_message({
            "role": "user",
            "content": user_prompt
        })
        for _ in range(self.MAX_RETRY):
            # print("="*20+"上下文"+"="*20)
            # print(f"{self.context.show_context()}\n")
            response = self.model.request(self.context.message)
            # print(f"大模型初始返回结果\n{response}\n")
            thought, tool_call, final_answer=extract_agent_response(response)
            thought_content=thought["content"]
            print("="*20+"大模型思考"+"="*20)
            print(f"{thought_content}\n")
            if(tool_call["has"]):
                # 调用工具
                tool_call_content=tool_call["content"]
                print("="*20+"大模型决定工具调用指令"+"="*20)
                print(f"{tool_call_content}\n")
                print(self.TOOLS_REGISTRY)
                tool_result = tool_run(TOOLS_REGISTRY=self.TOOLS_REGISTRY,tool_call_data=tool_call_content)
                print("="*20+"工具调用结果"+"="*20)
                print(f"{tool_result[:100]}{'...' if len(str(tool_result)) > 1000 else ''}\n")
                self.context.add_message({
                    "role": "tool",
                    "content": tool_result
                })
            elif(final_answer["has"]):
                final_answer_content=final_answer["content"]
                print("="*20+"大模型决定任务完成"+"="*20)
                print(f"{final_answer_content}\n")
                self.context.add_message({
                    "role": "assistant",
                    "content": final_answer
                })
                break

        
