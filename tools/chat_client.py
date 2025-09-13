import argparse
import json
import os
import asyncio
from openai import AzureOpenAI
from mcp.client.aio import Client, Tool

async def main():
    """Main function to run the MCP client and chat with the Azure AI LLM."""
    parser = argparse.ArgumentParser(description="MCP Client for Azure AI Chat")
    parser.add_argument("config_file", help="Path to the JSON config file with server URLs.")
    args = parser.parse_args()

    # --- 1. Load Configuration ---
    try:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
            server_urls = config.get("servers", [])
        if not server_urls:
            print(f"Error: No servers found in {args.config_file}")
            return
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing config file: {e}")
        return

    # --- 2. Connect to MCP Servers ---
    mcp_client = Client()
    for url in server_urls:
        try:
            await mcp_client.connect(url)
            print(f"Successfully connected to MCP server at {url}")
        except Exception as e:
            print(f"Failed to connect to MCP server at {url}: {e}")
    
    tools = await mcp_client.get_tools()
    if not tools:
        print("No tools found on any connected MCP server.")

    # --- 3. Setup Azure AI Client ---
    try:
        azure_endpoint = os.environ["AZURE_AI_ENDPOINT"]
        azure_api_key = os.environ["AZURE_AI_API_KEY"]
        azure_model_name = os.environ["AZURE_AI_MODEL_NAME"]
    except KeyError as e:
        print(f"Error: Missing environment variable {e}. Please set AZURE_AI_ENDPOINT, AZURE_AI_API_KEY, and AZURE_AI_MODEL_NAME.")
        return

    azure_llm_client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version="2024-02-01", # Adjust if necessary
    )

    # --- 4. Chat Loop ---
    print("\n--- MCP Chat Client ---")
    print("Type 'exit' to end the conversation.")
    
    messages = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = azure_llm_client.chat.completions.create(
                model=azure_model_name,
                messages=messages,
                tools=[tool.to_openai() for tool in tools],
                tool_choice="auto",
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"LLM wants to call tool: {function_name} with args: {function_args}")

                    # Find and execute the tool
                    tool_to_run = next((t for t in tools if t.name == function_name), None)
                    if tool_to_run:
                        result = await tool_to_run.run(**function_args)
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": str(result),
                            }
                        )
                    else:
                        print(f"Error: Tool '{function_name}' not found.")
                
                # Get the final response from the LLM after tool execution
                second_response = azure_llm_client.chat.completions.create(
                    model=azure_model_name,
                    messages=messages,
                )
                final_message = second_response.choices[0].message.content
                print(f"AI: {final_message}")
                messages.append({"role": "assistant", "content": final_message})
            else:
                ai_message = response_message.content
                print(f"AI: {ai_message}")
                messages.append({"role": "assistant", "content": ai_message})

        except Exception as e:
            print(f"An error occurred: {e}")
            messages.pop() # Remove the user message that caused the error

    await mcp_client.close()
    print("Client shut down.")

if __name__ == "__main__":
    asyncio.run(main())
