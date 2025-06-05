from mcp.server.fastmcp import FastMCP

from example.multimodal_example import markdown_to_pdf
from example.pollinations_example import text_2_image
from example.simple_tools_example import decimal_calculate, get_exchange_rate, now
from example.text2sql_example import get_data_base_ddl, execute_select_sql

# Create an MCP server
mcp = FastMCP("vanilla-mcp", stateless_http=True, json_response=True, host="127.0.0.1", port=8880)

mcp.add_tool(markdown_to_pdf)
mcp.add_tool(text_2_image)
mcp.add_tool(decimal_calculate)
mcp.add_tool(get_exchange_rate)
mcp.add_tool(now)
mcp.add_tool(get_data_base_ddl)
mcp.add_tool(execute_select_sql)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
