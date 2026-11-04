from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.tools.types import ToolMetadata
from llama_index.core.agent.react.base import ReActAgent
from llama_index.core.chat_engine.types import AgentChatResponse
from llama_index.llms.openai.base import OpenAI
import chainlit as cl
from chainlit.input_widget import Select, TextInput # "input_widgets" in older chainlit
import openai
from index_wikipages import create_index
from utils import get_apikey

index = None
agent = None

@cl.on_chat_start
async def on_chat_start():
    global index
    # Settings
    settings = await cl.ChatSettings(
        [
            Select(
                id="MODEL",
                label="OpenAI - GPT Model",
                values=["gpt-4o-mini"], # installed llama-index doesn't support gpt-5-nano
                initial_index=0,
            ),
            TextInput(
                id="WikiPageRequest",
                label="Request Wikipage(s)",
                placeholder="Please index: Wikipedia page, Wikipedia page2, etc.",
            ),
        ]
    ).send()
    cl.user_session.set("agent", None)

def wikisearch_engine(index):
    query_engine = index.as_query_engine(
        response_mode="compact",
        verbose=True,
        similarity_top_k=10,
        llm=OpenAI(model="gpt-4o-mini"), # default gpt-3.5-turbo is deprecated
    )
    return query_engine


def create_react_agent(MODEL, index):
    query_engine_tools = [
        QueryEngineTool(
            query_engine=wikisearch_engine(index),
            metadata=ToolMetadata(
                name="Wikipedia",
                description="Useful for performing searches on the Wikipedia knowledgebase.",
            ),
        )
    ]

    openai.api_key = get_apikey()
    llm = OpenAI(model=MODEL)
    agent = ReActAgent.from_tools(
        tools=query_engine_tools,
        llm=llm,
        verbose=True,
    )
    return agent


@cl.on_settings_update
async def setup_agent(settings):
    global agent
    global index
    request_query = settings["WikiPageRequest"]
    index = create_index(request_query)

    print("on_settings_update", settings)
    MODEL = settings["MODEL"]
    agent = create_react_agent(MODEL, index)
    cl.user_session.set("agent", agent)
    await cl.Message(
        author="Agent", content=f"""Wikipage(s) "{request_query}" successfully indexed"""
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Processes incoming messages from the user."""
    agent = cl.user_session.get("agent")
    
    if not agent:
        await cl.Message(
            author="Agent", 
            content="Agent is not available. Please set up the agent in the settings."
        ).send()
        return

    # chainlit 2.x passes a Message object, so pass its text to the agent
    response = await cl.make_async(agent.chat)(message.content)
    
    if isinstance(response, AgentChatResponse):
        final_response = response.response
    else:
        final_response = str(response)

    await cl.Message(author="Agent", content=final_response).send()