import pytest

from app.services.keyword_processing.intent import classify_intent
from app.services.keyword_processing.sort import sort_keywords_by_intent


def _scraped_product_fixture():
    return {
        "elements": {
            "productTitle": {"text": "Foam wipeable baby changing pad with straps"},
            "brand": {"text": "AcmeBaby"},
        }
    }


def test_classify_intent_basic():
    sp = _scraped_product_fixture()
    res = classify_intent("changing pad waterproof", scraped_product=sp, category="Relevant")
    assert 0 <= res.intent_score <= 3
    assert res.intent_score == 3  # product_type + attribute + use_case


def test_sort_keywords_by_intent_ordering():
    sp = _scraped_product_fixture()
    items = [
        {"phrase": "changing pad waterproof", "category": "Relevant", "base_relevancy_score": 7},
        {"phrase": "best changing pad", "category": "Design-Specific", "base_relevancy_score": 9},
        {"phrase": "stainless steel", "category": "Irrelevant", "base_relevancy_score": 10},
        {"phrase": "buy changing pad", "category": "Relevant", "base_relevancy_score": 4},
    ]

    view = sort_keywords_by_intent(items, sp)
    flat = view["flat_sorted"]

    # Expect a 3-intent near top; transactional "buy" should also be 3
    assert flat[0]["intent_score"] in (3,)
    # High intent should come before irrelevant (0)
    assert flat[-1]["intent_score"] == 0

    # Within same intent, higher relevancy should rank earlier
    # Find all intent==3 rows and check order by base_relevancy_score desc
    intent3 = [x for x in flat if x["intent_score"] == 3]
    if len(intent3) >= 2:
        for i in range(len(intent3) - 1):
            assert intent3[i]["base_relevancy_score"] >= intent3[i + 1]["base_relevancy_score"]
