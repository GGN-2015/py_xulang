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

        # 为了正确序列化匹配的括号
        # 我们这里先假设对象是一个 Sequence
        value = Sequence.deserialize(s)

        # 如果发现这个 Sequence 中唯一的元素就是 BraceSequence
        # 再把这个元素拿出来
        if len(value.objects) == 1 and isinstance(value.objects[0], BraceSequence):
            value = value.objects[0]
        
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
    
    # 一种简单的数据表达方式
    # 在 python 传参接口中使用
    def simple_express(self) -> list:
        if isinstance(self.value, BraceSequence):
            return [self.value.simple_express()]
        else:
            if not isinstance(self.value, Sequence):
                raise TypeError()
            return self.value.simple_express()

if __name__ == "__main__":
    test_list = [
        "[]",            # 没有元素 Sequence
        "[a]",           # 单个元素 Sequence
        "[a (b c) d]",   # 三个元素 Sequence
        "[(a (b c) d)]", # 一个 BraceSequence
        "[(a b) (c d)]", # 多个 BraceSequence
    ]
    for value in test_list:
        value_term = ValueTerm.deserialize(value)
        print(value_term.serialize())
        print(ValueTerm.from_json_obj(value_term.json_obj()).serialize())
        print(value_term.simple_express())
        print()
