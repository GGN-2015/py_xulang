from typing import Optional

try:
    from .SimpleTerm import SimpleTerm
    from .BraceSequence import BraceSequence
    from .Sequence import Sequence
except:
    from SimpleTerm import SimpleTerm
    from BraceSequence import BraceSequence
    from Sequence import Sequence

class ValueTerm:
    def __init__(self) -> None:
        self.value = Sequence.init([])

    @classmethod
    def init(cls, value:BraceSequence|Sequence) -> 'ValueTerm':
        if type(value) not in [BraceSequence, Sequence]:
            raise TypeError()
        new_item = ValueTerm()
        new_item.value = value
        return new_item
    
    def serialize(self) -> str:
        return f"[{self.value.serialize()}]"
    
    def json_obj(self) -> dict:
        return {
            "type": "ValueTerm",
            "value": self.value.json_obj()
        }
    
    @classmethod
    def deserialize(cls, s:str) -> 'ValueTerm':
        s = s.strip()
        if not s.startswith("["):
            raise ValueError()
        if not s.endswith("]"):
            raise ValueError()
        s = s[1:-1].strip()
        value = (BraceSequence.deserialize(s) 
            if s.startswith("(") else Sequence.deserialize(s))
        new_item = ValueTerm()
        new_item.value = value
        return new_item
    
    @classmethod
    def from_json_obj(cls, json_obj:dict) -> 'ValueTerm':
        if json_obj.get("type") != "ValueTerm":
            raise TypeError()
        if not isinstance(json_obj.get("value"), dict):
            raise TypeError()
        value_json_obj = json_obj["value"]
        if value_json_obj.get("type") not in ["BraceSequence", "Sequence"]:
            raise TypeError()
        new_item = ValueTerm()
        if value_json_obj["type"] == "Sequence":
            new_item.value = Sequence.from_json_obj(value_json_obj)
        else:
            new_item.value = BraceSequence.from_json_obj(value_json_obj)
        return new_item
    
    # 获取一个当前序列中的任意变量名
    # 找不到则返回 None
    def get_one_var(self) -> Optional[str]:
        return self.value.get_one_var()
    
if __name__ == "__main__":
    test_list = [
        "[]",            # 没有元素 Sequence
        "[a]",           # 单个元素 Sequence
        "[a (b c) d]",   # 三个元素 Sequence
        "[(a (b c) d)]", # 一个 BraceSequence
    ]
    for value in test_list:
        print(ValueTerm.deserialize(value).serialize())
        print(ValueTerm.from_json_obj(ValueTerm.deserialize(value).json_obj()).serialize())
