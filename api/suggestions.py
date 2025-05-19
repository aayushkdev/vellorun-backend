
import json
from openai import OpenAI

def get_place_recommendations(data, selected_categories, api_key, model="meta-llama/llama-3.3-8b-instruct:free", num_recommendations=3):
    """
    Get place recommendations based on selected categories using an LLM.
    
    Args:
        data (list): List of place dictionaries with at least _id, name, description, isActive, and category fields
        selected_categories (list): List of category names to filter places by
        api_key (str): Your OpenRouter API key
        model (str): The LLM model to use for recommendations
        num_recommendations (int): Number of recommendations to request
        
    Returns:
        str: The LLM's recommendation response
        
    Raises:
        Exception: If there's an issue with the API call or no valid response is received
    """
    # Filter active places by selected categories
    filtered_places = [
        {
            "id": place["_id"],
            "name": place["name"],
            "description": place["description"]
        }
        for place in data
        if place.get("isActive", False) and place.get("category") in selected_categories
    ]
    
    # Check if we have places to recommend
    if not filtered_places:
        return f"No active places found in the selected categories: {', '.join(selected_categories)}"
    
    # Build the messages for the LLM
    messages = [
        {
            "role": "system",
            "content": "You are a campus guide assistant."
        },
        {
            "role": "user",
            "content": (
                f"Given the following places: {json.dumps(filtered_places)}\n\n"
                f"Suggest {num_recommendations} must-visit places based on these tags: {', '.join(selected_categories)}.\n"
                "Return a short reason for each."
            )
        }
    ]
    
    # Initialize OpenAI client with OpenRouter base URL
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        # Send request to the LLM
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        # Check and return the response
        if completion and completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content
        else:
            raise Exception("No valid response received from the LLM")
    
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"


# Example Usage
# # Your API key here
    api_key = "API_KEY"

    # Get recommendations
    result = get_place_recommendations(
        data="your dataset variable",
        selected_categories=["Food"],
        api_key=api_key
    )



# print(result)

# to segregate categories you can use this py script
# # Step 1: Get unique categories
    categories = sorted({place['category'] for place in data})
    print("Available categories:")
    for cat in categories:
        print("-", cat)

    # Step 2: User selects one or more categories
    selected = input("Enter one or more categories separated by commas: ").strip().split(",")
    selected = [cat.strip() for cat in selected]

    # Step 3: Filter places based on selected categories and isActive
    filtered = [
        {
            "id": place["_id"],
            "name": place["name"],
            "description": place["description"]
        }
        for place in data
        if place["category"] in selected and place["isActive"]
    ]