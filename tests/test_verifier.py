from planner.verification import (
    VerificationResult,
    Verifier,
)


class FakeObjective:
    id = "objective-test"


class FakePlan:
    completed = True


class FakeResult:
    def __init__(
        self,
        success: bool,
        output=None,
        message: str = "",
    ):
        self.success = success
        self.output = output or {}
        self.message = message


def test_successful_execution_with_completed_plan_is_verified():
    verifier = Verifier()

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=True,
            output={
                "status": "opened",
                "application": "Chrome",
            },
        ),
    )

    assert isinstance(
        result,
        VerificationResult,
    )
    assert result.verified is True
    assert result.status == "verified"
    assert result.confidence == 1.0


def test_failed_execution_is_not_verified():
    verifier = Verifier()

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=False,
            message="No se pudo ejecutar la acción.",
        ),
    )

    assert result.verified is False
    assert result.status == "not_verified"
    assert result.confidence == 1.0
    assert result.metadata["status"] == "execution_failed"


def test_incomplete_plan_is_not_verified():
    verifier = Verifier()

    plan = FakePlan()
    plan.completed = False

    result = verifier.verify(
        FakeObjective(),
        plan,
        FakeResult(
            success=True,
            output={
                "status": "opened",
            },
        ),
    )

    assert result.verified is False
    assert result.status == "not_verified"
    assert result.metadata["status"] == "plan_incomplete"


def test_successful_execution_without_output_has_limited_confidence():
    verifier = Verifier()

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=True,
        ),
    )

    assert result.verified is True
    assert result.confidence == 0.70
    assert (
        result.metadata["status"]
        == "verified_with_limited_evidence"
    )


def test_output_evidence_is_recorded():
    verifier = Verifier()

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=True,
            output={
                "application": "Chrome",
                "status": "opened",
            },
        ),
    )

    assert result.verified is True

    output_evidence = [
        item
        for item in result.evidence
        if item["type"] == "output"
    ][0]

    assert output_evidence["status"] == "available"
    assert output_evidence["keys"] == [
        "application",
        "status",
    ]


def test_verification_contains_reason():
    verifier = Verifier()

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=True,
            output={
                "status": "ok",
            },
        ),
    )

    assert result.reason
    assert "ejecución" in result.reason.lower()


def test_verifier_does_not_execute_anything():
    verifier = Verifier()

    executed = False

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=True,
            output={
                "status": "ok",
            },
        ),
    )

    assert executed is False
    assert result.verified is True


def test_verification_metadata_contains_objective():
    verifier = Verifier()

    result = verifier.verify(
        FakeObjective(),
        FakePlan(),
        FakeResult(
            success=True,
            output={
                "status": "ok",
            },
        ),
    )

    assert (
        result.metadata["objective_id"]
        == "objective-test"
    )


if __name__ == "__main__":
    tests = [
        test_successful_execution_with_completed_plan_is_verified,
        test_failed_execution_is_not_verified,
        test_incomplete_plan_is_not_verified,
        test_successful_execution_without_output_has_limited_confidence,
        test_output_evidence_is_recorded,
        test_verification_contains_reason,
        test_verifier_does_not_execute_anything,
        test_verification_metadata_contains_objective,
    ]

    for test in tests:
        test()

    print(
        f"VERIFIER PASSED : "
        f"{len(tests)} FAILED : 0"
    )
