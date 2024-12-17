from bertopic import BERTopic
import json

with open("texts.json", "r") as r:
    docs = json.load(r)

topic_model = BERTopic(language="multilingual")
topics, probs = topic_model.fit_transform(docs)
