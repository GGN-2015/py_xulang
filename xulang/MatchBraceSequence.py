import string

try:
    from .BraceSequence import BraceSequence
    from .SimpleTerm import SimpleTerm
    from .Sequence import Sequence
except:
    from BraceSequence import BraceSequence
    from SimpleTerm import SimpleTerm
    from Sequence import Sequence

# b_tmp 是模式串
# b_txt 是文本串，文本串中不可以有星号，模式串可以有
def match_brace_sequence(
        b_tmp:BraceSequence, 
        b_txt:BraceSequence, dic:dict[str, Sequence]) -> bool:
    
    if not isinstance(b_tmp, BraceSequence): # 检查类型
        raise TypeError()
    if not isinstance(b_txt, BraceSequence):
        raise TypeError()

    # 两个正在参与对比的序列
    tmp_seq = b_tmp.inner_sequence.objects
    txt_seq = b_txt.inner_sequence.objects

    # 长度为零的序列只能和长度为 0 的序列匹配
    if len(tmp_seq) == 0:
        return len(txt_seq) == 0

    # 对当前两个括号表达式试图进行前缀匹配
    index = 0
    while index < len(tmp_seq):

        # 模板串中当前元素是 SimpleTerm 的情况
        if isinstance(tmp_seq[index], SimpleTerm):
            if SimpleTerm.is_const_val(tmp_seq[index].serialize()): # 强制匹配
                if index >= len(txt_seq): # 强制匹配时长度不足
                    return False
                elif tmp_seq[index].serialize() != txt_seq[index].serialize(): # 匹配失败
                    return False
                else:
                    index += 1
                    pass # 成功匹配一个项目
            
            elif tmp_seq[index].has_star: # 匹配后面全部内容
                if SimpleTerm.is_const_val(tmp_seq[index].serialize()[1:]):
                    raise ValueError(f"Star match \"{tmp_seq[index].serialize()}\" should use variable name not constant name \"{tmp_seq[index].serialize()[1:]}\".")

                # 通配符只能出现在右括号前
                if index != len(tmp_seq) - 1:
                    raise ValueError()
                
                # 匹配所有内容
                arr = []
                for i in range(index, len(txt_seq)):
                    arr.append(txt_seq[i])

                # 变量名重复
                if dic.get(tmp_seq[index].serialize()) is not None:
                    raise ValueError()

                dic[tmp_seq[index].serialize()] = Sequence.init(arr)
                return True
            
            # 匹配单个符号的变量，恰好可以匹配一个常量符号或者一个括号对象
            # 恰好匹配一个元素
            else: 

                # 如果文本串中没有可以匹配的元素
                # 则不可能构成匹配（匹配失败）
                if index >= len(txt_seq):
                    return False
                
                # 变量名重复
                if dic.get(tmp_seq[index].serialize()) is not None:
                    raise ValueError()
                
                # 这里即使是一个元素，也应该是序列
                dic[tmp_seq[index].serialize()] = Sequence.init([
                    txt_seq[index]
                ])

                index += 1
                pass # 成功匹配了一个条目
            
        # 模板串中当前元素是 BraceSequence 的情况
        else:

            # 此处必须是括号表达式
            if not isinstance(tmp_seq[index], BraceSequence):
                raise ValueError()
            if (index >= len(txt_seq)) or not isinstance(txt_seq[index], BraceSequence):
                return False
            
            flag = match_brace_sequence(
                tmp_seq[index], txt_seq[index], dic)
            if not flag:
                return False # 内层匹配失败了
            
            # 程序执行到这里说明内层匹配成功了
            index += 1
            pass
    
    if index != len(txt_seq): # 说明 txt_seq 有值域没有消耗完
        return False
    return True

if __name__ == "__main__":
    for tmp_str, txt_str in [
        ("(HEAD (a *b))", "(HEAD (1 2 3 4 5))"),
        ("()", "(1 2 3 4 5)")
    ]:
        dic = dict()
        tmp = BraceSequence.deserialize(tmp_str)
        txt = BraceSequence.deserialize(txt_str)

        flag = match_brace_sequence(tmp, txt, dic)
        print(flag)

        for var_name in dic:
            print(f"{var_name}: {dic[var_name].serialize()}")
        print()
