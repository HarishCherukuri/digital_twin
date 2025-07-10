import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace, ModelSettings
from openai.types.responses import ResponseTextDeltaEvent
from mcp_servers import memory_rag_server, memory_graph_server, slack_server
from question_tools import get_question_tools, get_questions_with_no_answer
import gradio as gr
from gradio.themes.utils import fonts
from uistyling import custom_css
from prompts import admin_system_prompt

load_dotenv(override=True)

tools = get_question_tools() 
MODEL = "gpt-4o-mini"
MODEL_SETTINGS = ModelSettings(temperature=0.0)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

examples = [
    "Are there any questions that are not answered yet?",
    "Please summarize your memory of me",
]


async def stream_response(messages, mcps):
    agent = Agent("Admin", instructions=admin_system_prompt, model=MODEL, tools=tools, mcp_servers=mcps)
    result = Runner.run_streamed(agent, messages)
    reply = ""
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            reply += event.data.delta
            yield reply


async def chat(message, history):
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages += [{"role": "user", "content": message}]
    with trace("Admin"):
        async with memory_rag_server() as rag_server:
            async with memory_graph_server() as graph_server:
                async with slack_server() as slack:
                    mcps = [rag_server, graph_server, slack]
                    async for chunk in stream_response(messages, mcps):
                        yield chunk


def get_admin_interface():
    theme = gr.themes.Default(primary_hue="blue")
    title = "Digital Twin Admin"
    return gr.ChatInterface(chat, type="messages", examples=examples, theme=theme, title=title)


async def main():
    interface = get_admin_interface()
    interface.launch(inbrowser=True, auth=[("admin", ADMIN_PASSWORD)])


if __name__ == "__main__":
    asyncio.run(main())