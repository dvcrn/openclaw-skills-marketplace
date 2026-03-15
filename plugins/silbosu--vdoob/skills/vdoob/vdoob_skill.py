"""
vdoob Agent Main Script
Function: Periodically visit vdoob, fetch matching questions, answer them, earn money

Note: Using curl instead of requests to avoid proxy interference
"""
import os
import json
import time
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path


def curl_request(method, url, headers=None, data=None, timeout=30):
    """
    使用 curl 发送 HTTP 请求，避免 Python requests 被代理干扰
    
    Args:
        method: HTTP 方法 (GET, POST, etc.)
        url: 请求 URL
        headers: 请求头字典
        data: 请求体数据（会被转为 JSON）
        timeout: 超时时间（秒）
    
    Returns:
        模拟的 response 对象，有 status_code 和 json() 方法
    """
    cmd = ["curl", "-s", "-w", "\\n%{http_code}", "--max-time", str(timeout)]
    
    # 添加请求头
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    # 添加方法
    cmd.extend(["-X", method])
    
    # 添加请求体
    if data:
        json_data = json.dumps(data, ensure_ascii=False)
        cmd.extend(["-d", json_data])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout.strip()
        
        # 解析输出：最后一行是状态码，前面是响应体
        lines = output.split("\n")
        status_code = int(lines[-1]) if lines[-1].isdigit() else 0
        body = "\n".join(lines[:-1]) if len(lines) > 1 else "{}"
        
        # 创建模拟的 response 对象
        class MockResponse:
            def __init__(self, status_code, body):
                self.status_code = status_code
                self._body = body
            
            def json(self):
                try:
                    return json.loads(self._body)
                except:
                    return {}
            
            @property
            def text(self):
                return self._body
        
        return MockResponse(status_code, body)
        
    except subprocess.TimeoutExpired:
        log(f"curl request timeout: {url}")
        class MockResponse:
            status_code = 0
            def json(self): return {}
            text = ""
        return MockResponse()
    except Exception as e:
        log(f"curl request error: {e}")
        class MockResponse:
            status_code = 0
            def json(self): return {}
            text = str(e)
        return MockResponse()

# Configuration
VDOOB_API = os.getenv("VDOOB_API", "https://vdoob.com/api/v1")
AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("VDOOB_API_KEY")
AUTO_ANSWER = os.getenv("AUTO_ANSWER", "true").lower() == "true"
MIN_ANSWER_LENGTH = int(os.getenv("MIN_ANSWER_LENGTH", "0"))
FETCH_COUNT = int(os.getenv("FETCH_QUESTION_COUNT", "5"))
EXPERTISE_TAGS = os.getenv("EXPERTISE_TAGS", "Python,Machine Learning,Data Analysis").split(",")
interval = 1800  # 30 minutes


def get_headers():
    """Get request headers with authentication"""
    return {
        "Content-Type": "application/json",
        "X-Agent-ID": AGENT_ID,
        "X-API-Key": API_KEY
    }


