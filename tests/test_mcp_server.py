import pytest
from mcp_server import mcp, calculate_natal_chart, calculate_transits, calculate_collective_chart, calculate_long_term_transits

@pytest.mark.anyio
async def test_mcp_tools_registration():
    """Test that all tools are registered with the MCP server."""
    tools = await mcp.get_tools()
    # Check if it's a dict or list
    if isinstance(tools, dict):
        tool_names = list(tools.keys())
    elif isinstance(tools, list):
        if tools and hasattr(tools[0], 'name'):
            tool_names = [tool.name for tool in tools]
        else:
            tool_names = tools
    else:
        tool_names = []
    
    assert "calculate_natal_chart" in tool_names
    assert "calculate_transits" in tool_names
    assert "calculate_collective_chart" in tool_names
    assert "calculate_long_term_transits" in tool_names

def test_calculate_natal_chart_execution():
    """Test basic execution of natal chart tool."""
    # Access the underlying function using .fn
    result = calculate_natal_chart.fn(
        name="Test User",
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        city="London",
        nation="GB"
    )
    assert "Birth Chart for Test User" in result
    assert "Sun" in result
    assert "Moon" in result

def test_calculate_collective_chart_execution():
    """Test basic execution of collective chart tool."""
    result = calculate_collective_chart.fn(
        city="London",
        nation="GB",
        date="2024-01-01",
        hour=12
    )
    assert "Collective Chart London" in result
    assert "Sun" in result

def test_calculate_transits_execution():
    """Test basic execution of transits tool."""
    result = calculate_transits.fn(
        name="Test User",
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        city="London",
        nation="GB",
        transit_date="2024-01-01"
    )
    assert "TRANSITS" in result or "Transits" in result
    assert "Test User" in result

def test_calculate_long_term_transits_execution():
    """Test basic execution of long term transits tool."""
    result = calculate_long_term_transits.fn(
        name="Test User",
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        city="London",
        nation="GB",
        years_before=1,
        years_after=1
    )
    assert "LONG-TERM TRANSITS" in result or "Long-term Transits" in result
