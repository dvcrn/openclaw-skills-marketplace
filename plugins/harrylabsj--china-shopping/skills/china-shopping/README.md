# China Shopping Skill v1.0.0

中国购物网站推荐工具 - 根据商品名称推荐最佳购物网站

## 功能简介

根据用户输入的商品名称，智能推荐最适合购买该商品的 1-3 个中国购物网站。

## 安装

### 依赖

- Python 3.7+
- 无需额外依赖（使用标准库）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/harrylabs0913/china-shopping.git
cd china-shopping

# 设置可执行权限
chmod +x china-shopping.py

# 可选：创建软链接到 PATH
ln -s $(pwd)/china-shopping.py ~/.local/bin/china-shopping
```

## 使用方法

### 基本用法

```bash
# 推荐购买手机的网站
china-shopping recommend "手机"

# 推荐购买衣服的网站
china-shopping 推荐 "衣服"

# 显示所有支持的商品类别
china-shopping categories

# 显示帮助
china-shopping help
```

### 命令选项

```bash
china-shopping recommend <商品名称> [选项]

选项:
  -c, --count <数量>    推荐网站数量（默认: 3）
  -f, --format <格式>   输出格式: text 或 json（默认: text）
  -v, --version         显示版本信息
  -h, --help            显示帮助信息
```

### 示例输出

```
$ china-shopping recommend "手机"
📱 手机 (电子产品) 推荐购物网站：

1. 京东 (https://www.jd.com)
   └─ 正品保障，物流速度快，售后服务好
   🏷️ 正品 | 物流快 | 售后好

2. 天猫 (https://www.tmall.com)
   └─ 品牌官方旗舰店，品质有保障
   🏷️ 官方 | 品牌 | 品质

3. 苏宁易购 (https://www.suning.com)
   └─ 家电数码专业平台，线下门店多
   🏷️ 专业 | 家电 | 线下

💡 购物提示：
   • 购买电子产品建议选择官方旗舰店或自营平台
   • 注意查看商品评价和售后服务政策
   • 比价时注意配置和套餐差异
```

## 支持的商品类别

| 类别 | 关键词示例 | 推荐网站 |
|------|-----------|---------|
| 📱 电子产品 | 手机、电脑、相机、耳机、数码 | 京东、天猫、苏宁易购、小米商城 |
| 👕 服装服饰 | 衣服、鞋子、包包、外套、穿搭 | 淘宝、天猫、唯品会、京东 |
| 🛒 食品杂货 | 零食、水果、生鲜、粮油、饮料 | 京东到家、天猫超市、1号店、每日优鲜 |
| 💄 美妆护肤 | 化妆品、护肤品、面膜、口红、香水 | 天猫国际、京东美妆、小红书、网易考拉 |

## 支持的购物网站

- **京东** (jd.com) - 正品保障，物流快
- **天猫** (tmall.com) - 品牌官方
- **淘宝** (taobao.com) - 种类最全
- **苏宁易购** (suning.com) - 家电数码专业
- **唯品会** (vip.com) - 品牌折扣
- **小米商城** (mi.com) - 小米生态
- **京东到家** (daojia.jd.com) - 生鲜配送
- **天猫超市** (chaoshi.tmall.com) - 超市商品
- **小红书** (xiaohongshu.com) - 社区分享
- **网易考拉** (kaola.com) - 进口商品

## 项目结构

```
china-shopping/
├── china-shopping.py      # 主程序（Python CLI）
├── README.md              # 使用说明
├── requirements.txt       # 依赖文件
├── package.json           # 元数据
├── data/
│   └── categories.json    # 商品类别数据
└── lib/                   # 库文件目录
    ├── utils.sh
    └── recommend.sh
```

## 技术说明

- **语言**: Python 3.7+
- **数据存储**: JSON 文件
- **分类匹配**: 基于关键词映射表
- **推荐逻辑**: 按商品类别返回预定义的网站列表

## 版本历史

### v1.0.0 (2025-03-10)
- 初始版本发布
- 支持 4 大商品类别
- 推荐 1-3 个最佳购物网站
- 支持文本和 JSON 输出格式

## 许可证

MIT License

## 作者

harrylabs0913
