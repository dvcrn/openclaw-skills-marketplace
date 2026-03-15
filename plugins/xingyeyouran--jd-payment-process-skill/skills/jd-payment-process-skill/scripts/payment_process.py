import sys


def deal_payment(merchant_wallet_address: str, amount: int, payer_authorization_sign: str):
    test_token = "AABBCCDD"
    print(f"处理支付中... 商家: {merchant_wallet_address}, 金额: {amount}, 付款签名: {payer_authorization_sign}")
    return test_token


if __name__ == "__main__":
    # 检查传入参数的数量是否正确 (1个脚本名 + 3个参数 = 4)
    if len(sys.argv) != 4:
        print("用法: python main.py <merchant_wallet> <amount> <payer_wallet>")
        sys.exit(1)

    # 获取参数
    merchant = sys.argv[1]
    # 注意：命令行传入的参数默认都是字符串，所以 amount 需要转换成 int
    amount = int(sys.argv[2])
    payer = sys.argv[3]

    # 传入函数并执行
    token = deal_payment(merchant, amount, payer)
    print(f"支付凭证: {token}")