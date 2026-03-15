#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import uuid
import time
import json
import argparse
import requests
from pathlib import Path
from typing import Optional

# ------------------------------------------------------
# 作者: 张发
# 修改: ClawHub Skill Adapter
# 文件：unidoc_parse.py
# 创建: 2025/8/18
# 修改: 2025/3/10
# 功能：UniDoc 文档解析工具 - ClawHub Skill 实现
# 版本：1.0.0
# 说明：基于 UniDoc API 实现文档格式转换
# 版权所有：云知声智能科技股份有限公司
# ------------------------------------------------------


# API Endpoints
BASE_URL = "http://unidoc.uat.hivoice.cn"
SYNC_UPLOAD_URL = f"{BASE_URL}/syncUploadFile"
ASYNC_UPLOAD_URL = f"{BASE_URL}/asyncUploadFile"
EXPORT_URL = f"{BASE_URL}/exportFile"
STATUS_URL = f"{BASE_URL}/getFileStatus"


class UniDocParser:
    """UniDoc 文档解析器"""

    def __init__(
        self,
        target_type: str = "md",
        func: str = "unisound",
        uid: Optional[str] = None
    ):
        """
        初始化解析器
        :param target_type: 目标格式 (md/json)
        :param func: 转换方法
        :param uid: 用户ID
        """
        self.target_type = target_type
        self.func = func
        self.uid = uid or uuid.uuid4().hex

    def sync_convert_file(self, file_path: str) -> str:
        """
        同步转换文件
        :param file_path: 文件路径
        :return: 转换后的内容
        """
        # 上传文件
        body = {"uid": self.uid, "func": self.func}
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(SYNC_UPLOAD_URL, data=body, files=files)

        res = response.json()

        # 检查响应
        if "result" not in res or res.get("result") is None:
            raise ValueError(f"API Error: {res.get('message', 'Unknown error')}")

        file_id = res.get("result").get("fileId")

        # 获取转换后的文件内容
        return self._export_file(file_id)

    def async_convert_file(self, file_path: str, poll_interval: int = 1) -> str:
        """
        异步转换文件
        :param file_path: 文件路径
        :param poll_interval: 轮询间隔（秒）
        :return: 转换后的内容
        """
        # 上传文件
        body = {"uid": self.uid, "func": self.func}
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(ASYNC_UPLOAD_URL, data=body, files=files)

        res = response.json()

        # 检查响应
        if "result" not in res or res.get("result") is None:
            raise ValueError(f"API Error: {res.get('message', 'Unknown error')}")

        file_id = res.get("result")

        # 轮询任务状态
        task_status = None
        max_attempts = 300  # 最多轮询5分钟
        attempts = 0

        while task_status not in ["SUCCESS", "FAILED"]:
            if attempts >= max_attempts:
                raise TimeoutError("File conversion timed out after 5 minutes")

            params = {"fileId": file_id}
            response = requests.get(url=STATUS_URL, params=params)
            status_res = response.json()
            task_status = status_res.get("result", {}).get("status")

            if task_status not in ["SUCCESS", "FAILED"]:
                time.sleep(poll_interval)
            attempts += 1

        if task_status == "FAILED":
            raise RuntimeError("File conversion failed on server")

        # 获取转换后的文件内容
        return self._export_file(file_id)

    def _export_file(self, file_id: str) -> str:
        """
        导出转换后的文件
        :param file_id: 文件ID
        :return: 文件内容
        """
        params = {"fileId": file_id, "targetType": self.target_type}
        response = requests.get(url=EXPORT_URL, params=params)
        export_res = response.json()
        file_url = export_res.get("result")

        if not file_url:
            raise ValueError(f"Export failed: {export_res.get('message', 'Unknown error')}")

        content = requests.get(file_url).content.decode('utf-8')
        return content


def parse_document(
    file_path: str,
    output_dir: str,
    format_type: str = "md",
    mode: str = "sync",
    func: str = "unisound",
    uid: Optional[str] = None
) -> str:
    """
    解析文档并保存到输出目录
    :param file_path: 文档路径
    :param output_dir: 输出目录
    :param format_type: 输出格式 (md/json)
    :param mode: 处理模式 (sync/async)
    :param func: 转换方法
    :param uid: 用户ID
    :return: 输出文件路径
    """
    # 验证输入文件
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # 创建解析器
    parser = UniDocParser(target_type=format_type, func=func, uid=uid)

    # 根据模式选择转换方式
    print(f"Parsing document: {file_path}")
    print(f"Mode: {mode.upper()}, Format: {format_type.upper()}")

    if mode == "async":
        content = parser.async_convert_file(file_path)
    else:
        content = parser.sync_convert_file(file_path)

    # 创建输出目录
    doc_name = Path(file_path).stem
    output_subdir = os.path.join(output_dir, doc_name)
    os.makedirs(output_subdir, exist_ok=True)

    # 保存输出文件
    output_filename = f"output.{format_type}"
    output_path = os.path.join(output_subdir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Output saved to: {output_path}")
    return output_path


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="UniDoc Document Parser - Convert documents using UniDoc API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF to Markdown (sync mode)
  %(prog)s document.pdf --format md

  # Convert DOCX to JSON (async mode)
  %(prog)s document.docx --format json --mode async

  # Custom output directory
  %(prog)s document.pdf --output ./my-output
        """
    )

    parser.add_argument(
        "file",
        help="Path to the document file to parse"
    )

    parser.add_argument(
        "--format",
        choices=["md", "json"],
        default="md",
        help="Output format (default: md)"
    )

    parser.add_argument(
        "--mode",
        choices=["sync", "async"],
        default="sync",
        help="Processing mode: sync or async (default: sync)"
    )

    parser.add_argument(
        "--func",
        default="unisound",
        help="Conversion method/algorithm (default: unisound)"
    )

    parser.add_argument(
        "--output",
        default="./unidoc-output",
        help="Output directory path (default: ./unidoc-output)"
    )

    parser.add_argument(
        "--uid",
        default=None,
        help="Custom user ID (auto-generated if not provided)"
    )

    args = parser.parse_args()

    try:
        output_path = parse_document(
            file_path=args.file,
            output_dir=args.output,
            format_type=args.format,
            mode=args.mode,
            func=args.func,
            uid=args.uid
        )
        print("\n✓ Document parsed successfully!")
        return 0

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except (ValueError, RuntimeError, TimeoutError) as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"✗ Network Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
