import re
from typing import Optional

class VarSet:
    def __init__(self) -> None:
        self.var_map:dict[str, str] = dict()

    # 定义一个变量
    def define_var(self, var_name:str, var_value:str):
        self.var_map[var_name] = var_value

    # 删除一个变量
    def undef_var(self, var_name:str):
        if self.var_map.get(var_name) is not None:
            del self.var_map[var_name]

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

    # 对一个字符串进行求值
    # 本质上就是替换，直到无法再替换为止
    def solve(self, s:str) -> str:
        while (can_replace := VarSet.what_can_replace(s)) is not None:
            var_name = can_replace[2:-1] # 删除前面的 "${" 和后面的 "}"
            if self.var_map.get(var_name) is None:
                raise ValueError(f"Macro var \"${{{var_name}}}\" is not defined.")
            s = s.replace(can_replace, self.var_map[var_name])
        
        # 把 "\n" 真的替换成换行符
        s = s.replace(r"\n", "\n")
        return s

if __name__ == "__main__":
    var_set = VarSet()
    var_set.define_var("x_1", "val_1")
    var_set.define_var("x_2", "val_2")
    var_set.define_var("d", "2")
    print(var_set.solve(r"${x_${d}}"))
