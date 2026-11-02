from __future__ import annotations

import time
import re
from memory import WorkingMemory
from memory.episode import Episode
from memory.episode_memory import EpisodeMemory
from memory.semantic_knowledge_extractor import (
    SemanticKnowledgeExtractor,
)
from memory.semantic_memory import SemanticMemory
from memory.semantic_retriever import SemanticRetriever

from planner.intent_provider import IntentProvider
from planner.objective_factory import ObjectiveFactory
from planner.planner import Planner
from planner.execution_context import ExecutionContext
from planner.context_builder import ContextBuilder
from planner.decision import DecisionEngine

from planner.verification import Verifier
from context import AssistantContext

from runtime.execution_result import ExecutionResult
from runtime.runtime import Runtime
from response.formatter import ResponseFormatter

from presence.presence_event_bus import PresenceEventBus
from documents.capability import DocumentCapability
from documents.cognitive import DocumentCognitiveAccess
from engine.cognitive_capabilities import CognitiveCapabilityRouter
from processes.capability import ProcessCapability
from processes.cognitive import ProcessCognitiveAccess
from rules.capability import RuleCapability
from rules.cognitive import RuleCognitiveAccess


class Engine:
    """
    Motor principal de NEXUS.

    Coordina el ciclo cognitivo completo:

        REQUEST
            ↓
        MEMORY
            ↓
        CONTEXT
            ↓
        CAPABILITIES
            ↓
        INTENT
            ↓
        DECISION
            ↓
        OBJECTIVE
            ↓
        PLAN
            ↓
        EXECUTION CONTEXT
            ↓
        RUNTIME
            ↓
        VERIFICATION
            ↓
        EPISODIC MEMORY
            ↓
        SEMANTIC LEARNING
            ↓
        RESPONSE

    El Engine coordina las capas.
    No ejecuta Actions directamente.
    """

    def __init__(
    self,
    runtime: Runtime,
    intent_provider: IntentProvider,
    memory: WorkingMemory | None = None,
    assistant_context: AssistantContext | None = None,
    document_capability: DocumentCapability | None = None,
    document_cognitive_access: DocumentCognitiveAccess | None = None,
    cognitive_capability_router: CognitiveCapabilityRouter | None = None,
    process_capability: ProcessCapability | None = None,
    process_cognitive_access: ProcessCognitiveAccess | None = None,
    rule_capability: RuleCapability | None = None,
    rule_cognitive_access: RuleCognitiveAccess | None = None,
    default_actor_id: str | None = None,
    default_actor_type: str | None = None,
    semantic_memory: SemanticMemory | None = None,
) -> None:

        self._runtime = runtime
        self._intent_provider = intent_provider
        self._assistant_context = (
            assistant_context
            if assistant_context is not None
            else AssistantContext()
        )
        self._document_capability = document_capability
        self._document_cognitive_access = document_cognitive_access
        self._cognitive_capability_router = cognitive_capability_router
        self._process_capability = process_capability
        self._process_cognitive_access = process_cognitive_access
        self._rule_capability = rule_capability
        self._rule_cognitive_access = rule_cognitive_access
        self._default_actor_id = default_actor_id
        self._default_actor_type = default_actor_type
        self._objective_factory = ObjectiveFactory()

        self._memory = (
            memory
            if memory is not None
            else WorkingMemory()
        )

        #
        # ---------------------------------------------------------
        # MEMORIA EPISÓDICA
        # ---------------------------------------------------------
        #

        self._episode_memory = EpisodeMemory(
            self._memory
        )

        #
        # ---------------------------------------------------------
        # CONSULTA EPISÓDICA
        # ---------------------------------------------------------
        #

        from memory.episode_query_engine import (
            EpisodeQueryEngine,
        )

        self._episode_query_engine = (
            EpisodeQueryEngine(
                self._episode_memory
            )
        )

        #
        # ---------------------------------------------------------
        # MEMORIA SEMÁNTICA
        # ---------------------------------------------------------
        #

        self._semantic_memory = semantic_memory if semantic_memory is not None else SemanticMemory()

        self._semantic_knowledge_extractor = (
            SemanticKnowledgeExtractor(
                self._semantic_memory
            )
        )

        self._semantic_retriever = (
            SemanticRetriever(
                self._semantic_memory
            )
        )

        #
        # ---------------------------------------------------------
        # CONTEXTO COGNITIVO
        # ---------------------------------------------------------
        #

        self._context_builder = ContextBuilder(
            semantic_retriever=self._semantic_retriever,
            assistant_context=self._assistant_context,
        )

        #
        # ---------------------------------------------------------
        # RESPONSE FORMATTER
        # ---------------------------------------------------------
        #

        self._response_formatter = ResponseFormatter()

        #
        # ---------------------------------------------------------
        # DECISION ENGINE
        # ---------------------------------------------------------
        #

        self._decision_engine = DecisionEngine()

        #
        # ---------------------------------------------------------
        # VERIFIER
        # ---------------------------------------------------------
        #

        self._verifier = Verifier()

        #
        # ---------------------------------------------------------
        # PLANNER
        # ---------------------------------------------------------
        #

        self._planner = Planner(
            tool_resolver=(
                self._runtime.tool_registry.resolve
            )
        )

        self._presence_events = PresenceEventBus()

    @property
    def response_formatter(self) -> ResponseFormatter:
        """
        Expone el formatter de respuestas de NEXUS.
        """

        return self._response_formatter

    @property
    def memory(self) -> WorkingMemory:
        """
        Expone la WorkingMemory del Engine.
        """

        return self._memory

    @property
    def semantic_memory(self) -> SemanticMemory:
        """
        Expone la memoria semántica de NEXUS.

        Se utiliza para inspección y para las capas
        cognitivas que necesiten consultar conocimiento.
        """

        return self._semantic_memory

    @property
    def semantic_retriever(self) -> SemanticRetriever:
        """
        Expone el recuperador semántico.
        """

        return self._semantic_retriever

    @property
    def decision_engine(self) -> DecisionEngine:
        """
        Expone el motor de decisión.
        """

        return self._decision_engine

    @property
    def verifier(self) -> Verifier:
        """
        Expone el verificador de objetivos.
        """

        return self._verifier

    @property
    def presence_events(self) -> PresenceEventBus:
        """
        Expone el bus de presencia de NEXUS.

        Los consumidores externos pueden suscribirse
        para observar transiciones reales del runtime.
        """

        return self._presence_events

    @property
    def document_capability(self) -> DocumentCapability | None:
        """
        Expone la capability cognitiva de documentos.

        El Engine conoce la capability, pero no conoce
        stores ni detalles internos del subsistema Documents.
        """

        return self._document_capability

    @property
    def document_cognitive_access(self) -> DocumentCognitiveAccess | None:
        """
        Expone el acceso cognitivo a Documents.

        El Engine recibe el contrato cognitivo ya compuesto
        y no conoce stores ni detalles internos de Documents.
        """
        return self._document_cognitive_access

    @property
    def cognitive_capability_router(
        self,
    ) -> CognitiveCapabilityRouter | None:
        """
        Expone el router de capabilities cognitivas.

        El Engine recibe el router ya compuesto y no conoce
        stores ni detalles internos de las capabilities.
        """
        return self._cognitive_capability_router

    @property
    def process_capability(self) -> ProcessCapability | None:
        return self._process_capability


    @property
    def process_cognitive_access(self) -> ProcessCognitiveAccess | None:
        return self._process_cognitive_access

    @property
    def rule_capability(self) -> RuleCapability | None:
        return self._rule_capability

    @property
    def rule_cognitive_access(self) -> RuleCognitiveAccess | None:
        return self._rule_cognitive_access

    def _handle_semantic_memory_intent(
        self,
        intent,
        original_text: str,
    ) -> ExecutionResult | None:
        # Resuelve las intenciones explícitas de memoria semántica de V1.
        supported_actions = {
            "system.remember_fact",
            "system.recall_fact",
            "system.recall_last_fact",
        }
        sub_intents = getattr(intent, "sub_intents", None)

        if isinstance(sub_intents, (list, tuple)) and sub_intents:
            intents = list(sub_intents)
        else:
            intents = [intent]
        # No interceptar compuestas que mezclen memoria con otras acciones.
        if not all(item.action in supported_actions for item in intents):
            return None

        
        # Validar todas las intenciones antes de modificar la memoria.
        for item in intents:
            parameters = item.parameters

            if item.action == "system.remember_fact":
                subject = parameters.get("subject")
                predicate = parameters.get("predicate")
                value = parameters.get("value")

                if not all(
                    isinstance(part, str) and part.strip()
                    for part in (subject, predicate, value)
                ):
                    return None

            elif item.action == "system.recall_fact":
                subject = parameters.get("subject", "user")
                predicate = parameters.get("predicate")

                if (
                    not isinstance(subject, str)
                    or not isinstance(predicate, str)
                    or not predicate.strip()
                ):
                    return None


        operations: list[dict[str, object]] = []
        responses: list[str] = []
        for item in intents:
            parameters = item.parameters
            if item.action == "system.remember_fact":
                subject = parameters.get("subject")
                predicate = parameters.get("predicate")
                value = parameters.get("value")
                if not all(
                    isinstance(part, str) and part.strip()
                    for part in (subject, predicate, value)
                ):
                    return None
                fact = self._semantic_memory.learn(
                    subject=subject,
                    predicate=predicate,
                    value=value.strip(),
                    source="user",
                )
                responses.append(f"Recordado: {fact.predicate} = {fact.value}.")
                operations.append({
                    "action": item.action,
                    "status": "stored",
                    "subject": fact.subject,
                    "predicate": fact.predicate,
                    "value": fact.value,
                })
                continue

            if item.action == "system.recall_fact":
                subject = parameters.get("subject", "user")
                predicate = parameters.get("predicate")

                if (
                    not isinstance(subject, str)
                    or not isinstance(predicate, str)
                    or not predicate.strip()
                ):
                    return None

                
                if predicate == "__all__":
                    user_facts = [
                        known_fact
                        for known_fact in self._semantic_memory.find_by_subject(
                            subject
                        )
                        if known_fact.source == "user"
                    ]

                    if not user_facts:
                        responses.append(
                            "Todavía no tengo ningún dato que me hayas pedido recordar."
                        )
                        operations.append({
                            "action": item.action,
                            "status": "not_found",
                        })
                    else:
                        facts_text = "; ".join(
                            f"{known_fact.predicate} = {known_fact.value}"
                            for known_fact in sorted(
                                user_facts,
                                key=lambda known_fact: known_fact.updated_at,
                                reverse=True,
                            )
                        )
                        responses.append(
                            f"Tengo registrado sobre vos: {facts_text}."
                        )
                        operations.append({
                            "action": item.action,
                            "status": "found",
                            "count": len(user_facts),
                        })

                    continue



                # Priorizar la coincidencia exacta.
                fact = self._semantic_memory.get(subject, predicate)

                # Si no existe una coincidencia exacta, buscar semánticamente.
                if fact is None:
                    matches = self._semantic_retriever.search(
                        original_text,
                        limit=10,
                    )
                    fact = next(
                        (
                            match.fact
                            for match in matches
                            if match.fact.subject == subject
                        ),
                        None,
                    )

                if fact is None:
                    responses.append(
                        f"Todavía no tengo registrado ese dato: {predicate}."
                    )
                    operations.append({
                        "action": item.action,
                        "status": "not_found",
                        "predicate": predicate,
                    })
                else:
                    responses.append(
                        f"Tengo registrado que {fact.predicate} es {fact.value}."
                    )
                    operations.append({
                        "action": item.action,
                        "status": "found",
                        "predicate": fact.predicate,
                        "value": fact.value,
                    })

                continue

            user_facts = [
                fact for fact in self._semantic_memory.find_by_subject("user")
                if fact.source == "user"
            ]
            if not user_facts:
                responses.append("Todavía no tengo ningún dato que me hayas pedido recordar.")
                operations.append({"action": item.action, "status": "not_found"})
            else:
                fact = max(user_facts, key=lambda known_fact: known_fact.updated_at)
                responses.append(f"Me pediste recordar: {fact.predicate} = {fact.value}.")
                operations.append({
                    "action": item.action,
                    "status": "found",
                    "predicate": fact.predicate,
                    "value": fact.value,
                })

        message = " ".join(responses)
        return ExecutionResult(
            success=True,
            message=message,
            output={"operations": operations},
            metadata={"action": intent.action, "original_text": original_text, "response": message},
        )

    async def execute(
        self,
        text: str,
    ) -> ExecutionResult:

        total_started_at = time.perf_counter()

        timings: dict[str, float] = {}

        #
        # ---------------------------------------------------------
        # 1. MEMORY
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        self._memory.add(
            "user_request",
            {
                "text": text,
            },
        )

        self._presence_events.emit_state(
        "listening",
        message="NEXUS recibió una solicitud.",
        )

        timings["memory"] = (
            time.perf_counter()
            - stage_started_at
        )

        #
        # ---------------------------------------------------------
        # 2. CONTEXTO COGNITIVO
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        memory_context = (
    self._context_builder.build(
        self._memory,
        semantic_query=text,
    )
)

        timings["cognitive_context"] = (
            time.perf_counter()
            - stage_started_at
        )

        self._memory.add(
            "cognitive_context",
            memory_context,
        )

        self._presence_events.emit_state(
            "understanding",
            message="NEXUS recuperó el contexto relevante.",
        )

        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        capabilities = self._runtime.tool_registry.describe()

        if self._cognitive_capability_router is not None:
            cognitive_operations = (
                self._cognitive_capability_router.available_operations()
            )

            capabilities = [
                *capabilities,
                *[
                    {
                        "action": operation.action,
                        "capability": operation.capability,
                        "operation": operation.operation,
                        "type": "cognitive",
                    }
                    for operation in cognitive_operations
                ],
            ]

        timings["capabilities"] = (
            time.perf_counter()
            - stage_started_at
        )

        #
        # ---------------------------------------------------------
        # 4. INTENT
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        self._presence_events.emit_state(
            "thinking",
            message="NEXUS está interpretando la solicitud.",
        )

        intent = (
            await self._intent_provider.recognize(
                text,
                capabilities,
                memory_context,
            )
        )

        timings["intent"] = (
            time.perf_counter()
            - stage_started_at
        )

        self._memory.add(
            "intent",
            {
                "action": intent.action,
                "confidence": intent.confidence,
                "parameters": intent.parameters,
                "original_text": intent.original_text,
            },
        )

        semantic_memory_result = self._handle_semantic_memory_intent(intent, text)
        if semantic_memory_result is not None:
            semantic_memory_result.metadata = {
                **semantic_memory_result.metadata,
                "timings": {
                    **timings,
                    "total": time.perf_counter() - total_started_at,
                },
            }
            self._memory.add(
                "execution_result",
                {
                    "success": semantic_memory_result.success,
                    "message": semantic_memory_result.message,
                    "output": semantic_memory_result.output,
                    "metadata": semantic_memory_result.metadata,
                },
            )
            self._presence_events.emit_state(
                "completed",
                message=semantic_memory_result.message,
                data={"action": intent.action},
            )
            return semantic_memory_result

        #
        # ---------------------------------------------------------
        # 5. DECISION
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        self._presence_events.emit_state(
            "deciding",
            message="NEXUS está evaluando la acción.",
            data={
                "intent": intent.action,
                "confidence": intent.confidence,
            },
        )

        cognitive_capability = None
        cognitive_capability_result = None

        if self._cognitive_capability_router is not None:
            cognitive_capability = self._cognitive_capability_router.select(
                action=intent.action,
                parameters=intent.parameters,
            )

        if cognitive_capability is not None:
            self._memory.add(
                "cognitive_capability",
                {
                    "capability": cognitive_capability.capability,
                    "operation": cognitive_capability.operation,
                    "parameters": dict(
                        cognitive_capability.parameters,
                    ),
                },
            )

            cognitive_capability_result = (
                self._cognitive_capability_router.invoke(
                    cognitive_capability,
                    context=memory_context,
                    assistant_context=self._assistant_context,
                )
            )

            self._memory.add(
                "cognitive_capability_result",
                {
                    "operation": cognitive_capability.operation,
                    "result": cognitive_capability_result,
                },
            )

            cognitive_capability_summary = (
                self._cognitive_capability_router.summarize_operation_result(
                    result=cognitive_capability_result,
                    operation=cognitive_capability.operation,
                )
            )

            memory_context = {
    **memory_context,
    "cognitive_capability_result": cognitive_capability_result,
    "cognitive_capability_summary": cognitive_capability_summary,
    "cognitive_evidence": {
    "operation": cognitive_capability_summary["operation"],
    "status": cognitive_capability_summary["status"],
    "has_results": cognitive_capability_summary["has_results"],
    "result_count": cognitive_capability_summary["result_count"],
},
}

        decision = self._decision_engine.decide(
            intent=intent,
            context=memory_context,
            capabilities=capabilities,
        )

        timings["decision"] = (
            time.perf_counter()
            - stage_started_at
        )

        self._memory.add(
            "decision",
            {
                "decision_id": decision.decision_id,
                "selected_action": (
                    decision.selected_action
                ),
                "confidence": decision.confidence,
                "reason": decision.reason,
                "requires_execution": (
                    decision.requires_execution
                ),
                "alternatives": list(
                    decision.alternatives
                ),
                "metadata": dict(
                    decision.metadata
                ),
            },
        )

        #
        # ---------------------------------------------------------
        # 6. INTENT DESCONOCIDO
        # ---------------------------------------------------------
        #


        if intent.action == "system.unknown":

            normalized_text = re.sub(
                r"[¿?¡!.,;:]+",
                "",
                text.lower().strip(),
            )

            greetings = {
                "hola",
                "hola nexus",
                "buenas",
                "buen día",
                "buen dia",
                "buenos días",
                "buenos dias",
                "buenas tardes",
                "buenas noches",
                "hey",
                "qué tal",
                "que tal",
            }

            is_greeting = normalized_text in greetings

            if is_greeting:
                message = (
                    "¡Hola! Soy NEXUS. "
                    "¿En qué puedo ayudarte?"
                )
            else:
                message = (
                    "NEXUS no pudo determinar "
                    "qué acción realizar."
                )

            result = ExecutionResult(
                success=is_greeting,
                message=message,
                output={},
                metadata={
                    "action": intent.action,
                    "original_text": text,
                    "decision": {
                        "decision_id": decision.decision_id,
                        "selected_action": decision.selected_action,
                        "confidence": decision.confidence,
                        "reason": decision.reason,
                        "requires_execution": decision.requires_execution,
                    },
                    "timings": {
                        **timings,
                        "total": (
                            time.perf_counter()
                            - total_started_at
                        ),
                    },
                },
            )

            result.metadata = {
    **result.metadata,
    "response": (
        message
        if is_greeting
        else self._response_formatter.format(result)
    ),
}

            self._memory.add(
                "execution_result",
                {
                    "success": result.success,
                    "message": result.message,
                    "output": result.output,
                    "metadata": result.metadata,
                },
            )

            self._presence_events.emit_state(
                "ready" if is_greeting else "failed",
                message=message,
                data={"action": intent.action},
            )

            return result


        # Las consultas cognitivas de Rules y Processes ya fueron
        # resueltas por sus capabilities. No deben volver a Runtime.
        if (
            cognitive_capability is not None
            and cognitive_capability.capability in {"rules", "processes"}
            and cognitive_capability.operation == "find_relevant"
            and (
                decision.is_executable
                or (
                    isinstance(cognitive_capability_summary, dict)
                    and cognitive_capability_summary.get("status") == "empty"
                )
            )
        ):
            capability_name = cognitive_capability.capability
            operation = f"{capability_name}.find_relevant"
            collection_name = capability_name

            items = getattr(
                cognitive_capability_result,
                collection_name,
                (),
            )

            item_items = []
            for item in items:
                item_status = getattr(item, "status", None)
                if hasattr(item_status, "value"):
                    item_status = item_status.value
                elif item_status is not None:
                    item_status = str(item_status)

                item_items.append(
                    {
                        "id": getattr(item, "id", None),
                        "name": getattr(item, "name", None),
                        "description": getattr(item, "description", None),
                        "status": item_status,
                    }
                )

            result = ExecutionResult(
                success=True,
                message=f"Consulta cognitiva de {capability_name.title()} completada.",
                output={
                    "operation": operation,
                    "status": "found" if item_items else "empty",
                    collection_name: item_items,
                    "total": len(item_items),
                },
                metadata={
                    "action": intent.action,
                    "original_text": text,
                    "cognitive_summary": cognitive_capability_summary,
                    "decision": {
                        "decision_id": decision.decision_id,
                        "selected_action": decision.selected_action,
                        "confidence": decision.confidence,
                        "reason": decision.reason,
                        "requires_execution": decision.requires_execution,
                    },
                },
            )

            response_text = self._response_formatter.format(result)
            total_time = time.perf_counter() - total_started_at

            result.metadata = {
                **result.metadata,
                "response": response_text,
                "timings": {
                    **timings,
                    "total": total_time,
                },
            }

            self._memory.add(
                "execution_result",
                {
                    "success": result.success,
                    "message": result.message,
                    "output": result.output,
                    "metadata": result.metadata,
                },
            )

            self._presence_events.emit_state(
                "completed",
                message=result.message,
                data={
                    "action": intent.action,
                    "result_count": len(item_items),
                },
            )

            return result


        # Las consultas cognitivas de Documents ya fueron resueltas
        # por la capability. No deben volver a ejecutarse en Runtime.
        if (
            cognitive_capability is not None
            and cognitive_capability.capability == "documents"
            and cognitive_capability.operation == "find_relevant"
            and (
                decision.is_executable
                or (
                    isinstance(cognitive_capability_summary, dict)
                    and cognitive_capability_summary.get("status") == "empty"
                )
            )
        ):
            query_result = getattr(
                cognitive_capability_result,
                "query",
                None,
            )
            documents = getattr(
                cognitive_capability_result,
                "documents",
                (),
            )

            document_items = [
                {
                    "name": getattr(document, "name", None),
                    "mime_type": getattr(document, "mime_type", None),
                    "description": getattr(document, "description", None),
                    "source": getattr(document, "source", None),
                }
                for document in documents
            ]

            result = ExecutionResult(
                success=True,
                message="Consulta cognitiva de Documents completada.",
                output={
                    "operation": "documents.find_relevant",
                    "status": (
                        "found" if document_items else "empty"
                    ),
                    "documents": document_items,
                    "total": getattr(
                        query_result,
                        "total",
                        len(document_items),
                    ),
                    "offset": getattr(query_result, "offset", 0),
                    "limit": getattr(query_result, "limit", None),
                    "has_more": getattr(
                        query_result,
                        "has_more",
                        False,
                    ),
                },
                metadata={
                    "action": intent.action,
                    "original_text": text,
                    "cognitive_summary": cognitive_capability_summary,
                    "decision": {
                        "decision_id": decision.decision_id,
                        "selected_action": decision.selected_action,
                        "confidence": decision.confidence,
                        "reason": decision.reason,
                        "requires_execution": decision.requires_execution,
                    },
                },
            )

            response_text = self._response_formatter.format(result)
            total_time = time.perf_counter() - total_started_at

            result.metadata = {
                **result.metadata,
                "response": response_text,
                "timings": {
                    **timings,
                    "total": total_time,
                },
            }

            self._memory.add(
                "execution_result",
                {
                    "success": result.success,
                    "message": result.message,
                    "output": result.output,
                    "metadata": result.metadata,
                },
            )

            self._presence_events.emit_state(
                "completed",
                message="Consulta cognitiva de Documents completada.",
                data={
                    "action": intent.action,
                    "result_count": len(document_items),
                },
            )

            return result



        #
        # ---------------------------------------------------------
        # 7. DECISION BLOCK
        # ---------------------------------------------------------
        #

        if not decision.is_executable:

            result = ExecutionResult(
                success=False,
                message=(
                    "NEXUS decidió no ejecutar "
                    "la acción solicitada."
                ),
                output={},
                metadata={
                    "action": intent.action,
                    "original_text": text,
                    "decision": {
                        "decision_id": (
                            decision.decision_id
                        ),
                        "selected_action": (
                            decision.selected_action
                        ),
                        "confidence": (
                            decision.confidence
                        ),
                        "reason": decision.reason,
                        "requires_execution": (
                            decision.requires_execution
                        ),
                        "alternatives": list(
                            decision.alternatives
                        ),
                    },
                    "timings": {
                        **timings,
                        "total": (
                            time.perf_counter()
                            - total_started_at
                        ),
                    },
                },
            )

            result.metadata = {
                **result.metadata,
                "response": (
                    self._response_formatter.format(
                        result
                    )
                ),
            }

            self._memory.add(
                "execution_result",
                {
                    "success": result.success,
                    "message": result.message,
                    "output": result.output,
                    "metadata": result.metadata,
                },
            )

            self._presence_events.emit_state(
                "needs_confirmation",
                message="NEXUS decidió no ejecutar la acción.",
                data={
                    "action": intent.action,
                    "decision": decision.reason,
                },
            )

            return result

        #
        # ---------------------------------------------------------
        # 8. OBJECTIVE
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        objective = (
            self._objective_factory.create(
                intent
            )
        )

        timings["objective"] = (
            time.perf_counter()
            - stage_started_at
        )

        self._memory.add(
            "objective",
            objective.model_dump(),
        )

        #
        # ---------------------------------------------------------
        # 9. PLAN
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        plan = self._planner.create_plan(
            objective,
            intent,
        )

        timings["planner"] = (
            time.perf_counter()
            - stage_started_at
        )

        self._memory.add(
            "plan",
            plan.model_dump(),
        )

        #
        # ---------------------------------------------------------
        # 10. EXECUTION CONTEXT
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        user = getattr(self._assistant_context, "user", None)
        actor_id = getattr(user, "id", None)

        if isinstance(actor_id, str) and actor_id.strip():
            actor_id = actor_id.strip()
            actor_type = "user"
        else:
            actor_id = self._default_actor_id
            actor_type = self._default_actor_type

        execution_context = ExecutionContext(
            objective=objective,
            plan=plan,
            actor_id=actor_id,
            actor_type=actor_type,
        )

        timings["execution_context"] = (
            time.perf_counter()
            - stage_started_at
        )

        #
        # ---------------------------------------------------------
        # 11. RUNTIME
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        self._presence_events.emit_state(
            "executing",
            message="NEXUS está ejecutando la acción.",
            data={
                "action": intent.action,
            },
        )

        result = await self._runtime.execute(
            execution_context
        )

        timings["runtime"] = (
            time.perf_counter()
            - stage_started_at
        )

        #
        # ---------------------------------------------------------
        # 12. VERIFICATION
        # ---------------------------------------------------------
        #

        stage_started_at = time.perf_counter()

        self._presence_events.emit_state(
            "verifying",
            message="NEXUS está verificando el resultado.",
            data={
                "action": intent.action,
            },
        )

        verification = self._verifier.verify(
            objective=objective,
            plan=plan,
            result=result,
        )

        timings["verification"] = (
            time.perf_counter()
            - stage_started_at
        )

        self._memory.add(
            "verification",
            {
                "verified": verification.verified,
                "confidence": (
                    verification.confidence
                ),
                "reason": verification.reason,
                "evidence": list(
                    verification.evidence
                ),
                "metadata": dict(
                    verification.metadata
                ),
            },
        )

        #
        # ---------------------------------------------------------
        # 13. ESTADO FINAL DEL OBJECTIVE
        # ---------------------------------------------------------
        #

        self._memory.add(
            "objective",
            objective.model_dump(),
        )

        #
        # ---------------------------------------------------------
        # 14. ESTADO FINAL DEL PLAN
        # ---------------------------------------------------------
        #

        self._memory.add(
            "plan_final",
            plan.model_dump(),
        )

        #
        # ---------------------------------------------------------
        # 15. RESPONSE + EXECUTION RESULT
        # ---------------------------------------------------------
        #

        total_time = (
            time.perf_counter()
            - total_started_at
        )

        timings["total"] = total_time

        result.metadata = {
            **result.metadata,
            "decision": {
                "decision_id": (
                    decision.decision_id
                ),
                "selected_action": (
                    decision.selected_action
                ),
                "confidence": decision.confidence,
                "reason": decision.reason,
                "requires_execution": (
                    decision.requires_execution
                ),
                "alternatives": list(
                    decision.alternatives
                ),
            },
            "verification": {
                "verified": (
                    verification.verified
                ),
                "confidence": (
                    verification.confidence
                ),
                "reason": verification.reason,
                "evidence": list(
                    verification.evidence
                ),
                "metadata": dict(
                    verification.metadata
                ),
            },
        }

        response_text = (
            self._response_formatter.format(
                result
            )
        )

        result.metadata = {
            **result.metadata,
            "response": response_text,
            "timings": timings,
        }

        self._memory.add(
            "execution_result",
            {
                "success": result.success,
                "message": result.message,
                "output": result.output,
                "artifacts": result.artifacts,
                "metadata": result.metadata,
                "execution_time": result.execution_time,
            },
        )

        #
        # ---------------------------------------------------------
        # 16. MEMORIA EPISÓDICA
        # ---------------------------------------------------------
        #
        # Solamente registramos acciones externas
        # exitosas Y verificadas.
        #
        # Esto es importante:
        #
        # ejecución exitosa
        #        ≠
        # objetivo confirmado
        #
        # El episodio pasa a memoria solamente cuando
        # existe evidencia suficiente para considerar
        # alcanzado el objetivo.
        #

        action = (
            self._runtime.action_registry.get(
                intent.action
            )
        )

        if (
            action is not None
            and not action.internal
            and result.success
            and verification.verified
        ):

            episode = Episode(
                action=intent.action,
                parameters=intent.parameters.copy(),
                original_text=text,
                success=True,
                output=result.output,
            )

            self._episode_memory.add(
                episode
            )

            #
            # -----------------------------------------------------
            # APRENDIZAJE SEMÁNTICO
            # -----------------------------------------------------
            #
            # Solamente aprendemos de experiencias
            # externas exitosas y verificadas.
            #

            self._semantic_knowledge_extractor.extract(
                episode
            )

        #
        # ---------------------------------------------------------
        # 17. ERROR
        # ---------------------------------------------------------
        #

        if not result.success:

            self._memory.add(
                "error",
                {
                    "message": result.message,
                    "action": intent.action,
                    "original_text": text,
                },
            )

        #
        # ---------------------------------------------------------
        # 18. VERIFICACIÓN FALLIDA
        # ---------------------------------------------------------
        #

        elif not verification.verified:

            self._memory.add(
                "verification_failure",
                {
                    "action": intent.action,
                    "original_text": text,
                    "reason": verification.reason,
                    "confidence": (
                        verification.confidence
                    ),
                    "evidence": list(
                        verification.evidence
                    ),
                },
            )

        if result.success and verification.verified:
            self._presence_events.emit_state(
                "completed",
                message="NEXUS completó y verificó la acción.",
                data={
                    "action": intent.action,
                    "verification_confidence": (
                        verification.confidence
                    ),
                },
            )
        else:
            self._presence_events.emit_state(
                "failed",
                message="NEXUS no pudo completar y verificar la acción.",
                data={
                    "action": intent.action,
                    "verification_confidence": (
                        verification.confidence
                    ),
                },
            )

        return result
