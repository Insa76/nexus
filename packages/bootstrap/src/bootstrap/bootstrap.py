from __future__ import annotations

import os
from pathlib import Path


from core.kernel import Kernel

from engine.engine import Engine
from memory.semantic_memory import SemanticMemory

from runtime.runtime import Runtime
from runtime.executor import Executor


from actions.registry import ActionRegistry

from actions.manager import ActionManager

from security import (
    ActionAuthorization,
    ActionPolicy,
    ActionPolicyStore,
    Actor,
    ActorRoleAssignment,
    AssignmentStore,
    AuthorizationService,
    Permission,
    PermissionAction,
    Role,
)

from security.sqlite_security_store import SQLiteSecurityStore
from security.sqlite_stores import (
    SQLiteAssignmentStore,
    SQLiteRoleStore,
)

from actions.open_app import OpenAppAction
from actions.open_file import OpenFileAction

from actions.set_volume import SetVolumeAction

from actions.get_volume import GetVolumeAction

from actions.get_time import GetTimeAction

from actions.mute import MuteAction

from actions.unmute import UnmuteAction

from actions.close_app import CloseAppAction

from actions.process_list import ProcessListAction

from actions.screen_capture import ScreenCaptureAction

from actions.get_volume_history import GetVolumeHistoryAction

from actions.restore_previous_volume import RestorePreviousVolumeAction

from actions.restore_previous_mute import RestorePreviousMuteAction

from actions.get_mute import GetMuteAction

from actions.get_recent_episodes import GetRecentEpisodesAction

from actions.get_last_episode import GetLastEpisodeAction

from actions.get_previous_episode import GetPreviousEpisodeAction

from actions.inspect_capture import InspectCaptureAction

from actions.inspect_screen import InspectScreenAction

from actions.query_episode import QueryEpisodeAction


from providers.provider_manager import ProviderManager

from providers.local_provider import LocalProvider

from providers.tool_registry import ToolRegistry


from planner.intent_recognizer import IntentRecognizer

from planner.rule_intent_provider import RuleIntentProvider

from planner.ollama_intent_provider import OllamaIntentProvider

from planner.hybrid_intent_provider import HybridIntentProvider


from memory import WorkingMemory

from memory.state_history import StateHistory

from memory.episode_memory import EpisodeMemory


from context import (
    AssistantContext,
    AssistantSession,
    AssistantSessionManager,
)


from documents import (
    DocumentCapability,
    DocumentCognitiveAccess,
    DocumentServices,
    build_document_services as compose_document_services,
)


from processes.capability import ProcessCapability

from processes.cognitive import ProcessCognitiveAccess

from processes.resolver import ProcessResolver

from processes.store import ProcessStore


from rules.capability import RuleCapability

from rules.cognitive import RuleCognitiveAccess

from rules.resolver import RuleResolver

from rules.store import RuleStore

from tasks.capability import TaskCapability
from tasks.cognitive import TaskCognitiveAccess
from tasks.resolver import TaskResolver
from tasks.store import TaskStore


from bootstrap.assistant_services import (
    AssistantServices,
    build_assistant_services,
)


from bootstrap.assistant_services_lifecycle import (
    AssistantServicesLifecycle,
)


from engine.cognitive_capabilities import CognitiveCapabilityRouter


def build_document_services() -> DocumentServices:
    """
    Construye el subsistema Documents de NEXUS.

    Documents mantiene sus propias dependencias y no conoce
    Runtime, Engine ni Scheduler.
    """

    return compose_document_services()


