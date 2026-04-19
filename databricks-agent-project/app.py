"""
Databricks Agent Application
Based on Projeto6.ipynb - LangGraph Agent with MLflow Tracing
"""

import os
import warnings
from typing import Any, Generator, Optional, Sequence, Union

import mlflow
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_node import ToolNode
from mlflow.langchain.chat_agent_langgraph import ChatAgentState, ChatAgentToolNode
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentChunk, ChatAgentMessage, ChatAgentResponse, ChatContext

warnings.filterwarnings('ignore')

# Configuration from environment variables
LLM_ENDPOINT_NAME = os.getenv("LLM_ENDPOINT_NAME", "databricks-meta-llama-3-3-70b-instruct")
UC_TOOL_NAMES = os.getenv("UC_TOOL_NAMES", "system.ai.python_exec").split(",")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "/databricks-agent-project")

# System prompt
SYSTEM_PROMPT = "Responda com precisão. Se não souber a resposta diga que não sabe ao invés de inventar respostas."


def create_tool_calling_agent(
    model: LanguageModelLike,
    tools: Union[ToolNode, Sequence[BaseTool]],
    system_prompt: Optional[str] = None,
) -> StateGraph:
    """Create a tool-calling agent using LangGraph."""
    
    # Bind model to tools
    model = model.bind_tools(tools)

    def should_continue(state: ChatAgentState):
        """Decide whether to continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if last_message.get("tool_calls"):
            return "continue"
        else:
            return "end"

    # Add system prompt if provided
    if system_prompt:
        preprocessor = RunnableLambda(
            lambda state: [{"role": "system", "content": system_prompt}] + state["messages"]
        )
    else:
        preprocessor = RunnableLambda(lambda state: state["messages"])

    model_runnable = preprocessor | model

    def call_model(state: ChatAgentState, config: RunnableConfig):
        """Call the model with processed messages."""
        response = model_runnable.invoke(state, config)
        return {"messages": [response]}

    # Create workflow
    workflow = StateGraph(ChatAgentState)
    workflow.add_node("agent", RunnableLambda(call_model))
    workflow.add_node("tools", ChatAgentToolNode(tools))
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        },
    )
    
    workflow.add_edge("tools", "agent")
    return workflow.compile()


class LangGraphChatAgent(ChatAgent):
    """Custom ChatAgent that wraps a LangGraph agent."""
    
    def __init__(self, agent: StateGraph):
        self.agent = agent

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> ChatAgentResponse:
        """Generate a complete response."""
        request = {"messages": self._convert_messages_to_dict(messages)}
        messages = []
        
        for event in self.agent.stream(request, stream_mode="updates"):
            for node_data in event.values():
                messages.extend(
                    ChatAgentMessage(**msg) for msg in node_data.get("messages", [])
                )
        
        return ChatAgentResponse(messages=messages)

    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> Generator[ChatAgentChunk, None, None]:
        """Generate streaming response."""
        request = {"messages": self._convert_messages_to_dict(messages)}
        
        for event in self.agent.stream(request, stream_mode="updates"):
            for node_data in event.values():
                yield from (
                    ChatAgentChunk(**{"delta": msg}) for msg in node_data["messages"]
                )


def main():
    """Main entry point for the Databricks App."""
    
    # Set MLflow experiment
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    # Enable MLflow autologging for LangChain
    mlflow.langchain.autolog()
    
    # Enable MLflow tracing for Databricks
    mlflow.databricks.enable_tracing()
    
    # Initialize LLM
    llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)
    
    # Initialize UC tools
    tools = []
    uc_toolkit = UCFunctionToolkit(function_names=UC_TOOL_NAMES)
    tools.extend(uc_toolkit.tools)
    
    # Create agent
    agent_graph = create_tool_calling_agent(llm, tools, SYSTEM_PROMPT)
    
    # Create ChatAgent wrapper
    agent = LangGraphChatAgent(agent_graph)
    
    # Log agent creation
    print(f"Agent initialized with endpoint: {LLM_ENDPOINT_NAME}")
    print(f"UC tools: {UC_TOOL_NAMES}")
    print(f"MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")
    
    # Test the agent
    test_message = {"messages": [{"role": "user", "content": "Oi. Testando o agente!"}]}
    response = agent.predict(test_message)
    print(f"Test response: {response.messages[-1].content}")
    
    return agent


if __name__ == "__main__":
    agent = main()
