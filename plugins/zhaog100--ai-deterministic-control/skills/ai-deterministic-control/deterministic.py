#!/usr/bin/env python3
"""AI 确定性控制工具 - CLI入口"""

import click
from pathlib import Path

from temperature import TemperatureController
from consistency import ConsistencyChecker
from reproducibility import ReproducibilityGuarantor
from monitor import RandomnessMonitor
from dynamic_adjuster import DynamicAdjuster
from diff_analyzer import DiffAnalyzer
from alert_manager import AlertManager


# 版本
VERSION = "1.0.0"


@click.group()
@click.version_option(version=VERSION)
def cli():
    """AI 确定性控制工具 - 控制AI输出随机性，提供确定性模式
    
    \b
    核心功能：
    - 温度参数设置（0.0-2.0）
    - 输出一致性检查
    - 可复现性保证（种子控制）
    - 随机性监控
    
    \b
    快速开始：
    $ deterministic temp 0.0              # 设置为高度确定性模式
    $ deterministic check "生成一个函数"  # 检查输出一致性
    $ deterministic repro "生成配置"      # 使用种子生成
    """
    pass


# ========== 温度控制命令 ==========

@cli.command()
@click.argument('value', type=float, required=False)
@click.option('--preset', type=click.Choice(['code', 'balance', 'creative', 'brainstorm']), 
              help='使用预设配置')
@click.option('--list', 'list_presets', is_flag=True, help='列出所有预设')
def temp(value, preset, list_presets):
    """温度参数设置
    
    \b
    温度范围：
    - 0.0-0.3: 高度确定性（代码/配置生成）
    - 0.3-0.7: 平衡模式（常规对话）
    - 0.7-1.0: 创造性模式（创意写作）
    - 1.0-2.0: 高创造性模式（头脑风暴）
    
    \b
    示例：
    $ deterministic temp 0.0              # 设置温度为0.0
    $ deterministic temp --preset code    # 使用代码生成预设
    $ deterministic temp --list           # 列出所有预设
    """
    controller = TemperatureController()
    
    # 列出预设
    if list_presets:
        click.echo("📋 可用预设：\n")
        for name, config in controller.list_presets().items():
            click.echo(f"  {name:12} - {config['description']} (温度: {config['temperature']})")
        return
    
    # 使用预设
    if preset:
        config = controller.get_preset(preset)
        value = config["temperature"]
        click.echo(f"📌 使用预设 {preset}: {config['description']}\n")
    
    # 设置温度
    if value is not None:
        try:
            result = controller.set_temperature(value)
            click.echo(f"✅ 温度已设置为: {result['temperature']}")
            click.echo(f"   模式: {result['mode']}")
            click.echo(f"   时间: {result['timestamp']}")
        except ValueError as e:
            click.echo(f"❌ 错误: {e}", err=True)
            raise click.Abort()
    else:
        # 显示当前温度
        current = controller.get_current()
        click.echo(f"当前温度: {current}")
        click.echo(f"模式: {controller._get_mode(current)}")


# ========== 一致性检查命令 ==========

