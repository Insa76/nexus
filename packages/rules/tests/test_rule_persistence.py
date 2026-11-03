from dataclasses import replace

from rules import Rule, RuleStatus, RuleStore


def test_rule_store_persists_and_reopens(tmp_path):
    db_path = tmp_path / "rules.sqlite3"
    original = Rule.create(
        "Regla persistente",
        description="Conserva su estado",
        user_id="user-1",
        organization_id="org-1",
        project_id="project-1",
    )
    first = RuleStore(db_path=db_path)
    first.add(original)

    reopened = RuleStore(db_path=db_path)
    assert reopened.get(original.id) == original
    assert reopened.list() == [original]
    assert reopened.count() == 1

    updated = replace(original, status=RuleStatus.INACTIVE)
    reopened.update(updated)
    assert RuleStore(db_path=db_path).get(original.id) == updated

    assert reopened.remove(original.id) == updated
    assert RuleStore(db_path=db_path).count() == 0


def test_rule_store_keeps_memory_mode_without_db_path():
    store = RuleStore()
    rule = Rule.create("Regla temporal")
    store.add(rule)
    assert store.get(rule.id) == rule
