from dotenv import load_dotenv
from agents import Agent, Runner, trace, ModelSettings
from mcp_servers import memory_rag_server, memory_graph_server, slack_server
from question_tools import get_question_tools
from prompts import dt_system_prompt
from uistyling import custom_css, EXAMPLE_QUESTIONS
from resources import name
import gradio as gr
from gradio.themes.utils import fonts

load_dotenv(override=True)
MODEL = "gpt-4.1"
MODEL_SETTINGS = ModelSettings(temperature=0.0)

custom_tools = get_question_tools()

async def chat(message, history):
    messages = [{"role": prior["role"], "content": prior["content"]} for prior in history]  
    messages += [{"role": "user", "content": message}]
    with trace("digital_twin"):
        async with memory_rag_server() as rag_server:
            async with memory_graph_server() as graph_server:
                async with slack_server() as slack:
                    mcps = [rag_server, graph_server, slack]
                    
                    agent = Agent("digital_twin", 
                                  instructions=dt_system_prompt, 
                                  model=MODEL, 
                                  model_settings=MODEL_SETTINGS, 
                                  tools=custom_tools,
                                  mcp_servers=mcps)
                    response = await Runner.run(agent, messages)
    return response.final_output

def get_interface():
    theme = gr.themes.Default(
        primary_hue="sky", neutral_hue="slate", font=[fonts.GoogleFont("Poppins"), "sans-serif"]
    )
    with gr.Blocks(
        css=custom_css,
        title=f"{name} | Digital Twin",
        theme=theme,
    ) as interface:
        with gr.Row(elem_classes="header-container"):
            gr.HTML(f"""
                <div class="main-title">{name}'s&nbsp;Digital&nbsp;Twin</div>
                <div class="subtitle">Ask me anything about my professional background, skills, and experience.</div>
            """)
        with gr.Row(elem_classes="examples-container"):
            gr.HTML('<div class="examples-title">💡 Try asking:</div>')
            with gr.Row():
                example_buttons = [
                    gr.Button(q, elem_classes="example-btn", size="sm") for q in EXAMPLE_QUESTIONS
                ]
        chatbot_interface = gr.ChatInterface(
            fn=chat,
            type="messages",
            title="",
            chatbot=gr.Chatbot(
                height=500,
                placeholder=f"👋 Hi! I'm {name}'s digital twin. Ask away…",
                type="messages",
                label=name,
                avatar_images=(None, "data/Harish_Pic.png"),
            ),
            textbox=gr.Textbox(
                placeholder="Ask me about my background, skills, projects, or experience…",
                container=False,
                scale=7,
            ),
        )
        for btn in example_buttons:
            btn.click(lambda q: q, inputs=[btn], outputs=[chatbot_interface.textbox])
        gr.HTML(f"<div class='footer'>{name}'s Digital Twin</div>")

    return interface

def main():
    interface = get_interface()
    interface.launch(inbrowser=True)

if __name__ == "__main__":
    main()