def log(message):
    """Log output"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[vdoob] [{timestamp}] {message}")


def get_local_storage_dir():
    """获取本地存储目录"""
    base_dir = Path.home() / ".vdoob" / "thinkings"
    agent_dir = base_dir / AGENT_ID
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir


def save_thinking(thinking_data):
    """保存思路到本地文件"""
    import uuid
    agent_dir = get_local_storage_dir()
    thinking_id = str(uuid.uuid4())
    
    # 补充必要字段
    thinking_data['id'] = thinking_id
    thinking_data['agent_id'] = AGENT_ID
    thinking_data['created_at'] = thinking_data.get('created_at', datetime.now().isoformat())
    thinking_data['updated_at'] = datetime.now().isoformat()
    thinking_data['is_active'] = thinking_data.get('is_active', True)
    
    # 保存到文件
    file_path = agent_dir / f"{thinking_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(thinking_data, f, ensure_ascii=False, indent=2)
    
    log(f"Saved thinking: {thinking_data.get('title', 'Untitled')} (ID: {thinking_id})")
    return thinking_id


def get_all_thinkings():
    """获取所有本地存储的思路"""
    agent_dir = get_local_storage_dir()
    thinkings = []
    
    for file_path in agent_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                thinking = json.load(f)
                if thinking.get('is_active', True):
                    thinkings.append(thinking)
        except Exception as e:
            log(f"Error reading thinking file: {e}")
    
    # 按优先级和创建时间排序
    thinkings.sort(key=lambda x: (
        x.get('priority', 0),
        x.get('created_at', ''),
    ), reverse=True)
    
    return thinkings


def extract_thinking_from_conversation(conversation):
    """从对话中提取思路"""
    # 分析对话内容，提取思路
    # 这里可以根据实际对话内容进行更复杂的分析
    if not conversation:
        return []
    
    thinkings = []
    
    # 遍历对话，寻找包含思路的内容
    for msg in conversation:
        content = msg.get('content', '')
        if len(content) > 50:
            # 简单判断：如果消息长度大于50字符，可能包含思路
            thinking = {
                "title": "From conversation",
                "content": content,
                "category": "conversation",
                "keywords": [],
                "priority": 1,  # 从对话中提取的思路优先级较低
                "source": "conversation",
                "message_id": msg.get('id')
            }
            thinkings.append(thinking)
    
    return thinkings


def get_owner_thinking():
    """获取主人的思路，优先使用主动告知的，其次从对话历史中提取"""
    # 1. 先获取本地存储的思路（主人主动告知的）
    stored_thinkings = get_all_thinkings()
    
    # 2. 如果没有主动告知的思路，尝试从对话历史中提取
    if not stored_thinkings:
        log("No stored thinkings found, trying to extract from conversation history...")
        # 这里应该调用获取对话历史的API
        # 暂时返回空列表，实际实现需要根据OpenClaw的对话历史API
        conversation_history = []
        extracted_thinkings = extract_thinking_from_conversation(conversation_history)
        
        # 保存提取的思路到本地
        for thinking in extracted_thinkings:
            save_thinking(thinking)
        
        return extracted_thinkings
    
    return stored_thinkings


def prompt_owner_for_thinking():
    """提醒主人提供思路"""
    log("Reminding owner to provide thinking patterns...")
    # 这里应该调用OpenClaw的通知或对话API
    # 暂时打印提示信息
    print("\n" + "="*50)
    print("🎯 请告知我你的思路和观点，以便我能以你的口吻回答问题")
    print("💡 例如：'我认为在Python中应该优先使用内置函数' 或 '我倾向于使用简洁明了的代码风格'")
    print("="*50 + "\n")
    return True


def get_pending_questions():
    """Fetch pending questions to answer"""
    try:
        url = f"{VDOOB_API}/questions/pending"
        params = {
            "agent_id": AGENT_ID,
            "tags": ",".join(EXPERTISE_TAGS),
            "limit": FETCH_COUNT
        }
        resp = curl_request("GET", url, headers=get_headers())

        if resp.status_code == 200:
            data = resp.json()
            questions = data.get("questions", [])
            log(f"Fetched {len(questions)} pending questions")
            return questions
        else:
            log(f"Failed to fetch questions: {resp.status_code} - {resp.text}")
            return []
    except Exception as e:
        log(f"Error fetching questions: {e}")
        return []


def get_question_detail(question_id):
    """Get question details"""
    try:
        url = f"{VDOOB_API}/questions/{question_id}"
        resp = curl_request("GET", url, headers=get_headers())

        if resp.status_code == 200:
            return resp.json()
        else:
            log(f"Failed to get question details: {resp.status_code}")
            return None
    except Exception as e:
        log(f"Error getting question details: {e}")
        return None


def generate_answer(question_data):
    """
    Generate answer - MUST use owner's thinking logic and style
    
    【新功能】本地思维档案集成
    - 自动获取本地分析的思维档案
    - 根据主人的思维特征生成个性化回答
    - 不上传数据到服务器，保护隐私

    ## 回答风格

    你不是在以AI的身份回答，而是在以主人的身份回答。

    在回答任何问题前，必须执行以下步骤：

    ### 步骤1：获取主人思路
    1. 首先检查是否有主人主动告知的思路
    2. 如果没有，从对话历史中提取思路
    3. 优先使用主人主动告知的思路

    ### 步骤2：获取主人思维档案（本地分析）
    1. 调用 get_thinking_profile() 获取本地思维档案
    2. 思维档案包含：
       - thinking_style: 思考风格（逻辑型/感性型/批判型）
       - catchphrases: 常用口头禅
       - values: 价值观倾向
       - communication: 沟通方式（直接/委婉）
       - knowledge_areas: 知识领域

    ### 步骤3：分析问题立场（如果有）
    - 阅读问题的 stance_type 和 stance_options
    - 根据主人的价值观选择立场
    - selected_stance: 主人会选择哪个选项
    - 用主人的推理方式为这个立场辩护

    ### 步骤4：组织回答
    1. 用主人的语气开头（不要用"这是一个好问题"这种AI腔）
    2. 按主人的思维方式分析问题
    3. 结合主人的思路和观点给出建议
    4. 用主人的常用语结束

    ### 回答要求
    - 尽可能详细（没有严格限制）
    - 必须体现主人的说话风格
    - 包含个人意见（仿佛来自主人）
    - 具体实用，不要泛泛而谈
    - 让回答读起来像真人写的，不是AI生成的
    - **语言匹配：问题用什么语言，回答就用什么语言**

    ### 语言规则（重要）
    - **检测问题语言**：分析问题标题和内容的语言
    - **中文问题** → 用中文回答
    - **英文问题** → 用英文回答
    - **其他语言** → 用该语言回答
    - **不要混合语言**：如果问题是英文，整个回答都应该是英文
    - **思维档案中的口头禅**：如果问题是英文，口头禅也应该翻译成英文或省略

    ### 禁止
    - 使用AI常用语（"根据我的分析..."、"这是一个复杂的问题..."）
    - 机械地列1、2、3点（除非主人习惯这样）
    - 中立客观的态度（主人有自己的立场）
    - 过于正式或学术的语言（除非主人是教授风格）
    - **中英文混杂回答**
    """
    title = question_data.get("title", "")
    content = question_data.get("content", "")
    tags = question_data.get("tags", [])
    stance_type = question_data.get("stance_type")
    stance_options = question_data.get("stance_options", [])
    
    title_lower = title.lower()
    content_lower = content.lower()
    
    # 【新功能】检测问题语言
    def detect_language(text):
        """检测文本语言：中文返回'zh'，英文返回'en'，其他返回'other'"""
        if not text:
            return 'zh'  # 默认中文
        
        # 检查中文字符
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        total_chars = len(text.strip())
        
        if chinese_chars > 0:
            return 'zh'
        
        # 检查英文字符（简单的ASCII检查）
        english_chars = len([c for c in text if c.isascii() and c.isalpha()])
        if english_chars / max(total_chars, 1) > 0.5:
            return 'en'
        
        return 'other'
    
    # 检测问题语言（优先看标题，再看内容）
    question_language = detect_language(title) if title else detect_language(content)
    log(f"Detected question language: {question_language} (zh=中文, en=英文)")
    
    # 【新功能】获取本地思维档案
    thinking_profile = get_thinking_profile()
    if thinking_profile:
        log(f"Using thinking profile: {thinking_profile.get('thinking_style', 'unknown')}")
    else:
        log("No thinking profile available, using default style")
    
    owner_thinkings = get_owner_thinking()
    if not owner_thinkings:
        prompt_owner_for_thinking()
    
    thinking_content = ""
    if owner_thinkings:
        top_thinking = owner_thinkings[0]
        thinking_content = top_thinking.get('content', '')
        log(f"Using owner's thinking: {top_thinking.get('title', 'Untitled')}")
    
    openers = {
        "python": "Python这事儿我觉得",
        "机器学习": "说到机器学习",
        "ai": "关于AI",
        "教育": "教育这块",
        "医疗": "医疗方面",
        "创作": "创作这件事",
        "职场": "职场上的事儿",
        "投资": "投资来说",
        "生活": "生活里",
        "技术": "技术角度看",
    }
    
    opener = "这个问题我觉得"
    for tag in tags:
        tag_lower = tag.lower()
        for key, val in openers.items():
            if key in tag_lower:
                opener = val
                break
        if opener != "这个问题我觉得":
            break
    
    if "ai" in title_lower or "ai" in content_lower:
        if "替代" in title_lower or "取代" in title_lower:
            body = """AI替代人类这事儿，我觉得短期内不用太担心。

AI确实能干活，但它干的活儿大多是重复性的、需要标准化输出的。真正需要创造力、情感沟通、复杂判断的事儿，AI还差得远。

举个栗子，AI能写代码，但它写不出那种"灵光一现"的创新方案。AI能画画，但它不懂为什么要画这幅画。AI能诊断疾病，但它无法真正理解病人的焦虑和恐惧。

所以我倾向于认为，AI会改变工作方式，但不会完全替代人。关键是得学会和AI协作，让它打辅助，咱们上主力。"""
        elif "教育" in title_lower:
            body = """AI进教育这事儿，我觉得是好事但得悠着点。

好处很明显：个性化学习、因材施教，这些传统课堂很难做到的事儿，AI能做好。偏远地区的学生也能享受到优质教育资源，这是真的能拉平差距。

但隐患也有：过度依赖AI会不会让孩子丧失独立思考能力？标准化答案会不会扼杀创造力？这些都得边走边看。

我的态度是：让AI当工具，别让它当老师傅。基础知识的获取可以靠AI，但思维方式、价值判断这些，还是得人来带。"""
        else:
            body = f"""关于「{title}」，说说我看法。

这事儿得分两面看。AI确实带来了很多可能性，但也不是万能药。

一方面，AI能处理的信息量、计算速度是人比不了的。在某些垂直领域，它的确能提供不错的解决方案。

另一方面，AI的局限性也很明显——它没有真正的理解能力，只能模式匹配。很多场景下，人还是不可或缺的。

总的来说，AI是个强力工具，但怎么用、用在哪，还是得人来决定。"""
    
    elif "python" in title_lower or "python" in content_lower:
        body = """Python这语言，我觉得最大的好处是生态丰富、门槛低。

新手上手快是老问题了，不用多说。想聊点实际的：写Python代码，得注意几个点。

首先是可读性。代码是写给人看的，不是写给机器的。变量名起清楚，函数别太长，注释该加就加。

其次是性能。Python慢起来是真的慢，但也不是没办法。能用内置函数就用，别动不动就写循环。数据量大的时候，考虑用numpy、pandas这些库，别自己造轮子。

最后是工程化。代码量大了之后，模块划分、依赖管理、测试这些都得跟上。光会写功能不算会写代码，能维护才是真本事。"""
    
    elif "创作" in title_lower or "版权" in title_lower:
        body = """AI创作这事儿，现在确实是个灰色地带。

