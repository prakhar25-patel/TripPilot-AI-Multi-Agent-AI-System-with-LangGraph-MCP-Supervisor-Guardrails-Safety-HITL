# import os
# import sys
# from pathlib import Path

# import certifi
# from dotenv import load_dotenv
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_groq import ChatGroq


# # ==========================================
# # Environment configuration
# # ==========================================

# os.environ["SSL_CERT_FILE"] = certifi.where()
# os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# load_dotenv()

# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
# # OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# # Automatically find the current project folder.
# # This replaces the hard-coded Windows paths.
# PROJECT_DIR = Path(__file__).resolve().parent
# # WEATHER_SERVER_PATH = PROJECT_DIR / "custom_weather_mcp_server.py"


# # Preserve the complete Windows environment when starting
# # local stdio MCP servers.
# # AVIATION_ENV = os.environ.copy()
# # AVIATION_ENV["AVIATION_STACK_API_KEY"] = (
# #     AVIATION_STACK_API_KEY or ""
# # )

# # WEATHER_ENV = os.environ.copy()
# # WEATHER_ENV["OPENWEATHER_API_KEY"] = (
# #     OPENWEATHER_API_KEY or ""
# # )


# # ==========================================
# # LLM
# # ==========================================

# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     api_key=GROQ_API_KEY
# )


# # ==========================================
# # MCP client configuration
# # ==========================================

# client = MultiServerMCPClient(
#     {
#         "tavily": {
#             "transport": "streamable_http",
#             "url": (
#                 "https://mcp.tavily.com/mcp/"
#                 f"?tavilyApiKey={TAVILY_API_KEY}"
#             )
#         },

#         "aviationstack": {
#             "transport": "stdio",
#             "command": "UVX_COMMAND",
#             "args": [
#                 "aviationstack-mcp"
#             ],
#             "env": {AVIATION_STACK_API_KEY }
#         }

#         # "weather": {
#         #     "transport": "stdio",

#         #     # Use the same Python environment that runs app.py.
#         #     "command": r"",

#         #     # Automatically use custom_weather_mcp_server.py
#         #     # from the current project directory.
#         #     "args": [
#         #         str(WEATHER_SERVER_PATH)
#         #     ],

#         #     "env": WEATHER_ENV
#         # }
#     }
# )


# # ==========================================
# # Diagnostic function
# # ==========================================

# async def get_all_tools():
#     """
#     Load each MCP server separately.

#     A broken server will no longer prevent the other
#     working servers from loading.
#     """

#     all_tools = []

#     for server_name in (
#         "tavily",
#         "aviationstack"
#         # "weather"
#     ):
#         try:
#             tools = await client.get_tools(
#                 server_name=server_name
#             )

#             all_tools.extend(tools)

#             print(
#                 f"\nAvailable tools from "
#                 f"{server_name} MCP:\n"
#             )

#             for tool in tools:
#                 print(tool.name)

#         except Exception as error:
#             print(
#                 f"\nCould not connect to "
#                 f"{server_name} MCP:\n{error}\n"
#             )

#     return all_tools


# # ==========================================
# # Tavily MCP tool
# # ==========================================

# search_tool = None


# async def initialize_mcp():
#     """
#     Initialize only Tavily.

#     Previously this function initialized all MCP servers,
#     so an AviationStack or Weather failure also caused
#     Tavily hotel search to fail.
#     """

#     global search_tool

#     if search_tool is not None:
#         return

#     tools = await client.get_tools(
#         server_name="tavily"
#     )

#     tools_by_name = {
#         tool.name: tool
#         for tool in tools
#     }

#     search_tool = tools_by_name.get(
#         "tavily_search"
#     )

#     if search_tool is None:
#         available_tools = ", ".join(
#             tools_by_name.keys()
#         )

#         raise RuntimeError(
#             "Tavily MCP connected, but the "
#             "'tavily_search' tool was not found. "
#             f"Available tools: "
#             f"{available_tools or 'none'}"
#         )


