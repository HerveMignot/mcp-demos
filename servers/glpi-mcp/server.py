import base64
import os
import requests

from dotenv import load_dotenv

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

load_dotenv()
GLPI_TOKEN_API = os.getenv("GLPI_TOKEN_API", "")

mcp = FastMCP("GLPI MCP Server")

# In-memory session storage (for demonstration purposes)
# In a production environment, use a more persistent storage
SESSIONS = {}
GLPI_URL = "http://localhost/glpi"  # Default GLPI URL, can be overridden on login

def get_glpi_url():
    """Returns the GLPI URL."""
    if not GLPI_URL:
        raise Exception("GLPI URL not set. Please login first.")
    return GLPI_URL

def get_session_token():
    """Returns the session token."""
    if "glpi_session_token" not in SESSIONS:
        raise Exception("Not logged in to GLPI. Please login first.")
    #mcp.log(f"Using MCP session id: {mcp.session_id()}")
    return SESSIONS["glpi_session_token"]


def get_headers(include_app_token: bool = True) -> dict:
    """Returns the headers for GLPI API calls."""
    headers = {
        "Content-Type": "application/json",
        "Session-Token": get_session_token(),
    }
    if include_app_token:
        headers["App-Token"] = GLPI_TOKEN_API
    return headers


@mcp.tool()
def glpi_login(glpi_url: str, username: str, password: str, app_token: str = GLPI_TOKEN_API) -> dict:
    """
    Logs in to GLPI using username and password to obtain a session token for subsequent API calls.

    This tool authenticates the user against the GLPI API and stores the session token in memory.
    The session token is then automatically used by other tools in this module.

    Args:
        glpi_url (str): The base URL of the GLPI instance (e.g., 'http://your-glpi-server.com').
        username (str): The GLPI username to authenticate with.
        password (str): The password for the GLPI user.
        app_token (str): The App-Token for the GLPI API. Can be found in Setup > General > API.
    """
    global GLPI_URL
    GLPI_URL = glpi_url
    # Encode username and password in base64
    auth_str = f"{username}:{password}"
    base64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "App-Token": app_token,
        "Authorization": f"Basic {base64_auth_str}",
    }
    try:
        response = requests.get(f"{glpi_url}/apirest.php/initSession", headers=headers)
        response.raise_for_status()
        session_token = response.json()["session_token"]
        # Store the session token in memory
        SESSIONS["glpi_session_token"] = session_token
        return {'status': "Successfully logged in to GLPI.", 'Session token': session_token}
    except requests.exceptions.RequestException as e:
        raise ToolError(f"Error logging in to GLPI: {e}")


@mcp.tool()
def glpi_logout() -> str:
    """
    Logs out from the current GLPI session and invalidates the session token.

    This tool should be called when the user has finished interacting with the GLPI API
    to ensure the session is properly closed.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        response = requests.get(f"{glpi_url}/apirest.php/killSession", headers=headers)
        response.raise_for_status()
        # Remove the session token from memory
        del SESSIONS["glpi_session_token"]
        return "Successfully logged out from GLPI."
    except Exception as e:
        raise ToolError(f"Error logging out from GLPI: {e}")


@mcp.tool()
def glpi_get_ticket(ticket_id: int) -> dict:
    """
    Retrieves detailed information about a specific ticket from GLPI.

    Args:
        ticket_id (int): The unique identifier for the ticket to retrieve.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        print(headers)
        response = requests.get(f"{glpi_url}/apirest.php/Ticket/{ticket_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ToolError(f"Error getting ticket: {e}")


@mcp.tool()
def glpi_list_tickets() -> list[dict]:
    """
    Retrieves a list of all tickets from GLPI.

    This tool returns a list of all tickets accessible by the authenticated user.
    The list can be long, so it may be useful to filter the results.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        response = requests.get(f"{glpi_url}/apirest.php/Ticket/", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ToolError(f"Error listing tickets: {e}")


@mcp.tool()
def glpi_create_ticket(title: str, content: str) -> dict:
    """
    Creates a new ticket in GLPI with a title and content.

    Args:
        title (str): The title of the new ticket.
        content (str): The main content or description of the ticket.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        data = {
            "input": {
                "name": title,
                "content": content,
            }
        }
        response = requests.post(f"{glpi_url}/apirest.php/Ticket", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ToolError(f"Error creating ticket: {e}")

@mcp.tool()
def glpi_update_ticket(ticket_id: int, title: str = None, content: str = None) -> dict:
    """
    Updates the title and/or content of an existing ticket in GLPI.

    Args:
        ticket_id (int): The unique identifier for the ticket to update.
        title (str, optional): The new title for the ticket. Defaults to None.
        content (str, optional): The new content for the ticket. Defaults to None.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        data = {
            "input": {}
        }
        if title:
            data["input"]["name"] = title
        if content:
            data["input"]["content"] = content
        
        if not data["input"]:
            return "Nothing to update."

        response = requests.put(f"{glpi_url}/apirest.php/Ticket/{ticket_id}", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ToolError(f"Error updating ticket: {e}")


@mcp.tool()
def glpi_add_ticket_followup(ticket_id: int, content: str) -> dict:
    """
    Adds a follow-up message to an existing ticket in GLPI.

    This is useful for adding comments, updates, or replies to a ticket.

    Args:
        ticket_id (int): The unique identifier for the ticket to add a follow-up to.
        content (str): The content of the follow-up message.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        data = {
            "input": {
                "itemtype": "Ticket",
                "items_id": ticket_id,
                "content": content,
            }
        }
        response = requests.post(f"{glpi_url}/apirest.php/ITILFollowup", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ToolError(f"Error adding followup to ticket: {e}")


@mcp.tool()
def glpi_solve_ticket(ticket_id: int) -> dict:
    """
    Marks a ticket in GLPI as solved.

    This changes the status of the ticket to 'solved'.

    Args:
        ticket_id (int): The unique identifier for the ticket to mark as solved.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        data = {
            "input": {
                "id": ticket_id,
                "status": 4, # Solved
            }
        }
        response = requests.put(f"{glpi_url}/apirest.php/Ticket/{ticket_id}", headers=headers, json=data)
        response.raise_for_status()
        return response..json()
    except Exception as e:
        raise ToolError(f"Error solving ticket: {e}")


@mcp.tool()
def glpi_close_ticket(ticket_id: int) -> dict:
    """
    Marks a ticket in GLPI as closed.

    This changes the status of the ticket to 'closed'.

    Args:
        ticket_id (int): The unique identifier for the ticket to mark as closed.
    """
    try:
        glpi_url = get_glpi_url()
        headers = get_headers()
        data = {
            "input": {
                "id": ticket_id,
                "status": 5, # Closed
            }
        }
        response = requests.put(f"{glpi_url}/apirest.php/Ticket/{ticket_id}", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise ToolError(f"Error closing ticket: {e}")


def run():
    """Runs the MCP server."""
    mcp.run()

if __name__ == "__main__":
    mcp.run()
