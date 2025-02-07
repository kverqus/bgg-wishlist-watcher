from rapidfuzz import process, fuzz


def find_best_matches(search_term, items):
    names = [item['name'] for item in items]

    matches = process.extract(search_term, names, scorer=fuzz.ratio)
    max_score = max(matches, key=lambda x: x[1])[1]

    return [items[names.index(match[0])] for match in matches if match[1] == max_score]
