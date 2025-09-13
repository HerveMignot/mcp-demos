# MCP Servers Demos

This repository contains a set of MCP (Model Context Protocol) servers to demonstrate the principles of MCP. These servers can be run locally or deployed online.

## Servers

The `servers` folder contains the following demo servers:

### Sample Demo

A simple MCP server with a single `hello` tool.

**To run this server:**

```bash
python -m servers.sample-demo.main
```

### Spare Parts Retailer

A more complex MCP server that simulates a spare parts retailer. It has tools to check availability, get part details, and order parts.

**To run this server:**

```bash
python -m servers.spare-parts-retailer.main
```

## Testing with the Semantic Kernel Chat Client

The `tools` folder contains a chat client (`sk_chat_client.py`) that uses the [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) to interact with the MCP servers.

This client is configured to automatically start and connect to the **Spare Parts Retailer** server.

### Prerequisites

Before running the client, you need to create a `.env` file in the `tools` directory with your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="your_deployment_name"
AZURE_OPENAI_ENDPOINT="your_endpoint"
AZURE_OPENAI_API_VERSION="your_api_version"
```

### Running the Client

To run the chat client, execute the following command from the root of the repository:

```bash
python tools/sk_chat_client.py
```

The client will start the `spare-parts-retailer` server in the background and you will be prompted to ask questions to the chat agent.