def build_engine(
    assistant_context: AssistantContext | None = None,
    assistant_session: AssistantSession | None = None,
) -> Engine:
    """
    Construye y configura completamente NEXUS.

    El AssistantContext es opcional para mantener compatibilidad
    con el arranque actual de NEXUS.
    """

    # El perfil cognitivo describe al usuario, pero no concede
    # permisos. La instalación local conserva su actor autorizado.
    # Esto evita que un ID de perfil recién creado cambie la identidad
    # de seguridad usada por ActionAuthorization.
    local_console_actor = Actor.system(
        "local-console",
        name="NEXUS Local Console",
    )
    security_actor = local_console_actor

    #
    # Working Memory
    #

    # Una única instancia compartida por todos
    # los componentes que necesiten memoria.

    memory = WorkingMemory()

    episode_memory = EpisodeMemory(
        memory
    )

    #
    # State History
    #

    state_history = StateHistory(
        memory
    )

    #
    # Kernel
    #

    kernel = Kernel()

    #
    # Runtime
    #

    runtime = Runtime(
        kernel=kernel
    )

    #
    # Provider Manager
    #

    provider_manager = ProviderManager()

    provider_manager.register(
        LocalProvider()
    )

    #
    # Action Registry
    #

    registry = ActionRegistry()

    #
    # Applications
    #

    registry.register(
        OpenAppAction(
            provider_manager
        )
    )

    registry.register(
        OpenFileAction(
            provider_manager
        )
    )

    registry.register(
        CloseAppAction()
    )

    registry.register(
        ProcessListAction(
            provider_manager
        )
    )

    registry.register(
        ScreenCaptureAction(
            provider_manager
        )
    )

    registry.register(
        InspectScreenAction()
    )

    registry.register(
        InspectCaptureAction()
    )

    registry.register(GetTimeAction())

    #
    # Episodic Memory
    #

    registry.register(
        QueryEpisodeAction(
            episode_memory
        )
    )

    #
    # Volume
    #

    registry.register(
        SetVolumeAction(
            provider_manager
        )
    )

    registry.register(
        GetVolumeAction(
            provider_manager
        )
    )

    registry.register(
        GetVolumeHistoryAction(
            state_history
        )
    )

    registry.register(
        GetRecentEpisodesAction(
            episode_memory
        )
    )

    registry.register(
        GetPreviousEpisodeAction(
            episode_memory
        )
    )

    registry.register(
        GetLastEpisodeAction(
            episode_memory
        )
    )

    registry.register(
        RestorePreviousVolumeAction(
            provider_manager,
            state_history,
        )
    )

    #
    # Mute / Unmute
    #

    registry.register(
        MuteAction(
            provider_manager
        )
    )

    registry.register(
        UnmuteAction(
            provider_manager
        )
    )

    registry.register(
        GetMuteAction(
            provider_manager
        )
    )

    registry.register(
        RestorePreviousMuteAction(
            provider_manager,
            state_history,
        )
    )

    #
    # Action Manager
    #

        #
    # Security: permisos de ejecución.
    #

    task_mutation_actions = (
        "tasks.create",
        "tasks.update",
        "tasks.transition",
    )
    action_names = [*registry.list(), *task_mutation_actions]

    permissions = frozenset(
        Permission(
            resource=action_name,
            action=PermissionAction.EXECUTE,
        )
        for action_name in action_names
    )


    local_role = Role(
        id="local_operator",
        name="Local Operator",
        permissions=permissions,
    )

    security_db_path = os.environ.get(
        "NEXUS_SECURITY_DB_PATH",
        str(Path.home() / ".nexus" / "security.db"),
    )

    security_database = SQLiteSecurityStore(security_db_path)
    role_store = SQLiteRoleStore(security_database)
    assignment_store = SQLiteAssignmentStore(security_database)

    stored_role = role_store.get(local_role.id)

    if stored_role is None:
        role_store.add(local_role)
    elif stored_role != local_role:
        role_store.update(local_role)

    persisted_local_role = role_store.get(local_role.id)

    if persisted_local_role is None:
        raise RuntimeError(
            "No se pudo recuperar el rol local desde SQLite."
        )

    assignment_store.add(
        ActorRoleAssignment(
            actor=local_console_actor,
            role=persisted_local_role,
        )
    )


    policy_store = ActionPolicyStore()

    for action_name in action_names:
        policy_store.register(
            ActionPolicy(
                action_name=action_name,
                permission=Permission(
                    resource=action_name,
                    action=PermissionAction.EXECUTE,
                ),
            )
        )

    authorization_service = AuthorizationService(
        assignment_store
    )

    action_authorization = ActionAuthorization(
        policy_store=policy_store,
        authorization=authorization_service,
    )

    manager = ActionManager(
        registry,
        action_authorization=action_authorization,
    )

    runtime.configure_actions(
        registry,
        manager
    )

    #
    # Tool Registry
    #

    tool_registry = ToolRegistry()

    tool_registry.register_many(
        provider_manager.tools()
    )

    tool_registry.register_many(
        registry.describe()
    )

    #
    # Exponer Tool Registry al Runtime
    #

    runtime.tool_registry = tool_registry

    #
    # Intent Providers
    #

    rule_provider = RuleIntentProvider(
        IntentRecognizer()
    )

    ollama_provider = OllamaIntentProvider(
        model="llama3:latest"
    )

    intent_provider = HybridIntentProvider(
        rule_provider=rule_provider,
        ollama_provider=ollama_provider,
    )

    #
    # Executor
    #

    executor = Executor(
        runtime
    )

    runtime.configure_executor(
        executor
    )

    session_manager = AssistantSessionManager()

    if assistant_session is not None:
        active_session = assistant_session

    elif assistant_context is not None:
        active_session = session_manager.start(
            assistant_context
        )

    else:
        active_session = None

    if active_session is not None:
        assistant_context = active_session.context

    #
    # Documents Capability
    #

    document_services = build_document_services()

    document_capability = DocumentCapability(
        context_access=document_services.context_access,
    )

    document_cognitive_access = DocumentCognitiveAccess(
        document_capability
    )

    #
    # Processes Capability
    #

    process_store = ProcessStore()

    process_resolver = ProcessResolver(
        process_store,
    )

    process_capability = ProcessCapability(
        store=process_store,
        resolver=process_resolver,
    )

    process_cognitive_access = ProcessCognitiveAccess(
        process_capability,
    )

    #
    # Rules Capability
    #

    rule_store = RuleStore()

    rule_resolver = RuleResolver(
        rule_store
    )

    rule_capability = RuleCapability(
        store=rule_store,
        resolver=rule_resolver,
    )

    rule_cognitive_access = RuleCognitiveAccess(
        rule_capability
    )

    #
    # Tasks Capability
    #

    task_db_path = os.environ.get(
        "NEXUS_TASKS_DB_PATH",
        str(Path.home() / ".nexus" / "tasks.sqlite3"),
    )
    task_store = TaskStore(db_path=task_db_path)
    task_resolver = TaskResolver(task_store)
    task_capability = TaskCapability(
        store=task_store,
        resolver=task_resolver,
    )
    task_cognitive_access = TaskCognitiveAccess(task_capability)

    #
    # Cognitive Capability Router
    #

    cognitive_capability_router = CognitiveCapabilityRouter(
        document_access=document_cognitive_access,
        process_access=process_cognitive_access,
        rule_access=rule_cognitive_access,
        task_access=task_cognitive_access,
    )

    #
    # Engine
    #

    semantic_memory_db_path = os.environ.get(
        "NEXUS_SEMANTIC_MEMORY_DB_PATH",
        str(Path.home() / ".nexus" / "semantic_memory.db"),
    )
    semantic_memory = SemanticMemory(db_path=semantic_memory_db_path)

    return Engine(
        runtime,
        intent_provider=intent_provider,
        semantic_memory=semantic_memory,
        memory=memory,
        assistant_context=assistant_context,
        document_capability=document_capability,
        document_cognitive_access=document_cognitive_access,
        cognitive_capability_router=cognitive_capability_router,
        process_capability=process_capability,
        process_cognitive_access=process_cognitive_access,
        rule_capability=rule_capability,
        rule_cognitive_access=rule_cognitive_access,
        default_actor_id=security_actor.id,
        default_actor_type=security_actor.actor_type.value,
        task_action_authorizer=lambda action_name: (
            action_authorization.is_allowed(local_console_actor, action_name)
        ),
    )


