def calculate_jaccard_similarity(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity = intersection / union
    return similarity

text1 = "This is an example sentence."
text2 = "This is a different example sentence."

jaccard_similarity_score = calculate_jaccard_similarity(text1, text2)
print(f"Jaccard Similarity: {jaccard_similarity_score}")
