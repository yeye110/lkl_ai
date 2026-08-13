import json
from typing import Optional, Dict, Any, Tuple

def extract_agent_response(response_text: str) -> Tuple[str, Optional[Dict], Optional[str]]:
    """
    从 Agent 的 JSON 响应中提取三个核心变量：
    
    Returns:
        thought (str): 思考内容
        tool_call (dict or None): 工具调用信息 {name, args, kwargs}，若不存在则为 None
        final_answer (str or None): 最终答案，若不存在则为 None

    Raises:
        ValueError: 如果格式错误或解析失败
    """
    try:
        # 清理可能的 Markdown 包装
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        parsed = json.loads(response_text)

        # 验证顶层结构
        required_keys = {"thought", "tool_call", "final_answer"}
        if not isinstance(parsed, dict) or not required_keys.issubset(parsed.keys()):
            raise ValueError(f"JSON 必须包含 {required_keys} 三个字段，当前为: {list(parsed.keys())}")

        # 提取 thought
        thought_field = parsed["thought"]
        if not isinstance(thought_field, dict) or not thought_field.get("has") or not isinstance(thought_field["content"], str):
            raise ValueError("thought 必须存在且 content 为字符串")
        thought = thought_field

        # 提取 tool_call（若存在且有效）
        tool_call_field = parsed["tool_call"]
        tool_call = tool_call_field


        # 提取 final_answer（若存在且有效）
        final_answer_field = parsed["final_answer"]
        final_answer = final_answer_field

        return thought, tool_call, final_answer

    except json.JSONDecodeError as e:
        raise ValueError(f"无法解析 JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"响应格式错误: {str(e)}")