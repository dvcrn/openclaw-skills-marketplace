# main.py（错敏检测 Skill）
import requests
import json
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_sensitive(content: str, sensitive_code_list: list = None):
    """
    错敏信息检测核心函数
    :param content: 待检测文本内容（必传）
    :param sensitive_code_list: 检测类型列表（可选，不传则不携带该参数）
    :return: 标准化检测结果
    """
    # 1. 入参校验
    if not content:
        return {"code": -1, "message": "待检测文本不能为空", "data": None}

    # 2. 构造请求参数
    request_data = {"content": content}
    if sensitive_code_list is not None and len(sensitive_code_list) > 0:
        request_data["sensitiveCodeList"] = sensitive_code_list

    # 3. 调用 UCAP 预发环境接口
    try:
        url = "https://safeguard-pre.ucap.com.cn/safe-guard-back/openApi/transferArithmetic"
        headers = {
            "Content-Type": "application/json"
        }

        # HTTP 请求（禁用 SSL 验证）
        response = requests.post(
            url=url,
            headers=headers,
            json=request_data,
            timeout=15,
            verify=False  # 禁用 SSL 验证
        )
        response.raise_for_status()

        # 4. 标准化返回结果
        return {
            "code": 0,
            "message": "检测成功",
            "data": response.json()
        }

    # 异常处理
    except requests.exceptions.Timeout:
        return {"code": -3, "message": "接口调用超时（15秒）", "data": None}
    except requests.exceptions.HTTPError as e:
        return {"code": -4, "message": f"接口返回错误：{str(e)}", "data": response.text if 'response' in locals() else None}
    except requests.exceptions.ConnectionError as e:
        return {"code": -5, "message": f"网络连接失败：{str(e)}", "data": None}
    except requests.exceptions.RequestException as e:
        return {"code": -6, "message": f"接口调用失败：{str(e)}", "data": None}
    except json.JSONDecodeError:
        return {"code": -7, "message": "接口返回非 JSON 格式数据", "data": response.text if 'response' in locals() else None}


# OpenClaw 标准入口函数
def run(params: dict):
    """
    OpenClaw 对话调用的标准入口
    :param params: OpenClaw 传入的参数字典
    :return: 检测结果
    """
    return check_sensitive(
        content=params.get("content"),
        sensitive_code_list=params.get("sensitive_code_list")
    )


# 本地测试代码
if __name__ == "__main__":
    test_result = check_sensitive(
        content="测试文本内容"
    )
    print(json.dumps(test_result, ensure_ascii=False, indent=2))
