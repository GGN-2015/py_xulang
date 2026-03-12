from typing import Optional

try:
    from .ValueMap import ValueMap
    from .ValueTerm import ValueTerm
    from .MatchBraceSequence import match_brace_sequence
    from .FillValueTerm import fill_value_term
    from .Sequence import Sequence
    from .BraceSequence import BraceSequence
    from .SimpleTerm import SimpleTerm
except:
    from ValueMap import ValueMap
    from ValueTerm import ValueTerm
    from MatchBraceSequence import match_brace_sequence
    from FillValueTerm import fill_value_term
    from Sequence import Sequence
    from BraceSequence import BraceSequence
    from SimpleTerm import SimpleTerm

class ValueMapWrap:
    def __init__(self, index:int, value_map:ValueMap, filepath:str, line_id:int) -> None:
        self.value_map = value_map
        self.filepath = filepath
        self.line_id = line_id
        self.index = index # index 决定重新排序后的顺序

class RuleSet:
    def __init__(self) -> None:

        # self.value_map_dict 是用于快速检索可行命令的关键
        # 该 dict 构建了一个映射：从第一个元素映射到对应的命令序列
        # 如果某个 value_map.left 的第一个元素是常量，则应该放入这个常量对应的序列
        # 否则应该放入 "" 对应的序列
        # "" 对应的序列表示所有 value_map.left 中没有元素或者第一个元素不是常量的规则
        self.value_map_dict:dict[str, list[ValueMapWrap]] = dict()

        # 记录最后一次匹配所使用的命令信息
        self.latest_used_rule:Optional[ValueMapWrap] = None

        # 记录当前规则集合中总共有多少条规则，用于给规则排序
        self.rule_count_now = 0
    
    def safe_append(self, dic: dict[str, list[ValueMapWrap]], key:str, val:ValueMapWrap):
        if dic.get(key) is None:
            dic[key] = []
        dic[key].append(val)

    def add_rule(self, value_map: ValueMap, filepath:str, line_id:int): # 新增规则
        if not isinstance(value_map, ValueMap):
            raise TypeError()
        if not isinstance(value_map.left, BraceSequence):
            raise TypeError()

        # 获得新的规则编号
        self.rule_count_now += 1
        
        bad = False

        # 先考虑没有任何元素的情况
        item_cnt = len(value_map.left.inner_sequence.objects)
        if (not bad) and item_cnt == 0:
            bad = True
        
        # 试图获取第一个元素（如果没有元素则获取到空）
        if not bad:
            first_item = value_map.left.inner_sequence.objects[0]
        else:
            first_item = None
        
        # 有元素但是第一个元素不是 SimpleTerm
        if (not bad) and not isinstance(first_item, SimpleTerm):
            if not isinstance(first_item, BraceSequence):
                raise TypeError()
            bad = True
        
        # 第一个元素是 SimpleTerm 但不是常量
        assert isinstance(first_item, SimpleTerm)
        if (not bad) and not SimpleTerm.is_const_val(first_item.serialize()):
            bad = True
        
        # 第一个元素不符合快速检索规则
        if bad:
            self.safe_append(
                self.value_map_dict, "", # 放入空字符串对应的序列
                ValueMapWrap(self.rule_count_now, value_map, filepath, line_id))
        
        # 第一个元素符合快速检索规则
        else:
            if not isinstance(first_item, SimpleTerm):
                raise TypeError()
            if not SimpleTerm.is_const_val(first_item.serialize()):
                raise ValueError()
            self.safe_append(
                self.value_map_dict, first_item.serialize(), # 放入空字符串对应的序列
                ValueMapWrap(self.rule_count_now, value_map, filepath, line_id))

    # 获取所有可以使用的命令
    # 在获取命令时根据第一个元素进行初筛
    # 这种初筛可以显著提升算法效率
    def get_all_value_map_wrap(self, first_item:Optional[str]) -> list[ValueMapWrap]:
        arr = []

        # first_item 为 None 表示不对第一个符号进行快速筛查
        if first_item is None:
            for item in self.value_map_dict:
                arr += self.value_map_dict[item]

        # 需要对第一个符号进行快速筛查
        # 注意记得考虑 "" 对应的所有规则也需要参与比较
        else:
            for key_term in set([first_item, ""]): # 需要使用 set 去重，因为 first_item 可能是 ""
                if self.value_map_dict.get(key_term) is not None:
                    arr += self.value_map_dict[key_term]

        # 按照插入顺序排序（保证优先级正确）
        return sorted(arr, key=lambda x:x.index)

    # 显示所有的规则
    def show_rules(self, prefix:Optional[str]) -> str:
        int_width = len(str(len(self.get_all_value_map_wrap(None)))) + 1 # 编号需要的宽度
        arr = [
            ((
                ("%" + str(int_width) + "d ")
                    % value_map_wrap.index) 
                + value_map_wrap.value_map.serialize() + "\n"
            )
            for value_map_wrap in self.get_all_value_map_wrap(prefix)
        ]
        return "".join(arr)
    
    # 删除某个前缀对应的所有规则
    def erase_rule(self, prefix:str):
        if self.value_map_dict.get(prefix) is not None:
            del self.value_map_dict[prefix]
    
    # 根据 value_term 中内容的第一个元素进行快速分类
    def select_first_term_key(self, value_term:ValueTerm):
        if not isinstance(value_term.value, BraceSequence):
            raise AssertionError()
        
        # 如果其中没有元素
        if len(value_term.value.inner_sequence.objects) == 0:
            return ""
        
        # 如果其中有至少一个元素
        # 如果这个元素是复杂元素，也不可能和任意常量进行匹配
        first_item = value_term.value.inner_sequence.objects[0]
        if not isinstance(first_item, SimpleTerm):
            return ""
        
        # 理论上 value_term 中不可以存在变量，因此只要有 SimpleTerm 就一定是常量
        if not SimpleTerm.is_const_val(first_item.serialize()):
            raise AssertionError()
        return first_item.serialize()

    # 执行一次所有简单规则
    def execute_simple_rules(self, value_term:ValueTerm) -> tuple[bool, ValueTerm]:
        if not isinstance(value_term.value, BraceSequence):
            return False, value_term
        
        # 计算初筛分类
        first_term_key = self.select_first_term_key(value_term)

        # 根据初筛分类快速排除对象
        for value_map_wrap in self.get_all_value_map_wrap(first_term_key):
            value_map = value_map_wrap.value_map

            # 检查是否还能替换
            if isinstance(value_term.value, Sequence):
                break

            assert isinstance(value_map.left, BraceSequence)
            if value_map.left.has_sub_brace(): # 跳过复杂规则
                continue

            dic = dict()
            flag = match_brace_sequence(
                value_map.left, value_term.value, dic)
            
            if flag:
                value_term = fill_value_term(
                    value_map.right, dic
                )
                self.latest_used_rule = value_map_wrap
                return True, value_term

        # 返回最终结果
        return False, value_term

    def try_match_sons(self, value_term:ValueTerm) -> tuple[bool, ValueTerm]:
        if isinstance(value_term.value, BraceSequence):
            sub_obj_list = value_term.value.inner_sequence.objects
            value_type = BraceSequence
        else:
            sub_obj_list = value_term.value.objects
            value_type = Sequence

        suc = False
        new_sub_obj_list = []
        for i in range(len(sub_obj_list)):
            if type(sub_obj_list[i]) not in [BraceSequence, Sequence] or suc:
                new_sub_obj_list.append(sub_obj_list[i])
                continue
            flag, new_obj = self.calc_once(ValueTerm.init(sub_obj_list[i]))

            if isinstance(new_obj.value, BraceSequence):
                new_sub_obj_list.append(new_obj.value)
            else:
                assert isinstance(new_obj.value, Sequence)
                new_sub_obj_list += new_obj.value.objects # 追加模式

            if flag:
                suc = True # 至少进行了一次替换

        if value_type is BraceSequence:
            return suc, ValueTerm.init(BraceSequence.init(
                Sequence.init(new_sub_obj_list)
            ))
        else:
            return suc, ValueTerm.init(
                Sequence.init(new_sub_obj_list)
            )

    # 计算一个表达式的最终结果
    # verbose 模式可以显示计算过程
    def calc(self, value_term:ValueTerm, verbose:bool, step_mode:bool) -> ValueTerm:
        if verbose:
            print("FROM:", value_term.serialize()[1:-1])
        while True:
            flag, value_term = self.calc_once(value_term)
            if flag == False:
                break
            if self.latest_used_rule is not None:
                if verbose:
                    print("\nRULE:", self.latest_used_rule.value_map.serialize())
            if verbose:
                print("OUTP:", value_term.serialize()[1:-1])
                if step_mode:
                    input("(Continue?) ") # press enter to continue
        return value_term

    # 使用当前规则集合进行必要的计算
    def calc_once(self, value_term:ValueTerm) -> tuple[bool, ValueTerm]:

        if type(value_term.value) not in [Sequence, BraceSequence]:
            raise TypeError()

        # 先考虑外层是括号的情况
        if isinstance(value_term.value, BraceSequence):
            
            # 先枚举无嵌套规则并执行
            # 此时当前层已经不再能执行
            flag, value_term = self.execute_simple_rules(value_term)
            if flag:
                return True, value_term

            # 试图递归对所有成员执行算法
            flag, value_term = self.try_match_sons(value_term)
            if flag:
                return True, value_term
            
            
            # 试图对当前层进行复杂规则替换
            # 此时仍然需要根据第一个对象进行快速初筛
            first_item_key = self.select_first_term_key(value_term)
            for value_map_wrap in self.get_all_value_map_wrap(first_item_key):
                value_map = value_map_wrap.value_map
                
                assert isinstance(value_map, ValueMap)
                assert isinstance(value_term.value, BraceSequence)

                if value_map.left.has_sub_brace(): # 复杂规则
                    dic = dict()
                    flag = match_brace_sequence(
                        value_map.left, value_term.value, dic)
                    
                    if flag:
                        value_term = fill_value_term(value_map.right, dic)
                        self.latest_used_rule = value_map_wrap
                        return True, value_term
            
            return False, value_term
        
        else:

            # 直接对子元素进行递归即可
            if not isinstance(value_term.value, Sequence):
                raise AssertionError()
            
            # 试图递归对所有成员执行算法
            flag, value_term = self.try_match_sons(value_term)
            if flag:
                return True, value_term

            return False, value_term