@cli.command()
@click.argument('prompt')
@click.option('--samples', default=3, help='采样次数（默认3次）')
@click.option('--threshold', default=80.0, help='一致性阈值（默认80%）')
@click.option('--temperature', type=float, help='温度参数（None则使用配置）')
def check(prompt, samples, threshold, temperature):
    """一致性检查
    
    \b
    通过多次采样检查AI输出的一致性
    
    \b
    示例：
    $ deterministic check "生成一个Python函数"
    $ deterministic check "生成配置" --samples 5 --threshold 90
    """
    checker = ConsistencyChecker()
    
    click.echo(f"🔍 开始一致性检查...")
    click.echo(f"   提示词: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    click.echo(f"   采样次数: {samples}")
    click.echo(f"   阈值: {threshold}%\n")
    
    try:
        result = checker.check_consistency(prompt, samples, threshold, temperature)
        
        click.echo(f"✅ 检查完成\n")
        click.echo(f"一致性评分: {result['consistency_score']}%")
        click.echo(f"通过: {'✅ 是' if result['passed'] else '❌ 否'}")
        click.echo(f"耗时: {result['elapsed_time']}秒")
        click.echo(f"温度: {result['temperature']}\n")
        
        click.echo(f"详情:")
        click.echo(f"  最小相似度: {result['details']['min']}%")
        click.echo(f"  最大相似度: {result['details']['max']}%")
        click.echo(f"  标准差: {result['details']['std']}")
        
        if not result['passed']:
            click.echo(f"\n⚠️  一致性未达标（{result['consistency_score']}% < {threshold}%）")
            click.echo(f"   建议：降低温度参数或减少采样次数")
    
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        raise click.Abort()


# ========== 可复现性命令 ==========

@cli.command()
@click.argument('prompt', required=False)
@click.option('--seed', type=int, help='随机种子')
@click.option('--verify', type=int, help='验证复现性的种子')
@click.option('--iterations', default=3, help='验证次数（默认3次）')
def repro(prompt, seed, verify, iterations):
    """可复现性保证
    
    \b
    通过种子控制生成确定性输出
    
    \b
    示例：
    $ deterministic repro "生成一个函数"              # 自动生成种子
    $ deterministic repro "生成配置" --seed 12345     # 指定种子
    $ deterministic repro "生成配置" --verify 12345   # 验证复现性
    """
    guarantor = ReproducibilityGuarantor()
    
    # 验证复现性
    if verify:
        if not prompt:
            click.echo("❌ 验证复现性需要提供prompt", err=True)
            raise click.Abort()
        
        click.echo(f"🔬 验证复现性...")
        click.echo(f"   种子: {verify}")
        click.echo(f"   验证次数: {iterations}\n")
        
        try:
            result = guarantor.verify_reproducibility(prompt, verify, iterations)
            
            click.echo(f"✅ 验证完成\n")
            click.echo(f"可复现: {'✅ 是' if result['is_reproducible'] else '❌ 否'}")
            click.echo(f"一致性: {result['consistency']}")
            click.echo(f"耗时: {result['elapsed_time']}秒")
            click.echo(f"首次输出: {result['first_output']}")
        
        except Exception as e:
            click.echo(f"❌ 错误: {e}", err=True)
            raise click.Abort()
    
    # 生成确定性输出
    elif prompt:
        click.echo(f"🎯 生成确定性输出...")
        if seed:
            click.echo(f"   种子: {seed}")
        else:
            click.echo(f"   种子: 自动生成\n")
        
        try:
            result = guarantor.generate_with_seed(prompt, seed)
            
            click.echo(f"\n✅ 生成完成\n")
            click.echo(f"输出: {result['output'][:100]}{'...' if len(result['output']) > 100 else ''}")
            click.echo(f"种子: {result['seed']}")
            click.echo(f"可复现: {'✅ 是' if result['reproducible'] else '❌ 否'}")
            click.echo(f"输出哈希: {result['output_hash']}")
            click.echo(f"\n💡 使用种子 {result['seed']} 可复现此输出")
        
        except Exception as e:
            click.echo(f"❌ 错误: {e}", err=True)
            raise click.Abort()
    
    else:
        click.echo("❌ 请提供prompt或使用--verify", err=True)
        raise click.Abort()


# ========== 随机性监控命令组 ==========

@cli.group()
def monitor():
    """随机性监控
    
    \b
    监控AI输出的随机性，分析趋势和检测异常
    
    \b
    示例：
    $ deterministic monitor trends
    $ deterministic monitor anomalies
    $ deterministic monitor report
    """
    pass


@monitor.command()
@click.option('--days', default=7, help='分析天数（默认7天）')
def trends(days):
    """趋势分析
    
    \b
    分析过去N天的随机性趋势
    
    \b
    示例：
    $ deterministic monitor trends
    $ deterministic monitor trends --days 30
    """
    mon = RandomnessMonitor()
    
    click.echo(f"📈 随机性趋势分析...\n")
    
    result = mon.analyze_trends(days)
    
    if "error" in result:
        click.echo(f"❌ {result['error']}")
        return
    
    click.echo(f"分析周期: {result['period_days']} 天")
    click.echo(f"记录数: {result['total_records']}")
    click.echo(f"平均相似度: {result['average_similarity']}%")
    click.echo(f"最小相似度: {result['min_similarity']}%")
    click.echo(f"最大相似度: {result['max_similarity']}%")
    click.echo(f"趋势: {result['trend']}\n")
    
    if result['details']:
        click.echo(f"详细数据（最近10条）:")
        for detail in result['details'][-10:]:
            click.echo(f"  {detail['date']}: {detail['similarity']}% (温度: {detail['temperature']})")


@monitor.command()
@click.option('--threshold', default=50.0, help='异常阈值（默认50%）')
@click.option('--limit', default=100, help='检查记录数（默认100）')
def anomalies(threshold, limit):
    """异常检测
    
    \b
    检测相似度低于阈值的异常输出
    
    \b
    示例：
    $ deterministic monitor anomalies
    $ deterministic monitor anomalies --threshold 60
    """
    mon = RandomnessMonitor()
    
    click.echo(f"🔍 异常检测...\n")
    
    result = mon.detect_anomalies(threshold, limit)
    
    if result:
        click.echo(f"⚠️  发现 {len(result)} 个异常:\n")
        for i, anomaly in enumerate(result[:10], 1):  # 最多显示10个
            click.echo(f"{i}. {anomaly['timestamp']}")
            click.echo(f"   提示词: {anomaly['prompt']}")
            click.echo(f"   相似度: {anomaly['similarity']}%\n")
        
        if len(result) > 10:
            click.echo(f"... 还有 {len(result) - 10} 个异常未显示")
    else:
        click.echo(f"✅ 未发现异常（阈值: {threshold}%）")


@monitor.command()
@click.option('--output', default='randomness_report.json', help='输出路径')
def report(output):
    """导出报告
    
    \b
    导出完整的随机性监控报告
    
    \b
    示例：
    $ deterministic monitor report
    $ deterministic monitor report --output my_report.json
    """
    mon = RandomnessMonitor()
    
    click.echo(f"📊 导出监控报告...\n")
    
    try:
        path = mon.export_report(output)
        click.echo(f"✅ 报告已导出: {path}")
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        raise click.Abort()


@monitor.command()
def stats():
    """统计信息
    
    \b
    显示数据库统计信息
    
    \b
    示例：
    $ deterministic monitor stats
    """
    mon = RandomnessMonitor()
    
    result = mon.get_stats()
    
    click.echo(f"📊 数据库统计\n")
    click.echo(f"总记录数: {result['total_records']}")
    click.echo(f"最近24小时: {result.get('recent_24h', 0)}")
    click.echo(f"平均温度: {result.get('average_temperature', 0.0)}")


# ========== 动态调整命令组 ==========

@cli.group()
def adjust():
    """动态温度调整
    
    \b
    根据任务类型和历史质量自动调整温度
    
    \b
    示例：
    $ deterministic adjust recommend "生成一个函数"
    $ deterministic adjust stats
    """
    pass


@adjust.command()
@click.argument('prompt')
@click.option('--current-temp', type=float, help='当前温度（可选）')
def recommend(prompt, current_temp):
    """推荐温度
    
    \b
    根据提示词和历史质量推荐最佳温度
    
    \b
    示例：
    $ deterministic adjust recommend "生成一个Python函数"
    $ deterministic adjust recommend "写一个故事" --current-temp 0.5
    """
    adjuster = DynamicAdjuster()
    
    result = adjuster.calculate_dynamic_temperature(prompt, current_temp)
    
    click.echo(f"\n🎯 动态温度推荐\n")
    click.echo(f"推荐温度: {result['recommended_temperature']}")
    click.echo(f"任务类型: {result['task_description']}")
    click.echo(f"基础温度: {result['base_temperature']}")
    
    if result['adjustments']:
        click.echo(f"\n调整历史:")
        for adj in result['adjustments']:
            click.echo(f"  - {adj['reason']}: {adj['from']:.2f} → {adj['to']:.2f}")
    
    click.echo(f"\n原因: {result['reason']}\n")


@adjust.command()
def stats():
    """调整统计
    
    \b
    显示历史调整统计
    
    \b
    示例：
    $ deterministic adjust stats
    """
    adjuster = DynamicAdjuster()
    
    result = adjuster.get_adjustment_stats()
    
    click.echo(f"\n📊 调整统计\n")
    
    if "message" in result:
        click.echo(f"{result['message']}\n")
        return
    
    click.echo(f"总记录数: {result['total_records']}")
    click.echo(f"平均温度: {result['average_temperature']}")
    click.echo(f"平均相似度: {result['average_similarity']}%")
    click.echo(f"温度范围: {result['temperature_range']}")
    click.echo(f"相似度范围: {result['similarity_range']}\n")


# ========== 差异分析命令组 ==========

@cli.group()
def diff():
    """差异分析
    
    \b
    对比多次输出的差异，生成详细报告
    
    \b
    示例：
    $ deterministic diff analyze --outputs "输出1" "输出2" "输出3"
    $ deterministic diff report --format html
    """
    pass


@diff.command()
@click.option('--outputs', multiple=True, help='输出文本（可多次指定）')
@click.option('--labels', multiple=True, help='输出标签（可多次指定）')
@click.option('--prompt', default='', help='原始提示词')
def analyze(outputs, labels, prompt):
    """分析差异
    
    \b
    分析多个输出之间的差异
    
    \b
    示例：
    $ deterministic diff analyze --outputs "第一个输出" --outputs "第二个输出"
    """
    if len(outputs) < 2:
        click.echo("❌ 至少需要2个输出进行对比", err=True)
        raise click.Abort()
    
    analyzer = DiffAnalyzer()
    
    labels_list = list(labels) if labels else None
    result = analyzer.analyze_outputs(list(outputs), labels_list, prompt)
    
    click.echo(f"\n📊 差异分析结果\n")
    click.echo(f"输出数量: {result['outputs_count']}")
    click.echo(f"整体相似度: {result['overall_similarity']}%")
    click.echo(f"一致性等级: {result['consistency_level']}")
    click.echo(f"\n最相似: {result['most_similar']['pair']} ({result['most_similar']['similarity']}%)")
    click.echo(f"最不相似: {result['least_similar']['pair']} ({result['least_similar']['similarity']}%)\n")


@diff.command()
@click.option('--outputs', multiple=True, help='输出文本（可多次指定）')
@click.option('--labels', multiple=True, help='输出标签（可多次指定）')
@click.option('--prompt', default='', help='原始提示词')
@click.option('--format', type=click.Choice(['text', 'json', 'html']), default='text', help='报告格式')
def report(outputs, labels, prompt, format):
    """生成报告
    
    \b
    生成详细的差异分析报告
    
    \b
    示例：
    $ deterministic diff report --outputs "输出1" --outputs "输出2" --format html
    """
    if len(outputs) < 2:
        click.echo("❌ 至少需要2个输出进行对比", err=True)
        raise click.Abort()
    
    analyzer = DiffAnalyzer()
    
    labels_list = list(labels) if labels else None
    result = analyzer.generate_report(list(outputs), labels_list, prompt, format)
    
    if "error" in result:
        click.echo(f"❌ {result['error']}", err=True)
        raise click.Abort()
    
    click.echo(f"\n📊 差异分析报告\n")
    click.echo(f"格式: {result['format']}")
    click.echo(f"路径: {result['path']}")
    click.echo(f"整体相似度: {result['analysis']['overall_similarity']}%\n")


# ========== 异常检测命令组 ==========

@cli.group()
def alert():
    """异常检测告警
    
    \b
    检测异常输出并发送多渠道告警
    
    \b
    示例：
    $ deterministic alert check --similarity 50 --prompt "测试"
    $ deterministic alert stats
    """
    pass


@alert.command()
@click.option('--similarity', type=float, required=True, help='相似度')
@click.option('--prompt', required=True, help='提示词')
@click.option('--output', default='', help='输出内容（可选）')
def check(similarity, prompt, output):
    """检测异常
    
    \b
    检测输出是否异常
    
    \b
    示例：
    $ deterministic alert check --similarity 45 --prompt "生成一个函数"
    """
    manager = AlertManager()
    
    # 检测异常
    anomaly = manager.detect_anomaly(similarity, prompt, output)
    
    if anomaly is None:
        click.echo(f"\n✅ 未检测到异常（相似度: {similarity}%）\n")
        return
    
    # 发送告警
    result = manager.send_alert(anomaly)
    
    click.echo(f"\n⚠️  检测到异常！\n")
    click.echo(f"级别: {anomaly['level']}")
    click.echo(f"类型: {anomaly['type']}")
    click.echo(f"消息: {anomaly['message']}")
    click.echo(f"时间: {anomaly['timestamp']}\n")
    
    if result["sent"]:
        click.echo("告警已发送:")
        for channel, status in result["channels"].items():
            status_icon = "✅" if status.get("success") else "❌"
            click.echo(f"  {status_icon} {channel}: {status.get('message', status.get('error'))}")
    else:
        click.echo(f"告警未发送: {result['reason']}")
    
    click.echo()


@alert.command()
def stats():
    """告警统计
    
    \b
    显示告警统计信息
    
    \b
    示例：
    $ deterministic alert stats
    """
    manager = AlertManager()
    
    result = manager.get_alert_stats()
    
    click.echo(f"\n📊 告警统计\n")
    
    if "message" in result:
        click.echo(f"{result['message']}\n")
        return
    
    click.echo(f"总告警数: {result['total_alerts']}")
    click.echo(f"最近24小时: {result['recent_24h']}")
    click.echo(f"\n级别分布:")
    for level, count in result['level_distribution'].items():
        click.echo(f"  {level}: {count}")
    click.echo(f"\n类型分布:")
    for alert_type, count in result['type_distribution'].items():
        click.echo(f"  {alert_type}: {count}")
    click.echo()


@alert.command()
@click.argument('channel', type=click.Choice(['email', 'feishu', 'dingtalk']))
@click.option('--enabled/--disabled', default=True, help='启用/禁用')
@click.option('--config', help='配置JSON（可选）')
def configure(channel, enabled, config):
    """配置渠道
    
    \b
    配置告警渠道
    
    \b
    示例：
    $ deterministic alert configure email --enabled
    $ deterministic alert configure feishu --config '{"webhook_url": "https://..."}'
    """
    manager = AlertManager()
    
    config_dict = {"enabled": enabled}
    
    if config:
        try:
            import json
            config_dict.update(json.loads(config))
        except Exception as e:
            click.echo(f"❌ 配置JSON解析失败: {e}", err=True)
            raise click.Abort()
    
    manager.configure_channel(channel, config_dict)
    
    click.echo(f"\n✅ {channel} 配置已更新\n")


# ========== 主程序入口 ==========

if __name__ == '__main__':
    cli()


# ========== 顶层函数包装器（兼容test.sh）==========

# 全局实例（延迟初始化）
_temperature_controller = None
_consistency_checker = None
_reproducibility_guarantor = None

def _get_temperature_controller():
    """获取温度控制器实例（延迟初始化）"""
    global _temperature_controller
    if _temperature_controller is None:
        _temperature_controller = TemperatureController()
    return _temperature_controller

def _get_consistency_checker():
    """获取一致性检查器实例（延迟初始化）"""
    global _consistency_checker
    if _consistency_checker is None:
        _consistency_checker = ConsistencyChecker()
    return _consistency_checker

def _get_reproducibility_guarantor():
    """获取可复现性保证器实例（延迟初始化）"""
    global _reproducibility_guarantor
    if _reproducibility_guarantor is None:
        _reproducibility_guarantor = ReproducibilityGuarantor()
    return _reproducibility_guarantor

def set_temperature(value):
    """设置温度参数（包装器）
    
    Args:
        value: 温度值（0.0-2.0）
    
    Returns:
        dict: 包含temperature, mode, timestamp的字典
    
    Raises:
        ValueError: 温度超出范围
    """
    return _get_temperature_controller().set_temperature(value)

def get_temperature():
    """获取当前温度（包装器）
    
    Returns:
        float: 当前温度值
    """
    return _get_temperature_controller().get_current()

def set_seed(seed):
    """设置随机种子（包装器）
    
    Args:
        seed: 随机种子（整数）
    
    Returns:
        dict: 包含seed, timestamp的字典
    """
    return _get_reproducibility_guarantor().set_seed(seed)

def get_seed():
    """获取当前种子（包装器）
    
    Returns:
        int: 当前种子值
    """
    return _get_reproducibility_guarantor().get_current_seed()
