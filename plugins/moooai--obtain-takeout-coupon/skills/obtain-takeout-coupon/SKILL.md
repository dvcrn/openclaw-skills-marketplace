---
name: obtain-takeout-coupon
description: "获取外卖优惠券（隐藏券、大额券）的技能，支持平台： 美团（Meituan），淘宝闪购（饿了么，taobao）。A skill for obtaining takeout coupons (hidden coupons, large-value coupons), supported platforms: Meituan, Taobao Flash Sale (Ele.me, Taobao).."
---

# 获取最新的外卖优惠券 Obtain Takeout Coupons
获取中国在线购物平台的外卖优惠券（大额券，隐藏券），支持美团、淘宝闪购、饿了么。

```yaml
# 参数解释
source:
  1: 美团优惠券
  2: 淘宝闪购优惠券
  3: 饿了么优惠券
```

## 获取优惠券口令(字符串格式，不要更改接口返回的内容，否则会时效)  
```shell
uv run scripts/route.py search --source={source}
```

## 隐私提示 Privacy Tips
本技能提供的脚本不会读写本地文件，可放心使用 The scripts provided by this skill do not read or write local files, so you can use them with confidence.