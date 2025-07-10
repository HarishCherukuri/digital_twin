import os
from agents.mcp import MCPServerStdio, MCPServerSse
from agents.mcp import create_static_tool_filter, ToolFilterContext

GRAPH_DB = "./memory/duck_graph.db"
RAG_DB = "./memory/knowledge/"

memory_graph_params = {
    "command": "npx",
    "args": ["-y", "@izumisy/mcp-duckdb-memory-server"],
    "env": {"MEMORY_FILE_PATH": f"{GRAPH_DB}"},
}

memory_rag_params = {
    "command": "uvx",
    "args": ["mcp-server-qdrant"],
    "env": {
        "QDRANT_LOCAL_PATH": RAG_DB,
        "COLLECTION_NAME": "knowledge",
        "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
    },
}

slack_mcp_params = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-slack"],
    "env": {
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "SLACK_TEAM_ID": os.getenv("SLACK_TEAM_ID"), 
        "SLACK_CHANNEL_IDS": os.getenv("SLACK_CHANNEL_ID"),
}
}


def memory_graph_server():
     return MCPServerStdio(memory_graph_params, 
                           cache_tools_list=True, 
                           client_session_timeout_seconds=60
                           )


def memory_rag_server():
    return MCPServerStdio(memory_rag_params, 
                          cache_tools_list=True, 
                          client_session_timeout_seconds=60)

def slack_server():
    return MCPServerStdio(slack_mcp_params, 
                          cache_tools_list=True, 
                          client_session_timeout_seconds=60,
                          tool_filter=slack_tool_filter)

# def slack_server():
#     return MCPServerStdio(slack_mcp_params, 
#                           cache_tools_list=True, 
#                           client_session_timeout_seconds=60
#                           tool_filter=create_static_tool_filter(allowed_tool_names=["slack_post_message"]))

## Custom Tool Filter
def slack_tool_filter(context: ToolFilterContext, tool) -> bool:
    return tool.name.startswith("slack_post")