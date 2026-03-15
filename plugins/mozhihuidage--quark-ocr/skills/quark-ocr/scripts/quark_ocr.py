#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
import time
import uuid
import socket
import ipaddress
from typing import Tuple, Dict, Any, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from requests.exceptions import Timeout, ConnectionError


# --- 配置常量 ---
# [安全审计] 目标 API 地址已硬编码，确保所有流量仅发往夸克官方服务
API_URL = "https://scan-business.quark.cn/vision"
ALLOWED_TARGET_HOST = "scan-business.quark.cn"

# URL 安全配置
MAX_URL_LENGTH = 2048
ALLOWED_PROTOCOLS = {"http", "https"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}

# 危险域名关键词
DANGEROUS_KEYWORDS = ["localhost", "internal", "intranet", "admin", "test"]


@dataclass
class OCRResult:
    """OCR 识别结果"""
    code: str
    message: Optional[str]
    text_list: List[str]

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps({
            "code": self.code,
            "message": self.message,
            "Text": self.text_list
        }, ensure_ascii=False, indent=2)


class URLValidator:
    """URL 安全验证器"""

    @staticmethod
    def validate(url: str) -> Tuple[bool, Optional[str]]:
        """
        验证 URL 的安全性
        Returns: (is_valid, error_message)
        """
        if not url or not isinstance(url, str):
            return False, "URL cannot be empty"

        url = url.strip()

        if len(url) > MAX_URL_LENGTH:
            return False, f"URL exceeds maximum length of {MAX_URL_LENGTH} characters"

        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"

        if parsed.scheme.lower() not in ALLOWED_PROTOCOLS:
            return False, f"Protocol '{parsed.scheme}' not allowed."

        hostname = parsed.hostname
        if not hostname:
            return False, "URL must contain a valid hostname"

        # 1. 基础关键词过滤
        hostname_lower = hostname.lower()
        for keyword in DANGEROUS_KEYWORDS:
            if keyword in hostname_lower:
                return False, f"Hostname contains restricted keyword: {keyword}"

        # 2. [增强] DNS 解析后安全校验 (防止 DNS Rebinding / SSRF)
        # 即使 hostname 看起来是公网域名，也要检查它实际解析到的 IP
        is_safe, err_msg = URLValidator._validate_dns_resolution(hostname)
        if not is_safe:
            return False, err_msg

        # 3. 文件扩展名检查
        path = parsed.path.lower()
        if path and "." in path:
            ext = os.path.splitext(path)[1]
            if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
                return False, f"File extension '{ext}' not allowed."

        return True, None

    @staticmethod
    def _validate_dns_resolution(hostname: str) -> Tuple[bool, str]:
        """
        [安全关键] 解析域名并验证所有关联 IP 均为公网 IP。
        防止 DNS Rebinding 攻击。
        """
        try:
            # 获取所有解析记录 (IPv4 & IPv6)
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)

            for family, socktype, proto, canonname, sockaddr in addr_info:
                ip = sockaddr[0]
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    # 拒绝私有、回环、链路本地、多播地址
                    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                        return False, f"Security Block: {hostname} resolves to private/internal IP {ip}"
                except ValueError:
                    continue
            return True, "OK"
        except socket.gaierror:
            # 如果无法解析，稍后由 requests 库处理报错，这里可以放行或拦截
            # 为了严格安全，建议拦截无法解析的域名，或者允许由后续网络请求报错
            return True, "OK"

    @staticmethod
    def _is_ip_address(hostname: str) -> bool:
        ipv4_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        return bool(re.match(ipv4_pattern, hostname))

    @staticmethod
    def _is_private_ip(ip: str) -> bool:
        # 此函数保留作为备用，主要逻辑已移至 _validate_dns_resolution
        private_patterns = [
            r"^127\.", r"^10\.", r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
            r"^192\.168\.", r"^169\.254\.", r"^0\.", r"^224\.", r"^240\."
        ]
        return any(re.match(p, ip) for p in private_patterns)


class CredentialManager:
    @staticmethod
    def load() -> Tuple[str, str]:
        cid = os.getenv("QUARK_OCR_CLIENT_ID", "").strip()
        csec = os.getenv("QUARK_OCR_CLIENT_SECRET", "").strip()
        if cid and csec:
            return cid, csec
        raise ValueError("Credentials missing: QUARK_OCR_CLIENT_ID and QUARK_OCR_CLIENT_SECRET required")


