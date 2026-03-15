#!/usr/bin/env python3
"""
夏娃知识图谱系统
结构化记住人物、公司、地点、事物之间的关系

功能:
- 实体管理: 人/公司/地点/事件
- 关系管理: 朋友/家人/同事/上下游
- 自动提取: 从对话中识别关系
- 查询推理: 关系路径查询
"""

import os
import json
import hashlib
from datetime import datetime
from collections import defaultdict

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
GRAPH_FILE = os.path.join(MEMORY_DIR, "knowledge_graph.json")

# 实体类型
ENTITY_TYPES = ["person", "company", "place", "event", "thing"]

# 关系类型
RELATION_TYPES = [
    "朋友", "家人", "同事", "合作伙伴", 
    "上下游", "客户", "供应商", "竞争对手",
    "任职", "投资", "股东", "校友", "老乡"
]

def load_graph():
    """加载知识图谱"""
    if os.path.exists(GRAPH_FILE):
        with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "updated_at": None,
        "nodes": {},      # 节点: {id: {type, name, attrs}}
        "edges": [],      # 边: {from, to, relation, source}
        "stats": {
            "total_nodes": 0,
            "total_edges": 0
        }
    }

def save_graph(data):
    """保存知识图谱"""
    data["updated_at"] = datetime.now().isoformat()
    with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_node(name, entity_type, attrs=None):
    """添加节点"""
    graph = load_graph()
    
    # 生成ID
    node_id = f"{entity_type}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
    
    if node_id not in graph["nodes"]:
        graph["nodes"][node_id] = {
            "id": node_id,
            "name": name,
            "type": entity_type,
            "attrs": attrs or {},
            "created_at": datetime.now().isoformat()
        }
        graph["stats"]["total_nodes"] = len(graph["nodes"])
    
    save_graph(graph)
    return node_id

def add_edge(from_name, to_name, relation, source=None):
    """添加关系边"""
    graph = load_graph()
    
    # 查找或创建节点
    from_id = None
    to_id = None
    
    for node_id, node in graph["nodes"].items():
        if node["name"] == from_name:
            from_id = node_id
        if node["name"] == to_name:
            to_id = node_id
    
    # 如果节点不存在，返回None
    if not from_id or not to_id:
        return None, "节点不存在"
    
    # 检查边是否已存在
    for edge in graph["edges"]:
        if edge["from"] == from_id and edge["to"] == to_id and edge["relation"] == relation:
            return None, "关系已存在"
    
    # 添加边
    edge = {
        "id": f"边_{hashlib.md5((from_id + to_id + relation).encode()).hexdigest()[:8]}",
        "from": from_id,
        "to": to_id,
        "relation": relation,
        "source": source or "manual",
        "created_at": datetime.now().isoformat()
    }
    graph["edges"].append(edge)
    graph["stats"]["total_edges"] = len(graph["edges"])
    
    save_graph(graph)
    return edge, "添加成功"

def extract_relations(text):
    """从文本中提取关系"""
    relations = []
    import re
    
    # 模式1: "我和X是Y"
    patterns = [
        r'我(.+?)是(.+?)的?([家人朋友同事合作伙伴])',
        r'我和(.+?)(是|认识)(.+?)的?([家人朋友同事合作伙伴])',
        r'(.+?)(是|认识)(.+?)的?([家人朋友同事合作伙伴])',
        r'(.+?)公司(.+?)是.*?([副总经理总经理])',
    ]
    
    # 简单模式匹配
    # "X是Y的家人/朋友"
    family_pattern = re.findall(r'([\u4e00-\u9fa5]{2,4})是(.+?)的?([家人朋友同事])', text)
    for match in family_pattern:
        relations.append({
            "from": "主人",
            "to": match[0],
            "relation": match[2],
            "type": "person"
        })
    
    # "我在X公司工作"
    work_pattern = re.findall(r'在(.+?公司)(?:工作|任职)', text)
    for match in work_pattern:
        relations.append({
            "from": "主人",
            "to": match,
            "relation": "任职",
            "type": "company"
        })
    
    # "X是Y的合作伙伴"
    partner_pattern = re.findall(r'([\u4e00-\u9fa5]{2,4})是(.+?)的?([合作伙伴上下游客户供应商])', text)
    for match in partner_pattern:
        relations.append({
            "from": "主人",
            "to": match[0],
            "relation": match[2],
            "type": "person"
        })
    
    return relations

def auto_build_from_text(text):
    """从文本自动构建图谱"""
    graph = load_graph()
    added = []
    
    # 提取关系
    relations = extract_relations(text)
    
    for rel in relations:
        from_name = rel.get("from", "主人")
        to_name = rel.get("to")
        relation = rel.get("relation")
        entity_type = rel.get("type", "person")
        
        if not to_name or not relation:
            continue
        
        # 添加节点
        from_id = add_node(from_name, "person")
        to_id = add_node(to_name, entity_type)
        
        # 添加边
        edge, msg = add_edge(from_name, to_name, relation, "auto")
        if edge:
            added.append(f"{from_name} --[{relation}]--> {to_name}")
    
    return added

