import random
import spacy
from .models import Place, VisitedPlace

nlp = spacy.load("en_core_web_sm")

def parse_query(query):
    doc = nlp(query)
    keywords = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    results = []

    for place in Place.objects.all():
        match_score = len(set(keywords) & set(place.keywords))
        if match_score > 0:
            results.append((place, match_score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [place for place, _ in results[:5]]

def get_dynamic_suggestion_message(place, user_xp):
    messages = [
        f"{place.name} is now unlocked! Ready for your next adventure?",
        f"Hey! You can now visit {place.name}. Don’t miss out!",
        f"Explore {place.name}! It’s waiting for you.",
        f"{place.name} unlocked! Time to plan your trip!",
    ]
    if user_xp < place.xp_unlock:
        messages = [
            f"{place.name} will unlock when you reach {place.xp_unlock} XP. Keep exploring!",
            f"Almost there! Visit more places to unlock {place.name}.",
            f"Get {place.xp_unlock - user_xp} more XP to unlock {place.name}!",
        ]
    return random.choice(messages)

def get_smart_suggestions(user):
    visited_ids = set(VisitedPlace.objects.filter(user=user).values_list("place_id", flat=True))
    user_xp = user.profile.xp
    unvisited_places = Place.objects.exclude(id__in=visited_ids)

    suggestions = []

    # Prioritize special places
    important_places = Place.objects.filter(name__icontains="Main Library")
    for place in important_places:
        if place.id not in visited_ids:
            suggestions.append(f"You haven’t checked out the {place.name} yet. Wanna go there?")

    # Suggest newly unlocked places
    newly_unlocked = [p for p in unvisited_places if user_xp >= p.xp_unlock]
    random.shuffle(newly_unlocked)  # Shuffle to keep variety

    for place in newly_unlocked:
        if len(suggestions) >= 3:
            break
        suggestions.append(get_dynamic_suggestion_message(place, user_xp))

    # If not enough suggestions, encourage visiting other places
    if len(suggestions) < 3:
        still_locked = [p for p in unvisited_places if user_xp < p.xp_unlock]
        still_locked_sorted = sorted(still_locked, key=lambda p: p.xp_unlock)
        for place in still_locked_sorted:
            if len(suggestions) >= 3:
                break
            suggestions.append(get_dynamic_suggestion_message(place, user_xp))

    return suggestions[:3]