# async def tavily_mcp_search(query: str):
#     await initialize_mcp()

#     result = await search_tool.ainvoke(
#         {
#             "query": query
#         }
#     )

#     return result


# # ==========================================
# # AviationStack MCP tools
# # ==========================================

# aviation_tools = {}


# async def initialize_aviation_tools():
#     global aviation_tools

#     if aviation_tools:
#         return

#     # Load only AviationStack.
#     # Tavily and Weather will not be initialized here.
#     tools = await client.get_tools(
#         server_name="aviationstack"
#     )

#     aviation_tools = {
#         tool.name: tool
#         for tool in tools
#     }

#     if not aviation_tools:
#         raise RuntimeError(
#             "AviationStack MCP connected but "
#             "returned no tools."
#         )


# async def aviation_mcp_call(
#     tool_name: str,
#     tool_args: dict = None
# ):
#     await initialize_aviation_tools()

#     tool = aviation_tools.get(tool_name)

#     if tool is None:
#         available_tools = ", ".join(
#             sorted(aviation_tools.keys())
#         )

#         raise ValueError(
#             f"AviationStack tool '{tool_name}' "
#             "was not found. "
#             f"Available tools: "
#             f"{available_tools or 'none'}"
#         )

#     result = await tool.ainvoke(
#         tool_args or {}
#     )

#     return result


# ==========================================
# Weather MCP tools
# ==========================================

# weather_tool = None
# forecast_tool = None


# async def initialize_weather_tools():
#     global weather_tool
#     global forecast_tool

#     if (
#         weather_tool is not None
#         and forecast_tool is not None
#     ):
#         return

#     if not WEATHER_SERVER_PATH.exists():
#         raise FileNotFoundError(
#             "Weather MCP server file was not found: "
#             f"{WEATHER_SERVER_PATH}"
#         )

#     # Load only Weather.
#     # Tavily and AviationStack will not be started.
#     tools = await client.get_tools(
#         server_name="weather"
#     )

#     tools_by_name = {
#         tool.name: tool
#         for tool in tools
#     }

#     weather_tool = tools_by_name.get(
#         "get_current_weather"
#     )

#     forecast_tool = tools_by_name.get(
#         "get_forecast"
#     )

#     missing_tools = []

#     if weather_tool is None:
#         missing_tools.append(
#             "get_current_weather"
#         )

#     if forecast_tool is None:
#         missing_tools.append(
#             "get_forecast"
#         )

#     if missing_tools:
#         available_tools = ", ".join(
#             tools_by_name.keys()
#         )

#         raise RuntimeError(
#             "Missing Weather MCP tools: "
#             f"{', '.join(missing_tools)}. "
#             f"Available tools: "
#             f"{available_tools or 'none'}"
#         )


# async def weather_mcp_search(city: str):
#     await initialize_weather_tools()

#     result = await weather_tool.ainvoke(
#         {
#             "city": city
#         }
#     )

#     return result


# async def forecast_mcp_search(city: str):
#     await initialize_weather_tools()

#     result = await forecast_tool.ainvoke(
#         {
#             "city": city
#         }
#     )

#     return result


# ==========================================
# Destination extractor
# ==========================================

# def extract_destination(query: str) -> str:
#     prompt = f"""
# Extract only the destination city or country from the travel request.

# Travel request:
# {query}

# Return only the destination name.
# Do not add any explanation.
# """

#     response = llm.invoke(prompt)

#     destination = str(
#         response.content
#     ).strip()

#     if not destination:
#         raise ValueError(
#             "The destination could not be extracted."
#         )

#     return destination


#  upgraded mcp

import os
import shutil
import sys
from pathlib import Path
from typing import Any

import certifi
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient


