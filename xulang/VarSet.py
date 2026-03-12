import re
from typing import Optional

# 描述宏替换过程中使用到的变量集合
# 记录了每个变量的取值，以及一个栈空间（栈中只有值，没有变量名）
class VarSet:
    def __init__(self) -> None:

        # 记录所有宏变量的值
        # 注意：宏变量的值中可能含有换行符
        self.var_map:dict[str, str] = dict()

        # 维护一个变量值构成的栈
        # 可以在变量名冲突的前提下缓存变量信息
        self.var_val_stack:list[str] = []

    # 定义一个变量
    def define_var(self, var_name:str, var_value:str):
        self.var_map[var_name] = var_value

    # 删除一个变量
    def undef_var(self, var_name:str):
        if self.var_map.get(var_name) is not None:
            del self.var_map[var_name]

    # 把一个指定变量的值送到栈里
    def push_var(self, var_name:str):
        if self.var_map.get(var_name) is None:
            raise ValueError(f"Macro var {var_name} is not defined.")
        
        # 列表尾部是栈顶
        self.var_val_stack.append(self.var_map[var_name])

    # 从堆栈里取出一个值，存入指定的变量名
    def pop_var(self, var_name:str):
        if len(self.var_val_stack) == 0:
            raise ValueError("Macro stack is empty, can not pop.")
        self.var_map[var_name] = self.var_val_stack.pop()

    # 找到初次匹配的位置
    # 如果找不到返回 None
    @classmethod
    def match_first_or_empty(cls, pattern: str, text: str) -> Optional[str]:
        match = re.search(pattern, text)
        return match.group() if match else None

    # 找到可能可以替换的变量
    # 如果找到了则连着 ${...} 一起返回，如果找不到则返回 None
    @classmethod
    def what_can_replace(cls, s:str) -> Optional[str]:
        return cls.match_first_or_empty(r"\${[^{}\s]+}", s)

    # 只进行一次必要的替换，其他操作都不做
    # 如果含有字符型换行符，则替换成真换行符
    # 返回值的 bool 代表是否成功进行了替换操作
    def solve_once(self, s:str) -> tuple[bool, str]:
        if s.find(r"\n") != -1:
            s = s.replace(r"\n", "\n", count=1)
            return True, s
        if (can_replace := VarSet.what_can_replace(s)) is not None:
            var_name = can_replace[2:-1] # 删除前面的 "${" 和后面的 "}"
            if self.var_map.get(var_name) is None:
                raise ValueError(f"Macro var \"${{{var_name}}}\" is not defined.")
            s = s.replace(can_replace, self.var_map[var_name])
            return True, s
        return False, s

if __name__ == "__main__":
    var_set = VarSet()
    var_set.define_var("x_1", "val_1")
    var_set.define_var("x_2", "val_2")
    var_set.define_var("d", "2")
    print(var_set.solve_once(r"${x_${d}}"))
