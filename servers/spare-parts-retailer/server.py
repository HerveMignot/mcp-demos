from fastmcp import FastMCP
from catalog import SPARE_PARTS_CATALOG

mcp = FastMCP("Automotive Spare Parts Retailer")

@mcp.tool()
def check_availability(part_type: str, car_model: str) -> str:
    """Check the availability of a certain type of spare part for a specific car model."""
    available_parts = []
    for part in SPARE_PARTS_CATALOG:
        if part["type"].lower() == part_type.lower() and part["compatibility"]["model"].lower() == car_model.lower():
            available_parts.append(part)
    
    if not available_parts:
        return f"No {part_type} found for {car_model}."
    
    response = f"Available {part_type} for {car_model}:\n"
    for part in available_parts:
        response += f"- {part['name']} (Ref: {part['reference_id']}, Stock: {part['stock']})\n"
    return response

@mcp.tool()
def get_part_details(reference_id: str) -> str:
    """Get detailed information about a spare part using its reference ID."""
    for part in SPARE_PARTS_CATALOG:
        if part["reference_id"] == reference_id:
            return (
                f"Details for {part['name']}:\n"
                f"- Reference ID: {part['reference_id']}\n"
                f"- Type: {part['type']}\n"
                f"- Compatibility: {part['compatibility']['model']} ({part['compatibility']['start_year']} - {part['compatibility']['end_year']})\n"
                f"- Stock: {part['stock']}"
            )
    return f"Part with reference ID {reference_id} not found."

@mcp.prompt()
def get_customer_id() -> str:
    """Please provide your customer ID to proceed with the order."""
    # In a real scenario, this would involve a user prompt.
    # For this demo, we can't actually prompt the user, so we'll have to imagine it.
    pass

@mcp.tool()
def order_part(reference_id: str, customer_id: str) -> str:
    """Order a spare part by its reference ID for a given customer ID. The part must be in stock."""
    for part in SPARE_PARTS_CATALOG:
        if part["reference_id"] == reference_id:
            if part["stock"] > 0:
                part["stock"] -= 1  # Decrement stock
                return f"Order successful! Part {part['name']} (Ref: {reference_id}) has been ordered for customer {customer_id}. New stock level: {part['stock']}."
            else:
                return f"Error: Part {part['name']} (Ref: {reference_id}) is out of stock."
    return f"Part with reference ID {reference_id} not found."

def run():
    """Runs the MCP server."""
    mcp.run()


if __name__ == "__main__":
    mcp.run()
