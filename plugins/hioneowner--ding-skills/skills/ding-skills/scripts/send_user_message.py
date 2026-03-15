"""机器人发送单聊消息

用法: python scripts/send_user_message.py "<userId>" "<robotCode>" "<消息内容>"
"""

import sys
import os
import json as json_mod
sys.path.insert(0, os.path.dirname(__file__))
from dingtalk_client import get_access_token, api_request, handle_error, output


def main():
    args = [a for a in sys.argv[1:] if a != "--debug"]
    if len(args) < 3:
        output({"success": False, "error": {"code": "INVALID_ARGS", "message": "用法: python scripts/send_user_message.py \"<userId>\" \"<robotCode>\" \"<消息内容>\""}})
        sys.exit(1)

    user_id = args[0]
    robot_code = args[1]
    message = args[2]

    try:
        token = get_access_token()
        print("正在发送单聊消息...", file=sys.stderr)
        result = api_request("POST", "/robot/oToMessages/batchSend", token, json_body={
            "robotCode": robot_code,
            "userIds": [user_id],
            "msgKey": "sampleText",
            "msgParam": json_mod.dumps({"content": message}),
        })
        output({
            "success": True,
            "userId": user_id,
            "robotCode": robot_code,
            "processQueryKey": result.get("processQueryKey"),
            "flowControlledStaffIdList": result.get("flowControlledStaffIdList", []),
            "invalidStaffIdList": result.get("invalidStaffIdList", []),
            "message": message,
        })
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
