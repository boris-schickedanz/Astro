import pytest

from mcp_server import (
    calculate_full_reading,
    calculate_natal_chart,
    calculate_transits,
    mcp,
)


@pytest.mark.anyio
async def test_mcp_tools_registration():
    """All three tools must register with the MCP server."""
    tools = await mcp.get_tools()
    if isinstance(tools, dict):
        tool_names = list(tools.keys())
    elif isinstance(tools, list):
        tool_names = [t.name if hasattr(t, "name") else t for t in tools]
    else:
        tool_names = []

    assert "calculate_natal_chart" in tool_names
    assert "calculate_transits" in tool_names
    assert "calculate_full_reading" in tool_names


def test_calculate_natal_chart_execution():
    """Natal block must include header, planets, and the new analysis sections."""
    result = calculate_natal_chart.fn(
        name="Test User", year=1990, month=1, day=1,
        hour=12, minute=0, city="London", nation="GB",
    )
    assert "Birth Chart for Test User" in result
    assert "Sun" in result
    assert "Chart Balance:" in result
    assert "Chart Ruler:" in result
    assert "ANNUAL PROFECTION" in result


def test_calculate_transits_execution():
    """Predictions block must include current transits, long-term, and SR."""
    result = calculate_transits.fn(
        name="Test User", year=1990, month=1, day=1,
        hour=12, minute=0, city="London", nation="GB",
    )
    assert "TRANSITS CALCULATION" in result
    assert "SIGNIFICANT LONG-TERM TRANSITS" in result
    assert "SOLAR RETURN" in result


def test_calculate_full_reading_combines_blocks():
    result = calculate_full_reading.fn(
        name="Test User", year=1990, month=1, day=1,
        hour=12, minute=0, city="London", nation="GB",
    )
    assert "Birth Chart for Test User" in result
    assert "ANNUAL PROFECTION" in result
    assert "TRANSITS CALCULATION" in result
    assert "SOLAR RETURN" in result
