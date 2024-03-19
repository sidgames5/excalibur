import os
from typing import List, Tuple

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.output_parsers import (
    ReActJsonSingleInputOutputParser,
)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.render import render_text_description_and_args
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from langchain_community.tools import DuckDuckGoSearchRun
from modules.smalltalk import SmalltalkTool
from modules.weather import WeatherTool
from modules.timetool import DateTimeTool


llm = ChatOllama(
    model=os.environ.get("AI_MODEL"),
    temperature=0,
    base_url=os.environ["OLLAMA_BASE_URL"],
    streaming=True,
)
# # Just me testing
# from langchain_community.chat_models import ChatOpenAI
# llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.environ.get("OPENAI_API_KEY"))


chat_model_with_stop = llm.bind(stop=["\nObservation"])
tools = [DuckDuckGoSearchRun(), SmalltalkTool(), WeatherTool(), DateTimeTool()]

# Inspiration taken from hub.pull("hwchase17/react-json")
system_message = f"""Answer the following questions as best you can.
You can answer directly if the user is greeting you or similar.
Otherise, you have access to the following tools:

{render_text_description_and_args(tools).replace('{', '{{').replace('}', '}}')}

The way you use the tools is by specifying a json blob.
Specifically, this json should have a `action` key (with the name of the tool to use)
and a `action_input` key (with the input to the tool going here).
The only values that should be in the "action" field are: {[t.name for t in tools]}
The $JSON_BLOB should only contain a SINGLE action, 
do NOT return a list of multiple actions.
Here is an example of a valid $JSON_BLOB:
```
{{{{
    "action": $TOOL_NAME,
    "action_input": $INPUT
}}}}
```
The $JSON_BLOB must always be enclosed with triple backticks!


ALWAYS use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action:```
$JSON_BLOB
```
Observation: the result of the action... 
(this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Reminder to always use the exact responce format as shown above.'
"""

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=system_message),
        # MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def _format_chat_history(chat_history: List[Tuple[str, str]]):
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_messages(x["intermediate_steps"]),
        "chat_history": lambda x: (
            _format_chat_history(x["chat_history"]) if x.get("chat_history") else []
        ),
    }
    | prompt
    | chat_model_with_stop
    | ReActJsonSingleInputOutputParser()
)


# Add typing for input
class AgentInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True).with_types(
    input_type=AgentInput
)
