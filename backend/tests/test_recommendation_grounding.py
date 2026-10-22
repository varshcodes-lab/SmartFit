import services.recommendation_engine as engine


def _disable_llm(monkeypatch):
    def unavailable_client():
        raise RuntimeError("LLM disabled in test")

    monkeypatch.setattr(engine, "_get_groq_client", unavailable_client)


def test_knowledge_documents_have_truthful_source_types():
    docs = engine._load_knowledge()
    # Ten existing internal documents plus three external references.
    assert len(docs) == 13
    assert sum(d.get("source_type") == "internal_guidance" for d in docs) == 10
    assert sum(d.get("source_type") == "external_reference" for d in docs) == 3

    for doc in docs:
        expected = (
            "external_reference"
            if str(doc.get("url") or "").strip()
            else "internal_guidance"
        )
        assert doc["source_type"] == expected
        assert doc.get("title")
        assert doc.get("source")
        assert str(doc.get("content") or "").strip()


def test_retrieval_preserves_source_types():
    docs = engine.retrieve_knowledge(
        "chest push-up dumbbell equipment",
        limit=4,
    )
    assert docs

    for doc in docs:
        expected = (
            "external_reference"
            if str(doc.get("url") or "").strip()
            else "internal_guidance"
        )
        assert doc["source_type"] == expected


def test_explanation_matches_returned_recommendations(monkeypatch):
    _disable_llm(monkeypatch)
    result = engine.generate_recommendations({
        "goal": "muscle_gain",
        "experience": "beginner",
        "equipment": ["dumbbell"],
        "preferences": [],
        "target_muscles": ["chest"],
        "performance_score": 65,
        "workout_history": [],
    })

    explanation = result["explanation"]
    assert "## Ranked exercises" in explanation
    assert " ? score:" not in explanation

    for rank, item in enumerate(result["recommendations"], 1):
        line = (
            f"{rank}. **{item['name']}** - score: "
            f"{item['score']:.0f}/100; selection score: "
            f"{item['selection_score']:.0f}/100."
        )
        assert line in explanation

        reasons = item.get("reasons") or []
        if reasons:
            text = "; ".join(str(reason) for reason in reasons)
            assert f"Why it matched: {text}." in explanation


def test_response_sources_match_retrieved_documents(monkeypatch):
    _disable_llm(monkeypatch)
    result = engine.generate_recommendations({
        "goal": "general_fitness",
        "experience": "beginner",
        "equipment": ["none"],
        "preferences": [],
        "target_muscles": [],
        "performance_score": 50,
        "workout_history": [],
    })

    assert len(result["sources"]) == len(result["retrieved_knowledge"])

    for source, doc in zip(result["sources"], result["retrieved_knowledge"]):
        assert source["title"] == doc["title"]
        assert source["source"] == doc["source"]
        assert source["url"] == str(doc.get("url") or "").strip()
        assert source["source_type"] == (
            "external_reference"
            if source["url"]
            else "internal_guidance"
        )