if __name__ == "__main__":
    rule_set = RuleSet()
    rule_set.add_rule(ValueMap.deserialize("""
        (IF TRUE a b) => a"""), "<TEST>", 1)
    rule_set.add_rule(ValueMap.deserialize("""
        (IF FALSE a b) => b"""), "<TEST>", 2)
    rule_set.add_rule(ValueMap.deserialize("""
        (HEAD ()) => """), "<TEST>", 3)
    rule_set.add_rule(ValueMap.deserialize("""
        (HEAD (a *b)) => a"""), "<TEST>", 4)
    rule_set.add_rule(ValueMap.deserialize("""
        (REV ()) => ()"""), "<TEST>", 5)    
    rule_set.add_rule(ValueMap.deserialize("""
        (REV (a)) => (a)"""), "<TEST>", 6)
    rule_set.add_rule(ValueMap.deserialize("""
        (REV (a *b)) => (MERGE (REV (*b)) (a))"""), "<TEST>", 7)
    rule_set.add_rule(ValueMap.deserialize("""
        (MERGE (*a) (*b)) => (*a *b)"""), "<TEST>", 8)
    rule_set.add_rule(ValueMap.deserialize("""
        (TAIL (*a)) => (HEAD (REV (*a)))"""), "<TEST>", 9)
    
    for value_term_str in [
        "(IF TRUE 1 (TAIL (A B C D E)))",
        "(IF FALSE X (TAIL (A B C D E)))"
    ]:
        print("=" * 40)
        value_term = ValueTerm.deserialize(f"[{value_term_str}]")
        rule_set.calc(value_term, True, False)
