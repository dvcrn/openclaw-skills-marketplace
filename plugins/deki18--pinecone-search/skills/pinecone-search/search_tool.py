#!/usr/bin/env python3
"""
Pinecone 向量搜索工具
用途：搜索本地知识库

环境变量要求：
- PINECONE_API_KEY: Pinecone API Key
- EMBEDDING_API_KEY: 向量嵌入 API Key
- EMBEDDING_BASE_URL: 向量嵌入 API 地址
- EMBEDDING_MODEL: 向量嵌入模型（可选，默认 text-embedding-3-large）
- INDEX_NAME: Pinecone 索引名称（可选，默认 workspace）
- NAMESPACE: Pinecone 命名空间（可选）
"""

import os
import sys
import argparse
from pathlib import Path
from openai import OpenAI
from pinecone import Pinecone

def load_env_file():
    """Load .env file from skill directory"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and key not in os.environ:
                        os.environ[key] = value

def load_config():
    """加载配置"""
    config = {
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
        "EMBEDDING_API_KEY": os.getenv("EMBEDDING_API_KEY"),
        "EMBEDDING_BASE_URL": os.getenv("EMBEDDING_BASE_URL"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
        "INDEX_NAME": os.getenv("INDEX_NAME", "workspace"),
        "NAMESPACE": os.getenv("NAMESPACE", "")
    }

    # 验证必需配置
    missing = [k for k, v in config.items() if k in ["PINECONE_API_KEY", "EMBEDDING_API_KEY", "EMBEDDING_BASE_URL"] and not v]
    if missing:
        print(f"❌ 缺少必需的配置: {', '.join(missing)}", file=sys.stderr)
        print(f"\n请创建 .env 文件并配置以下环境变量:", file=sys.stderr)
        print(f"  PINECONE_API_KEY=your_api_key", file=sys.stderr)
        print(f"  EMBEDDING_API_KEY=your_api_key", file=sys.stderr)
        print(f"  EMBEDDING_BASE_URL=your_api_url", file=sys.stderr)
        sys.exit(1)

    return config

def search(query: str, top_k: int = 3, config=None):
    """
    执行向量搜索

    Args:
        query: 搜索查询
        top_k: 返回结果数量
        config: 配置字典

    Returns:
        搜索结果列表
    """
    if config is None:
        config = load_config()

    try:
        # 初始化 Pinecone
        pc = Pinecone(api_key=config["PINECONE_API_KEY"])

        # 检查索引是否存在
        indexes = pc.list_indexes().names()
        if config["INDEX_NAME"] not in indexes:
            print(f"❌ 索引 '{config['INDEX_NAME']}' 不存在", file=sys.stderr)
            print(f"可用索引: {indexes}", file=sys.stderr)
            return []

        # 获取索引
        index = pc.Index(config["INDEX_NAME"])

        # 初始化 OpenAI 客户端
        client = OpenAI(
            api_key=config["EMBEDDING_API_KEY"],
            base_url=config["EMBEDDING_BASE_URL"]
        )

        # 生成查询向量
        response = client.embeddings.create(
            model=config["EMBEDDING_MODEL"],
            input=query,
            encoding_format="float"
        )

        query_vector = response.data[0].embedding

        # 执行搜索
        namespace = config["NAMESPACE"] if config["NAMESPACE"] else None
        search_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            include_values=False,
            namespace=namespace
        )

        # 格式化结果
        formatted_results = []
        if search_results.matches:
            for i, match in enumerate(search_results.matches, 1):
                metadata = match.metadata or {}
                formatted_results.append({
                    "rank": i,
                    "score": match.score,
                    "text": metadata.get("text", match.id),
                    "source": metadata.get("source", match.id)
                })
        else:
            print("ℹ️  未找到匹配结果")
            return []

        return formatted_results

    except Exception as e:
        print(f"❌ 搜索失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Pinecone 知识库搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python search_tool.py "混凝土浇筑标准是什么？"
  python search_tool.py "查询内容" --top-k 5
        """
    )
    parser.add_argument("query", type=str, help="搜索查询")
    parser.add_argument("--top-k", type=int, default=3, help="返回结果数量 (默认: 3)")

    args = parser.parse_args()

    # Load .env file first
    load_env_file()

    # 加载配置
    config = load_config()

    print(f"🔍 正在搜索: {args.query}\n")

    # 执行搜索
    results = search(args.query, args.top_k, config)

    if results:
        print("=" * 60)
        for result in results:
            print(f"\n【结果 #{result['rank']}】")
            print(f"匹配度: {result['score']:.4f}")
            print(f"来源: {result['source']}")
            print(f"内容:")
            print(f"  {result['text']}")
            print("-" * 60)
    else:
        print("❌ 未找到任何结果")

if __name__ == "__main__":
    main()
