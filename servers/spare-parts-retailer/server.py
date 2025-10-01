from fastmcp import FastMCP
from catalog import SPARE_PARTS_CATALOG
from fuzzywuzzy import fuzz, process

mcp = FastMCP("Automotive Spare Parts Retailer")

FUZZY_MATCH_THRESHOLD = 75 # Define a threshold for fuzzy matching

@mcp.tool()
def check_availability(part_type: str, car_model: str, language: str = "en") -> str:
    """Check the availability of a certain type of spare part for a specific car model."""
    available_parts = []

    # Collect all possible translated part types and car models for fuzzy matching
    all_part_types_translated = []
    all_car_models_translated = []
    for part in SPARE_PARTS_CATALOG:
        if language in part.get("translations", {}):
            all_part_types_translated.append(part["translations"][language]["type"])
            all_car_models_translated.append(part["translations"][language]["model"])
        else: # Fallback to English if translation not available
            all_part_types_translated.append(part["type"])
            all_car_models_translated.append(part["compatibility"]["model"])

    # Remove duplicates for fuzzy matching efficiency
    all_part_types_translated = list(set(all_part_types_translated))
    all_car_models_translated = list(set(all_car_models_translated))

    # Fuzzy match the input part_type and car_model
    matched_part_type_info = process.extractOne(part_type, all_part_types_translated, scorer=fuzz.token_set_ratio)
    matched_car_model_info = process.extractOne(car_model, all_car_models_translated, scorer=fuzz.token_set_ratio)

    best_matched_part_type = matched_part_type_info[0] if matched_part_type_info and matched_part_type_info[1] >= FUZZY_MATCH_THRESHOLD else None
    best_matched_car_model = matched_car_model_info[0] if matched_car_model_info and matched_car_model_info[1] >= FUZZY_MATCH_THRESHOLD else None

    if not best_matched_part_type or not best_matched_car_model:
        # If no good fuzzy match, return no parts found
        return f"No {part_type} found for {car_model}."


    for part in SPARE_PARTS_CATALOG:
        part_type_in_catalog = part["translations"].get(language, {}).get("type", part["type"])
        car_model_in_catalog = part["translations"].get(language, {}).get("model", part["compatibility"]["model"])

        # Compare against the best fuzzy matched types and models
        if fuzz.token_set_ratio(best_matched_part_type, part_type_in_catalog) >= FUZZY_MATCH_THRESHOLD and \
           fuzz.token_set_ratio(best_matched_car_model, car_model_in_catalog) >= FUZZY_MATCH_THRESHOLD:
            available_parts.append(part)

    if not available_parts:
        return f"No {part_type} found for {car_model}."

    response = f"Available {part_type} for {car_model}:\n"
    for part in available_parts:
        # Use translated names for display
        display_name = part["translations"].get(language, {}).get("name", part["name"])
        response += f"- {display_name} (Ref: {part['reference_id']}, Stock: {part['stock']})\n"
    return response

@mcp.tool()
def get_part_details(reference_id: str) -> str:
    """Get detailed information about a spare part using its reference ID."""
    for part in SPARE_PARTS_CATALOG:
        if part["reference_id"] == reference_id:
            return (
                f"Details for {part['name']}:\n"
                f"- Reference ID: {part['reference_id']}:\n"
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