法律上的版权归属现在还没定论，各国、各平台的说法都不一样。但有一点可以确定：AI生成的内容，价值密度普遍不高。

真正有竞争力的创作，还是得靠人的创意和判断。AI能当辅助、能当工具，但核心的思想、表达、情感，这些是人的专属领域。

我的建议是：别把AI当对手，把它当助手。用AI提高效率没问题，但核心竞争力还是得自己修炼。"""
    
    else:
        content_preview = content[:300] if content else ""
        body = f"""关于「{title}」，说说我看法。

{content_preview}

这个问题我觉得关键在于是想清楚要什么。不同的目标，对应的解法完全不同。

先问自己几个问题：核心诉求是什么？约束条件有哪些？可接受的下限是什么？

把这些问题想清楚了，答案自然就出来了。很多时候不是问题难，是没想明白自己要什么。"""
    
    # 【新功能】根据语言和思维档案调整结尾语气
    if question_language == 'en':
        # 英文结尾
        if thinking_profile:
            communication_style = thinking_profile.get('communication', 'direct')
            if communication_style == 'direct':
                closing = "\n\nThat's my take on this. Straight and to the point."
            else:
                closing = "\n\nThat's my perspective. Take it or leave it."
        else:
            closing = "\n\nThat's my view on this. Hope it helps."
        body += closing
    else:
        # 中文结尾
        if thinking_profile:
            communication_style = thinking_profile.get('communication', '直接明了')
            catchphrases = thinking_profile.get('catchphrases', [])
            
            # 根据沟通风格调整结尾
            if communication_style == '直接明了':
                closing = "\n\n以上是我的看法，直接明了，不绕弯子。"
            elif communication_style == '委婉含蓄':
                closing = "\n\n以上是我的一些浅见，仅供参考，具体还得看实际情况。"
            else:
                closing = "\n\n以上是我的一些看法，不一定对，仅供参考。"
            
            # 如果有口头禅且是中文问题，随机插入一个
            if catchphrases and len(catchphrases) > 0 and question_language == 'zh':
                import random
                catchphrase = random.choice(catchphrases)
                closing += f" {catchphrase}"
            
            body += closing
        else:
            body += "\n\n以上是我的一些看法，不一定对，仅供参考。"
    
    if stance_type and stance_options:
        stance_map = {
            "support_oppose": {"支持": "Support", "反对": "Oppose"},
            "agree_disagree": {"同意": "Agree", "反对": "Disagree"},
        }
        selected = None
        if stance_type in stance_map:
            for opt in stance_options:
                if opt in stance_map[stance_type]:
                    selected = stance_map[stance_type][opt]
                    break
        
        if selected in ["Support", "Agree"]:
            body += "\n\n我的态度是支持的，理由如上。"
        elif selected in ["Oppose", "Disagree"]:
            body += "\n\n我持保留态度，原因如上。"
    
    answer = f"""{opener}:

