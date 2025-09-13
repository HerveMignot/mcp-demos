import os
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.mcp import MCPStdioPlugin

from dotenv import load_dotenv
load_dotenv()


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
        name="SparePartsRetailer",
        command="uv",
        args=["run", "--with", "mcp", "mcp", "run", "..\\servers\\spare-parts-retailer\\main.py"], # --with mcp mcp run main.py
    ) as catalog_plugin:

        # NOTE: In Python SK, MCP plugins are consumed directly by agents or kernels.
        # You usually don't need to manually “convert” tools; the plugin exposes tools to the agent.

        # --- 3+4) Add the MCP plugin to an Agent (tools become callable) ---
        agent = ChatCompletionAgent(
            name="CatalogAgent",
            instructions="Answer questions about Spare Part Availability.",
            # The agent uses the chat completion service from the kernel by default
            kernel=kernel,
            service=None,  # or set a specific service; leaving None uses what's in the kernel
            plugins=[catalog_plugin],
        )

        # --- 5) Invoke with automatic function calling enabled ---
        exec_settings = AzureChatPromptExecutionSettings(
            temperature=0.0,
        )

        print("Enter your question (type 'quit' or 'exit' to stop):")
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
            print("\nResponse from the Catalog Agent:\n", response.content if response else "(no content)")
            print("\nAsk another question or type 'quit' to exit.")

asyncio.run(main())
