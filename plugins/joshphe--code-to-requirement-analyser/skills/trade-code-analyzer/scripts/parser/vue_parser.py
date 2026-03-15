# scripts/parser/vue_parser.py
import re
import ast
from typing import List, Dict, Any, Optional
from .base import BaseCodeParser, ParsedComponent, ParsedAPI, ParsedRule

class VueParser(BaseCodeParser):
    """Vue单文件组件解析器"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.template = ""
        self.script = ""
        self.style = ""
        self._split_sections()
        
    def _split_sections(self):
        """分割SFC三个部分"""
        # 提取template
        template_match = re.search(
            r'<template(?:\s+[^>]*)?>(.*?)</template>', 
            self.content, re.DOTALL
        )
        self.template = template_match.group(1) if template_match else ""
        
        # 提取script
        script_match = re.search(
            r'<script(?:\s+[^>]*)?>(.*?)</script>', 
            self.content, re.DOTALL
        )
        self.script = script_match.group(1) if script_match else ""
        
        # 提取style（可选）
        style_match = re.search(
            r'<style(?:\s+[^>]*)?>(.*?)</style>', 
            self.content, re.DOTALL
        )
        self.style = style_match.group(1) if style_match else ""
        
    def parse(self) -> Dict[str, Any]:
        """主解析方法"""
        return {
            "file_info": {
                "path": self.file_path,
                "type": "vue",
                "size": len(self.content),
                "has_scoped_style": 'scoped' in (re.search(r'<style[^>]*>', self.content) or [''])[0]
            },
            "structure": {
                "template_lines": len(self.template.splitlines()),
                "script_lines": len(self.script.splitlines()),
                "imports": self._extract_imports(),
                "components_used": self._extract_component_usage()
            },
            "components": [c.__dict__ for c in self.extract_components()],
            "apis": [a.__dict__ for a in self.extract_apis()],
            "business_rules": [r.__dict__ for r in self.extract_business_rules()],
            "data_model": self._extract_data_model(),
            "computed_properties": self._extract_computed(),
            "watchers": self._extract_watchers(),
            "lifecycle_hooks": self._extract_lifecycle(),
            "complexity": self.calculate_complexity()
        }
    
    def extract_components(self) -> List[ParsedComponent]:
        """提取Vue组件"""
        components = []
        
        # 匹配组件标签（支持自闭合和双标签）
        pattern = r'<([A-Z][a-zA-Z0-9]*|[a-z]+-[a-z-]+)(?:\s+([^>]*?))?/?>'
        
        for match in re.finditer(pattern, self.template):
            tag_name = match.group(1)
            attrs_str = match.group(2) or ""
            attrs = self._parse_attrs(attrs_str)
            
            # 推断组件类型和业务语义
            comp_type, business_semantic = self._infer_component_type(tag_name, attrs)
            
            component = ParsedComponent(
                name=tag_name,
                type=comp_type,
                props=attrs,
                events=self._extract_events(attrs_str),
                children=[],  # 简化处理，实际需要递归解析
                source_range=(self._get_line_number(match.start()), 
                            self._get_line_number(match.end())),
                business_semantic=business_semantic
            )
            components.append(component)
        
        return components
    
    def _infer_component_type(self, tag: str, attrs: Dict) -> tuple:
        """推断组件类型和业务语义"""
        # 表单组件
        form_components = {
            'el-input': ('input', '文本输入'),
            'el-select': ('select', '选项选择'),
            'el-date-picker': ('date', '日期选择'),
            'el-form': ('form', '表单容器'),
            'a-input': ('input', '文本输入'),
            'a-select': ('select', '选项选择'),
            'van-field': ('input', '移动端输入'),
        }
        
        # 表格组件
        table_components = {
            'el-table': ('table', '数据列表'),
            'a-table': ('table', '数据列表'),
            'el-table-column': ('column', '列表字段'),
        }
        
        # 操作组件
        action_components = {
            'el-button': ('button', self._infer_button_purpose(attrs)),
            'a-button': ('button', self._infer_button_purpose(attrs)),
            'el-dropdown': ('menu', '下拉菜单'),
        }
        
        # 展示组件
        display_components = {
            'el-card': ('card', '信息卡片'),
            'el-descriptions': ('detail', '详情展示'),
        }
        
        all_types = {**form_components, **table_components, 
                    **action_components, **display_components}
        
        if tag in all_types:
            return all_types[tag]
        
        # 自定义组件：根据props推断
        if 'v-model' in str(attrs) or 'model-value' in str(attrs):
            return ('custom-input', '自定义输入组件')
        if 'data-source' in str(attrs) or 'data' in str(attrs):
            return ('custom-table', '自定义表格')
            
        return ('unknown', None)
    
    def _infer_button_purpose(self, attrs: Dict) -> Optional[str]:
        """推断按钮用途"""
        text = attrs.get('text', '') or attrs.get('slot-default', '')
        if any(kw in text for kw in ['提交', '保存', '确认', 'Submit', 'Save']):
            return '提交操作'
        if any(kw in text for kw in ['查询', '搜索', 'Search', 'Query']):
            return '查询操作'
        if any(kw in text for kw in ['新增', '添加', 'Add', 'New']):
            return '新增操作'
        if any(kw in text for kw in ['删除', 'Remove', 'Delete']):
            return '删除操作'
        if any(kw in text for kw in ['导出', 'Export', '下载', 'Download']):
            return '导出操作'
        if any(kw in text for kw in ['打印', 'Print']):
            return '打印操作'
        return '通用操作'
    
    def extract_apis(self) -> List[ParsedAPI]:
        """提取API调用"""
        apis = []
        
        # 匹配this.$http/axios/fetch调用
        patterns = [
            # this.$http.get(url, config)
            (r'this\.\$http\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"](?:,\s*([^)]+))?\)', 
             'vue-http'),
            # axios.request(config)
            (r'axios\.(request|get|post|put|delete|patch)\(([^)]+)\)', 
             'axios'),
            # fetch(url, config)
            (r'fetch\([\'"]([^\'"]+)[\'"](?:,\s*([^)]+))?\)', 
             'fetch'),
        ]
        
        for pattern, api_type in patterns:
            for match in re.finditer(pattern, self.script):
                if api_type == 'vue-http':
                    method, url, config = match.groups()
                    config = config or ""
                elif api_type == 'axios':
                    method, args = match.groups()
                    url = self._extract_url_from_args(args)
                    config = args
                else:  # fetch
                    url, config = match.groups()
                    method = 'fetch'
                    config = config or ""
                
                # 解析参数
                params = self._extract_params_from_config(config)
                
                # 查找响应处理（向后搜索）
                response_handler = self._find_response_handler(match.end())
                
                api = ParsedAPI(
                    method=method.upper(),
                    endpoint=url,
                    params=params,
                    response_handler=response_handler,
                    business_purpose=self._infer_api_purpose(url, method)
                )
                apis.append(api)
        
        return apis
    
    def _infer_api_purpose(self, url: str, method: str) -> Optional[str]:
        """推断API业务用途"""
        url_lower = url.lower()
        
        # RESTful模式识别
        if method == 'POST' and any(kw in url_lower for kw in ['create', 'add', 'new', 'submit']):
            return '创建资源'
        if method == 'PUT' and any(kw in url_lower for kw in ['update', 'modify', 'edit']):
            return '更新资源'
        if method == 'DELETE' or method == 'POST' and 'delete' in url_lower:
            return '删除资源'
        if method == 'GET':
            if any(kw in url_lower for kw in ['list', 'query', 'search', 'get']):
                return '查询列表'
            if any(kw in url_lower for kw in ['detail', 'info', 'getbyid']):
                return '查询详情'
            if any(kw in url_lower for kw in ['dict', 'enum', 'options']):
                return '获取字典'
        
        # 交易特定模式
        if any(kw in url_lower for kw in ['trade', 'order', 'transaction']):
            return '交易操作'
        if any(kw in url_lower for kw in ['audit', 'approve', 'check']):
            return '审核操作'
        if any(kw in url_lower for kw in ['settlement', 'clear']):
            return '清算结算'
            
        return None
    
    def extract_business_rules(self) -> List[ParsedRule]:
        """提取业务规则"""
        rules = []
        
        # 1. 提取验证规则（表单验证）
        validation_patterns = [
            (r'rules\s*:\s*\{([^}]+)\}', 'object'),  # el-form rules
            (r'validator\s*:\s*([^,}\]]+)', 'function'),  # 自定义验证器
            (r'required\s*:\s*true', 'required'),  # 必填
            (r'pattern\s*:\s*\/([^\/]+)\/', 'regex'),  # 正则
        ]
        
        # 2. 提取条件逻辑
        condition_patterns = [
            (r'if\s*\(([^)]+)\)\s*\{', 'condition'),
            (r'switch\s*\(([^)]+)\)', 'switch'),
            (r'\?([^:]+):', 'ternary'),
        ]
        
        # 3. 提取权限控制
        permission_patterns = [
            (r'v-if=["\'][^"\']*(?:permission|auth|role)[^"\']*["\']', 'permission-directive'),
            (r'checkPermission\([^)]+?\)', 'permission-check'),
            (r'hasRole\([^)]+?\)', 'role-check'),
        ]
        
        for pattern, rule_type in validation_patterns + condition_patterns + permission_patterns:
            for match in re.finditer(pattern, self.script):
                source = match.group(0)
                expression = match.group(1) if match.groups() else source
                
                rule = ParsedRule(
                    rule_type=self._categorize_rule(rule_type, source),
                    expression=expression[:200],  # 限制长度
                    source=source[:100],
                    confidence=self._calculate_rule_confidence(rule_type, source),
                    business_meaning=self._interpret_rule(rule_type, expression)
                )
                rules.append(rule)
        
        return rules
    
    def _categorize_rule(self, rule_type: str, source: str) -> str:
        """分类规则类型"""
        if rule_type in ['object', 'function', 'required', 'regex']:
            return 'validation'
        if rule_type in ['condition', 'switch', 'ternary']:
            return 'flow'
        if 'permission' in rule_type or 'role' in rule_type:
            return 'permission'
        return 'unknown'
    
    def _interpret_rule(self, rule_type: str, expression: str) -> Optional[str]:
        """解释规则的业务含义"""
        # 使用规则库或简单启发式解释
        if 'required' in expression:
            return "必填校验"
        if any(kw in expression for kw in ['amount', 'money', 'price']):
            return "金额相关规则"
        if any(kw in expression for kw in ['date', 'time']):
            return "日期时间规则"
        if any(kw in expression for kw in ['status', 'state']):
            return "状态判断规则"
        return None
    
    def _calculate_rule_confidence(self, rule_type: str, source: str) -> float:
        """计算规则提取的置信度"""
        base_confidence = {
            'required': 0.95,
            'regex': 0.85,
            'condition': 0.70,
            'permission-directive': 0.90,
        }.get(rule_type, 0.60)
        
        # 根据代码清晰度调整
        if len(source) > 200:  # 复杂表达式
            base_confidence -= 0.1
        if '/*' in source or '//' in source:  # 有注释
            base_confidence += 0.05
            
        return min(0.99, max(0.30, base_confidence))
    
    def _extract_data_model(self) -> Dict[str, Any]:
        """提取数据模型（data函数返回的对象）"""
        # 匹配data() { return {...} } 或 data: () => ({...})
        pattern = r'(?:data\s*\(\)\s*\{|data\s*:\s*(?:function|\(\)\s*=>)\s*\{)\s*return\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        match = re.search(pattern, self.script)
        
        if match:
            data_content = match.group(1)
            # 提取顶级属性
            props = re.findall(r'(\w+)\s*:\s*', data_content)
            return {"properties": props, "raw": data_content[:500]}
        return {}
    
    def _extract_computed(self) -> List[Dict]:
        """计算属性"""
        pattern = r'computed\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        match = re.search(pattern, self.script)
        if match:
            content = match.group(1)
            # 简单提取计算属性名
            properties = re.findall(r'(\w+)\s*\(\s*\)\s*\{', content)
            return [{"name": p, "type": "computed"} for p in properties]
        return []
    
    def _extract_watchers(self) -> List[Dict]:
        """监听器"""
        pattern = r'watch\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        match = re.search(pattern, self.script)
        if match:
            content = match.group(1)
            watchers = re.findall(r'[\'"]?(\w+)[\'"]?\s*:', content)
            return [{"target": w, "type": "watcher"} for w in watchers]
        return []
    
    def _extract_lifecycle(self) -> List[str]:
        """生命周期钩子"""
        hooks = ['created', 'mounted', 'updated', 'destroyed', 
                'beforeCreate', 'beforeMount', 'beforeUpdate', 'beforeDestroy']
        found = []
        for hook in hooks:
            if re.search(rf'\b{hook}\s*\(\)', self.script):
                found.append(hook)
        return found
    
    def _parse_attrs(self, attrs_str: str) -> Dict[str, Any]:
        """解析HTML属性"""
        attrs = {}
        # 匹配 :prop="value" 或 prop="value" 或 @event="handler"
        pattern = r'([:@]?)(\w+(?:-\w+)*)\s*=\s*["\']([^"\']+)["\']'
        for match in re.finditer(pattern, attrs_str):
            prefix, name, value = match.groups()
            key = f"{prefix}{name}"
            attrs[key] = value
        return attrs
    
    def _extract_events(self, attrs_str: str) -> List[str]:
        """提取事件绑定"""
        return re.findall(r'@(\w+)', attrs_str)
    
    def _extract_imports(self) -> List[str]:
        """提取导入的依赖"""
        imports = re.findall(r'import\s+\{?([^}]+)\}?\s+from\s+[\'"]([^\'"]+)[\'"]', self.script)
        return [{"name": i[0].strip(), "source": i[1]} for i in imports]
    
    def _extract_component_usage(self) -> List[str]:
        """提取components注册"""
        match = re.search(r'components\s*:\s*\{([^}]+)\}', self.script)
        if match:
            return [c.strip() for c in match.group(1).split(',')]
        return []
    
    def _get_line_number(self, pos: int) -> int:
        """获取字符位置对应的行号"""
        return self.content[:pos].count('\n') + 1
    
    def _extract_params_from_config(self, config: str) -> Dict[str, Any]:
        """从配置字符串提取参数"""
        params = {}
        # 简化实现，实际可用AST解析
        matches = re.findall(r'(\w+)\s*:\s*([^,]+)', config)
        for key, value in matches[:5]:  # 限制数量
            params[key] = value.strip()
        return params
    
    def _extract_url_from_args(self, args: str) -> str:
        """从axios参数提取URL"""
        # 尝试匹配url属性
        url_match = re.search(r'url\s*:\s*[\'"]([^\'"]+)[\'"]', args)
        if url_match:
            return url_match.group(1)
        # 尝试匹配第一个字符串参数
        str_match = re.search(r'[\'"]([^\'"]+)[\'"]', args)
        return str_match.group(1) if str_match else "unknown"
    
    def _find_response_handler(self, start_pos: int) -> Optional[str]:
        """查找API调用后的响应处理"""
        # 向后搜索.then或await后的处理
        snippet = self.script[start_pos:start_pos+500]
        
        then_match = re.search(r'\.then\s*\([^)]*=\s*>?\s*\{([^}]+)\}', snippet)
        if then_match:
            return then_match.group(1)[:100]
        
        catch_match = re.search(r'\.catch\s*\([^)]*=\s*>?\s*\{([^}]+)\}', snippet)
        if catch_match:
            return f"Error: {catch_match.group(1)[:50]}"
        
        return None