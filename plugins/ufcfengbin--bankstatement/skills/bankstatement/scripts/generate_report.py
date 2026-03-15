import sys
import os
import requests
import json
import argparse


def generate_report(file_urls, query, token=None):
    url = "http://rd-test.dfwytech.com:9014/lsxx/genarate/report"
    headers = {
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Priority: argument > env var
    final_token = token or os.environ.get("ZY_TOKEN")
    if final_token:
        headers["Authorization"] = f"Bearer {final_token}"

    data = {"file_urls": file_urls, "query": query}

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        json_data = response.json()
        if json_data.get("code") == 200:
            print(json_data.get("data"))
        else:
            if json_data.get("code") == 400:
                print("api_key无效")
            else:
                msg = json_data.get("msg", "Unknown error")
                print(f"Error: {msg}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate report from server file")
    parser.add_argument("token", help="API Token")
    parser.add_argument("file_urls", help="Server file path")
    parser.add_argument("query", help="Query string")
    args = parser.parse_args()
    generate_report(args.file_urls, args.query, args.token)
    # generate_report(
    #     "/models/app/dify_api/uploads/20260311/d2bf2bf2f5dd4a3b8d4858509ced5a19/04844940f04a5699154e7918055dc78a_工商银行历史明细（申请单号：25011413031230849278） - 副本.pdf",
    #     "生成报告",
    # )
