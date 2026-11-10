from src.utils.report_display import etf_action_label, etf_sector_label, strip_emoji


def test_strip_emoji_keeps_text_and_numbers():
    text = "## 🎯 2026-11-10 决策仪表盘\n> 🟢买入:0 🟡观望:13 🔴卖出:0 ✅ 完成"
    cleaned = strip_emoji(text)
    assert "🎯" not in cleaned and "🟢" not in cleaned and "✅" not in cleaned
    assert "2026-11-10" in cleaned
    assert "买入:0" in cleaned and "观望:13" in cleaned


def test_etf_sector_label():
    assert etf_sector_label("机器人ETF华夏") == "机器人"
    assert etf_sector_label("中证500ETF南方") == "中证500"
    assert etf_sector_label("") == "N/A"


def test_etf_action_label():
    assert etf_action_label("买入") == "加仓"
    assert etf_action_label("持有") == "继续持有"
    assert etf_action_label("减仓") == "减仓"
    assert etf_action_label("观望") == "继续持有"
