import pytest
from datetime import datetime
from models.article import Article
from processors.deduplicator import Deduplicator

def test_jaccard_similarity():
    d = Deduplicator()
    set1 = {"apple", "launches", "new", "iphone"}
    set2 = {"apple", "launches", "new", "ipad"}
    sim = d.jaccard_similarity(set1, set2)
    assert sim > 0.5

def test_deduplication():
    d = Deduplicator()
    a1 = Article(
        id="1", title="OpenAI releases new GPT model", content="...", description="...",
        url="https://site.com/1", canonical_url="https://site.com/1",
        pub_date=datetime.utcnow(), source="A"
    )
    a2 = Article(
        id="2", title="OpenAI releases new GPT model today", content="...", description="...",
        url="https://site2.com/2", canonical_url="https://site2.com/2",
        pub_date=datetime.utcnow(), source="B"
    )
    results = d.deduplicate([a1, a2])
    assert len(results) == 1