def build_assistant_runtime(
    assistant_context: AssistantContext | None = None,
    assistant_session: AssistantSession | None = None,
) -> tuple[
    Engine,
    AssistantServices,
    AssistantServicesLifecycle,
]:
    """
    Construye el Engine cognitivo, los servicios del Assistant Layer
    y su lifecycle.

    El Engine, los servicios y su ciclo de vida mantienen
    responsabilidades separadas.
    """

    engine = build_engine(
        assistant_context=assistant_context,
        assistant_session=assistant_session,
    )

    services = build_assistant_services()

    lifecycle = AssistantServicesLifecycle(
        services
    )

    return engine, services, lifecycle


def _print_result(result) -> None:
    """
    Presenta el resultado de una ejecución
    de NEXUS de forma legible.
    """


    if result.success:

        print("NEXUS >", end=" ")

        response = (
            result.metadata.get("response")
            if isinstance(result.metadata, dict)
            else None
        )

        if response:
            print(response)
        elif result.message and result.message != "Execution completed successfully.":
            print(result.message)
        elif result.output:
            print(result.output)
        else:
            print("Listo.")

        return

    print(
        f"NEXUS > {result.message}"
    )



async def _interactive_loop(
    engine: Engine,
) -> None:
    """
    Loop interactivo persistente de NEXUS.

    El Engine y el event loop permanecen vivos
    durante toda la sesión.
    """

    print()

    print("Escribí una instrucción.")

    print("Escribí 'salir' para cerrar NEXUS.")

    print()

    while True:

        try:

            text = input(
                "Usuario > "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt,
        ):

            print()

            break

        if not text:
            continue

        if text.lower() in {
            "salir",
            "exit",
            "quit",
        }:

            break

        try:

            result = await engine.execute(
                text
            )

            _print_result(
                result
            )

        except Exception as exc:

            print(
                f"NEXUS > Error interno: {exc}"
            )

        print()



async def _main_async() -> None:
    """
    Inicializa NEXUS, mantiene una sesión interactiva
    persistente y gestiona el ciclo de vida de sus servicios.
    """

    print()
    print("=" * 50)
    print("          NEXUS Cognitive OS")
    print("=" * 50)
    print()

    engine, services, lifecycle = build_assistant_runtime()

    print("✓ Kernel")
    print("✓ Runtime")
    print("✓ Providers")
    print("✓ Actions")
    print("✓ Intent Providers")
    print("✓ Executor")
    print("✓ Engine")
    print("✓ Reminder Store")
    print("✓ Reminder Scheduler")
    print()

    try:
        await lifecycle.start()

        print("=" * 50)
        print("NEXUS READY")
        print("=" * 50)

        await _interactive_loop(engine)

    finally:
        await lifecycle.stop()

        close_semantic_memory = getattr(
            engine.semantic_memory,
            "close",
            None,
        )

        if callable(close_semantic_memory):
            close_semantic_memory()

        print()
        print("NEXUS detenido.")



def main() -> None:
    """
    Punto de entrada de NEXUS.
    """

    import asyncio

    asyncio.run(
        _main_async()
    )
