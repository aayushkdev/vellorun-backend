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
            "id": place["id"],
            "name": place["name"],
            "description": place["description"],
            "visits": place["visits"],
            "is_match": place.get("category") in selected_categories,
        }
        for place in data
        if place.get("approved", False)
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
                f"You are given a list of places with their names, descriptions, and whether they match the user's interests:\n\n"
                f"{json.dumps(filtered_places)}\n\n"
                f"From these, select {num_recommendations} of the most interesting or important places. "
                f"Prioritize places where 'is_match' is true (i.e., they match the user's interests), but if none exist, pick the best available based on other factors.\n"
                "Only return a comma-separated string of place IDs (integers). No extra text."
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
        
        if completion and completion.choices:
            return completion.choices[0].message.content
        else:
            raise Exception("No valid response received from the LLM")
    
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"