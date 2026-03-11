import os
import re
import traceback
from typing import Optional

try:
    from .RuleSet import RuleSet
    from .ValueMap import ValueMap
    from .ValueTerm import ValueTerm
    from .Sequence import Sequence
    from .BraceSequence import BraceSequence
    from .MatchBraceSequence import match_brace_sequence
    from .VarSet import VarSet
except:
    from RuleSet import RuleSet
    from ValueMap import ValueMap
    from ValueTerm import ValueTerm
    from Sequence import Sequence
    from BraceSequence import BraceSequence
    from MatchBraceSequence import match_brace_sequence
    from VarSet import VarSet

# 当前目录
DIRNOW = os.path.dirname(
    os.path.abspath(__file__))

# 标准库的 include 文件
INCLUDE_DIR = os.path.join(DIRNOW, 
    "include")

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
            os.path.abspath(path) for path in include_path_list] + [
                INCLUDE_DIR] 
        # 一定要把标准库放在最后
        # 因为 include_path 越靠前优先级越高

        # 用来记录，当前的运行模式是否是交互式的
        self.interactive_cli = False

        # 用于记录所有被宏指令 #define 出来的变量
        self.var_set = VarSet()

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
        all_lines = list(open(filepath, "r", encoding="utf-8"))
        line_id_raw = 0
        while line_id_raw < len(all_lines):
            line = all_lines[line_id_raw].strip()
            cnt = 1 # 记录目前的内容包括了多少行

            # 如果一行内容的末尾是右斜杠
            # 那么这一行应该和下一行连接起来视为一体的
            while line != "" and line[-1] == "\\" and line_id_raw + cnt < len(all_lines):
                line = line[:-1] + all_lines[line_id_raw + cnt].strip()
                cnt += 1
            while line != "" and line[-1] == "\\":
                line = line[:-1]
            if line.find("//") != -1:                          # 字符串中能够找到注释信息
                line = line.split("//", maxsplit=1)[0].strip() # 删除注释信息

            # 行号，要求从 1 开始
            # 多行内容合并后以第一行内容为准
            line_id = line_id_raw + 1 
            new_cmd_list.append(CommandWrap(filepath, line_id, line))

            # 跳过中间合并的行
            line_id_raw += cnt
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

    # 假设 self.cmd_list 中刚刚删除的命令是一个 #if 命令
    # 我们在这个序列中找到 #if 失败后的跳转位置
    # 如果找不到则返回 None
    # 这个命令也可以用来找 #else 匹配的 #endif
    # else_cnt_max = 1 表示我们正在处理 if 的跳转
    # else_cnt_max = 0 表示我们正在处理 else 的跳转
    def get_match_else_or_end_if_pos(self, else_cnt_max:int=1) -> Optional[int]:
        if else_cnt_max not in [0, 1]:
            raise AssertionError()
        layer = 1

        # 存储与当前 if 可能匹配的
        else_list = []
        end_if_list = []

        index = 0
        while index < len(self.cmd_list):
            if self.cmd_list[index].command.strip() == "#if":
                layer += 1
            elif self.cmd_list[index].command.strip() == "#endif":
                layer -= 1
            
            # 找到对应的内容
            # else 由于不执行 layer 的减法，因此应当和开始的 if 处于同一层次
            if layer == 1 and self.cmd_list[index].command.strip() == "#else":
                else_list.append(index)

            # endif 由于会对 layer - 1
            # 因此需要找到低一层的 endif 才是匹配的
            if layer == 0 and self.cmd_list[index].command.strip() == "#endif":
                end_if_list.append(index)

            # 没有找到与当前行匹配的 #endif
            index += 1
            if len(end_if_list) > 0: # 足够使用了
                break
        
        # 检查是否找到了恰好足够数目的 endif 和 else
        if len(end_if_list) == 0:
            raise ValueError("No matching \"#endif\" found.")
        if len(else_list) > else_cnt_max:
            raise ValueError("Redundant \"#else\" found.")
        
        # 找到匹配的 else 的行号
        # 如果 if 失败了可以跳到这里去
        if else_cnt_max == 1:
            return else_list[0] if len(else_list) == 1 else end_if_list[0]

        # else 只能跳转到 endif 不能跳转到其他 else
        else:
            return end_if_list[0]
        
    # 执行特殊命令（井号开头的命令）
    def execute_special_cmd(self, cmd_now:CommandWrap):
        if self.verbose:
            print("FROM:", cmd_now.command.strip()) # 特殊命令就输出一个原始命令就行
        
        # 分离命令头部和命令内容
        try:
            first_part, other_part = cmd_now.command.split(maxsplit=1)
            first_part = first_part.strip()
        except:
            first_part = cmd_now.command.strip()
            other_part = ""
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

        elif first_part == "exit":   # 直接停止程序
            self.cmd_list.clear()    # 通过清空后续代码的方式停止程序 (文件模式)

            # 如果是交互式命令行模式，则输出再见
            if self.interactive_cli: 
                # 注意，交互式命令行只有在读取文件中的 #exit 时才会遇到这种情况
                print(f"Bye. \n(#exit from {cmd_now.filepath}:{cmd_now.line_id})")
            self.interactive_cli = False 

        # 宏判断语句
        # 用法：#if value_1 value_2
        # 如果 value_2 的计算结果，可以和 value_1 中给出的模式匹配
        # 因此 value_1 和 value_2 必须都是括号表达式
        # 则继续执行
        # 否则跳转到对应的 #else 或者 #endif
        elif first_part == "if": 
            value_term = ValueTerm.deserialize(f"[{other_part}]")
            if not isinstance(value_term.value, Sequence) or len(value_term.value.objects) != 2:
                raise TypeError("\"#if\" requires exactly two parenthesized expressions.")
            
            # 提取出模板和值
            tmplate_term, brace_seq = value_term.value.objects
            if not isinstance(tmplate_term, BraceSequence) or not isinstance(brace_seq, BraceSequence):
                raise TypeError("\"#if\" requires exactly two parenthesized expressions.")
            
            # 检查是否能够完整匹配
            dic = dict()
            value_term = ValueTerm()     # 构建一个恰好包含一个 BraceSequence 的 ValueTerm
            value_term.value = brace_seq # type:ignore
            value_term = self.rule_set.calc(value_term, self.verbose)

            # 看前面给出的模板是否能和后面的内容匹配
            if isinstance(value_term.value, BraceSequence):
                flag = match_brace_sequence(tmplate_term, value_term.value, dic)
            else:
                flag = False

            # 由于条件正确，什么都不用做
            # 让程序继续执行即可
            if flag:
                if self.verbose:
                    print("INFO:", "\"#if\" match failed.") 

            # 如果条件不正确
            # 那么需要跳转到下一个 #else 或者 #endif 后
            else:
                # else_cnt_max=1 的含义是，最多可以吸收一个 else （当前语句是 if）
                skip_index = self.get_match_else_or_end_if_pos(else_cnt_max=1)
                if skip_index is None:
                    raise ValueError("No matching \"#else\" or \"#endif\" found.")
                # 中间的命令暴力跳过不执行
                self.cmd_list = self.cmd_list[skip_index+1:] 

                if self.verbose:
                    print("INFO:", f"{skip_index+1} lines skipped by \"#if\".")
        
        # 执行 #else 时，直接跳转到对应的 #endif 处即可
        elif first_part == "else":
            # else_cnt_max=10 的含义是，不能吸收else （当前语句是 else）
            skip_index = self.get_match_else_or_end_if_pos(else_cnt_max=0)
            if skip_index is None:
                raise ValueError("No matching \"#endif\" found.")
            # 中间的命令暴力跳过不执行
            self.cmd_list = self.cmd_list[skip_index+1:] 

            if self.verbose:
                print("INFO:", f"{skip_index+1} lines skipped by \"#else\".")

        # 该语句没有任何功能
        elif first_part == "endif":
            pass
        
        # 用于定义预处理替换变量
        elif first_part == "define":
            # 从命令中获取变量名称与其中存储的信息
            try:
                var_name, var_value = other_part.split(maxsplit=1)
            except:
                var_name = other_part
                var_value = ""
            var_name = var_name.strip()
            var_value = var_value.strip()
            if var_name == "": # 变量名为空
                raise ValueError("\"#define\" should followed by a var name.")
            if not bool(re.fullmatch(r'[_A-Za-z\.][_A-Za-z0-9\.]*', var_name)):
                raise ValueError(f"var name \"{var_name}\" is not allowed.")
            self.var_set.define_var(var_name, var_value)

        # 删除 define 定义出来的变量
        elif first_part == "undef":
            var_name = other_part.strip()
            if not bool(re.fullmatch(r'[_A-Za-z\.][_A-Za-z0-9\.]*', var_name)):
                raise ValueError(f"var name \"{var_name}\" is not allowed.")
            self.var_set.undef_var(var_name)

        # 没有匹配到相关命令
        else:
            raise ValueError(f"Special command \"#{first_part}\" not found!")

    # 执行指定的命令
    def execute_cmd(self, first_cmd:CommandWrap):

        # 开始考虑当前命令的执行
        # 注：井号开头的行不会做预处理替换
        if first_cmd.command.strip() == "": # 跳过空行
            return
        
        elif first_cmd.command.startswith("//"): # 跳过注释
            return

        # 对命令本身进行宏替换
        # 宏替换过程在所有东西之前做
        # 对于井号开头的命令，不做任何替换处理
        # 只对于一般语句进行替换处理
        if not first_cmd.command.strip().startswith("#"):
            preprocesspr_output = self.var_set.solve(first_cmd.command)
            preprocesspr_output = [
                line.strip()
                for line in preprocesspr_output.split("\n")
                if line.strip() != ""
            ]

            # 输出预处理器的输入以及预处理器的输出
            if self.verbose:
                if preprocesspr_output == [] or preprocesspr_output[0] != first_cmd.command:
                    print("\nPREI:", first_cmd.command)
                    print("PREO:", preprocesspr_output)

            # 说明这一行命令中没有命令
            if len(preprocesspr_output) == 0:
                return
            
            # 如果有多行命令，本次执行只能执行一条
            # 其余命令保持相同的行号，放在下次执行时再说
            elif len(preprocesspr_output) >= 1:
                first_cmd.command = preprocesspr_output[0]
                new_cmd_list = [
                    CommandWrap(first_cmd.filepath, first_cmd.line_id, preprocesspr_output[i])
                    for i in range(1, len(preprocesspr_output))
                ]
                self.cmd_list = new_cmd_list + self.cmd_list # 首部追加

        if first_cmd.command.startswith("#"): # 特殊命令
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
        self.interactive_cli = True # 表示进入交互式命令模式
        line_id = 1

        # 文件中的 exit 命令通过 self.interactive_cli = False 退出交互式命令行
        while self.interactive_cli: 

            try:
                cmd = input(">>> ").strip()
                if cmd == "#exit": # 退出执行
                    print(f"Bye. \n(#exit from <STDIN>:{line_id})")
                    break

                # 由于 #if 需要向后查询后文的代码
                # 但是我们的交互式命令输入暂时不支持多行输入
                # 因此我们暂时禁止命令行使用这个命令（将来可能可以解禁）
                if len(cmd.split()) >= 1 and cmd.split()[0] == "#if":
                    print(f"<STDIN>:{line_id} ValueError: \"#if\" is not allowed in interactive mode.")
                    continue

                self.cmd_list.append(CommandWrap("<STDIN>", line_id, cmd.strip()))

                # 空行和注释不增加编号
                if cmd.strip() == "" or cmd.strip().startswith("//"):
                    continue

                try:
                    # 执行所有出现的命令，直到无法执行为止
                    self.execute_all()
                except Exception as e:    # 遇到报错，输出错误信息
                    print(e)              # 当出现报错时，清空命令区域
                    self.cmd_list.clear() # 后续可以继续交互
                
                # 只有在正确执行时编号才增加
                line_id += 1
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                print("Use #exit to quit xulang interactive CLI.")
            except Exception as e:
                if str(e) == "": # 如果没有错误信息
                    traceback.print_exc()
                else: # 有错误信息则输出错误信息
                    print(f"<STDIN>:{line_id} {type(e).__name__}: {str(e)}")
        
        # 退出交互模式
        self.interactive_cli = False

    # 注意：需要使用绝对路径调用 filepath
    def run_file(self, filepath:str):
        try:
            self.include_file(filepath)
            try:
                # 执行所有出现的命令，直到无法执行为止
                self.execute_all()
            except Exception as e:    # 遇到报错，输出错误信息
                print(e)              # 当出现报错时，清空命令区域
                self.cmd_list.clear() # 退出程序
            print("(Execution finished normally.)") # 显示出执行正常结束

        except KeyboardInterrupt:
            print("(Execution killed by user.)")

if __name__ == "__main__":
    file_runner = FileRunner([])
    file_runner.interactive_ui()
