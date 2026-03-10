import string
from typing import Optional

class SimpleTerm:
    def __init__(self) -> None:
        self.content = "simple_term" # 具体内容名称
        self.has_star = False        # 前缀 star

    @classmethod
    def init(cls, msg:str, has_star:bool) -> 'SimpleTerm':
        if not isinstance(has_star, bool):
            raise TypeError()
        if not isinstance(msg, str) or len(msg) == 0:
            raise TypeError()
        if msg == "_":
            raise ValueError('"_" is not an available identifier.') # 不能只留一个下划线
        if msg == ".":
            raise ValueError('"." is not an available identifier.') # 不能只留一个下划线
        if msg.find("..") != -1:
            raise ValueError('No consecutive dots in identifier.')
        if msg.startswith("."):
            raise ValueError('No leading dot in identifier.')
        if msg.endswith("."):
            raise ValueError("No trailing dot in identifier.")
        for i in range(len(msg)):
            if msg[i] not in (["_", "."] + [
                    char_now for char_now in string.ascii_letters
                ] + [
                    str(num_now) for num_now in range(10)
                ]):
                raise ValueError(f"Illegal character '{msg[i]}'.") # 字母数字下划线
            
        new_item = SimpleTerm()
        new_item.content = msg
        new_item.has_star = has_star
        return new_item
    
    def serialize(self) -> str:
        head = "*" if self.has_star else ""
        return head + self.content

    def json_obj(self) -> dict:
        return {
            "type": "SimpleTerm",
            "content": self.content,
            "has_star": self.has_star
        }

    @classmethod
    def deserialize(cls, s:str) -> 'SimpleTerm':
        s = s.strip()
        has_star = s.startswith("*")
        if has_star:
            s = s[1:] # 分离开头的 star
        return SimpleTerm.init(s, has_star)

    @classmethod
    def from_json_obj(cls, json_obj:dict) -> 'SimpleTerm':
        if json_obj.get("type") != "SimpleTerm":
            raise TypeError()
        if not isinstance(json_obj.get("content"), str):
            raise TypeError()
        if not isinstance(json_obj.get("has_star"), bool):
            raise TypeError()
        return SimpleTerm.init(
            json_obj["content"], json_obj["has_star"])
    
    # 大写字母或者数字开头的符号串
    # 视为常量
    @classmethod
    def is_const_val(cls, s:str) -> bool:
        if s == "":
            raise AssertionError()
        return s[0] in string.ascii_uppercase or s[0] in string.digits
    
    # 如果当前变量不是常量，则返回自己的序列化名
    # 如果当前变量是常量，则返回 None
    def get_one_var(self) -> Optional[str]:
        if SimpleTerm.is_const_val(self.serialize()):
            return None
        else:
            return self.serialize()

if __name__ == "__main__":
    term = SimpleTerm.init("hello", False)
    print(term.serialize())
    print(term.json_obj())
    print(SimpleTerm.deserialize(term.serialize()).json_obj())
