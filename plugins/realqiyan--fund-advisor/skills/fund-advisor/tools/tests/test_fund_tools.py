"""
基金持仓管理系统 - 单元测试
"""
import os
import sys
import tempfile
import pytest
import json
from pathlib import Path
from datetime import date
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

# 添加 tools 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database
from src.csv_importer import CSVImporter
from src.statistics import Statistics
from src.models import FundHolding, FundInfo, FundType, GroupColumn
from src.cli import cli


# 测试数据 fixture
@pytest.fixture
def sample_csv_path():
    """返回 sample.csv 文件路径"""
    return str(Path(__file__).parent.parent / "data" / "sample.csv")


@pytest.fixture
def temp_db():
    """创建临时数据库，测试结束后自动清理"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    db = Database(db_path)
    yield db
    # 清理临时文件
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_db_path(temp_db):
    """返回临时数据库路径"""
    return temp_db.db_path


class TestDatabase:
    """数据库操作测试"""

    def test_database_init(self, temp_db_path):
        """测试数据库初始化"""
        db = Database(temp_db_path)
        assert db.db_path == temp_db_path

    def test_upsert_fund_holding(self, temp_db):
        """测试插入/更新持仓记录"""
        holding = FundHolding(
            fund_code="004137",
            fund_name="博时合惠货币市场基金",
            share_class="前收费",
            fund_manager="博时基金",
            fund_account="051132630566",
            sales_agency="蚂蚁（杭州）基金销售",
            trade_account="00000000000000736",
            holding_shares=60994.63,
            share_date=date(2026, 2, 25),
            nav=1.0000,
            nav_date=date(2026, 2, 25),
            asset_value=60994.63,
            settlement_currency="人民币",
            dividend_method="红利转投",
            fund_type=FundType.PUBLIC_FUND
        )

        result = temp_db.upsert_fund_holding(holding)
        assert result is True

        # 验证数据已插入
        holdings = temp_db.get_fund_holdings()
        assert len(holdings) == 1
        assert holdings[0].fund_code == "004137"
        assert holdings[0].fund_name == "博时合惠货币市场基金"

    def test_upsert_fund_info(self, temp_db):
        """测试插入/更新基金信息"""
        info = FundInfo(
            fund_code="004137",
            fund_name="博时合惠货币市场基金",
            fund_invest_type="货币型",
            risk_5_level=1,
            nav=1.0000,
            nav_date=date(2026, 2, 25),
        )

        result = temp_db.upsert_fund_info(info)
        assert result is True

        # 验证数据已插入
        saved_info = temp_db.get_fund_info("004137")
        assert saved_info is not None
        assert saved_info.fund_name == "博时合惠货币市场基金"
        assert saved_info.fund_invest_type == "货币型"

    def test_clear_all_holdings(self, temp_db):
        """测试清空持仓"""
        # 先插入一条记录
        holding = FundHolding(
            fund_code="004137",
            fund_name="测试基金",
            share_class="",
            fund_manager="测试管理人",
            fund_account="test_account",
            sales_agency="测试机构",
            trade_account="test_trade",
            holding_shares=100.0,
            share_date=date(2026, 2, 25),
            nav=1.0,
            nav_date=date(2026, 2, 25),
            asset_value=100.0,
            settlement_currency="人民币",
            dividend_method="",
            fund_type=FundType.PUBLIC_FUND
        )
        temp_db.upsert_fund_holding(holding)

        # 清空
        count = temp_db.clear_all_holdings()
        assert count == 1

        # 验证已清空
        holdings = temp_db.get_fund_holdings()
        assert len(holdings) == 0

    def test_get_all_fund_code(self, temp_db):
        """测试获取所有基金代码"""
        # 插入测试数据
        for code in ["004137", "001821", "004137"]:  # 故意重复
            holding = FundHolding(
                fund_code=code,
                fund_name=f"测试基金{code}",
                share_class="",
                fund_manager="测试",
                fund_account=f"account_{code}",
                sales_agency="测试",
                trade_account=f"trade_{code}",
                holding_shares=100.0,
                share_date=date(2026, 2, 25),
                nav=1.0,
                nav_date=date(2026, 2, 25),
                asset_value=100.0,
                settlement_currency="人民币",
                dividend_method="",
                fund_type=FundType.PUBLIC_FUND
            )
            temp_db.upsert_fund_holding(holding)

        codes = temp_db.get_all_fund_code()
        assert len(codes) == 2  # 去重后应该只有2个
        assert "004137" in codes
        assert "001821" in codes


class TestCSVImporter:
    """CSV 导入测试"""

    def test_validate_csv(self, temp_db, sample_csv_path):
        """测试 CSV 验证"""
        importer = CSVImporter(temp_db)
        is_valid, errors = importer.validate_csv(sample_csv_path)
        assert is_valid is True
        assert len(errors) == 0

    def test_import_from_csv(self, temp_db, sample_csv_path):
        """测试 CSV 导入"""
        importer = CSVImporter(temp_db)
        success, fail, errors = importer.import_from_csv(sample_csv_path)

        assert success == 3  # sample.csv 有3条记录
        assert fail == 0
        assert len(errors) == 0

        # 验证数据已导入
        holdings = temp_db.get_fund_holdings()
        assert len(holdings) == 3

        # 验证第一条记录
        first_holding = holdings[0]  # 按资产价值降序
        assert first_holding.fund_code == "004137"
        assert first_holding.fund_name == "博时合惠货币市场基金"
        assert first_holding.holding_shares == 60994.63

    def test_import_csv_twice(self, temp_db, sample_csv_path):
        """测试重复导入（upsert 行为）"""
        importer = CSVImporter(temp_db)

        # 第一次导入
        success1, fail1, _ = importer.import_from_csv(sample_csv_path)
        assert success1 == 3

        # 第二次导入（应该更新现有记录，而不是新增）
        success2, fail2, _ = importer.import_from_csv(sample_csv_path)
        assert success2 == 3

        # 验证记录数仍然是3
        holdings = temp_db.get_fund_holdings()
        assert len(holdings) == 3


class TestStatistics:
    """统计查询测试"""

    @pytest.fixture(autouse=True)
    def setup_data(self, temp_db, sample_csv_path):
        """每个测试前导入测试数据"""
        importer = CSVImporter(temp_db)
        importer.import_from_csv(sample_csv_path)
        self.stats = Statistics(temp_db)

    def test_show_group_statistics_fund_code(self, capsys):
        """测试按基金代码分组统计"""
        self.stats.show_group_statistics(GroupColumn.FUND_CODE)
        captured = capsys.readouterr()
        assert "004137" in captured.out
        assert "基金代码分布" in captured.out

    def test_show_group_statistics_fund_manager(self, capsys):
        """测试按基金管理人分组统计"""
        self.stats.show_group_statistics(GroupColumn.FUND_MANAGER)
        captured = capsys.readouterr()
        assert "博时基金" in captured.out
        assert "基金管理人分布" in captured.out

    def test_show_query_result(self, capsys):
        """测试条件查询"""
        self.stats.show_query_result(GroupColumn.FUND_MANAGER, "博时")
        captured = capsys.readouterr()
        assert "博时" in captured.out
        assert "查询结果" in captured.out

    def test_show_fund_detail(self, capsys):
        """测试基金详情"""
        self.stats.show_fund_detail("004137")
        captured = capsys.readouterr()
        # 没有fund_info时只显示持仓表格
        assert "我的持仓" in captured.out
        assert "60,994.63" in captured.out

    def test_show_fund_detail_not_found(self, capsys):
        """测试查询不存在的基金"""
        self.stats.show_fund_detail("999999")
        captured = capsys.readouterr()
        assert "未找到基金" in captured.out

    def test_show_group_statistics_json_format(self, capsys):
        """测试 group 命令 JSON 输出"""
        self.stats.show_group_statistics(GroupColumn.FUND_MANAGER, output_format="json")
        captured = capsys.readouterr()
        # 验证输出是有效 JSON
        result = json.loads(captured.out)
        assert "items" in result
        assert "summary" in result
        assert "column" in result
        assert result["column"] == "基金管理人"
        # 验证 summary 包含预期字段
        assert "total_count" in result["summary"]
        assert "total_value" in result["summary"]
        # 验证 items 包含数据
        assert len(result["items"]) > 0
        assert "name" in result["items"][0]
        assert "count" in result["items"][0]
        assert "total" in result["items"][0]
        assert "percentage" in result["items"][0]

    def test_show_query_result_json_format(self, capsys):
        """测试 query 命令 JSON 输出"""
        self.stats.show_query_result(GroupColumn.FUND_MANAGER, "博时", output_format="json")
        captured = capsys.readouterr()
        # 验证输出是有效 JSON
        result = json.loads(captured.out)
        assert "items" in result
        assert "summary" in result
        assert "query" in result
        assert result["query"]["column"] == "基金管理人"
        assert result["query"]["value"] == "博时"
        # 验证 summary 包含预期字段
        assert "total_count" in result["summary"]
        assert "total_value" in result["summary"]
        # 验证 items 包含数据
        assert len(result["items"]) > 0
        item = result["items"][0]
        assert "fund_code" in item
        assert "fund_name" in item
        assert "fund_manager" in item
        assert "holding_shares" in item
        assert "asset_value" in item


class TestGroupStatistics:
    """分组统计功能测试"""

    @pytest.fixture(autouse=True)
    def setup_data(self, temp_db, sample_csv_path):
        """每个测试前导入测试数据并添加基金信息"""
        importer = CSVImporter(temp_db)
        importer.import_from_csv(sample_csv_path)

        # 添加基金信息（用于投资类型统计）
        for code, invest_type in [("004137", "货币型"), ("001821", "债券型"), ("025561", "货币型")]:
            info = FundInfo(
                fund_code=code,
                fund_name=f"测试基金{code}",
                fund_invest_type=invest_type,
                nav=1.0,
                nav_date=date(2026, 2, 25),
            )
            temp_db.upsert_fund_info(info)

        self.db = temp_db

    def test_get_group_statistics_by_manager(self):
        """测试按管理人分组统计"""
        data = self.db.get_group_statistics("fund_manager")
        assert len(data) > 0
        assert any("博时基金" in str(item['name']) for item in data)

    def test_get_group_statistics_by_sales_agency(self):
        """测试按销售机构分组统计"""
        data = self.db.get_group_statistics("sales_agency")
        assert len(data) > 0
        assert any("蚂蚁" in str(item['name']) for item in data)

    def test_get_group_statistics_by_invest_type(self):
        """测试按投资类型分组统计"""
        data = self.db.get_group_statistics("invest_type")
        assert len(data) > 0
        assert any("货币型" in str(item['name']) for item in data)

    def test_query_holdings_by_fund_code(self):
        """测试按基金代码查询"""
        holdings = self.db.query_holdings("fund_code", "004137")
        assert len(holdings) == 1
        assert holdings[0].fund_code == "004137"

    def test_query_holdings_by_fund_name(self):
        """测试按基金名称模糊查询"""
        holdings = self.db.query_holdings("fund_name", "货币")
        assert len(holdings) >= 2  # 至少有两个货币基金

    def test_query_holdings_by_manager(self):
        """测试按基金管理人模糊查询"""
        holdings = self.db.query_holdings("fund_manager", "博时")
        assert len(holdings) == 1
        assert holdings[0].fund_manager == "博时基金"


class TestModels:
    """数据模型测试"""

    def test_fund_holding_primary_key(self):
        """测试持仓记录主键"""
        holding = FundHolding(
            fund_code="004137",
            fund_name="测试",
            share_class="",
            fund_manager="",
            fund_account="account1",
            sales_agency="",
            trade_account="trade1",
            holding_shares=100.0,
            share_date=date(2026, 2, 25),
            nav=1.0,
            nav_date=date(2026, 2, 25),
            asset_value=100.0,
            settlement_currency="人民币",
            dividend_method="",
            fund_type=FundType.PUBLIC_FUND
        )
        assert holding.primary_key == ("account1", "trade1", "004137")

    def test_group_column_display_name(self):
        """测试分组列中文名称"""
        assert GroupColumn.get_display_name(GroupColumn.FUND_CODE) == "基金代码"
        assert GroupColumn.get_display_name(GroupColumn.FUND_MANAGER) == "基金管理人"
        assert GroupColumn.get_display_name(GroupColumn.INVEST_TYPE) == "投资类型"

    def test_fund_info_is_money_market_fund(self):
        """测试货币基金判断"""
        info = FundInfo(
            fund_code="004137",
            fund_name="博时合惠货币市场基金",
            fund_invest_type="货币型"
        )
        assert info.is_money_market_fund() is True

        info2 = FundInfo(
            fund_code="000001",
            fund_name="股票型基金",
            fund_invest_type="股票型"
        )
        assert info2.is_money_market_fund() is False


class TestCLI:
    """CLI 命令测试"""

    @pytest.fixture
    def runner(self):
        """Click CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def temp_db_with_data(self, temp_db, sample_csv_path):
        """创建带测试数据的临时数据库"""
        importer = CSVImporter(temp_db)
        importer.import_from_csv(sample_csv_path)
        return temp_db

    def test_cli_help(self, runner):
        """测试 CLI 帮助命令"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert '基金持仓管理系统' in result.output

    def test_cli_group_command(self, runner, temp_db_with_data):
        """测试 group 命令"""
        result = runner.invoke(cli, ['--db', temp_db_with_data.db_path, 'group', '-c', 'fund_manager'])
        assert result.exit_code == 0
        assert '基金管理人分布' in result.output
        assert '博时基金' in result.output

    def test_cli_query_command(self, runner, temp_db_with_data):
        """测试 query 命令"""
        result = runner.invoke(cli, ['--db', temp_db_with_data.db_path, 'query', '-c', 'fund_code', '-v', '004137'])
        assert result.exit_code == 0
        assert '查询结果' in result.output
        assert '004137' in result.output

    def test_cli_detail_command(self, runner, temp_db_with_data):
        """测试 detail 命令"""
        result = runner.invoke(cli, ['--db', temp_db_with_data.db_path, 'detail', '004137'])
        assert result.exit_code == 0
        assert '我的持仓' in result.output

    def test_cli_import_csv_command(self, runner, temp_db, sample_csv_path):
        """测试 import-csv 命令"""
        result = runner.invoke(cli, ['--db', temp_db.db_path, 'import-csv', sample_csv_path])
        assert result.exit_code == 0
        assert '导入完成' in result.output
        assert '成功: 3 条' in result.output

    @patch('src.cli.EnvChecker')
    @patch('src.cli.MCPService')
    def test_cli_sync_all_command(self, mock_mcp_class, mock_env_class, runner, temp_db_with_data):
        """测试 sync --all 命令"""
        # Mock EnvChecker
        mock_env = MagicMock()
        mock_env.check_mcporter_installed.return_value = True
        mock_env.check_qieman_mcp_configured.return_value = True
        mock_env_class.return_value = mock_env

        # Mock MCPService
        mock_mcp = MagicMock()
        mock_mcp.sync_fund_info.return_value = (3, 0)  # 成功3条，失败0条
        mock_mcp.sync_fund_holdings.return_value = (3, 0)
        mock_mcp_class.return_value = mock_mcp

        result = runner.invoke(cli, ['--db', temp_db_with_data.db_path, 'sync', '--all'])

        assert result.exit_code == 0
        assert '同步基金基础信息' in result.output
        assert '同步基金持仓详情' in result.output
        assert '成功: 3' in result.output

        # 验证 MCP 方法被调用
        mock_mcp.sync_fund_info.assert_called_once()
        mock_mcp.sync_fund_holdings.assert_called_once()

    def test_cli_group_command_json_format(self, runner, temp_db_with_data):
        """测试 CLI group -f json"""
        result = runner.invoke(cli, ['--db', temp_db_with_data.db_path, 'group', '-c', 'fund_manager', '-f', 'json'])
        assert result.exit_code == 0
        # 验证输出是有效 JSON
        output = json.loads(result.output)
        assert "items" in output
        assert "summary" in output
        assert "column" in output
        assert output["column"] == "基金管理人"

    def test_cli_query_command_json_format(self, runner, temp_db_with_data):
        """测试 CLI query -f json"""
        result = runner.invoke(cli, ['--db', temp_db_with_data.db_path, 'query', '-c', 'fund_code', '-v', '004137', '-f', 'json'])
        assert result.exit_code == 0
        # 验证输出是有效 JSON
        output = json.loads(result.output)
        assert "items" in output
        assert "summary" in output
        assert "query" in output
        assert output["query"]["column"] == "基金代码"
        assert output["query"]["value"] == "004137"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])