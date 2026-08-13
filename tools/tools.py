import os
from pathlib import Path
from typing import List


ROOT = Path(__file__).parent.parent
log_path = ROOT/"record"


def ListFilesTool(directory) -> str:
    """
    遍历目录文件工具
    :param directory:需要遍历的文件夹路径
    :return: 需要遍历的文件夹下所有文件名
    :rtype: str
    """

    try:
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return "\n".join(files)
    except Exception as e:
        return f"遍历目录时出错: {str(e)}"



def ReadFileTool(file_paths: List[str]) -> str:
    """
    读取文件工具
    逐个读取指定文件的内容并汇总
    :param file_paths: 要读取的文件路径列表，可能有多个路径，例如['PhoneParameter\\Apple-iphone-16-20251103.html','PhoneParameter\\Apple-iphone-16e-20251103.html,PhoneParameter\\Apple-iphone-17-20251103.html,PhoneParameter\\Apple-iphone-17-pro-20251103.html']
    :type file_paths: List[str]
    :return: 返回查看的手机信息文件中的所有信息
    :rtype: str
    """

    try:
        contents = []
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 为每个文件添加标识，方便后续处理
                contents.append(f"--- 文件: {file_path} ---\n{content}\n--- 结束: {file_path} ---\n")
        return "\n".join(contents)
    except Exception as e:
        return f"读取文件时出错: {str(e)}"
    
def WriteFileTool(file_path: str, content: str) -> str:
    """
    写入文件工具
    将内容写入指定文件
    :param file_path: 要写入的文件路径
    :type file_path: str
    :param content: 要写入的文件内容
    :type content: str
    :return: 写入是否成功
    :rtype: str
    
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f"成功写入文件: {file_path}"
    except Exception as e:
        return f"写入文件时出错: {str(e)}"