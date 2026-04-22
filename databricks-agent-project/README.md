# Databricks Agent Project

🤖 Production-ready AI Agent with LangGraph, Databricks Agents, and MLflow Tracing

## Overview

This project demonstrates how to build **production-ready AI agents** on Databricks using:
- **LangGraph**: Agent orchestration with tool calling and state management
- **Databricks LangChain**: LLM integration with foundation models
- **MLflow Tracing**: Full observability and debugging capabilities
- **Unity Catalog Functions**: Governed tool integration
- **ChatDatabricks**: Serverless model serving integration

Based on Data Science Academy's AI Agent course material.

## Project Structure

```
databricks-agent-project/
├── databricks.yaml        # Databricks Asset Bundle configuration
├── README.md              # This file
└── src/                   # Source code and notebooks
    ├── agent_ai.ipynb     # Main development notebook with agent implementation
    └── requirements.txt   # Python dependencies
```

## Features

- **🏗️ LangGraph Agent**: Tool-calling agent with conditional routing and state management
- **📊 MLflow Tracing**: Full observability with automatic logging and debugging
- **🔧 Unity Catalog Tools**: Integration with UC functions (e.g., `system.ai.python_exec`)
- **🤖 ChatDatabricks**: LLM integration with Databricks foundation models
- **📡 Streaming Support**: Both predict and predict_stream modes for real-time interactions
- **🎯 Custom ChatAgent**: MLflow-compatible agent wrapper for deployment
- **🔍 Non-deprecated APIs**: Uses latest UCFunctionToolkit from databricks_langchain.uc_ai

## Prerequisites

- ✅ Databricks workspace with Unity Catalog enabled
- ✅ Model serving endpoint configured (e.g., `databricks-meta-llama-3-3-70b-instruct`)
- ✅ Appropriate permissions for UC functions
- ✅ Databricks CLI installed and configured
- ✅ Python environment with required dependencies

## Setup

1. **Install Dependencies**

```bash
# Install required packages
pip install -r src/requirements.txt

# Or install individually
pip install databricks-agents>=0.16.0 mlflow>=2.20.2 databricks-langchain langgraph==0.3.4 langchain-core langchain databricks-sdk
```

2. **Configure Environment Variables**

```python
# In your notebook or script
LLM_ENDPOINT_NAME = "databricks-meta-llama-3-3-70b-instruct"
uc_tool_names = ["system.ai.python_exec"]
system_prompt = "Responda com precisão. Se não souber a resposta diga que não sabe ao invés de inventar respostas."
```

3. **Deploy to Databricks Workspace**

```bash
# Sync files to workspace
databricks sync . /Workspace/Users/your-email/databricks-agent-project
```

## Agent Architecture

### Components

1. **🤖 LLM**: ChatDatabricks with foundation model endpoint
2. **🔧 Tools**: Unity Catalog functions using UCFunctionToolkit (non-deprecated)
3. **🏗️ Agent Graph**: LangGraph StateGraph with conditional routing
4. **📊 MLflow Integration**: Automatic logging and tracing enabled
5. **🎯 ChatAgent Wrapper**: MLflow-compatible interface for deployment

### Agent Flow

```
User Message
     ↓
Agent Node (LLM with tools)
     ↓
  Tool Calls?
     ↓
   /   \
  Yes   No
  ↓     ↓
Tools  END
  ↓
Agent Node (LLM with tool results)
     ↓
   Response
```

### State Management

The agent uses `ChatAgentState` to maintain:
- **Message History**: Complete conversation context
- **Tool Results**: Output from UC function calls
- **Routing Decisions**: Conditional flow control

## Development

### Running the Agent

Open `src/agent_ai.ipynb` in the Databricks workspace and run the cells sequentially:

1. **Environment Setup**: Import dependencies and restart Python
2. **LLM Configuration**: Set up ChatDatabricks endpoint
3. **Tool Integration**: Configure Unity Catalog functions
4. **Agent Creation**: Build LangGraph agent with tool calling
5. **Testing**: Verify functionality with predict and streaming modes

### Key Code Components

```python
# Create the agent
dsa_agente_ia = create_tool_calling_agent(llm, tools, system_prompt)

# Wrap with MLflow interface
DSA_AGENTE = LangGraphChatAgent(dsa_agente_ia)

# Test predictions
response = DSA_AGENTE.predict({"messages": [{"role": "user", "content": "Hello!"}]})

# Test streaming
for chunk in DSA_AGENTE.predict_stream({"messages": [{"role": "user", "content": "Question"}]}):
    print(chunk.delta.content, end="", flush=True)
```

### MLflow Tracing

Tracing is automatically enabled via:
- `mlflow.langchain.autolog()`: Logs LangChain operations
- Automatic experiment tracking for all agent executions

View traces in MLflow Experiments to debug and monitor agent performance.

## Deployment

### Deploy with Databricks Asset Bundle (DAB)

```bash
# Validate bundle
databricks bundle validate

# Deploy to workspace
databricks bundle deploy

# Deploy specific target
databricks bundle deploy --target production
```

## Monitoring

### MLflow Traces

Navigate to MLflow Experiments in the workspace:
1. Open Experiments
2. Select `/databricks-agent-project`
3. View traces for debugging and performance analysis

## Troubleshooting

### Common Issues

1. **UC Function Not Found**: Verify `UC_TOOL_NAMES` are correct and accessible
2. **Model Endpoint Not Ready**: Check endpoint status in Model Serving
3. **MLflow Tracing Not Working**: Ensure MLflow experiment exists
4. **Permission Denied**: Verify service principal has UC function permissions

## Resources

- [Databricks Agents Documentation](https://docs.databricks.com/en/generative-ai/agents.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [MLflow Tracing](https://mlflow.org/docs/latest/tracing/)

## License

Based on Projeto6 from Data Science Academy - www.datascienceacademy.com.br
