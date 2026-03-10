import os
import traceback
from typing import Optional

try:
    from .RuleSet import RuleSet
    from .ValueMap import ValueMap
    from .ValueTerm import ValueTerm
except:
    from RuleSet import RuleSet
    from ValueMap import ValueMap
    from ValueTerm import ValueTerm

class CommandWrap:
    def __init__(self, filepath:str, line_id:int, command:str) -> None:
        self.filepath = filepath
        self.line_id = line_id
        self.command = command

class FileRunner:
    def __init__(self, include_path_list:list[str]) -> None:
        if not isinstance(include_path_list, list): # 必须是 list
            raise TypeError()
        for include_path in include_path_list:
            if not isinstance(include_path, str): # 必须是字符串
                raise TypeError()
            if not os.path.isdir(include_path):
                raise FileNotFoundError(f"Include path \"{include_path}\" not found.")

        # 记录已经被引入的所有路径
        # 保证同一个文件第二次 include 时不再执行
        self.exists_path:set[str] = set()

        # 记录所有还没有执行的指令
        self.cmd_list:list[CommandWrap] = []

        # 记录目前所有的匹配规则
        self.rule_set = RuleSet()

        # 当前指令执行是否需要输出（手动设置为 True 可以执行命令时显示执行路径）
        self.verbose = False

        # 报错是否需要打开源代码位置信息
        self.extra_error_info = False

        # 记录所有可以 include 的路径
        #   这里的 "." 是一个特殊路径，表示被运行的脚本所在的目录
        #   而不是当前工作路径
        # self.include_path 中除了 "." 之外都是绝对路径
        self.include_path = ["."] + [
            os.path.abspath(path) for path in include_path_list]

    # 返回值表示是否是第一次加载
    # 不是第一次加载时候跳过
    # 这里的 filepath 必须使用绝对路径
    def include_file(self, filepath:str) -> bool:
        if not os.path.isabs(filepath): # 应当使用绝对路径
            raise ValueError()
        if not os.path.isfile(filepath): # 文件不存在，抛出异常
            raise FileNotFoundError()
        if filepath in self.exists_path: # 不是第一次加载
            return False
        # 是第一次加载
        self.exists_path.add(filepath)
        new_cmd_list:list[CommandWrap] = []
        for line_id_raw, line in enumerate(list(open(filepath, "r", encoding="utf-8"))):
            line = line.strip()
            line_id = line_id_raw + 1 # 行号，要求从 1 开始
            new_cmd_list.append(CommandWrap(filepath, line_id, line))
        self.cmd_list = new_cmd_list + self.cmd_list # 将新命令从头部追加到命令序列
        return True
    
    # 当前命令有可能来自命令行输入而不是文件
    def get_dirnow(self, filepath_str:str) -> str:
        if filepath_str == "<STDIN>": # 获取当前工作目录作为 DIRNOW
            return os.path.abspath(os.getcwd())
        else:
            return os.path.dirname(os.path.abspath(filepath_str))

    # 在所有可以使用的 include_path 中找到第一个匹配项目
    # cmd_file_now 是当前正在执行的命令所在的文件
    def get_first_match_dir(self, filename:str, cmd_file_now:str) -> Optional[str]:
        for path_now in self.include_path:
            # 这里的 "." 是一个特殊目录，表示当前脚本所在目录
            # 如果当前脚本是交互式输入的，则该目录是工作目录
            if path_now == ".":
                path_now = self.get_dirnow(cmd_file_now)
            hypo_filepath = os.path.abspath(os.path.join(path_now, filename))
            if os.path.isfile(hypo_filepath):
                return path_now
        return None

    # 执行特殊命令（井号开头的命令）
    def execute_special_cmd(self, cmd_now:CommandWrap):
        if self.verbose:
            print("FROM:", cmd_now.command.strip()) # 特殊命令就输出一个原始命令就行
        
        # 分离命令头部和命令内容
        first_part, other_part = cmd_now.command.split(maxsplit=1)
        assert first_part.startswith("#")
        first_part = first_part[1:]

        # 在这里给出所有特殊命令对应的列表
        if first_part == "include":         # 引入新文件命令
            rel_filepath = other_part.strip() # 获取文件相对路径
            if rel_filepath == "":            # 没有指定文件名
                raise ValueError()
            dirnow = self.get_first_match_dir(rel_filepath, cmd_now.filepath)
            if dirnow is None:
                raise FileNotFoundError(f"Can not include file \"{rel_filepath}\".")
            new_filepath = os.path.abspath(os.path.join(dirnow, rel_filepath))
            self.include_file(new_filepath.strip())

        else:
            raise ValueError(f"Special command \"#{first_part}\" not found!")

    # 执行指定的命令
    def execute_cmd(self, first_cmd:CommandWrap):
        if first_cmd.command.strip() == "": # 跳过空行
            return
        
        elif first_cmd.command.startswith("//"): # 跳过注释
            return

        elif first_cmd.command.startswith("#"): # 特殊命令
            self.execute_special_cmd(first_cmd)

        else:
            if first_cmd.command.find("=>") != -1: # 新增规则命令
                if self.verbose:
                    print("NEWR:", first_cmd.command)
                self.rule_set.add_rule(
                    ValueMap.deserialize(first_cmd.command))
        
            else: # 执行命令并输出计算结果
                value_term = ValueTerm.deserialize(f"[{first_cmd.command.strip()}]")
                if value_term.get_one_var() is not None:
                    raise ValueError(f"No variables (like \"{value_term.get_one_var()}\") allowed in the current expression.")
                new_value_term = self.rule_set.calc(value_term, self.verbose)
                print(new_value_term.serialize().strip()[1:-1]) # 输出前去掉中括号

    # 执行一条命令
    # 成功执行返回 True, 没有可执行命令返回 False
    # 执行命令时出错抛出异常
    def execute_one(self) -> bool:
        if len(self.cmd_list) == 0:
            return False
        # 获取第一条命令
        first_cmd, self.cmd_list = self.cmd_list[0], self.cmd_list[1:]
        if not isinstance(first_cmd, CommandWrap):
            raise TypeError()
        try:
            self.execute_cmd(first_cmd)
        except Exception as e:
            if self.extra_error_info or str(e) == "": # 报错信息太简单时候必须提供错误理由
                extra_info = f"\n{traceback.format_exc()}"
            else:
                extra_info = ""
            raise Exception(f"{first_cmd.filepath}:{first_cmd.line_id} {type(e).__name__}: {str(e)} {extra_info}")
        return True
    
    # 执行所有命令
    # 知道出现错误或者执行结束
    def execute_all(self):
        while True:
            flag = self.execute_one()
            if not flag: # 说明已经没有命令可以执行了
                break
    
    # 启动一个交互式用户界面
    def interactive_ui(self):
        line_id = 0
        while True:
            line_id += 1

            try:
                cmd = input(">>> ").strip()
                if cmd == "#exit": # 退出执行
                    print("Bye.")
                    break
                self.cmd_list.append(CommandWrap("<STDIN>", line_id, cmd.strip()))

                try:
                    # 执行所有出现的命令，直到无法执行为止
                    self.execute_all()
                except Exception as e:    # 遇到报错，输出错误信息
                    print(e)              # 当出现报错时，清空命令区域
                    self.cmd_list.clear() # 后续可以继续交互
            
            except:
                print("\nKeyboardInterrupt")
                print("Use #exit to quit xulang interactive CLI.")

    def run_file(self, filepath:str):
        self.include_file(filepath)
        self.execute_all() # 执行到无法执行为止

if __name__ == "__main__":
    file_runner = FileRunner([])
    file_runner.interactive_ui()
