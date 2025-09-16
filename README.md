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

The `tools` folder contains a chat client (`sk_chat_client.py`) that uses the [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) to interact with MCP servers.

The client is configured via a JSON file passed as a command-line argument, and it can connect to both local (`stdio`) and remote (`http`) MCP servers.

### Prerequisites

Before running the client, you need to create a `.env` file in the `tools` directory with your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="your_deployment_name"
AZURE_OPENAI_ENDPOINT="your_endpoint"
AZURE_OPENAI_API_VERSION="your_api_version"
```

### Configuration

The chat client uses a JSON configuration file to set up the MCP plugin and the chat agent. The `type` field in the `mcp_plugin` section determines whether to connect to a local server (`stdio`) or a remote one (`http`).

Example configuration files are provided in the `tools` directory:

*   **`agent_config_stdio.json`**: Connects to a local server as a subprocess.
    ```json
    {
      "mcp_plugin": {
        "type": "stdio",
        "name": "SparePartsRetailer",
        "command": "fastmcp",
        "args": ["run", "servers/spare-parts-retailer/server.py"]
      },
      "chat_agent": {
        "name": "CatalogAgent",
        "instructions": "Answer questions about Spare Part Availability."
      }
    }
    ```

*   **`agent_config_http.json`**: Connects to a remote server over HTTP.
    ```json
    {
      "mcp_plugin": {
        "type": "http",
        "name": "RemoteServer",
        "url": "http://localhost:8000/mcp"
      },
      "chat_agent": {
        "name": "RemoteAgent",
        "instructions": "Interact with the remote server."
      }
    }
    ```

### Running the Client

To run the chat client, execute the following command from the root of the repository, passing the path to your desired configuration file.

**To connect to a local server (stdio):**
```bash
python tools/sk_chat_client.py --config tools/agent_config_stdio.json
```

**To connect to a remote server (http):**
```bash
python tools/sk_chat_client.py --config tools/agent_config_http.json
``` 
