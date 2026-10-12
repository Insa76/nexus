import asyncio
from types import SimpleNamespace

from planner.intent import Intent
from runtime.execution_result import ExecutionResult
from engine.engine import Engine
from planner.objective import Objective
from planner.plan import ExecutionPlan


class FakeToolRegistry:
    def describe(self):
        return {}

    def resolve(self, action_name):
        return SimpleNamespace(
            name=action_name
        )


class FakeActionRegistry:
    def __init__(self, action=None):
        self.action = action

    def get(self, action_name):
        return self.action


class FakeEpisodeMemory:
    def __init__(self):
        self.episodes = []

    def add(self, episode):
        self.episodes.append(episode)


class FakeSemanticKnowledgeExtractor:
    def __init__(self):
        self.extracted = []

    def extract(self, episode):
        self.extracted.append(episode)


class FakeRuntime:
    def __init__(
        self,
        result,
        action=None,
    ):
        self.tool_registry = FakeToolRegistry()
        self.action_registry = FakeActionRegistry(
            action=action
        )
        self.action_manager = SimpleNamespace()
        self.result = result

    async def execute(self, context):
        return self.result


class FakeIntentProvider:
    def __init__(self, intent):
        self.intent = intent

    async def recognize(
        self,
        text,
        capabilities,
        memory_context,
    ):
        return self.intent


class FakeDecisionEngine:
    def decide(
        self,
        intent,
        context,
        capabilities,
    ):
        return SimpleNamespace(
            decision_id="decision-test",
            selected_action=intent.action,
            confidence=1.0,
            reason="test",
            requires_execution=True,
            alternatives=[],
            metadata={},
            is_executable=True,
        )


class FakeObjectiveFactory:
    def create(self, intent):
        return Objective(
            id="objective-test",
            title="Learning Boundary Test",
            description="Learning Boundary Test",
            metadata={
                "original_text": intent.original_text,
            },
        )


class FakePlanner:
    def create_plan(
        self,
        objective,
        intent,
    ):
        return ExecutionPlan(
            objective_id=objective.id,
            steps=[],
            current_step=0,
            completed=True,
            metadata={},
        )


class FakeVerifier:
    def __init__(
        self,
        verified=True,
        confidence=1.0,
        reason="verified",
    ):
        self.verified = verified
        self.confidence = confidence
        self.reason = reason

    def verify(
        self,
        objective,
        plan,
        result,
    ):
        return SimpleNamespace(
            verified=self.verified,
            confidence=self.confidence,
            reason=self.reason,
            evidence=["test_evidence"],
            metadata={},
        )


def make_intent(
    action="test.action",
):
    return Intent(
        action=action,
        confidence=1.0,
        parameters={},
        original_text="test request",
    )


def make_result(
    success=True,
):
    return ExecutionResult(
        success=success,
        message=(
            "success"
            if success
            else "failure"
        ),
        output={
            "status": (
                "completed"
                if success
                else "failed"
            )
        },
        artifacts={},
        metadata={},
    )


def build_engine(
    result,
    action,
    verification=True,
):
    intent = make_intent()

    runtime = FakeRuntime(
        result=result,
        action=action,
    )

    provider = FakeIntentProvider(
        intent
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=provider,
    )

    engine._decision_engine = (
        FakeDecisionEngine()
    )

    engine._objective_factory = (
        FakeObjectiveFactory()
    )

    engine._planner = (
        FakePlanner()
    )

    engine._verifier = FakeVerifier(
        verified=verification,
        confidence=(
            1.0
            if verification
            else 0.4
        ),
        reason=(
            "verified"
            if verification
            else "verification failed"
        ),
    )

    engine._episode_memory = (
        FakeEpisodeMemory()
    )

    engine._semantic_knowledge_extractor = (
        FakeSemanticKnowledgeExtractor()
    )

    return engine


def test_verified_external_success_is_learned():
    action = SimpleNamespace(
        internal=False
    )

    engine = build_engine(
        result=make_result(True),
        action=action,
        verification=True,
    )

    result = asyncio.run(
        engine.execute("test request")
    )

    assert result.success is True

    assert (
        len(
            engine._episode_memory.episodes
        )
        == 1
    )

    assert (
        len(
            engine
            ._semantic_knowledge_extractor
            .extracted
        )
        == 1
    )


def test_internal_action_is_not_learned():
    action = SimpleNamespace(
        internal=True
    )

    engine = build_engine(
        result=make_result(True),
        action=action,
        verification=True,
    )

    result = asyncio.run(
        engine.execute("test request")
    )

    assert result.success is True

    assert (
        len(
            engine._episode_memory.episodes
        )
        == 0
    )

    assert (
        len(
            engine
            ._semantic_knowledge_extractor
            .extracted
        )
        == 0
    )


def test_failed_execution_is_not_learned():
    action = SimpleNamespace(
        internal=False
    )

    engine = build_engine(
        result=make_result(False),
        action=action,
        verification=True,
    )

    result = asyncio.run(
        engine.execute("test request")
    )

    assert result.success is False

    assert (
        len(
            engine._episode_memory.episodes
        )
        == 0
    )

    assert (
        len(
            engine
            ._semantic_knowledge_extractor
            .extracted
        )
        == 0
    )


def test_unverified_success_is_not_learned():
    action = SimpleNamespace(
        internal=False
    )

    engine = build_engine(
        result=make_result(True),
        action=action,
        verification=False,
    )

    result = asyncio.run(
        engine.execute("test request")
    )

    assert result.success is True

    assert (
        len(
            engine._episode_memory.episodes
        )
        == 0
    )

    assert (
        len(
            engine
            ._semantic_knowledge_extractor
            .extracted
        )
        == 0
    )


def test_failed_execution_is_recorded_as_error():
    action = SimpleNamespace(
        internal=False
    )

    engine = build_engine(
        result=make_result(False),
        action=action,
        verification=True,
    )

    asyncio.run(
        engine.execute("test request")
    )

    error_entries = [
        item
        for item in engine.memory.all()
        if item.type == "error"
    ]

    assert len(error_entries) == 1


def test_verification_failure_is_recorded_without_learning():
    action = SimpleNamespace(
        internal=False
    )

    engine = build_engine(
        result=make_result(True),
        action=action,
        verification=False,
    )

    asyncio.run(
        engine.execute("test request")
    )

    verification_failures = [
        item
        for item in engine.memory.all()
        if item.type == "verification_failure"
    ]

    assert len(
        verification_failures
    ) == 1

    assert (
        len(
            engine
            ._semantic_knowledge_extractor
            .extracted
        )
        == 0
    )


def main():
    tests = [
        (
            "test_verified_external_success_is_learned",
            test_verified_external_success_is_learned,
        ),
        (
            "test_internal_action_is_not_learned",
            test_internal_action_is_not_learned,
        ),
        (
            "test_failed_execution_is_not_learned",
            test_failed_execution_is_not_learned,
        ),
        (
            "test_unverified_success_is_not_learned",
            test_unverified_success_is_not_learned,
        ),
        (
            "test_failed_execution_is_recorded_as_error",
            test_failed_execution_is_recorded_as_error,
        ),
        (
            "test_verification_failure_is_recorded_without_learning",
            test_verification_failure_is_recorded_without_learning,
        ),
    ]

    passed = 0

    for name, test in tests:
        try:
            test()
            print(f"PASS: {name}")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {name}")
            print(
                f"      {type(exc).__name__}: {exc}"
            )

    print()
    print(
        f"LEARNING 7.1: "
        f"{passed}/{len(tests)} PASSED"
    )


if __name__ == "__main__":
    main()
