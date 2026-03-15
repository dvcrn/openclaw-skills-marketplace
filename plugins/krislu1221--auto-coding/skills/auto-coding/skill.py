"""
Auto-Coding Skill - OpenClaw 技能注册
自动编码 - OpenClaw Skill Registration
"""

import re
import asyncio
from typing import Optional

# 支持 Skill 模式和非 Skill 模式导入
try:
    from nanobot.agent.skill import Skill
    from openclaw.sessions import sessions_spawn
    HAS_OPENCLAW = True
except ImportError:
    Skill = object
    sessions_spawn = None
    HAS_OPENCLAW = False

# 支持直接运行和模块导入两种模式
try:
    from .agent_controller import AutonomousCodingController
except ImportError:
    from agent_controller import AutonomousCodingController


class AutoCodingSkill(Skill):
    """
    Auto-Coding - 自主编码 Agent 技能
    
    触发方式:
    - /auto-coding 创建一个 Todo 应用
    - /autonomous-coding 创建一个 Todo 应用 (兼容旧命令)
    - 帮我创建一个天气查询 Web 应用
    - 帮我开发一个个人博客系统
    """
    
    name = "auto-coding"
    description = "Auto-Coding - 多 Agent 协作编程系统，自动将需求转化为可运行的应用"
    
    # 触发模式
    triggers = [
        r'/auto-coding\s+([\s\S]+)',
        r'/autonomous-coding\s+([\s\S]+)',  # 兼容旧命令
        r'帮我创建一个 ([\s\S]+)',
        r'帮我开发一个 ([\s\S]+)',
    ]
    
    async def execute(self, context: dict) -> str:
        """
        执行技能
        
        Args:
            context: 包含 message, session_id 等信息
        
        Returns:
            执行结果文本
        """
        message = context.get('message', '')
        
        # 提取需求
        requirements = self.extract_requirements(message)
        if not requirements:
            return self._format_response(
                status="error",
                message="❌ 未找到有效的项目需求\n\n请使用以下格式：\n- /auto-coding 创建一个 Todo 应用\n- 帮我创建一个天气查询 Web 应用\n- 帮我开发一个个人博客系统"
            )
        
        # 生成项目名称
        project_name = self._generate_project_name(requirements)
        
        # 返回开始通知
        start_msg = self._format_response(
            status="started",
            message=f"🚀 自主编码 Agent 启动\n\n📝 项目名称：{project_name}\n📋 需求：{requirements}\n\n⏱️  预计需要数分钟，请稍候...",
            project_name=project_name,
            requirements=requirements
        )
        
        # 异步执行 (不阻塞回复)
        asyncio.create_task(self._run_auto_coding(project_name, requirements))
        
        return start_msg
    
    def extract_requirements(self, message: str) -> Optional[str]:
        """从消息中提取需求"""
        for pattern in self.triggers:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        return None
    
    def _generate_project_name(self, requirements: str) -> str:
        """从需求生成项目名称"""
        # 简单实现：取前几个词
        words = requirements.replace('的', ' ').split()
        name = ''.join(words[:3])
        # 移除特殊字符
        name = re.sub(r'[^\w\s-]', '', name)
        name = name.replace(' ', '-').lower()
        return name or "auto-project"
    
    def _format_response(
        self,
        status: str,
        message: str,
        project_name: str = None,
        requirements: str = None
    ) -> str:
        """格式化响应"""
        if status == "started":
            return message
        
        elif status == "completed":
            return f"""
🎉 自主编码完成！

📝 项目：{project_name}
📊 进度：{message}

📁 项目位置：/tmp/auto-coding-projects/{project_name}/

查看进度报告：
```bash
cd /tmp/auto-coding-projects/{project_name}/
cat feature_list.json
```
"""
        
        elif status == "error":
            return f"❌ 自主编码失败\n\n{message}"
        
        return message
    
    async def _run_auto_coding(self, project_name: str, requirements: str):
        """
        运行自主编码 (后台任务)
        Run auto-coding (background task)
        
        通过 sessions_send 发送进度更新
        Send progress updates via sessions_send
        """
        try:
            from .agent_controller import AutonomousCodingController
            
            controller = AutonomousCodingController(
                project_name=project_name,
                requirements=requirements
            )
            
            # 运行完整周期
            result = await controller.run_full_cycle()
            
            # 发送完成通知 (通过 sessions_send)
            if HAS_OPENCLAW and sessions_spawn:
                # TODO: 实现进度通知
                pass
            
        except Exception as e:
            # 发送错误通知
            print(f"自主编码失败：{e}")
    
    async def run_with_progress(self, project_name: str, requirements: str, max_iterations: int = None):
        """
        运行并返回进度 (用于同步调用)
        
        Args:
            project_name: 项目名称
            requirements: 需求描述
            max_iterations: 最大迭代次数
        
        Returns:
            最终结果
        """
        controller = AutonomousCodingController(
            project_name=project_name,
            requirements=requirements
        )
        
        result = await controller.run_full_cycle(max_iterations=max_iterations)
        return self._format_response(
            status="completed",
            message=f"完成 {result['completed']}/{result['total']} 个任务 ({result['percentage']}%)",
            project_name=project_name
        )


# Skill 注册函数
def register():
    """注册 Skill"""
    return AutoCodingSkill()


# 直接运行测试
if __name__ == "__main__":
    print("Auto-Coding Skill 测试")
    print("="*50)
    
    skill = AutoCodingSkill()
    
    # 测试触发器
    test_messages = [
        "/auto-coding 创建一个 Todo 应用",
        "/autonomous-coding 创建一个天气查询 Web 应用",  # 兼容旧命令
        "帮我开发一个 个人博客系统",
    ]
    
    print("\n测试触发器匹配:")
    for msg in test_messages:
        requirements = skill.extract_requirements(msg)
        if requirements:
            project_name = skill._generate_project_name(requirements)
            print(f"✅ '{msg}' → 项目：{project_name}, 需求：{requirements}")
        else:
            print(f"❌ '{msg}' → 未匹配")
    
    print("\n" + "="*50)
    print("Skill 注册测试完成!")
