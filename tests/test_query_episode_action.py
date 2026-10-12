from memory.episode import Episode
from memory.episode_memory import EpisodeMemory
from memory.working_memory import WorkingMemory
from planner.execution_context import ExecutionContext
from planner.objective import Objective
from planner.plan import ExecutionPlan, PlanStep
from actions.query_episode import QueryEpisodeAction


def check(
    condition: bool,
    message: str,
) -> None:

    if not condition:
        raise AssertionError(message)


def create_context(
    plan: ExecutionPlan,
) -> ExecutionContext:

    objective = Objective(
        id="test-objective",
        title="Consultar memoria episódica",
    )

    return ExecutionContext(
        objective=objective,
        plan=plan,
    )


async def run() -> None:

    memory = WorkingMemory()
    episode_memory = EpisodeMemory(memory)

    episode_memory.add(
        Episode(
            action="system.close_app",
            parameters={
                "application": "chrome",
            },
            original_text="cerrá Chrome",
            success=True,
            output={
                "status": "closed",
                "application": "chrome",
            },
        )
    )

    action = QueryEpisodeAction(
        episode_memory
    )

    #
    # Consulta válida
    #

    plan = ExecutionPlan(
        objective_id="test-objective",
        steps=[
            PlanStep(
                id="query",
                name="Query episode",
                description="Consulta un episodio anterior.",
                action="system.query_episode",
                metadata={
                    "action": "system.close_app",
                    "field": "application",
                },
            )
        ],
    )

    context = create_context(plan)

    await action.execute(
        context,
        plan.steps[0],
    )

    result = context.results.get(
        "episode_query_result"
    )

    check(
        isinstance(result, dict),
        "La acción debería producir un resultado estructurado.",
    )

    check(
        result.get("status") == "found",
        "El estado debería ser found.",
    )

    check(
        result.get("action") == "system.close_app",
        "La acción consultada debería ser system.close_app.",
    )

    check(
        result.get("field") == "application",
        "El campo consultado debería ser application.",
    )

    check(
        result.get("value") == "chrome",
        "El valor recuperado debería ser chrome.",
    )

    check(
        result.get("original_text") == "cerrá Chrome",
        "Debería conservarse el texto original del episodio.",
    )

    #
    # Consulta sin episodio
    #

    missing_plan = ExecutionPlan(
        objective_id="missing-objective",
        steps=[
            PlanStep(
                id="query",
                name="Query missing episode",
                description="Consulta un episodio inexistente.",
                action="system.query_episode",
                metadata={
                    "action": "system.mute",
                    "field": "status",
                },
            )
        ],
    )

    missing_context = create_context(
        missing_plan
    )

    await action.execute(
        missing_context,
        missing_plan.steps[0],
    )

    check(
        bool(missing_context.errors),
        "Una consulta sin episodio debería producir un error.",
    )

    #
    # Campo inexistente
    #

    invalid_field_plan = ExecutionPlan(
        objective_id="invalid-field-objective",
        steps=[
            PlanStep(
                id="query",
                name="Query invalid field",
                description="Consulta un campo inexistente.",
                action="system.query_episode",
                metadata={
                    "action": "system.close_app",
                    "field": "unknown_field",
                },
            )
        ],
    )

    invalid_field_context = create_context(
        invalid_field_plan
    )

    await action.execute(
        invalid_field_context,
        invalid_field_plan.steps[0],
    )

    check(
        bool(invalid_field_context.errors),
        "Un campo inexistente debería producir un error.",
    )

    #
    # Parámetros inválidos
    #

    invalid_parameters_plan = ExecutionPlan(
        objective_id="invalid-parameters-objective",
        steps=[
            PlanStep(
                id="query",
                name="Query invalid parameters",
                description="Consulta con parámetros inválidos.",
                action="system.query_episode",
                metadata={},
            )
        ],
    )

    invalid_parameters_context = create_context(
        invalid_parameters_plan
    )

    await action.execute(
        invalid_parameters_context,
        invalid_parameters_plan.steps[0],
    )

    check(
        bool(invalid_parameters_context.errors),
        "Parámetros inválidos deberían producir un error.",
    )

    #
    # Resultado estructurado completo
    #

    check(
        context.results.get("status") == "found",
        "El resultado general debería conservar status=found.",
    )

    check(
        context.results.get("action") == "system.close_app",
        "El resultado debería conservar la acción.",
    )

    check(
        context.results.get("field") == "application",
        "El resultado debería conservar el campo.",
    )

    check(
        context.results.get("value") == "chrome",
        "El resultado debería conservar el valor.",
    )

    print("=" * 72)
    print("QUERY EPISODE ACTION")
    print("=" * 72)
    print("PASSED : 10")
    print("FAILED : 0")
    print("=" * 72)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
