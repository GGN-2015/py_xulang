import sys
import os
import json
from . import FileRunner, get_version

# 从命令行中拆分出所有 -I 命令处理
def split_include_path(argv_list:list[str]) -> tuple[list[str], list[str]]:
    CMD_PREFIX = "-I"
    index = 0
    new_argv_list = []     # 删除 -I 命令后的其他命令
    include_path_list = [] # 拆分出所有 include_path
    while index < len(argv_list):
        if argv_list[index].startswith(CMD_PREFIX):
            if len(argv_list[index]) == len(CMD_PREFIX):
                include_path_list.append(argv_list[index + 1].strip())
                index += 2

            else:
                if len(argv_list[index]) <= len(CMD_PREFIX): # 一定更长
                    raise AssertionError()
                other_part = argv_list[index][len(CMD_PREFIX):] # 删除前缀
                include_path_list.append(other_part.strip())
                index += 1
        
        else: # 无关命令
            new_argv_list.append(argv_list[index])
            index += 1
    
    # 返回拆分后的结果
    # 注意 "-I." 以及 "-I.." 之类的写法需要改写成当前工作目录相对路径
    return new_argv_list, [
        os.path.abspath(os.getcwd()) if include_path == "." else (
        os.path.dirname(os.path.abspath(os.getcwd())) if include_path == ".." else include_path)
        for include_path in include_path_list
    ]

def main(argv_list:list[str]) -> int:
    argv_list, inlcude_path_list = split_include_path(argv_list)

    try:
        file_runner = FileRunner(inlcude_path_list)
    except Exception as e:
        print("<CMD>:1", e)
        return 1

    if argv_list == []: # 启动交互式命令行
        print(f"xulang interactive command line v{get_version()}")
        file_runner.interactive_ui()

    else:
        if len(argv_list) > 1:
            print("Usage:")
            print("    python3 -m xulang")
            print("    python3 -m xulang -I <include_path>")
            print("    python3 -m xulang <source_file>")
            return 1

        filepath = argv_list[0]
        if not os.path.isfile(filepath):
            print(f"File \"{filepath}\" not found!")
            return 1
        file_runner.run_file(filepath)

    return 0

# 运行主程序
sys.exit(main(json.loads(json.dumps(sys.argv[1:]))))