def query_relation(person_a, person_b):
    """查询A和B的关系"""
    graph = load_graph()
    
    # 查找节点ID
    a_id = None
    b_id = None
    
    for node_id, node in graph["nodes"].items():
        if node["name"] == person_a:
            a_id = node_id
        if node["name"] == person_b:
            b_id = node_id
    
    if not a_id or not b_id:
        return None, "未找到相关节点"
    
    # 查找直接关系
    for edge in graph["edges"]:
        if edge["from"] == a_id and edge["to"] == b_id:
            from_node = graph["nodes"].get(edge["from"], {})
            to_node = graph["nodes"].get(edge["to"], {})
            return {
                "from": from_node.get("name"),
                "to": to_node.get("name"),
                "relation": edge["relation"]
            }, "直接关系"
        
        if edge["from"] == b_id and edge["to"] == a_id:
            from_node = graph["nodes"].get(edge["from"], {})
            to_node = graph["nodes"].get(edge["to"], {})
            return {
                "from": to_node.get("name"),
                "to": from_node.get("name"),
                "relation": edge["relation"]
            }, "直接关系"
    
    # 查找间接关系 (通过中间人)
    for edge in graph["edges"]:
        if edge["from"] == a_id:
            # A认识C，C认识B
            for edge2 in graph["edges"]:
                if edge2["from"] == edge["to"] and edge2["to"] == b_id:
                    c_node = graph["nodes"].get(edge["to"], {})
                    from_node = graph["nodes"].get(a_id, {})
                    to_node = graph["nodes"].get(b_id, {})
                    return {
                        "path": [
                            from_node.get("name"),
                            c_node.get("name"),
                            to_node.get("name")
                        ],
                        "relations": [edge["relation"], edge2["relation"]]
                    }, "间接关系"
    
    return None, "未找到关系"

def get_person_network(person_name):
    """获取某人的关系网络"""
    graph = load_graph()
    
    # 找到节点
    person_id = None
    for node_id, node in graph["nodes"].items():
        if node["name"] == person_name:
            person_id = node_id
            break
    
    if not person_id:
        return None, "未找到该人物"
    
    # 找所有相关边
    network = {
        "person": person_name,
        "relations": []
    }
    
    for edge in graph["edges"]:
        if edge["from"] == person_id:
            to_node = graph["nodes"].get(edge["to"], {})
            network["relations"].append({
                "name": to_node.get("name"),
                "relation": edge["relation"],
                "type": to_node.get("type")
            })
        elif edge["to"] == person_id:
            from_node = graph["nodes"].get(edge["from"], {})
            network["relations"].append({
                "name": from_node.get("name"),
                "relation": edge["relation"],
                "type": from_node.get("type")
            })
    
    return network, "成功"

def get_my_network():
    """获取主人的关系网络"""
    return get_person_network("主人")

def get_stats():
    """获取图谱统计"""
    graph = load_graph()
    
    # 按类型统计节点
    type_count = defaultdict(int)
    for node in graph["nodes"].values():
        type_count[node.get("type", "unknown")] += 1
    
    # 按类型统计关系
    rel_count = defaultdict(int)
    for edge in graph["edges"]:
        rel_count[edge.get("relation", "unknown")] += 1
    
    return {
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "node_types": dict(type_count),
        "relation_types": dict(rel_count)
    }

# CLI入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 eva_knowledge_graph.py add <人物> <关系> <对方>  - 添加关系")
        print("  python3 eva_knowledge_graph.py query <A> <B>            - 查询关系")
        print("  python3 eva_knowledge_graph.py network <人物>           - 查看关系网络")
        print("  python3 eva_knowledge_graph.py my                       - 我的关系网")
        print("  python3 eva_knowledge_graph.py build <文本>             - 从文本自动构建")
        print("  python3 eva_knowledge_graph.py stats                   - 统计")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) >= 5:
            from_name = sys.argv[2]
            relation = sys.argv[3]
            to_name = sys.argv[4]
            
            # 自动添加节点
            add_node(from_name, "person")
            add_node(to_name, "person")
            
            edge, msg = add_edge(from_name, to_name, relation)
            if edge:
                print(f"✅ 添加成功: {from_name} --[{relation}]--> {to_name}")
            else:
                print(f"⏭️ {msg}")
        else:
            print("用法: add <人物> <关系> <对方>")
            print("关系: 朋友/家人/同事/合作伙伴/上下游")
    
    elif action == "query":
        if len(sys.argv) >= 4:
            a = sys.argv[2]
            b = sys.argv[3]
            result, msg = query_relation(a, b)
            if result:
                print(f"✅ {msg}: {result}")
            else:
                print(f"⏭️ {msg}")
        else:
            print("用法: query <A> <B>")
    
    elif action == "network":
        name = sys.argv[2] if len(sys.argv) > 2 else "主人"
        network, msg = get_person_network(name)
        if network:
            print(f"=== {name}的关系网络 ===")
            for r in network.get("relations", []):
                print(f"  {r['relation']}: {r['name']} ({r['type']})")
        else:
            print(f"⏭️ {msg}")
    
    elif action == "my":
        network, msg = get_my_network()
        if network:
            print("=== 主人的关系网络 ===")
            for r in network.get("relations", []):
                print(f"  {r['relation']}: {r['name']} ({r['type']})")
        else:
            print("⏭️ 暂无关系")
    
    elif action == "build":
        text = sys.argv[2] if len(sys.argv) > 2 else "测试文本"
        added = auto_build_from_text(text)
        if added:
            print("✅ 自动构建:")
            for a in added:
                print(f"  + {a}")
        else:
            print("⏭️ 未提取到新关系")
    
    elif action == "stats":
        stats = get_stats()
        print("=== 知识图谱统计 ===")
        print(f"节点数: {stats['nodes']}")
        print(f"边数: {stats['edges']}")
        print(f"节点类型: {stats['node_types']}")
        print(f"关系类型: {stats['relation_types']}")
    
    else:
        print(f"❌ 未知动作: {action}")
