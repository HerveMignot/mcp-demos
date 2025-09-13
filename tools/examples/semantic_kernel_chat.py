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
    # If you omit these, the class also reads from env vars / .env
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  # optional
        )
)

async def main():
    # --- 2) Create an MCP client (GitHub server via npx stdio) ---
    # Requires Node + npx and the GitHub MCP server package
    # If you have a GitHub PAT, pass it via env to the server (optional for read-only queries).
    env = {}
    if os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"):
        env["GITHUB_PERSONAL_ACCESS_TOKEN"] = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    async with MCPStdioPlugin(
        name="GitHub",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env=env or None,
    ) as github_plugin:

        # NOTE: In Python SK, MCP plugins are consumed directly by agents or kernels.
        # You usually don't need to manually “convert” tools; the plugin exposes tools to the agent.

        # --- 3+4) Add the MCP plugin to an Agent (tools become callable) ---
        agent = ChatCompletionAgent(
            name="GitHubAgent",
            instructions="Answer questions about GitHub repositories.",
            # The agent uses the chat completion service from the kernel by default
            kernel=kernel,
            service=None,  # or set a specific service; leaving None uses what's in the kernel
            plugins=[github_plugin],
        )

        # --- 5) Invoke with automatic function calling enabled ---
        exec_settings = AzureChatPromptExecutionSettings(
            temperature=0.0,
            # In Python SK, function choice is automatic when plugins expose tools;
            # you can still pass settings via KernelArguments if desired.
        )

        question = "Summarize the last four commits to the microsoft/semantic-kernel repository?"
        args = KernelArguments(settings=exec_settings)

        # Use the agent to let the LLM call MCP tools as needed
        response_stream = agent.invoke(question, arguments=args)
        response = None
        async for msg in response_stream:
            response = msg  # keep last
        print("\n\nResponse from GitHubAgent:\n", response.content if response else "(no content)")

        # --- (Optional) Kernel-only prompt invocation with function-calling ---
        # If you prefer not to create an Agent, you can attach the plugin to the kernel, too:
        # kernel.plugins.append(github_plugin)
        # result = await kernel.invoke_prompt(
        #     prompt=question,
        #     arguments=KernelArguments(settings=exec_settings),
        # )
        # print("\n\nKernel invoke_prompt result:\n", result)

asyncio.run(main())
