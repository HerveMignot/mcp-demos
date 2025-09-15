# MCP Servers Demos

This repository contains a set of MCP (Model Context Protocol) servers to demonstrate the principles of MCP. These servers can be run locally or deployed online.

## Servers

The `servers` folder contains the following demo servers:

### Sample Demo

A simple MCP server with a single `hello` tool.

**To run this server:**

```bash
cd servers/sample-demo
fastmcp run server.py
```

### Spare Parts Retailer

A more complex MCP server that simulates a spare parts retailer. It has tools to check availability, get part details, and order parts.

**To run this server:**

```bash
cd servers/spare-parts-retailer
fastmcp run server.py
```

### Debugging with MCP Inspector

FastMPC comes with a MCP Inspector tool: a webapp allowing to test the MCP Server.

Follow instructions provided to use this web application (use Connect button to discuss with the MCP Server).

```bash
cd servers/spare-parts-retailer
fastmcp dev server.py
```
PS: make sure to use `server.py` and not `.\\server.py` on Windows.


## Testing with the Semantic Kernel Chat Client

The `tools` folder contains a chat client (`sk_chat_client.py`) that uses the [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) to interact with the MCP servers.

The client is configured via a JSON file passed as a command-line argument.

### Prerequisites

Before running the client, you need to create a `.env` file in the `tools` directory with your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="your_deployment_name"
AZURE_OPENAI_ENDPOINT="your_endpoint"
AZURE_OPENAI_API_VERSION="your_api_version"
```

### Configuration

The chat client requires a JSON configuration file to set up the MCP plugin and the chat agent. Here is an example `agent_config.json` file:

```json
{
  "mcp_plugin": {
    "name": "SparePartsRetailer",
    "command": "fastmcp",
    "args": ["run", "..\\servers\\spare-parts-retailer\\server.py"]
  },
  "chat_agent": {
    "name": "CatalogAgent",
    "instructions": "Answer questions about Spare Part Availability."
  }
}
```

### Running the Client

To run the chat client, execute the following command from the root of the repository, passing the path to your configuration file:

```bash
cd tools
python ./sk_chat_client.py --config ../servers/<your-server>/agent_config.json
```

The client will start the MCP server specified in the configuration file in the background and you will be prompted to ask questions to the chat agent.

**Remark**: Make sure to start the chat client from a directory such that any path in the agent configuration json is valid.
In the example above, the path to the main server is correct if configuration file is read from the tools directory.
```bash
python .\sk_chat_client.py --config ..\servers\spare-parts-retailer\agent_config.json
```` 
