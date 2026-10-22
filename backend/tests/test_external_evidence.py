from services.recommendation_engine import _load_knowledge


EXPECTED_IDS = {
    "who_physical_activity_adults_2020",
    "cdc_adult_activity_guidance",
    "acsm_resistance_training_position_stand",
}


def test_external_references_have_urls_publishers_and_evidence_claims():
    docs = _load_knowledge()
    by_id = {d.get("id"): d for d in docs}
    assert EXPECTED_IDS.issubset(by_id)
    for doc_id in EXPECTED_IDS:
        doc = by_id[doc_id]
        assert doc.get("source_type") == "external_reference"
        assert doc.get("url", "").startswith("https://")
        assert doc.get("publisher")
        assert doc.get("title")
        assert len(doc.get("content", "")) >= 100
        assert doc.get("evidence_claims")
        assert doc.get("evidence_scope")


def test_internal_guidance_remains_internal():
    for doc in _load_knowledge():
        if not str(doc.get("url") or "").startswith("https://"):
            assert doc.get("source_type") == "internal_guidance"


def test_external_ids_and_urls_are_unique():
    docs = [
        d for d in _load_knowledge()
        if d.get("source_type") == "external_reference"
    ]
    assert len([d["id"] for d in docs]) == len({d["id"] for d in docs})
    assert len([d["url"] for d in docs]) == len({d["url"] for d in docs})


def test_acsm_scope_does_not_claim_smartfit_is_validated():
    doc = next(
        d for d in _load_knowledge()
        if d.get("id") == "acsm_resistance_training_position_stand"
    )
    text = (doc.get("content", "") + doc.get("evidence_scope", "")).casefold()
    assert "does not establish" in text or "does not validate" in text
