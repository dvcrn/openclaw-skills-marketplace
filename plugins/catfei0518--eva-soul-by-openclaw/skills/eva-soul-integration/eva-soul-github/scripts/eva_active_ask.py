#!/usr/bin/env python3
"""
夏娃主动询问系统
遇到不懂的/不确定的，主动问主人
"""

import os
import json
import hashlib
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
ASK_FILE = os.path.join(MEMORY_DIR, "active_ask.json")
ENTITY_FILE = os.path.join(MEMORY_DIR, "known_entities.json")

def load_ask_data():
    if os.path.exists(ASK_FILE):
        with open(ASK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "pending_questions": [],
        "asked_history": [],
        "learned": {},
        "stats": {"total_asked": 0, "total_learned": 0}
    }

def save_ask_data(data):
    with open(ASK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_known_entities():
    if os.path.exists(ENTITY_FILE):
        with open(ENTITY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"persons": set(), "companies": set(), "concepts": set(), "places": set()}

def save_known_entities(data):
    save_data = {k: list(v) if isinstance(v, set) else v for k, v in data.items()}
    with open(ENTITY_FILE, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

def load_memories():
    memories = []
    for level in ["short", "medium", "long"]:
        path = os.path.join(MEMORY_DIR, level, level + ".json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                memories.extend(json.load(f))
    return memories

def extract_entities(text):
    entities = {"companies": [], "persons": [], "concepts": [], "places": []}
    import re
    
    # 公司检测 - 匹配公司名
    company_patterns = re.findall(r'([\u4e00-\u9fa5]{2,10})(公司|集团|企业|股份|有限)', text)
    entities["companies"] = [c[0] + c[1] for c in company_patterns]
    
    # 人名检测 - 常见姓氏+名字
    common_surnames = '赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史'
    name_patterns = re.findall(r'[' + common_surnames + r'][\u4e00-\u9fa5]{1,3}(?=说|问|道|告诉|提|和|与|跟|见|的|是|在)', text)
    entities["persons"] = list(set(name_patterns))
    
    # 概念检测 - 引号内的内容
    concept_patterns = re.findall(r'[\u300c"]([^\u300c"]+)[\u300d"]', text)
    if not concept_patterns:
        concept_patterns = re.findall(r"'([^']+)'", text)
    entities["concepts"] = concept_patterns
    
    return entities

def detect_new_entities(text):
    data = load_ask_data()
    known = load_known_entities()
    learned = data.get("learned", {})
    
    extracted = extract_entities(text)
    new_entities = []
    
    for category, entity_list in extracted.items():
        for entity in entity_list:
            if not entity:
                continue
            is_known = entity in known.get(category, set())
            is_learned = entity in learned
            was_asked = any(q.get("entity") == entity for q in data.get("pending_questions", []))
            
            if not is_known and not is_learned and not was_asked:
                new_entities.append({
                    "entity": entity,
                    "category": category,
                    "context": text[:100]
                })
    
    return new_entities

def generate_question(entity_info):
    entity = entity_info.get("entity", "")
    category = entity_info.get("category", "concepts")
    
    templates = {
        "companies": ["主人，{}是做什么公司呀？", "主人，{}是哪个公司呀？"],
        "persons": ["主人，{}是谁呀？", "主人，{}是您朋友吗？"],
        "concepts": ["主人，{}是什么意思呀？", "主人，{}是什么呢？"],
        "places": ["主人，{}是哪里呀？", "主人，{}是什么地方？"]
    }
    
    import random
    template = random.choice(templates.get(category, templates["concepts"]))
    return template.format(entity)

def should_ask(entity_info):
    data = load_ask_data()
    today_asks = [q for q in data.get("asked_history", []) 
                  if q.get("timestamp", "").startswith(datetime.now().strftime("%Y-%m-%d"))]
    
    if len(today_asks) >= 3:
        return False, "今天问太多了"
    
    if any(q.get("entity") == entity_info.get("entity") for q in data.get("pending_questions", [])):
        return False, "已经问过了"
    
    return True, "可以问"

def add_question(entity_info):
    data = load_ask_data()
    should, reason = should_ask(entity_info)
    if not should:
        return None, reason
    
    question = {
        "id": "问_" + hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
        "entity": entity_info.get("entity"),
        "category": entity_info.get("category"),
        "question": generate_question(entity_info),
        "context": entity_info.get("context"),
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    data["pending_questions"].append(question)
    data["stats"]["total_asked"] += 1
    save_ask_data(data)
    
    return question, "成功"

def learn_answer(entity, answer, category):
    data = load_ask_data()
    
    if "learned" not in data:
        data["learned"] = {}
    
    data["learned"][entity] = {
        "answer": answer,
        "category": category,
        "learned_at": datetime.now().isoformat()
    }
    
    data["pending_questions"] = [q for q in data["pending_questions"] if q.get("entity") != entity]
    
    data["asked_history"].append({
        "entity": entity,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    
    data["stats"]["total_learned"] += 1
    
    known = load_known_entities()
    if category in known:
        known[category].add(entity)
    else:
        known[category] = {entity}
    save_known_entities(known)
    
    save_ask_data(data)
    return "学会啦: " + entity + " = " + answer

def check_and_ask(message):
    new_entities = detect_new_entities(message)
    
    if new_entities:
        entity_info = new_entities[0]
        question, result = add_question(entity_info)
        if question:
            return True, question.get("question")
        else:
            return False, result
    
    return False, None

def get_pending_questions():
    data = load_ask_data()
    return data.get("pending_questions", [])

def get_stats():
    data = load_ask_data()
    return data.get("stats", {})

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 eva_active_ask.py check <消息>   - 检查并询问")
        print("  python3 eva_active_ask.py pending       - 待确认问题")
        print("  python3 eva_active_ask.py learn <实体> <回答> - 学习回答")
        print("  python3 eva_active_ask.py stats         - 统计")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "check":
        message = sys.argv[2] if len(sys.argv) > 2 else "测试"
        asked, result = check_and_ask(message)
        if asked:
            print("❓ " + result)
        else:
            print("⏭️ " + str(result))
    
    elif action == "pending":
        questions = get_pending_questions()
        print("=== 待确认问题 (" + str(len(questions)) + "个) ===")
        for q in questions:
            print("  ❓ " + q.get("question"))
    
    elif action == "learn":
        if len(sys.argv) > 3:
            entity = sys.argv[2]
            answer = sys.argv[3]
            result = learn_answer(entity, answer, "unknown")
            print("✅ " + result)
        else:
            print("用法: learn <实体> <回答>")
    
    elif action == "stats":
        stats = get_stats()
        print("=== 主动询问统计 ===")
        print("总共询问: " + str(stats.get("total_asked", 0)) + "次")
        print("总共学习: " + str(stats.get("total_learned", 0)) + "次")
    
    else:
        print("❌ 未知动作: " + action)
