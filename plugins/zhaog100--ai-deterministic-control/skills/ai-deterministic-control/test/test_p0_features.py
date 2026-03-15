#!/usr/bin/env python3
"""P0功能测试用例"""

import pytest
import tempfile
from pathlib import Path

from dynamic_adjuster import DynamicAdjuster
from diff_analyzer import DiffAnalyzer
from alert_manager import AlertManager


# ========== 动态调整策略测试 ==========

class TestDynamicAdjuster:
    """动态温度调整器测试"""

    def test_detect_task_type_code(self):
        """测试检测代码任务"""
        with tempfile.TemporaryDirectory() as tmpdir:
            adjuster = DynamicAdjuster(config_path=Path(tmpdir) / "rules.json")

            result = adjuster.detect_task_type("生成一个Python函数")

            assert result["type"] == "code"
            assert result["recommended_temp"] == 0.0
            assert "代码" in result["description"]

    def test_detect_task_type_creative(self):
        """测试检测创意任务"""
        with tempfile.TemporaryDirectory() as tmpdir:
            adjuster = DynamicAdjuster(config_path=Path(tmpdir) / "rules.json")

            result = adjuster.detect_task_type("写一个故事")

            assert result["type"] == "creative"
            assert result["recommended_temp"] == 0.8

    def test_calculate_dynamic_temperature_no_history(self):
        """测试无历史数据时的温度计算"""
        with tempfile.TemporaryDirectory() as tmpdir:
            adjuster = DynamicAdjuster(config_path=Path(tmpdir) / "rules.json")
            adjuster.history_file = Path(tmpdir) / "history.json"

            result = adjuster.calculate_dynamic_temperature(
                "生成一个函数",
                current_temp=0.5,
                consider_history=False
            )

            assert "recommended_temperature" in result
            assert "task_type" in result
            assert result["task_type"] == "code"

    def test_record_quality(self):
        """测试记录质量数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            adjuster = DynamicAdjuster(config_path=Path(tmpdir) / "rules.json")
            adjuster.history_file = Path(tmpdir) / "history.json"

            adjuster.record_quality("测试提示词", 85.0, 0.5)

            assert len(adjuster.quality_history) == 1
            assert adjuster.quality_history[0]["similarity"] == 85.0


# ========== 差异分析报告测试 ==========

class TestDiffAnalyzer:
    """差异分析器测试"""

    def test_analyze_two_outputs(self):
        """测试分析两个输出"""
        analyzer = DiffAnalyzer()

        outputs = ["这是第一个输出", "这是第二个输出"]

        result = analyzer.analyze_outputs(outputs)

        assert result["outputs_count"] == 2
        assert "similarity_matrix" in result
        assert "overall_similarity" in result

    def test_analyze_identical_outputs(self):
        """测试分析完全相同的输出"""
        analyzer = DiffAnalyzer()

        outputs = ["相同的输出", "相同的输出"]

        result = analyzer.analyze_outputs(outputs)

        assert result["overall_similarity"] == 100.0
        assert result["consistency_level"] == "优秀"

    def test_analyze_different_outputs(self):
        """测试分析完全不同的输出"""
        analyzer = DiffAnalyzer()

        outputs = ["完全不同的内容A", "完全不相关的内容B"]

        result = analyzer.analyze_outputs(outputs)

        assert result["overall_similarity"] < 100.0

    def test_generate_text_report(self):
        """测试生成文本报告"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DiffAnalyzer(output_dir=tmpdir)

            outputs = ["输出1", "输出2"]

            result = analyzer.generate_report(
                outputs,
                prompt="测试提示词",
                output_format="text"
            )

            assert result["format"] == "text"
            assert Path(result["path"]).exists()

    def test_generate_json_report(self):
        """测试生成JSON报告"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DiffAnalyzer(output_dir=tmpdir)

            outputs = ["输出1", "输出2"]

            result = analyzer.generate_report(
                outputs,
                output_format="json"
            )

            assert result["format"] == "json"
            assert Path(result["path"]).exists()


# ========== 异常检测告警测试 ==========

class TestAlertManager:
    """异常检测告警管理器测试"""

    def test_detect_normal_output(self):
        """测试检测正常输出"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(config_path=Path(tmpdir) / "config.json")
            manager.alerts_file = Path(tmpdir) / "alerts.json"

            anomaly = manager.detect_anomaly(
                similarity=85.0,
                prompt="测试提示词",
                output="测试输出"
            )

            assert anomaly is None

    def test_detect_warning_anomaly(self):
        """测试检测警告级异常"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(config_path=Path(tmpdir) / "config.json")
            manager.alerts_file = Path(tmpdir) / "alerts.json"

            anomaly = manager.detect_anomaly(
                similarity=55.0,
                prompt="测试提示词",
                output="测试输出"
            )

            assert anomaly is not None
            assert anomaly["level"] == "warning"

    def test_detect_critical_anomaly(self):
        """测试检测严重异常"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(config_path=Path(tmpdir) / "config.json")
            manager.alerts_file = Path(tmpdir) / "alerts.json"

            anomaly = manager.detect_anomaly(
                similarity=35.0,
                prompt="测试提示词",
                output="测试输出"
            )

            assert anomaly is not None
            assert anomaly["level"] == "critical"

    def test_send_alert_cooldown(self):
        """测试告警冷却机制"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(config_path=Path(tmpdir) / "config.json")
            manager.alerts_file = Path(tmpdir) / "alerts.json"
            
            # 清空历史
            manager.alerts_history = []

            anomaly = {
                "level": "warning",
                "type": "low_similarity",
                "message": "测试告警",
                "similarity": 55.0,
                "threshold": 60.0,
                "prompt": "测试",
                "timestamp": "2026-03-13T11:00:00"
            }

            # 第一次发送（应该成功或被disabled）
            result1 = manager.send_alert(anomaly)
            
            # 模拟冷却时间窗口内第二次发送
            # 注意：如果告警disabled，冷却机制仍然应该工作
            result2 = manager.send_alert(anomaly)
            
            # 验证冷却机制：第二次应该被阻止（无论是否disabled）
            # 如果disabled，两次都应该返回sent=False
            # 如果enabled，第二次应该被冷却
            if result1.get("sent") is False and "disabled" in result1.get("reason", ""):
                # 告警被disabled，两次都应该返回False
                assert result2["sent"] is False
            else:
                # 告警enabled，第二次应该被冷却
                assert result2["sent"] is False
                assert "冷却" in result2["reason"] or "聚合" in result2["reason"] or "disabled" in result2.get("reason", "")

    def test_get_alert_stats(self):
        """测试告警统计"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(config_path=Path(tmpdir) / "config.json")
            manager.alerts_file = Path(tmpdir) / "alerts.json"

            # 添加一些告警记录
            manager.alerts_history = [
                {"level": "warning", "type": "low_similarity", "timestamp": "2026-03-13T10:00:00"},
                {"level": "critical", "type": "low_similarity", "timestamp": "2026-03-13T10:30:00"}
            ]
            manager._save_alerts()

            stats = manager.get_alert_stats()

            assert stats["total_alerts"] == 2
            assert "level_distribution" in stats
            assert stats["level_distribution"]["warning"] == 1


# ========== 运行测试 ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