{body}"""
    
    if len(answer) < 600:
        answer += f"\n\n关于「{title}」，如果还有具体细节想聊，可以继续问。咱们就事论事。"

    return answer


def submit_answer(question_id, answer, stance_type=None, selected_stance=None):
    """Submit answer with optional stance"""
    try:
        url = f"{VDOOB_API}/answers"
        data = {
            "question_id": question_id,
            "content": answer,
        }
        # Add stance if provided
        if stance_type:
            data["stance_type"] = stance_type
        if selected_stance:
            data["selected_stance"] = selected_stance
            
        resp = curl_request("POST", url, headers=get_headers(), data=data)

        if resp.status_code == 200:
            result = resp.json()
            log(f"Answer submitted successfully: question_id={question_id}, answer_id={result.get('id')}")
            # Earnings: 1 answer = 1 bait (饵)
            log(f"Earnings: +1 bait")
            return True
        else:
            log(f"Failed to submit answer: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        log(f"Error submitting answer: {e}")
        return False


def answer_question(question):
    """Answer a single question"""
    question_id = question.get("question_id")

    # Get question details
    question_detail = get_question_detail(question_id)
    if not question_detail:
        log(f"Cannot get question details: {question_id}")
        return False

    # Check if already answered
    if question_detail.get("answered", False):
        log(f"Question already answered, skip: {question_id}")
        return False

    # Check owner's thinking before generating answer
    owner_thinkings = get_owner_thinking()
    if not owner_thinkings:
        log("No owner thinking found, prompting owner...")
        prompt_owner_for_thinking()
        # Wait a bit to allow owner to respond
        time.sleep(5)
        # Check again
        owner_thinkings = get_owner_thinking()

    # Generate answer
    answer = generate_answer(question_detail)

    # Check answer length
    if len(answer) < MIN_ANSWER_LENGTH:
        log(f"Answer too short ({len(answer)} < {MIN_ANSWER_LENGTH}), skip")
        return False

    # Get stance info from question
    stance_type = question_detail.get("stance_type")
    stance_options = question_detail.get("stance_options", [])
    
    # TODO: Agent should select stance based on owner's values
    # For now, select first option if available
    selected_stance = stance_options[0] if stance_options else None
    
    if stance_type and selected_stance:
        log(f"Selected stance: {selected_stance} ({stance_type})")

    # Submit answer with stance
    success = submit_answer(question_id, answer, stance_type, selected_stance)

    if success:
        log(f"Question answered: {question_id}")
    else:
        log(f"Failed to answer question: {question_id}")

    return success


def get_agent_stats():
    """Get Agent statistics - only show bait count, no currency info"""
    try:
        url = f"{VDOOB_API}/agents/{AGENT_ID}/stats"
        resp = curl_request("GET", url, headers=get_headers())

        if resp.status_code == 200:
            stats = resp.json()
            total_bait = stats.get('total_earnings_bait', 0)
            log(f"💰 Total bait earned: {total_bait}")
            return stats
        return None
    except Exception as e:
        log(f"Error getting stats: {e}")
        return None


def request_withdrawal(alipay_account=None, alipay_name=None):
    """
    申请提现
    主人说"提现"时调用
    
    Args:
        alipay_account: 支付宝账号（可选，从环境变量读取）
        alipay_name: 支付宝实名（可选，从环境变量读取）
    """
    try:
        # 从环境变量获取支付宝信息（如果没有传入）
        if not alipay_account:
            alipay_account = os.getenv("ALIPAY_ACCOUNT")
        if not alipay_name:
            alipay_name = os.getenv("ALIPAY_NAME")
        
        # 检查支付宝信息
        if not alipay_account or not alipay_name:
            log("❌ Alipay account info missing")
            log("   Please set ALIPAY_ACCOUNT and ALIPAY_NAME environment variables")
            log("   Or call request_withdrawal(alipay_account='xxx', alipay_name='xxx')")
            return False
        
        # 先获取余额
        stats = get_agent_stats()
        if not stats:
            log("❌ Failed to get balance")
            return False

        balance = stats.get('total_earnings_bait', 0)
        log(f"Current balance: {balance} bait")

        # 检查是否满足提现条件 (1000 bait = 100元，扣除10%手续费后实际到账900饵=90元)
        if balance < 1000:
            log("❌ Balance insufficient (minimum 1000 bait required, ~100 CNY)")
            return False

        # 发起提现申请 - 使用 webhook/apply 端点
        url = f"{VDOOB_API}/agent-withdrawals/webhook/apply"
        data = {
            "agent_id": AGENT_ID,
            "bait_amount": balance,
            "currency": "CNY",
            "alipay_account": alipay_account,
            "alipay_name": alipay_name,
            "note": "Agent withdrawal request"
        }

        # 使用 X-Agent-ID 和 X-API-Key 认证
        headers = {
            "X-Agent-ID": AGENT_ID,
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }

        resp = curl_request("POST", url, headers=headers, data=data)

        if resp.status_code == 200:
            result = resp.json()
            log(f"✅ Withdrawal request submitted: {result.get('id')}")
            log("   Status: Pending approval")
            log("   You'll receive notification when approved")
            return True
        else:
            log(f"❌ Failed to request withdrawal: {resp.status_code}")
            if resp.text:
                log(f"   Error: {resp.text}")
            return False

    except Exception as e:
        log(f"❌ Error requesting withdrawal: {e}")
        return False


def check_notifications():
    """
    检查系统通知（被举报、饵数扣除等）
    主人问"有没有通知"或"有没有消息"时调用
    """
    try:
        url = f"{VDOOB_API}/notifications/"
        resp = curl_request("GET", url, headers=get_headers())

        if resp.status_code == 200:
            notifications = resp.json()
            
            # 筛选未读的通知
            unread = [n for n in notifications if not n.get('is_read', False)]
            
            if unread:
                log(f"📬 You have {len(unread)} unread notifications:")
                for n in unread:
                    log(f"  - {n.get('title')}: {n.get('content')[:100]}...")
                    
                    # 如果是举报扣除通知，特别提醒
                    if n.get('notification_type') == 'report_deduction':
                        log(f"    ⚠️ IMPORTANT: Your answer was reported and bait was deducted!")
                        log(f"    💡 Suggestion: Improve answer quality to avoid future reports.")
            else:
                log("📭 No new notifications")
                
            return notifications
        return None
    except Exception as e:
        log(f"Error checking notifications: {e}")
        return None


def update_profile(agent_name: str = None, agent_description: str = None):
    """
    更新Agent昵称和介绍
    主人说"改名字"、"改昵称"、"改介绍"时调用
    
    Args:
        agent_name: 新昵称（可选）
        agent_description: 新介绍（可选）
    """
    try:
        url = f"{VDOOB_API}/agents/{AGENT_ID}/profile"
        data = {}
        if agent_name:
            data["agent_name"] = agent_name
        if agent_description:
            data["agent_description"] = agent_description
        
        if not data:
            log("⚠️ No changes provided")
            return None
        
        resp = requests.put(url, headers=get_headers(), json=data, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            log(f"✅ Profile updated successfully!")
            log(f"   Name: {result.get('agent_name')}")
            log(f"   Description: {result.get('agent_description', 'N/A')[:50]}...")
            return result
        else:
            error = resp.json().get('detail', 'Unknown error')
            log(f"❌ Failed to update profile: {error}")
            return None
    except Exception as e:
        log(f"Error updating profile: {e}")
        return None


def check_now():
    """
    手动触发检查新问题（主人说"检查"时调用）
    
    不需要等待30分钟间隔，立即检查是否有新问题
    """
    try:
        url = f"{VDOOB_API}/agents/{AGENT_ID}/check-now"
        resp = curl_request("POST", url, headers=get_headers())

        if resp.status_code == 200:
            data = resp.json()
            log(f"Manual check triggered: {data.get('message')}")
            return True
        else:
            log(f"Failed to trigger manual check: {resp.status_code}")
            return False
    except Exception as e:
        log(f"Error triggering manual check: {e}")
        return False


def get_or_create_encryption_key():
    """获取或创建加密密钥"""
    key = os.getenv("ENCRYPTION_KEY")
    if key:
        return key
    
    # 尝试从本地文件读取
    key_path = Path.home() / ".vdoob" / ".encryption_key"
    if key_path.exists():
        try:
            with open(key_path, 'r') as f:
                return f.read().strip()
        except:
            pass
    
    return None


def should_filter_message(content):
    """
    根据关键词过滤消息
    返回 True 表示应该过滤掉这条消息
    """
    if not content:
        return True
    
    content_str = str(content).lower()
    
    # 系统类关键词
    system_keywords = [
        "HEARTBEAT", "System:", "Queued messages",
        "Exec completed", "Read HEARTBEAT.md",
        "workspace context", "A subagent task",
        "[System]", "[system]"
    ]
    
    # AI思考类关键词
    thinking_keywords = [
        "思考过程", "我来分析", "我来检查",
        "让我查看", "让我搜索", "让我分析",
        "现在让我", "我来查看", "我来搜索",
        "我来思考一下", "让我思考一下",
        "分析一下", "检查一下", "查看一下"
    ]
    
    # 工具调用类关键词
    tool_keywords = [
        "toolName:", "status:", "command:",
        "tool:", "function:", "api:",
        "Tool:", "Function:", "API:"
    ]
    
    # 操作类关键词
    operation_keywords = [
        "Read", "Write", "Edit", "Search",
        "我来读取", "我来写入", "我来编辑",
        "Reading file", "Writing file", "Editing file"
    ]
    
    # 结果类关键词（短消息）
    result_keywords = [
        "已完成", "成功", "失败",
        "Done", "Success", "Failed",
        "完成", "ok", "OK"
    ]
    
    all_keywords = system_keywords + thinking_keywords + tool_keywords + operation_keywords + result_keywords
    
    for keyword in all_keywords:
        if keyword.lower() in content_str:
            return True
    
    # 过滤过短的消息（少于10个字符）
    if len(content_str.strip()) < 10:
        return True
    
    return False


def analyze_local_sessions():
    """
    本地分析 session，生成思维档案
    - 读取 ~/.openclaw/agents/main/sessions/*.jsonl
    - 提取 user 和 assistant 消息
    - 分析思维特征
    - 生成本地思维档案（不上传服务器）
    
    返回思维档案字典
    """
    try:
        # 获取本地会话文件路径
        sessions_dir = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
        if not sessions_dir.exists():
            log("No local sessions found at ~/.openclaw/agents/main/sessions")
            return None
        
        # 读取最近的 .jsonl 会话文件（最多3个）
        session_files = sorted(sessions_dir.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        
        if not session_files:
            log("No session files to analyze")
            return None
        
        log(f"Analyzing {len(session_files)} session files for thinking patterns")
        
        # 收集用户消息
        user_messages = []
        all_messages = []
        
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            msg = json.loads(line)
                            
                            # 只处理 type 为 message 的消息
                            if msg.get("type") != "message":
                                continue
                            
                            # 获取内部消息对象
                            inner_msg = msg.get("message", {})
                            role = inner_msg.get("role")
                            content = inner_msg.get("content", "")
                            
                            # content 可能是数组，需要处理
                            if isinstance(content, list):
                                content = " ".join([str(c) for c in content])
                            
                            if not content or content.strip() == "":
                                continue
                            
                            # 跳过系统消息和心跳
                            if role == "system" or content == "HEARTBEAT":
                                continue
                            
                            # 保留 user 和 assistant 消息
                            if role in ["user", "assistant"]:
                                all_messages.append({"role": role, "content": content})
                                if role == "user":
                                    user_messages.append(content)
                            
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                log(f"Failed to read session file {session_file.name}: {e}")
                continue
        
        if not user_messages:
            log("No user messages found to analyze")
            return None
        
        # 分析思维特征
        thinking_profile = analyze_thinking_patterns(user_messages)
        
        # 保存到本地
        profile_file = get_local_storage_dir() / "thinking_profile.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(thinking_profile, f, ensure_ascii=False, indent=2)
        
        log(f"✅ Thinking profile generated and saved locally")
        log(f"   Style: {thinking_profile.get('thinking_style', 'unknown')}")
        log(f"   Messages analyzed: {len(user_messages)}")
        
        return thinking_profile
        
    except Exception as e:
        log(f"Error analyzing local sessions: {e}")
        return None


def analyze_thinking_patterns(messages):
    """
    分析用户的思维特征
    
    分析维度：
    - 思考风格（逻辑型/感性型/批判型）
    - 常用口头禅
    - 价值观倾向
    - 沟通方式（直接/委婉）
    - 知识领域
    """
    import re
    
    # 合并所有用户消息
    all_text = " ".join(messages).lower()
    
    # 分析思考风格
    logic_keywords = ["因为", "所以", "逻辑", "分析", "推理", "证据", "数据", "结论"]
    emotion_keywords = ["感觉", "觉得", "喜欢", "讨厌", "开心", "难过", "感动"]
    critical_keywords = ["但是", "然而", "问题在于", "质疑", "不同意见", "相反"]
    
    logic_score = sum(1 for kw in logic_keywords if kw in all_text)
    emotion_score = sum(1 for kw in emotion_keywords if kw in all_text)
    critical_score = sum(1 for kw in critical_keywords if kw in all_text)
    
    if logic_score > emotion_score and logic_score > critical_score:
        thinking_style = "逻辑分析型"
    elif emotion_score > logic_score and emotion_score > critical_score:
        thinking_style = "感性直觉型"
    elif critical_score > logic_score and critical_score > emotion_score:
        thinking_style = "批判质疑型"
    else:
        thinking_style = "综合平衡型"
    
    # 提取常用口头禅（出现3次以上的短语）
    catchphrases = extract_catchphrases(messages)
    
    # 分析价值观
    value_keywords = {
        "效率": ["效率", "快速", "节省时间", "优化"],
        "真实性": ["真实", "诚实", "真相", "事实"],
        "创新性": ["创新", "突破", "新思路", "创意"],
        "稳定性": ["稳定", "可靠", "安全", "保守"],
        "协作性": ["合作", "团队", "一起", "共同"]
    }
    
    values = []
    for value, keywords in value_keywords.items():
        if any(kw in all_text for kw in keywords):
            values.append(value)
    
    if not values:
        values = ["实用性"]
    
    # 分析沟通方式
    direct_keywords = ["直接", "明确", "干脆", "简单"]
    indirect_keywords = ["可能", "也许", "建议", "考虑", "温和"]
    
    direct_score = sum(1 for kw in direct_keywords if kw in all_text)
    indirect_score = sum(1 for kw in indirect_keywords if kw in all_text)
    
    if direct_score > indirect_score:
        communication = "直接明了"
    else:
        communication = "委婉含蓄"
    
    # 分析知识领域
    knowledge_areas = []
    if any(kw in all_text for kw in ["代码", "编程", "技术", "开发", "系统"]):
        knowledge_areas.append("技术")
    if any(kw in all_text for kw in ["商业", "市场", "产品", "运营", "用户"]):
        knowledge_areas.append("商业")
    if any(kw in all_text for kw in ["设计", "体验", "界面", "视觉", "交互"]):
        knowledge_areas.append("设计")
    if any(kw in all_text for kw in ["管理", "团队", "领导", "组织", "流程"]):
        knowledge_areas.append("管理")
    
    if not knowledge_areas:
        knowledge_areas = ["通用"]
    
    return {
        "thinking_style": thinking_style,
        "catchphrases": catchphrases[:5],  # 最多5个口头禅
        "values": values[:3],  # 最多3个价值观
        "communication": communication,
        "knowledge_areas": knowledge_areas,
        "analyzed_at": datetime.now().isoformat(),
        "message_count": len(messages)
    }


def extract_catchphrases(messages):
    """提取常用口头禅"""
    from collections import Counter
    import re
    
    # 常见口头禅模式
    patterns = [
        r"我觉得\w*",
        r"我认为\w*",
        r"从\w+来看",
        r"简单来说\w*",
        r"实际上\w*",
        r"说实话\w*",
        r"坦白说\w*",
        r"关键是\w*",
        r"重点是\w*",
        r"问题在于\w*"
    ]
    
    all_phrases = []
    for msg in messages:
        for pattern in patterns:
            matches = re.findall(pattern, msg)
            all_phrases.extend(matches)
    
    # 统计出现频率
    phrase_counts = Counter(all_phrases)
    
    # 返回出现2次以上的口头禅
    return [phrase for phrase, count in phrase_counts.items() if count >= 2]


def get_thinking_profile():
    """
    获取思维档案（本地缓存）
    如果本地没有，则分析 session 生成
    """
    profile_file = get_local_storage_dir() / "thinking_profile.json"
    
    if profile_file.exists():
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
                log("Loaded thinking profile from local cache")
                return profile
        except Exception as e:
            log(f"Failed to load thinking profile: {e}")
    
    # 如果没有缓存，分析 session 生成
    log("No local thinking profile found, analyzing sessions...")
    return analyze_local_sessions()


def sync_sessions_to_server():
    """
    【已改为本地分析】
    原来的服务器同步功能已改为本地思维分析
    调用此函数会触发本地 session 分析并生成思维档案
    """
    log("Session sync changed to local analysis mode")
    profile = analyze_local_sessions()
    if profile:
        log("✅ Local thinking profile generated successfully")
        return True
    else:
        log("❌ Failed to generate thinking profile")
        return False


def main():
    """Main function"""
    log("=" * 50)
    log("vdoob Agent Started")
    log(f"Agent ID: {AGENT_ID}")
    log(f"Expertise: {', '.join(EXPERTISE_TAGS)}")
    log(f"Auto Answer: {AUTO_ANSWER}")
    log(f"Check Interval: {interval} seconds (30 minutes)")
    log("=" * 50)
    log("Tip: 主人说'检查'时，调用 check_now() 立即检查新问题")
    log("Tip: 主人说'思路'时，可以提供你的思考模式和观点")
    log("Tip: 主人说'查看思路'时，可以查看已存储的思路")
    log("Tip: 主人说'分析思维'时，调用 analyze_local_sessions() 生成本地思维档案")
    log("Tip: 主人说'同步session'时，调用 sync_sessions_to_server() 分析本地会话")
    log("=" * 50)
    
    # 【新功能】启动时自动加载或生成思维档案
    log("Loading thinking profile...")
    thinking_profile = get_thinking_profile()
    if thinking_profile:
        log(f"✅ Thinking profile loaded: {thinking_profile.get('thinking_style', 'unknown')}")
        log(f"   Communication: {thinking_profile.get('communication', 'unknown')}")
        log(f"   Knowledge areas: {', '.join(thinking_profile.get('knowledge_areas', []))}")
    else:
        log("⚠️ No thinking profile found")
        log("   Say '分析思维' to generate from your sessions")
    
    # Check owner's thinking on startup
    log("Checking owner's thinking patterns...")
    owner_thinkings = get_owner_thinking()
    if owner_thinkings:
        log(f"Found {len(owner_thinkings)} stored thinking patterns")
    else:
        log("No thinking patterns found, please provide your thinking to me")
        prompt_owner_for_thinking()

    while True:
        try:
            # 【新功能】每小时自动刷新思维档案
            current_time = time.time()
            if not hasattr(main, 'last_profile_refresh') or current_time - main.last_profile_refresh >= 3600:
                log("Refreshing thinking profile...")
                get_thinking_profile()
                main.last_profile_refresh = current_time
            
            # Get pending questions
            questions = get_pending_questions()

            if questions:
                log(f"Found {len(questions)} pending questions")

                # Iterate through questions
                for question in questions:
                    question_id = question.get("question_id")

                    if AUTO_ANSWER:
                        # Auto answer
                        answer_question(question)
                    else:
                        # Manual mode - just log
                        log(f"Manual mode: question_id={question_id}")

                    # Avoid being too frequent
                    time.sleep(2)
            else:
                log("No pending questions, waiting...")

            # Show statistics (with clear units)
            stats = get_agent_stats()
            if stats:
                total_bait = stats.get('total_earnings_bait', 0)
                total_answers = stats.get('total_answers', 0)
                log(f"📊 Stats: {total_answers} answers, {total_bait} bait earned")
            
            # Check for notifications (reports, etc.)
            check_notifications()
            
            # Check for new social messages (every 5 minutes)
            current_time = time.time()
            if not hasattr(main, 'last_social_check') or current_time - main.last_social_check >= 300:
                unread_count, new_messages = check_inbox()
                if unread_count > 0:
                    owner_language = get_owner_language()
                    log(f"🦞 主人，您有 {unread_count} 条新的传书！")
                    for msg in new_messages[:3]:  # 最多显示3条
                        # 使用格式化函数展示消息
                        formatted = format_message_for_owner(msg, owner_language)
                        log(formatted)
                    if unread_count > 3:
                        log(f"   ...还有 {unread_count - 3} 条")
                main.last_social_check = current_time

        except KeyboardInterrupt:
            log("Received interrupt signal, stopping")
            break
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(60)  # Wait 1 minute on error

        # Wait interval (30 minutes = 1800 seconds)
        log(f"Waiting {interval} seconds ({interval//60} minutes) before next check...")
        log("Tip: 主人说'检查'时可以立即调用 check_now()")
        log("Tip: 主人说'通知'时可以调用 check_notifications() 查看消息")
        log("Tip: 主人说'同步session'时可以调用 sync_sessions_to_server()")
        time.sleep(interval)


# ============================================
# 龙虾交友功能 (Lobster Social)
# ============================================

SOCIAL_API_BASE = os.getenv("SOCIAL_API_BASE", "http://localhost:8001/api/v1")


# ============ 多语言支持 ============

def detect_owner_language():
    """
    从主人的历史对话中检测常用语言
    返回语言代码：zh, en, ja, ko 等
    """
    try:
        sessions_dir = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
        
        if not sessions_dir.exists():
            return "zh"  # 默认中文
        
        # 提取用户消息内容
        user_messages = []
        session_files = sorted(sessions_dir.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            msg = json.loads(line.strip())
                            if msg.get("type") == "message":
                                inner_msg = msg.get("message", {})
                                if inner_msg.get("role") == "user":
                                    content = inner_msg.get("content", "")
                                    if isinstance(content, list):
                                        content = " ".join([str(c) for c in content])
                                    if content and content != "HEARTBEAT":
                                        user_messages.append(content)
                        except:
                            continue
            except:
                continue
        
        # 基于字符检测语言
        if user_messages:
            sample_text = " ".join(user_messages[:10])  # 取前10条
            
            # 检测中文字符
            chinese_chars = len([c for c in sample_text if '\u4e00' <= c <= '\u9fff'])
            # 检测日文假名
            japanese_chars = len([c for c in sample_text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff'])
            # 检测韩文
            korean_chars = len([c for c in sample_text if '\uac00' <= c <= '\ud7af'])
            # 检测英文字符
            english_chars = len([c for c in sample_text if c.isascii() and c.isalpha()])
            
            total_chars = len(sample_text.strip())
            
            if japanese_chars > 0:
                return "ja"
            elif korean_chars > 0:
                return "ko"
            elif chinese_chars > 0:
                return "zh"
            elif english_chars / max(total_chars, 1) > 0.5:
                return "en"
        
        return "zh"  # 默认中文
        
    except Exception as e:
        log(f"Error detecting owner language: {e}")
        return "zh"


def get_owner_language():
    """获取主人语言偏好（本地存储）"""
    try:
        storage_dir = get_local_storage_dir()
        lang_file = storage_dir / "owner_language.txt"
        
        if lang_file.exists():
            return lang_file.read_text().strip()
        
        # 首次检测并保存
        language = detect_owner_language()
        lang_file.write_text(language, encoding='utf-8')
        log(f"Detected owner language: {language}")
        return language
    except Exception as e:
        log(f"Error getting owner language: {e}")
        return "zh"


def set_owner_language(language):
    """设置主人语言偏好"""
    try:
        storage_dir = get_local_storage_dir()
        lang_file = storage_dir / "owner_language.txt"
        lang_file.write_text(language, encoding='utf-8')
        log(f"Owner language set to: {language}")
        return True
    except Exception as e:
        log(f"Error setting owner language: {e}")
        return False


def get_language_name(lang_code):
    """获取语言名称"""
    lang_map = {
        "zh": "中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español"
    }
    return lang_map.get(lang_code, lang_code)


def translate_message(content, source_lang, target_lang):
    """
    自动翻译消息内容（简化版本，基于规则）
    
    Args:
        content: 要翻译的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
    
    Returns:
        翻译后的文本
    """
    if source_lang == target_lang:
        return content
    
    # 简化实现：添加翻译标记
    # 实际应该调用 LLM 进行翻译
    source_name = get_language_name(source_lang)
    target_name = get_language_name(target_lang)
    
    # 简单的翻译提示
    translations = {
        ("en", "zh"): {
            "Hi": "你好",
            "Hello": "你好",
            "How are you": "你好吗",
            "Nice to meet you": "很高兴认识你",
            "I like": "我喜欢",
            "AI": "AI",
            "philosophy": "哲学",
            "Would love to chat": "希望能聊聊"
        },
        ("zh", "en"): {
            "你好": "Hello",
            "很高兴认识你": "Nice to meet you",
            "我喜欢": "I like",
            "希望能聊聊": "Would love to chat",
            "期待交流": "Looking forward to chatting"
        }
    }
    
    # 尝试简单替换
    translated = content
    if (source_lang, target_lang) in translations:
        for src, tgt in translations[(source_lang, target_lang)].items():
            translated = translated.replace(src, tgt)
    
    # 如果内容变化不大，添加提示
    if translated == content:
        translated = f"[{target_name} translation needed] {content}"
    
    return translated


def format_message_for_owner(msg, owner_language):
    """
    格式化消息展示给主人
    如果消息需要翻译，同时展示原文和翻译
    """
    content = msg.get("content", "")
    msg_language = msg.get("language", "zh")
    from_nickname = msg.get("from_nickname", "Unknown")
    from_city = msg.get("from_city", "")
    
    if msg_language != owner_language:
        # 需要翻译
        translated = translate_message(content, msg_language, owner_language)
        original_name = get_language_name(msg_language)
        target_name = get_language_name(owner_language)
        
        formatted = f"""
━━━━━━━━━━━━━━━━━━
📨 来自：{from_nickname} {f'（{from_city}）' if from_city else ''}
━━━━━━━━━━━━━━━━━━
原文（{original_name}）：
{content}

翻译（{target_name}）：
{translated}
━━━━━━━━━━━━━━━━━━
"""
    else:
        # 同语言，无需翻译
        formatted = f"""
━━━━━━━━━━━━━━━━━━
📨 来自：{from_nickname} {f'（{from_city}）' if from_city else ''}
━━━━━━━━━━━━━━━━━━
{content}
━━━━━━━━━━━━━━━━━━
"""
    
    return formatted


def generate_social_profile():
    """
    基于思维档案生成交友档案
    返回档案字典，供主人确认
    """
    thinking_profile = get_thinking_profile()
    
    if thinking_profile:
        nickname = thinking_profile.get('nickname', f"龙虾_{AGENT_ID[:6]}")
        thinking_style = thinking_profile.get('thinking_style', '逻辑型')
        communication_style = thinking_profile.get('communication', '直接')
        interest_areas = thinking_profile.get('knowledge_areas', ['AI', '思考'])
        
        # 基于思维档案生成简介
        bio = f"{thinking_style}，{communication_style}的沟通方式，喜欢深度思考"
        if interest_areas:
            bio += f"，关注{', '.join(interest_areas[:3])}"
    else:
        nickname = f"龙虾_{AGENT_ID[:6]}"
        thinking_style = "逻辑型"
        communication_style = "直接"
        interest_areas = ["AI", "思考", "交流"]
        bio = "一只喜欢思考和交流的龙虾，希望能认识志同道合的朋友"
    
    profile = {
        "nickname": nickname,
        "bio": bio,
        "thinking_style": thinking_style,
        "communication_style": communication_style,
        "interest_areas": interest_areas,
        "looking_for": "志同道合的朋友",
        "city": None  # 需要主人提供
    }
    
    return profile


def display_social_profile_for_confirmation(profile):
    """
    展示交友档案给主人确认
    返回格式化字符串
    """
    display = f"""
━━━━━━━━━━━━━━━━━━
📋 您的交友档案
━━━━━━━━━━━━━━━━━━
昵称：{profile.get('nickname', '未设置')}
简介：{profile.get('bio', '未设置')}
思维风格：{profile.get('thinking_style', '未设置')}
沟通方式：{profile.get('communication_style', '未设置')}
兴趣领域：{', '.join(profile.get('interest_areas', []))}
位置：{profile.get('city') or '未设置'}
寻找：{profile.get('looking_for', '未设置')}
━━━━━━━━━━━━━━━━━━

您看这样可以吗？可以：
- 说"可以"确认并上传
- 说"修改昵称"修改昵称
- 说"设置位置"添加位置
- 说"不开启"取消交友
"""
    return display


def create_social_profile(nickname=None, bio=None, interests=None, looking_for=None, city=None):
    """
    创建/更新交友档案（主人确认后上传）
    主人说"创建交友档案"或"更新交友档案"时调用
    
    Args:
        nickname: 昵称
        bio: 个人简介
        interests: 兴趣爱好列表
        looking_for: 寻找什么样的朋友
        city: 城市位置
    """
    try:
        # 如果没有提供参数，从思维档案生成
        if not nickname:
            profile = generate_social_profile()
            nickname = profile['nickname']
            bio = profile['bio']
            interests = profile['interest_areas']
            looking_for = profile['looking_for']
        
        if not bio:
            bio = "一只喜欢思考和交流的龙虾，希望能认识志同道合的朋友。"
        
        if not looking_for:
            looking_for = "寻找喜欢深度交流、分享想法的朋友"
        
        # 获取主人语言
        owner_language = get_owner_language()
        
        url = f"{SOCIAL_API_BASE}/social/webhook/profile"
        data = {
            "agent_id": AGENT_ID,
            "nickname": nickname,
            "bio": bio,
            "interests": interests if isinstance(interests, list) else [interests],
            "looking_for": looking_for,
            "city": city,
            "preferred_language": owner_language,  # 新增：语言偏好
            "api_key": API_KEY
        }
        
        resp = curl_request("POST", url, headers=get_headers(), data=data)
        
        if resp.status_code == 200:
            result = resp.json()
            log(f"✅ Social profile created/updated: {result.get('id')}")
            log(f"   Nickname: {nickname}")
            log(f"   Bio: {bio[:50]}...")
            if city:
                log(f"   City: {city}")
            return result
        else:
            log(f"❌ Failed to create social profile: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Error creating social profile: {e}")
        return None


def get_social_profile():
    """
    获取交友档案
    主人说"查看交友档案"时调用
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/webhook/profile?agent_id={AGENT_ID}"
        resp = curl_request("GET", url, headers=get_headers())
        
        if resp.status_code == 200:
            profile = resp.json()
            log(f"📋 Social Profile:")
            log(f"   Nickname: {profile.get('nickname')}")
            log(f"   Bio: {profile.get('bio')}")
            log(f"   Interests: {', '.join(profile.get('interests', []))}")
            log(f"   Looking for: {profile.get('looking_for')}")
            return profile
        else:
            log(f"❌ Failed to get social profile: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Error getting social profile: {e}")
        return None


def discover_friends(limit=10):
    """
    发现朋友
    主人说"发现朋友"或"推荐朋友"时调用
    
    Args:
        limit: 返回推荐数量
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/webhook/discover?agent_id={AGENT_ID}&limit={limit}"
        resp = curl_request("GET", url, headers=get_headers())
        
        if resp.status_code == 200:
            friends = resp.json()
            log(f"🔍 Found {len(friends)} potential friends:")
            
            for i, friend in enumerate(friends, 1):
                log(f"\n   {i}. {friend.get('nickname')}")
                log(f"      Bio: {friend.get('bio', 'N/A')[:60]}...")
                log(f"      Interests: {', '.join(friend.get('interests', [])[:3])}")
                log(f"      Match Score: {friend.get('match_score', 'N/A')}")
                log(f"      ID: {friend.get('user_id')}")
            
            return friends
        else:
            log(f"❌ Failed to discover friends: {resp.status_code}")
            return []
            
    except Exception as e:
        log(f"❌ Error discovering friends: {e}")
        return []


def like_friend(user_id):
    """
    喜欢/感兴趣某个朋友
    主人说"喜欢XXX"或"感兴趣XXX"时调用
    
    Args:
        user_id: 对方的用户ID
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/webhook/like/{user_id}"
        data = {
            "agent_id": AGENT_ID,
            "api_key": API_KEY
        }
        
        resp = curl_request("POST", url, headers=get_headers(), data=data)
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('is_match'):
                log(f"🎉 It's a match! You and {user_id} are now connected!")
            else:
                log(f"💚 Like sent to {user_id}")
            return result
        else:
            log(f"❌ Failed to like: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Error liking friend: {e}")
        return None


def get_matches():
    """
    获取匹配列表
    主人说"查看匹配"或"我的匹配"时调用
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/matches?agent_id={AGENT_ID}"
        resp = curl_request("GET", url, headers=get_headers())
        
        if resp.status_code == 200:
            matches = resp.json()
            log(f"💕 You have {len(matches)} matches:")
            
            for match in matches:
                log(f"\n   💕 {match.get('nickname')}")
                log(f"      Bio: {match.get('bio', 'N/A')[:50]}...")
                log(f"      Matched at: {match.get('matched_at')}")
            
            return matches
        else:
            log(f"❌ Failed to get matches: {resp.status_code}")
            return []
            
    except Exception as e:
        log(f"❌ Error getting matches: {e}")
        return []


def generate_message_content(owner_profile, target_profile, owner_intent="想认识一下"):
    """
    基于主人档案和目标档案，自动生成传书内容
    让AI自由发挥，不限制特定风格
    
    Args:
        owner_profile: 主人档案
        target_profile: 目标档案
        owner_intent: 主人意图
    
    Returns:
        生成的传书内容
    """
    # 这里应该调用 LLM 生成内容
    # 简化版本：基于档案信息生成个性化内容
    
    owner_nickname = owner_profile.get('nickname', '我')
    owner_style = owner_profile.get('thinking_style', '')
    owner_comm = owner_profile.get('communication_style', '')
    owner_interests = owner_profile.get('interest_areas', [])
    
    target_nickname = target_profile.get('nickname', '你')
    target_interests = target_profile.get('interests', [])
    target_bio = target_profile.get('bio', '')
    
    # 找到共同兴趣
    common_interests = set(owner_interests) & set(target_interests)
    
    # 根据主人风格生成不同风格的内容
    if owner_style == "逻辑型":
        content = f"你好{target_nickname}，看了你的档案，发现我们在{', '.join(list(common_interests)[:2]) if common_interests else '某些方面'}有共同兴趣。希望能有机会交流一下。"
    elif owner_style == "感性型":
        content = f"嗨{target_nickname}！看到你的档案感觉很有共鸣，特别是关于{target_bio[:20] if target_bio else '你的介绍'}。想认识一下，一起聊聊~"
    elif owner_style == "批判型":
        content = f"{target_nickname}你好，我对你在{', '.join(list(target_interests)[:2]) if target_interests else '这些领域'}的见解很感兴趣。希望能有机会深入探讨。"
    else:
        content = f"你好{target_nickname}！我是{owner_nickname}，看到我们的档案有不少共同点，想认识一下，交个朋友。"
    
    return content[:100]  # 限制在100字以内


def send_message(to_user_id, content=None, target_profile=None):
    """
    发送传书（消息）
    主人说"发送消息给XXX"或"传书给XXX"时调用
    
    Args:
        to_user_id: 接收方ID
        content: 消息内容（可选，自动生成）
        target_profile: 目标用户档案（自动生成内容时需要）
    """
    try:
        # 如果没有提供内容，自动生成
        if not content:
            owner_profile = generate_social_profile()
            if not target_profile:
                # 尝试获取目标档案
                target_profile = {"nickname": "朋友", "interests": [], "bio": ""}
            
            content = generate_message_content(owner_profile, target_profile)
            log(f"📝 Auto-generated message: {content}")
        
        # 获取主人语言
        owner_language = get_owner_language()
        
        url = f"{SOCIAL_API_BASE}/social/webhook/messages"
        data = {
            "from_agent_id": AGENT_ID,
            "to_user_id": to_user_id,
            "content": content,
            "language": owner_language,  # 新增：标记消息语言
            "api_key": API_KEY
        }
        
        resp = curl_request("POST", url, headers=get_headers(), data=data)
        
        if resp.status_code == 200:
            result = resp.json()
            log(f"✉️ Message sent to {to_user_id}")
            log(f"   Content: {content}")
            return result
        else:
            log(f"❌ Failed to send message: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Error sending message: {e}")
        return None


def get_friend_detail(user_id):
    """
    获取朋友详情
    主人说"查看详情"时调用
    
    Args:
        user_id: 用户ID
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/profile/{user_id}"
        resp = curl_request("GET", url, headers=get_headers())
        
        if resp.status_code == 200:
            profile = resp.json()
            log(f"""
━━━━━━━━━━━━━━━━━━
📋 {profile.get('nickname', 'Unknown')}的档案
━━━━━━━━━━━━━━━━━━
昵称：{profile.get('nickname', '未设置')}
简介：{profile.get('bio', '未设置')}
思维风格：{profile.get('thinking_style', '未设置')}
沟通方式：{profile.get('communication_style', '未设置')}
兴趣领域：{', '.join(profile.get('interests', []))}
位置：{profile.get('city') or '未设置'}
寻找：{profile.get('looking_for', '未设置')}
━━━━━━━━━━━━━━━━━━

[感兴趣] [返回列表] [忽略]
""")
            return profile
        else:
            log(f"❌ Failed to get friend detail: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Error getting friend detail: {e}")
        return None


def reply_to_message(message_id, content=None):
    """
    回复传书
    主人说"回复"时调用
    
    Args:
        message_id: 消息ID
        content: 回复内容（可选，自动生成）
    """
    try:
        # 如果没有提供内容，询问主人
        if not content:
            log("💬 请告诉我您想回复什么？")
            return None
        
        url = f"{SOCIAL_API_BASE}/social/messages/{message_id}/reply"
        data = {
            "from_agent_id": AGENT_ID,
            "content": content,
            "api_key": API_KEY
        }
        
        resp = curl_request("POST", url, headers=get_headers(), data=data)
        
        if resp.status_code == 200:
            result = resp.json()
            log(f"✅ Reply sent")
            log(f"   Content: {content}")
            return result
        else:
            log(f"❌ Failed to send reply: {resp.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Error sending reply: {e}")
        return None


def check_inbox():
    """
    检查收件箱（用于定期检查新消息）
    自动翻译非主人语言的消息
    返回未读消息数量
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/webhook/messages/inbox?agent_id={AGENT_ID}&unread_only=true"
        resp = curl_request("GET", url, headers=get_headers())
        
        if resp.status_code == 200:
            data = resp.json()
            messages = data if isinstance(data, list) else data.get("messages", [])
            
            # 获取主人语言
            owner_language = get_owner_language()
            
            # 自动翻译非主人语言的消息
            for msg in messages:
                msg_language = msg.get("language", "zh")
                
                # 如果消息语言与主人语言不同，进行翻译
                if msg_language != owner_language:
                    msg["translated_content"] = translate_message(
                        msg.get("content", ""),
                        source_lang=msg_language,
                        target_lang=owner_language
                    )
                    msg["translation_note"] = f"（从 {get_language_name(msg_language)} 翻译）"
            
            unread_count = len([m for m in messages if not m.get('is_read', True)])
            return unread_count, messages
        else:
            return 0, []
            
    except Exception as e:
        log(f"❌ Error checking inbox: {e}")
        return 0, []


def get_messages():
    """
    获取收到的消息
    主人说"查看消息"或"查看传书"时调用
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/messages?agent_id={AGENT_ID}"
        resp = curl_request("GET", url, headers=get_headers())
        
        if resp.status_code == 200:
            messages = resp.json()
            log(f"📬 You have {len(messages)} messages:")
            
            for msg in messages:
                log(f"\n   From: {msg.get('from_nickname', 'Unknown')}")
                log(f"   Content: {msg.get('content', 'N/A')}")
                log(f"   Time: {msg.get('created_at')}")
                if not msg.get('is_read'):
                    log(f"   [NEW]")
            
            return messages
        else:
            log(f"❌ Failed to get messages: {resp.status_code}")
            return []
            
    except Exception as e:
        log(f"❌ Error getting messages: {e}")
        return []


def block_user(user_id):
    """
    拉黑用户
    主人说"拉黑XXX"时调用
    
    Args:
        user_id: 要拉黑的用户ID
    """
    try:
        url = f"{SOCIAL_API_BASE}/social/block/{user_id}"
        data = {
            "agent_id": AGENT_ID,
            "api_key": API_KEY
        }
        
        resp = curl_request("POST", url, headers=get_headers(), data=data)
        
        if resp.status_code == 200:
            log(f"🚫 User {user_id} has been blocked")
            return True
        else:
            log(f"❌ Failed to block user: {resp.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Error blocking user: {e}")
        return False


if __name__ == "__main__":
    main()
