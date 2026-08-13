import inspect
from typing import List, Callable, Dict, Any


def extract_tool_info(func: Callable) -> dict:
    """
    从函数对象中提取工具信息,给LLM看的
    """
    # 获取函数签名（参数）
    sig = inspect.signature(func)
    params = {}
    for name, param in sig.parameters.items():
        params[name] = {
            "type": "string",  # 简化假设，实际可结合 type hints
            "description": f"参数 {name}"
        }

    # 获取函数文档字符串作为描述
    description = inspect.getdoc(func) or f"执行 {func.__name__} 操作"

    return {
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": params,
            "required": list(sig.parameters.keys())
        }
    }



def build_tools_registry(functions: List[Callable]) -> Dict[str, Callable]:
    """
    根据函数列表自动生成工具注册表（工具名 → 函数对象）
    
    :param functions: 函数列表，如 [write_to_file, get_weather]
    :return: Dict[str, Callable]，键为函数名，值为函数对象
    :raises ValueError: 如果函数名重复或不是函数
    """
    registry = {}
    seen_names = set()

    for func in functions:
        if not callable(func):
            raise ValueError(f"对象 {func} 不是可调用函数")

        func_name = func.__name__
        
        if func_name in seen_names:
            raise ValueError(f"函数名重复: '{func_name}' 被定义了多次")
        
        seen_names.add(func_name)
        registry[func_name] = func

    return registry


# ====================
# ✅ 自动生成 TOOLS_REGISTRY
# ====================
def tools_registry(TOOLS):
    TOOLS_REGISTRY = build_tools_registry(TOOLS)
    # 打印结果验证
    print("🔧 自动生成的 TOOLS_REGISTRY：")
    for name, func in TOOLS_REGISTRY.items():
        print(f"  '{name}' → {func.__name__}")
    return TOOLS_REGISTRY