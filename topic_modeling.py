# %%
import json
import re
import string
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords


nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

with open("texts.json", "r", encoding="utf-8") as f:
    docs = json.load(f)


def preprocess_text(doc):
    doc = doc.lower()  # Lowercase
    doc = re.sub(r"https?://\S+|www\.\S+", "", doc)  # Remove URLs
    doc = doc.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    doc = re.sub(r"\s+", " ", doc).strip()  # Remove extra whitespace

    # Tokenize and remove stop words
    tokens = doc.split()
    tokens = [w for w in tokens if w not in stop_words]

    # Reconstruct the string after removing stopwords
    doc = " ".join(tokens)
    return doc


docs = [preprocess_text(d) for d in docs if isinstance(d, str) and len(d.strip()) > 0]

# %%
embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")

topic_model = BERTopic(language="multilingual", embedding_model=embedding_model)
topics, probs = topic_model.fit_transform(docs)

topic_model.reduce_topics(docs, nr_topics=50)

# %%
topic_info = topic_model.get_topic_info()
print(topic_info.head(10))

# %%
topic_words = topic_model.get_topic(0)  # 토픽 0의 대표 단어와 스코어
print(topic_words)

# %%
fig = topic_model.visualize_topics()
fig.show()

# %%
fig = topic_model.visualize_hierarchy()
fig.show()

# %%