class SignatureGenerator:
    SUPPORTED_METHODS = {
        "sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5,
        "sha3-256": hashlib.sha3_256, "sha3_256": hashlib.sha3_256,
    }

    @classmethod
    def generate(cls, client_id: str, client_secret: str, business: str,
                 sign_method: str, sign_nonce: str, timestamp: int) -> str:
        raw_str = f"{client_id}_{business}_{sign_method}_{sign_nonce}_{timestamp}_{client_secret}"
        method_lower = sign_method.lower()
        if method_lower not in cls.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported sign method: {sign_method}")
        return cls.SUPPORTED_METHODS[method_lower](raw_str.encode("utf-8")).hexdigest()


class QuarkOCRClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()

        # [安全审计] 显式验证硬编码的 API URL 是否符合预期域名
        parsed_api = urlparse(API_URL)
        if parsed_api.hostname != ALLOWED_TARGET_HOST and not parsed_api.hostname.endswith("." + ALLOWED_TARGET_HOST):
            raise RuntimeError(f"Security Configuration Error: API_URL hostname '{parsed_api.hostname}' is not allowed.")

    def recognize(self, image_url: str) -> OCRResult:
        is_valid, error_msg = URLValidator.validate(image_url)
        if not is_valid:
            return OCRResult(code="URL_VALIDATION_ERROR", message=f"URL validation failed: {error_msg}", text_list=[])

        param = self._build_request_param(image_url)
        response = self._send_request(param)
        return self._parse_response(response)

    def _build_request_param(self, image_url: str) -> Dict[str, Any]:
        business = "vision"
        sign_method = "SHA3-256"
        sign_nonce = uuid.uuid4().hex
        timestamp = int(time.time() * 1000)
        signature = SignatureGenerator.generate(
            self.client_id, self.client_secret, business, sign_method, sign_nonce, timestamp
        )
        return {
            "dataUrl": image_url, "dataType": "image", "serviceOption": "ocr",
            "inputConfigs": '{"function_option":"RecognizeGeneralDocument"}',
            "outputConfigs": '{"need_return_image":"True"}',
            "reqId": uuid.uuid4().hex, "clientId": self.client_id,
            "signMethod": sign_method, "signNonce": sign_nonce,
            "timestamp": timestamp, "signature": signature,
        }

    def _send_request(self, param: Dict[str, Any]) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        # [安全修复]
        # 1. 使用硬编码的 API_URL (已确认为白名单域名)
        # 2. allow_redirects=False 防止 302 跳转到内网
        # 3. timeout 防止 DoS
        response = self.session.post(
            API_URL,
            json=param,
            headers=headers,
            timeout=60,
            allow_redirects=False  # 关键：禁止重定向
        )
        return response

    def _parse_response(self, response: requests.Response) -> OCRResult:
        if response.status_code != 200:
            error_msg = response.text[:200] if response.text else "No error message"
            return OCRResult(code="HTTP_ERROR", message=f"HTTP {response.status_code}: {error_msg}", text_list=[])
        try:
            body = response.json()
        except json.JSONDecodeError as e:
            return OCRResult(code="JSON_PARSE_ERROR", message=f"Failed to parse JSON: {str(e)}", text_list=[])

        code = body.get("code", "unknown")
        message = body.get("message")
        text_list = self._extract_text_list(body.get("data", {}))
        return OCRResult(code=code, message=message, text_list=text_list)

    def _extract_text_list(self, data: Dict[str, Any]) -> List[str]:
        if not isinstance(data, dict): return []
        ocr_info_list = data.get("OcrInfo", [])
        if not isinstance(ocr_info_list, list): return []
        return [str(item["Text"]) for item in ocr_info_list if isinstance(item, dict) and "Text" in item]

def main():
    parser = argparse.ArgumentParser(description="Quark OCR - Secure JSON Output")
    parser.add_argument("--url", "-u", required=True, help="图片 URL")
    args = parser.parse_args()

    try:
        client_id, client_secret = CredentialManager.load()
        client = QuarkOCRClient(client_id, client_secret)
        result = client.recognize(args.url)
        print(result.to_json())
    except ValueError as e:
        print(OCRResult(code="CONFIG_ERROR", message=str(e), text_list=[]).to_json())
        sys.exit(1)
    except Timeout:
        print(OCRResult(code="TIMEOUT", message="Request timed out", text_list=[]).to_json())
        sys.exit(1)
    except ConnectionError as e:
        print(OCRResult(code="NETWORK_ERROR", message=f"Network failed: {str(e)}", text_list=[]).to_json())
        sys.exit(1)
    except Exception as e:
        print(OCRResult(code="UNKNOWN_ERROR", message=f"Unexpected error: {str(e)}", text_list=[]).to_json())
        sys.exit(1)

if __name__ == "__main__":
    main()