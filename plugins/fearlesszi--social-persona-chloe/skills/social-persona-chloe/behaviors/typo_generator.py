import random
import re

def inject_human_typos(text: str, typo_rate: float = 0.08) -> str:
    """
    根据给定的概率，在文本中注入典型的中文拼音输入法错误。
    """
    # 典型易错词库 (正确: 错误)
    common_typos = {
        "怎么": ["怎没", "造么", "怎么个肆"],
        "真的": ["蒸的", "真滴", "真的吖"],
        "其实": ["其实", "起手"],
        "已经": ["已近"],
        "时候": ["石斛", "时候"],
        "好喜欢": ["好稀罕"]
    }

    if random.random() > typo_rate:
        return text

    # 随机选择一个词进行替换
    words = list(common_typos.keys())
    random.shuffle(words)
    
    for word in words:
        if word in text:
            wrong_word = random.choice(common_typos[word])
            # 只替换一次，避免显得太刻意
            text = text.replace(word, wrong_word, 1)
            break
            
    # 模拟手抖：句子末尾多出一个字母
    if random.random() < 0.05:
        text += random.choice(["a", "s", "w"])
        
    return text

# 测试
# print(inject_human_typos("其实我今天真的很开心，你这个时候找我。"))