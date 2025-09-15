import os
import asyncio
import json
import argparse
import logging

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.mcp import MCPStdioPlugin

from dotenv import load_dotenv
load_dotenv()

#logging.basicConfig(level=logging.DEBUG)

# --- 0) Parse command-line arguments and load configuration ---
parser = argparse.ArgumentParser()
parser.add_argument('--config', default='agent_config.json', help='Path to the configuration file.')
cli_args = parser.parse_args()

with open(cli_args.config, 'r') as config_file:
    config = json.load(config_file)

mcp_plugin_config = config['mcp_plugin']
chat_agent_config = config['chat_agent']


# --- 1) Build a Kernel with OpenAI Chat Completion ---
kernel = Kernel()
kernel.add_service(
    AzureChatCompletion(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  # optional
        )
)

async def main():
    # --- 2) Create an MCP client---

    async with MCPStdioPlugin(
        name=mcp_plugin_config['name'],
        command=mcp_plugin_config['command'],
        args=mcp_plugin_config['args'],
    ) as mcp_plugin:

        # NOTE: In Python SK, MCP plugins are consumed directly by agents or kernels.
        # You usually don't need to manually ‘convert’ tools; the plugin exposes tools to the agent.

        # --- 3+4) Add the MCP plugin to an Agent (tools become callable) ---
        agent = ChatCompletionAgent(
            name=chat_agent_config['name'],
            instructions=chat_agent_config['instructions'],
            # The agent uses the chat completion service from the kernel by default
            kernel=kernel,
            service=None,  # or set a specific service; leaving None uses what's in the kernel
            plugins=[mcp_plugin],
        )

        # --- 5) Invoke with automatic function calling enabled ---
        exec_settings = AzureChatPromptExecutionSettings(
            temperature=0.0,
        )

        print(f"Enter your question to the {chat_agent_config['name']} (type 'quit' or 'exit' to stop):")
        while True:
            question = input("> ").strip()
            if question.lower() in ("quit", "exit"):
                print("Exiting.")
                break

            args = KernelArguments(settings=exec_settings)
            response_stream = agent.invoke(question, arguments=args)
            response = None
            async for msg in response_stream:
                response = msg  # keep last
            print(f"\nResponse from the {chat_agent_config['name']}:\n", response.content if response else "(no content)")
            print("\nAsk another question or type 'quit' to exit.")

if __name__ == "__main__":
    asyncio.run(main())