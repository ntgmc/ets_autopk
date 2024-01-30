import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(text1, text2):
    # 使用 jieba 分词
    words1 = ' '.join(jieba.cut(text1))
    words2 = ' '.join(jieba.cut(text2))

    vectorizer = CountVectorizer().fit_transform([words1, words2])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))
    
    return similarity[0][0]

def calculate_jaccard_similarity(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity = intersection / union
    return similarity


# 示例
text1 = "我喜欢学习Python编程"
text2 = "学习编程很有趣"

similarity_score = calculate_cosine_similarity(text1, text2)
print(f"相似度：{similarity_score}")
