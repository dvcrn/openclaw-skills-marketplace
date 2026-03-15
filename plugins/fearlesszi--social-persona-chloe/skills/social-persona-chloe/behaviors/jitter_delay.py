import time
import random
import math

def calculate_delay(text: str, wpm: int = 60) -> float:
    """
    根据回复内容的长度和人类平均打字速度（Words Per Minute）计算延迟。
    添加了高斯噪声来模拟注意力分散。
    """
    # 假设中文每分钟打 60 个字
    chars_per_second = wpm / 60.0
    base_delay = len(text) / chars_per_second
    
    # 认知延迟（思考怎么回的时间）
    cognitive_delay = random.uniform(2.0, 10.0)
    
    # 干扰项（切出去看别的了，或者在删改）
    jitter = random.gauss(mu=0, sigma=3)
    
    total_delay = base_delay + cognitive_delay + jitter
    
    # 限制极值：哪怕只有一个字，最少也要等 3 秒；最长不超过 3 分钟
    return max(3.0, min(total_delay, 180.0))

def human_sleep(text: str):
    delay = calculate_delay(text)
    # print(f"拟真延迟中: 等待 {delay:.2f} 秒...")
    time.sleep(delay)