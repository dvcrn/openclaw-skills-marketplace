# 效率工坊 - 商务邮件自动回复模板

**版本：** v2.0  
**日期：** 2026-03-08  
**团队：** 效率工坊 | Efficiency Lab

---

## 📧 模板列表

### 模板 1：商机询价邮件
- **触发词：** 询价/报价/价格/多少钱/合作/定制/开发/项目
- **回复模板：** template_business_inquiry
- **优先级：** 高（立即回复）

### 模板 2：一般咨询邮件
- **触发词：** 咨询/了解/询问/详情/功能/服务
- **回复模板：** template_consultation
- **优先级：** 中（1 小时内回复）

### 模板 3：技术对接邮件
- **触发词：** API/接口/集成/对接/技术
- **回复模板：** template_technical
- **优先级：** 中（1 小时内回复）

---

## 🎯 使用方式

在 check_emails_complete.py 中调用：
```python
def get_reply_template(email_type, keywords_found):
    """根据邮件类型获取回复模板"""
    if email_type == 'priority' or any(kw in keywords_found for kw in ['询价', '报价', '合作']):
        return REPLY_TEMPLATES['business_inquiry']
    elif any(kw in keywords_found for kw in ['API', '接口', '技术']):
        return REPLY_TEMPLATES['technical']
    else:
        return REPLY_TEMPLATES['consultation']
```

---

**完整模板内容见邮件回复代码**
