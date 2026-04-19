# Databricks Agent Project

AI Agent application built with LangGraph, Databricks Agents, and MLflow Tracing.

## Overview

This project demonstrates how to build and deploy AI agents on Databricks using:
- **LangGraph**: Agent orchestration with tool calling
- **Databricks Agents**: Framework for agent deployment
- **MLflow Tracing**: Observability and debugging
- **Unity Catalog Functions**: Tool integration

Based on Projeto6.ipynb from Data Science Academy.

## Project Structure

```
databricks-agent-project/
├── app.yaml               # Databricks Apps configuration
├── databricks.yaml        # Databricks Asset Bundle configuration
├── app.py                 # Main agent application (LangGraph + MLflow)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── notebooks/             # Jupyter notebooks for development
│   └── Projeto6.ipynb     # Original notebook from DSA
├── src/                   # Python source code modules
└── resources/             # Databricks resources
```

## Features

- **LangGraph Agent**: Tool-calling agent with conditional routing
- **MLflow Tracing**: Full observability with autologging
- **Unity Catalog Tools**: Integration with UC functions (e.g., `system.ai.python_exec`)
- **ChatDatabricks**: LLM integration with Databricks model endpoints
- **Streaming Support**: Both predict and predict_stream modes

## Prerequisites

- Databricks workspace with Unity Catalog enabled
- Model serving endpoint configured (e.g., `databricks-meta-llama-3-3-70b-instruct`)
- Appropriate permissions for UC functions
- Databricks CLI installed and configured

## Setup

1. **Configure Environment Variables**

```bash
export LLM_ENDPOINT_NAME="databricks-meta-llama-3-3-70b-instruct"
export UC_TOOL_NAMES="system.ai.python_exec"
export MLFLOW_EXPERIMENT_NAME="/databricks-agent-project"
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Deploy to Databricks Workspace**

```bash
# Sync files to workspace
databricks sync . /Workspace/Users/your-email/databricks-agent-project

# Deploy the app
databricks apps deploy databricks-agent-project \
  --source-code-path /Workspace/Users/your-email/databricks-agent-project
```

## Agent Architecture

### Components

1. **LLM**: ChatDatabricks with model endpoint
2. **Tools**: Unity Catalog functions (UCFunctionToolkit)
3. **Agent Graph**: LangGraph StateGraph with conditional routing
4. **MLflow Integration**: Autologging and tracing enabled

### Agent Flow

```
User Message → Agent Node → Tool Calls? 
                         ↓ Yes
                    Tools Node → Agent Node → Response
                         ↓ No
                    END
```

## Development

### Running Locally

```bash
# Run the app locally with Databricks Connect
databricks apps run-local --prepare-environment --debug

# Or run directly
python app.py
```

### Testing the Agent

```python
from app import main

agent = main()

# Test predict
response = agent.predict({
    "messages": [{"role": "user", "content": "Oi. Testando!"}]
})
print(response.messages[-1].content)

# Test streaming
for chunk in agent.predict_stream({
    "messages": [{"role": "user", "content": "Explique o que é Tesouro Direto"}]
}):
    print(chunk.delta.content, end="")
```

### MLflow Tracing

Tracing is automatically enabled via:
- `mlflow.langchain.autolog()`: Logs LangChain operations
- `mlflow.databricks.enable_tracing()`: Databricks-specific tracing

View traces in MLflow Experiments under `/databricks-agent-project`.

## Deployment

### Deploy with Databricks Apps CLI

```bash
# Create app
databricks apps create databricks-agent-project

# Deploy from workspace
databricks apps deploy databricks-agent-project \
  --source-code-path /Workspace/Users/your-email/databricks-agent-project \
  --mode AUTO_SYNC

# Get app status
databricks apps get databricks-agent-project
```

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

### App Logs

View logs in the Databricks workspace under Apps > databricks-agent-project > Logs.

## Troubleshooting

### Common Issues

1. **UC Function Not Found**: Verify `UC_TOOL_NAMES` are correct and accessible
2. **Model Endpoint Not Ready**: Check endpoint status in Model Serving
3. **MLflow Tracing Not Working**: Ensure MLflow experiment exists
4. **Permission Denied**: Verify service principal has UC function permissions

### Debug Mode

Enable debug logging:

```bash
export MLFLOW_TRACING=true
export MLFLOW_TRACE_SAMPLING_RATIO=1.0
python app.py
```

## Resources

- [Databricks Agents Documentation](https://docs.databricks.com/en/generative-ai/agents.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [MLflow Tracing](https://mlflow.org/docs/latest/tracing/)
- [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)

## License

Based on Projeto6 from Data Science Academy - www.datascienceacademy.com.br
