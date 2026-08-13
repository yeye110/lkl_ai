import json
from typing import Any, Dict, Optional


# ====================
# 安全提取并执行 tool_call 的函数
# ====================
def tool_run(TOOLS_REGISTRY,tool_call_data: Dict[str, Any]) -> str:
    """
    从结构化 tool_call 中提取 name 和 kwargs，调用对应函数，返回结果字符串
    :param tool_call_data: 来自 Agent 的 tool_call.content 字段
    :return: 工具执行结果（字符串）
    """
    # 1. 提取函数名
    tool_name = tool_call_data.get("name")
    if not isinstance(tool_name, str):
        return f"❌ 工具名无效: {tool_name}"

    # 2. 提取 kwargs（允许为空 dict）
    kwargs = tool_call_data.get("kwargs", {})
    if not isinstance(kwargs, dict):
        return f"❌ kwargs 必须是字典，当前类型: {type(kwargs)}"

    # 3. 检查工具是否存在
    if tool_name not in TOOLS_REGISTRY:
        return f"❌ 工具 '{tool_name}' 未注册"

    func = TOOLS_REGISTRY[tool_name]

    # 4. 调用函数（使用 **kwargs）
    try:
        result = func(**kwargs)
        return str(result)  # 确保返回字符串
    except TypeError as e:
        return f"❌ 参数错误: {str(e)}（请检查参数名或类型）"
    except Exception as e:
        return f"❌ 执行异常: {str(e)}"



