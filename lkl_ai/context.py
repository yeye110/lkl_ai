from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
from datetime import datetime, timezone
import json

# ====================
# 1. Message 类
# ====================
@dataclass
class Message:
    role: str  # 'user', 'tool', 'agent'
    content: str = None  # 主要内容（文本或 JSON 字符串）
    thought: str = None #思考
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # 仅当 role == 'assistant' 时有效：AI 要调用的工具（请求）
    tool_call: Optional[Dict[str, Any]] = None  #tool_calls: Optional[List[Dict[str, Any]]] = None  # 如：[{"id": "call_123", "name": "get_weather", "arguments": {...}}]
    
    # 仅当 role == 'tool' 时有效：工具返回的响应（结果）
    tool_call_id: Optional[str] = None  # 匹配 assistant 的 tool_call.id
    tool_result: Optional[Any] = None   # 工具执行结果（如：{"temperature": 25}）
    
    # 仅当 role == 'agent' 且任务完成时有效：最终回答
    final_answer: Optional[str] = None  # 不要和 content 混用，如果用了 final_answer，content 可留空或写“正在思考...”





# ====================
# 2. Context 类
# ====================
@dataclass
class Context:
    session_id: str
    user_id: str
    instruction: str 
    system_prompt: str
    message: list = field(default_factory=list)
    tools: List[Dict[str,Any]] = field(default_factory=list)  # ✅ 使用结构化类，非 Dict[str, Any]

    def __str__(self):
        lines = []

        # 标题
        lines.append("=" * 70)
        lines.append(f"CONTEXT - Session: {self.session_id} | User: {self.user_id}")
        lines.append("=" * 70)

        # 系统配置
        lines.append("\n📌 SYSTEM CONFIG")
        lines.append(f"   Instruction: {self.instruction[:80]}{'...' if len(self.instruction) > 80 else ''}")
        lines.append(f"   System Prompt: {self.system_prompt[:80]}{'...' if len(self.system_prompt) > 80 else ''}")
        if self.current_user_prompt:
            lines.append(f"   Current User Prompt: {self.current_user_prompt[:80]}{'...' if len(self.current_user_prompt) > 80 else ''}")

        # 工具列表
        if self.tools:
            lines.append("\n🛠️  TOOLS ({} available):".format(len(self.tools)))
            for tool in self.tools:  # ← 遍历列表，不是字典
                name = tool.get("name", "unknown")
                desc = tool.get("description", "No description")
                lines.append(f"   - {name}: {desc[:80]}{'...' if len(desc) > 80 else ''}")

                # 打印 parameters 结构
                params = tool.get("parameters", {})
                if params:
                    lines.append("        parameters:")
                    lines.append(f"          type: {params.get('type', 'unknown')}")
                    required = params.get("required", [])
                    lines.append(f"          required: {required}")
                    props = params.get("properties", {})
                    if props:
                        lines.append("          properties:")
                        for prop_name, prop_info in props.items():
                            prop_str = str(prop_info).replace("\n", " ").replace("\r", "")
                            lines.append(f"            {prop_name}: {prop_str}")

        # 对话历史
        lines.append("\n💬 CONVERSATION HISTORY ({} messages):".format(len(self.conversation)))
        for i, msg in enumerate(self.conversation, 1):
            role = msg.role.upper()
            timestamp = msg.timestamp.strftime("%H:%M:%S")

            # 根据 role 构造内容
            if msg.role == "user":
                content = msg.content or "[empty]"
            elif msg.role == "angent":
                if msg.tool_call:
                    content = f"[TOOL CALL] {', '.join(msg.tool_call)}"
                elif msg.final_answer:
                    content = f"[FINAL ANSWER] {msg.final_answer}"
                else:
                    content = msg.content or "[empty]"
            elif msg.role == "tool":
                result = msg.tool_result
                if isinstance(result, dict):
                    result_str = str(result).replace("\n", " ").replace("\r", "")[:80]
                    content = f"[TOOL RESULT] {result_str}"
                else:
                    content = f"[TOOL RESULT] {str(result)[:80]}"


            # 截断内容，避免过长
            if len(content) > 100:
                content = content[:100] + "..."

            lines.append(f"   [{i:2d}] {role:<20} [{timestamp}] {content}")

        lines.append("=" * 70)
        return "\n".join(lines)

    def context_init(self):
        # 1. 系统指令（System）
        all_system_prompt=""
        if self.instruction:
            all_system_prompt+=f"## 任务说明\n{self.instruction}\n"

        if self.system_prompt:
            all_system_prompt+=f"## 系统指令\n{self.system_prompt}\n"

            # 3. 可用工具（Tools）
            if self.tools:
                all_system_prompt+"## 可用工具"
                for tool in self.tools:
                    all_system_prompt+=f"### {tool['name']}"
                    all_system_prompt+=f"描述：{tool['description']}"
                    all_system_prompt+=f"参数格式：{json.dumps(tool['parameters'], ensure_ascii=False, indent=2)}"
                    all_system_prompt+=""  # 空行分隔
        system = {
            "role": "system",
            "content": all_system_prompt
        }
        self.message.append(system)


    
    def show_context(self) -> str:
        """
        将 Context 转换为 LLM 可理解的 prompt 字符串
        所有文本内容截断至最多 500 个字符（含），确保输出可控
        """
        MAX_LENGTH = 500
        lines = []

        def truncate(text: str) -> str:
            """安全截断函数，确保输入为字符串并限制长度"""
            if text is None:
                return ""
            s = str(text).strip()
            return s if len(s) <= MAX_LENGTH else s[:MAX_LENGTH] + "..."  # 添加省略号提示截断

        # 1. 系统指令（System）
        if self.system_prompt:
            content = truncate(self.system_prompt)
            lines.append(f"## 系统指令\n{content}\n")

        # 2. 任务说明（Instruction）
        if self.instruction:
            content = truncate(self.instruction)
            lines.append(f"## 任务说明\n{content}\n")

        # 3. 可用工具（Tools）
        if self.tools:
            lines.append("## 可用工具")
            for tool in self.tools:
                name = truncate(tool.get("name", "未知工具"))
                desc = truncate(tool.get("description", ""))
                params = tool.get("parameters", {})

                lines.append(f"### {name}")
                lines.append(f"描述：{desc}")

                # 参数格式化（JSON），也做截断保护
                try:
                    param_str = json.dumps(params, ensure_ascii=False, indent=2)
                    param_truncated = truncate(param_str)
                    lines.append(f"参数格式：{param_truncated}")
                except Exception as e:
                    lines.append(f"参数格式：序列化失败 - {truncate(str(e))}")
                lines.append("")  # 工具间空行

        # 4. 当前用户输入
        if self.current_user_prompt:
            content = truncate(self.current_user_prompt)
            lines.append(f"\n## 当前用户输入\n{content}\n")

        # 5. 对话历史（Conversation）
        lines.append("## 对话历史(当前进度)")
        for msg in self.conversation:
            if msg.role == "user":
                content = truncate(msg.content)
                lines.append(f"用户: {content}")
            elif msg.role == "tool":
                if hasattr(msg, "thought") and msg.thought:
                    thought = truncate(msg.thought)
                    lines.append(f"当前思考: {thought}")
                if hasattr(msg, "tool_call") and msg.tool_call:
                    call = truncate(msg.tool_call)
                    lines.append(f"调用工具: {call}")
                if hasattr(msg, "tool_result") and msg.tool_result:
                    result = truncate(msg.tool_result)
                    lines.append(f"调用工具结果: {result}")
            elif msg.role == "agent":
                final = msg.final_answer if msg.final_answer else msg.content
                final = truncate(final)
                lines.append(f"agent最终回答: {final}")

        return "\n".join(lines).strip()


    def add_message(self, message: Dict[str,str]):
        """安全添加消息到对话历史"""
        self.message.append(message)

    def get_last_assistant_message(self) -> Optional[Message]:
        """获取最后一条 assistant 消息"""
        for msg in reversed(self.conversation):
            if msg.role == 'assistant':
                return msg
        return None

