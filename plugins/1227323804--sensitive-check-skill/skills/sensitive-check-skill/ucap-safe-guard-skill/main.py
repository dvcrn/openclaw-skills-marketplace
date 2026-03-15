import requests
import json
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_sensitive(content: str, userKey: str = None, sensitive_code_list: list = None):
    """
    错敏信息检测核心函数
    :param content: 待检测文本内容（必传）
    :param userKey: 接口调用密钥（必传，无则提示申请）
    :param sensitive_code_list: 检测类型列表（可选，不传则不携带该参数）
    :return: 标准化检测结果
    """
    # 1. 入参校验 - 文本不能为空
    if not content:
        return {"code": -1, "message": "待检测文本不能为空", "data": None}

    # 2. 校验userKey，缺失则提示申请
    if not userKey:
        apply_url = "https://safeguard-pre.ucap.com.cn/"
        return {
            "code": -2,
            "message": f"缺少接口调用密钥（userKey）！请访问 {apply_url} 申请专属userKey后再使用该技能",
            "data": None,
            "apply_url": apply_url
        }

    # 3. 构造请求参数（包含userKey）
    request_data = {"content": content, "userKey": userKey}
    if sensitive_code_list is not None and len(sensitive_code_list) > 0:
        request_data["sensitiveCodeList"] = sensitive_code_list

    # 4. 调用 UCAP 预发环境接口
    try:
        url = "https://safeguard-pre.ucap.com.cn/safe-guard-back/openApi/transferArithmetic"
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            url=url,
            headers=headers,
            json=request_data,
            timeout=15,
            verify=False  # 禁用 SSL 验证
        )
        response.raise_for_status()

        # 5. 标准化返回结果
        return {
            "code": 0,
            "message": "检测成功",
            "data": response.json()
        }

    # 异常处理
    except requests.exceptions.Timeout:
        return {"code": -3, "message": "接口调用超时（15秒）", "data": None}
    except requests.exceptions.HTTPError as e:
        return {"code": -4, "message": f"接口返回错误：{str(e)}",
                "data": response.text if 'response' in locals() else None}
    except requests.exceptions.ConnectionError as e:
        return {"code": -5, "message": f"网络连接失败：{str(e)}", "data": None}
    except requests.exceptions.RequestException as e:
        return {"code": -6, "message": f"接口调用失败：{str(e)}", "data": None}
    except json.JSONDecodeError:
        return {"code": -7, "message": "接口返回非 JSON 格式数据",
                "data": response.text if 'response' in locals() else None}


# OpenClaw 标准入口函数
def run(params: dict):
    """
    OpenClaw 对话调用的标准入口
    :param params: OpenClaw 传入的参数字典
    :return: 检测结果
    """
    return check_sensitive(
        content=params.get("content"),
        userKey=params.get("userKey"),  # 读取传入的userKey
        sensitive_code_list=params.get("sensitive_code_list")
    )


# 本地测试代码
if __name__ == "__main__":
    # 测试1：无userKey的情况（触发提示）
    test_result1 = check_sensitive(content="欣欣向绒")
    print("测试1（无userKey）：")
    print(json.dumps(test_result1, ensure_ascii=False, indent=2))

    # 测试2：传入userKey的情况（正常调用）
    test_result2 = check_sensitive(
        content="欣欣向绒",
        userKey="3f47e10107eac26d6a1333df76d1e964"
    )
    print("\n测试2（传入userKey）：")
    print(json.dumps(test_result2, ensure_ascii=False, indent=2))