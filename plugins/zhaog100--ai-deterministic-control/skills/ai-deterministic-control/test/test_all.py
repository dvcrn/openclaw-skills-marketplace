#!/usr/bin/env python3
"""测试用例 - AI 确定性控制工具"""

import pytest
import tempfile
import json
from pathlib import Path

from config import ConfigManager
from temperature import TemperatureController
from consistency import ConsistencyChecker
from reproducibility import ReproducibilityGuarantor
from monitor import RandomnessMonitor


# ========== 配置管理测试 ==========

class TestConfigManager:
    """配置管理测试"""
    
    def test_load_default_config(self):
        """测试加载默认配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))
            
            assert manager.get("temperature") == 0.5
            assert manager.get("api_provider") == "mock"  # 默认使用mock（测试模式）
    
    def test_set_config(self):
        """测试设置配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))
            
            manager.set("temperature", 0.8)
            assert manager.get("temperature") == 0.8
    
    def test_update_config(self):
        """测试批量更新配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            manager = ConfigManager(str(config_path))
            
            manager.update({
                "temperature": 0.3,
                "api_provider": "deepseek"
            })
            
            assert manager.get("temperature") == 0.3
            assert manager.get("api_provider") == "deepseek"


# ========== 温度控制测试 ==========

class TestTemperatureController:
    """温度控制测试"""
    
    def test_set_temperature_valid(self):
        """测试设置有效温度"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            controller = TemperatureController(str(config_path))
            
            result = controller.set_temperature(0.8)
            
            assert result["temperature"] == 0.8
            assert result["mode"] == "创造性模式"
            assert result["success"] is True
    
    def test_set_temperature_invalid(self):
        """测试设置无效温度"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            controller = TemperatureController(str(config_path))
            
            with pytest.raises(ValueError, match="温度必须在0.0-2.0之间"):
                controller.set_temperature(3.0)
    
    def test_get_preset(self):
        """测试获取预设"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            controller = TemperatureController(str(config_path))
            
            preset = controller.get_preset("code")
            
            assert preset["temperature"] == 0.0
            assert "高度确定性" in preset["description"]
    
    def test_use_preset(self):
        """测试使用预设"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            controller = TemperatureController(str(config_path))
            
            result = controller.use_preset("creative")
            
            assert result["temperature"] == 0.8
    
    def test_get_mode(self):
        """测试模式判断"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            controller = TemperatureController(str(config_path))
            
            assert controller._get_mode(0.1) == "高度确定性"
            assert controller._get_mode(0.5) == "平衡模式"
            assert controller._get_mode(0.9) == "创造性模式"
            assert controller._get_mode(1.5) == "高创造性模式"


# ========== 一致性检查测试 ==========

class TestConsistencyChecker:
    """一致性检查测试"""
    
    def test_check_consistency_pass(self):
        """测试一致性检查通过"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            db_path = Path(tmpdir) / "history.db"
            
            manager = ConfigManager(str(config_path))
            manager.set("history_db", str(db_path))
            manager.set("api_provider", "mock")
            
            checker = ConsistencyChecker(str(config_path))
            result = checker.check_consistency("测试提示词", samples=2, threshold=80.0)
            
            assert "consistency_score" in result
            assert "passed" in result
            assert result["samples"] == 2
    
    def test_check_consistency_with_custom_temperature(self):
        """测试自定义温度的一致性检查"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            db_path = Path(tmpdir) / "history.db"
            
            manager = ConfigManager(str(config_path))
            manager.set("history_db", str(db_path))
            manager.set("api_provider", "mock")
            
            checker = ConsistencyChecker(str(config_path))
            result = checker.check_consistency("测试", samples=2, temperature=0.0)
            
            assert result["temperature"] == 0.0
    
    def test_save_and_get_history(self):
        """测试保存和获取历史"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            db_path = Path(tmpdir) / "history.db"
            
            manager = ConfigManager(str(config_path))
            manager.set("history_db", str(db_path))
            manager.set("api_provider", "mock")
            
            checker = ConsistencyChecker(str(config_path))
            checker.check_consistency("测试", samples=2)
            
            history = checker.get_history(limit=5)
            
            assert len(history) >= 2


# ========== 复现保证测试 ==========

class TestReproducibilityGuarantor:
    """复现保证测试"""
    
    def test_generate_with_seed(self):
        """测试使用种子生成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            seeds_file = Path(tmpdir) / "seeds.json"
            
            manager = ConfigManager(str(config_path))
            manager.set("seeds_file", str(seeds_file))
            manager.set("api_provider", "mock")
            
            guarantor = ReproducibilityGuarantor(str(config_path))
            result = guarantor.generate_with_seed("测试提示词", seed=12345)
            
            assert "output" in result
            assert result["seed"] == 12345
            assert result["reproducible"] is True
    
    def test_verify_reproducibility_success(self):
        """测试验证复现性成功"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            seeds_file = Path(tmpdir) / "seeds.json"
            
            manager = ConfigManager(str(config_path))
            manager.set("seeds_file", str(seeds_file))
            manager.set("api_provider", "mock")
            
            guarantor = ReproducibilityGuarantor(str(config_path))
            result = guarantor.verify_reproducibility("测试", seed=12345, iterations=2)
            
            assert "is_reproducible" in result
            assert result["iterations"] == 2
    
    def test_seed_recording(self):
        """测试种子记录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            seeds_file = Path(tmpdir) / "seeds.json"
            
            manager = ConfigManager(str(config_path))
            manager.set("seeds_file", str(seeds_file))
            manager.set("api_provider", "mock")
            
            guarantor = ReproducibilityGuarantor(str(config_path))
            guarantor.generate_with_seed("测试", seed=99999)
            
            record = guarantor.get_seed_record(99999)
            
            assert record is not None
            assert record["seed"] == 99999


# ========== 随机性监控测试 ==========

class TestRandomnessMonitor:
    """随机性监控测试"""
    
    def test_analyze_trends_insufficient_data(self):
        """测试数据不足的趋势分析"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            monitor = RandomnessMonitor(str(config_path))
            result = monitor.analyze_trends(days=7)
            
            assert "error" in result
    
    def test_detect_anomalies_no_data(self):
        """测试无数据时的异常检测"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            monitor = RandomnessMonitor(str(config_path))
            result = monitor.detect_anomalies()
            
            assert result == []
    
    def test_export_report(self):
        """测试导出报告"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            output_path = Path(tmpdir) / "report.json"
            
            monitor = RandomnessMonitor(str(config_path))
            path = monitor.export_report(str(output_path))
            
            assert Path(path).exists()
            
            with open(path, 'r') as f:
                report = json.load(f)
            
            assert "generated_at" in report
            assert "trends" in report
            assert "anomalies" in report
    
    def test_get_stats(self):
        """测试获取统计信息"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            monitor = RandomnessMonitor(str(config_path))
            result = monitor.get_stats()
            
            assert "total_records" in result
            assert "db_exists" in result


# ========== 运行测试 ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
