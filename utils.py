import re

from rapidfuzz import fuzz


def find_best_matches(search_term, items, threshold=90):
    # Remove anything inside parentheses for a cleaner 
    # comparison (to avoid lower match percentage when 
    # editions and language tags are included in parenthesis)
    cleaned_query = re.sub(r'\s*\([^)]*\)', '', search_term).strip()
    matched_items = []

    for item in items:
        # Remove anything inside parentheses for the item name
        cleaned_name = re.sub(r'\s*\([^)]*\)', '', item['name']).strip()

        # Compare cleaned names with a fuzzy matching ratio
        score = fuzz.ratio(cleaned_query.lower(), cleaned_name.lower())

        if score >= threshold:
            matched_items.append(item)

    return matched_items