# =========================================================
# Environment setup
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Support both environment-variable names.
AVIATION_STACK_API_KEY = (
    os.getenv("AVIATION_STACK_API_KEY")
    or os.getenv("AVIATIONSTACK_API_KEY")
)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UVX_COMMAND = shutil.which("uvx") or "uvx"


def _require_env(name: str, value: str | None) -> str:
    """Return an environment value or raise a readable setup error."""

    if not value:
        raise RuntimeError(
            f"{name} is missing. "
            f"Add {name}=your_key to the project .env file."
        )

    return value


def _subprocess_env(**updates: str | None) -> dict[str, str]:
    """
    Preserve the current Windows/Conda environment and add MCP API keys.
    """

    env = os.environ.copy()

    for key, value in updates.items():
        if value:
            env[key] = value

    return env


# =========================================================
# LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=_require_env("GROQ_API_KEY", GROQ_API_KEY),
)


# =========================================================
# MCP client
# =========================================================

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={TAVILY_API_KEY or ''}"
            ),
        },

        "aviationstack": {
            "transport": "stdio",
            "command": UVX_COMMAND,
            "args": [
                "aviationstack-mcp",
            ],
            "env": _subprocess_env(
                AVIATION_STACK_API_KEY=AVIATION_STACK_API_KEY,
            ),
        }

        
    }
)


async def _get_server_tool(
    server_name: str,
    tool_name: str,
):
    """
    Load one tool from one MCP server.

    This prevents a broken weather or AviationStack server from
    crashing an unrelated Tavily request.
    """

    if server_name == "tavily":
        _require_env(
            "TAVILY_API_KEY",
            TAVILY_API_KEY,
        )

    elif server_name == "aviationstack":
        _require_env(
            "AVIATION_STACK_API_KEY",
            AVIATION_STACK_API_KEY,
        )

        if shutil.which("uvx") is None:
            raise RuntimeError(
                "uvx was not found. Install uv, reopen the terminal, "
                "activate the travel environment, and run "
                "`uvx --version`."
            )

    

    # Important: load only the requested MCP server.
    tools = await client.get_tools(
        server_name=server_name,
    )

    tool = next(
        (
            item
            for item in tools
            if item.name == tool_name
        ),
        None,
    )

    if tool is None:
        available_tools = (
            ", ".join(
                sorted(item.name for item in tools)
            )
            or "none"
        )

        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found "
            f"on server '{server_name}'. "
            f"Available tools: {available_tools}"
        )

    return tool


# =========================================================
# MCP connection test
# =========================================================

async def get_all_tools() -> None:
    """
    Test every MCP server independently.

    One failed server will not stop the remaining tests.
    """

    for server_name in (
        "tavily",
        "aviationstack"
    ):
        try:
            tools = await client.get_tools(
                server_name=server_name,
            )

            tool_names = (
                ", ".join(
                    tool.name
                    for tool in tools
                )
                or "no tools"
            )

            print(
                f"{server_name}: OK -> {tool_names}"
            )

        except Exception as exc:
            print(
                f"{server_name}: FAILED -> "
                f"{type(exc).__name__}: {exc}"
            )


# =========================================================
# Tavily MCP
# =========================================================

async def tavily_mcp_search(query: str):
    search_tool = await _get_server_tool(
        "tavily",
        "tavily_search",
    )

    return await search_tool.ainvoke(
        {
            "query": query,
        }
    )


# =========================================================
# AviationStack MCP
# =========================================================

async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
):
    aviation_tool = await _get_server_tool(
        "aviationstack",
        tool_name,
    )

    return await aviation_tool.ainvoke(
        tool_args or {}
    )



# =========================================================
# Destination extractor
# =========================================================

def extract_destination(query: str) -> str:
    prompt = f"""
Extract only the destination city or country from the travel request.

Travel request:
{query}

Return only the destination name.
Do not add any explanation.
"""

    response = llm.invoke(prompt)

    destination = str(
        response.content
    ).strip()

    if not destination:
        raise ValueError(
            "The destination could not be extracted."
        )

    return destination