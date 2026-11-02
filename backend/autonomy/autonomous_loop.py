import asyncio
import logging

from core.self_model import self_model
from autonomy.worker_controller import adjust_workers
from learning.learning_engine import learning_engine
from brain.anomaly_detector import anomaly_detector
from brain.workflow_optimizer import analyze_workflows, suggest_fixes
from brain.nexus_voice import speak
from realtime.ws import manager as ws

from goals.goals_manager import list_goals
from ai.planner import create_plan, plan_to_workflow


async def autonomous_loop():

    await speak("He iniciado mi ciclo autónomo de monitoreo.")

    while True:

        try:

            # =========================
            # SNAPSHOT DEL SISTEMA
            # =========================

            snapshot = self_model.snapshot()

            # guardar historial
            self_model.history.append(snapshot)

            # evitar crecimiento infinito
            if len(self_model.history) > 100:
                self_model.history.pop(0)

            risk = self_model.evaluate_risk(snapshot)
            health = self_model.health_score(snapshot)

            anomaly = anomaly_detector.detect(self_model.history)

            # =========================
            # VOZ DEL SISTEMA
            # =========================

            await speak(
                f"Estado actual: salud del sistema {health}%, nivel de riesgo {risk}."
            )

            # =========================
            # DETECCIÓN DE ANOMALÍAS
            # =========================

            if anomaly:

                await speak(
                    "He detectado una anomalía en el comportamiento del sistema.",
                    "warning"
                )

            # =========================
            # WORKFLOW OPTIMIZER
            # =========================

            problems = analyze_workflows()

            if problems:

                suggestions = suggest_fixes(problems)

                print("🧠 Nexus suggestions:", suggestions)

                await speak(
                    "He encontrado oportunidades para optimizar algunos workflows."
                )

                await ws.broadcast({
                    "type": "nexus_suggestions",
                    "suggestions": suggestions
                })

            # =========================
            # AJUSTE AUTOMÁTICO WORKERS
            # =========================

            await adjust_workers()

            # =========================
            # LEARNING ENGINE
            # =========================

            learning = learning_engine.analyze_recent_failures()

            if learning:

                learning_engine.save_learning(learning)

                await speak(
                    "He aprendido algo nuevo analizando errores recientes."
                )

                await ws.broadcast({
                    "type": "nexus_learning",
                    "message": learning["message"]
                })

            # =========================
            # GOAL SYSTEM
            # =========================

            goals = list_goals()

            for g in goals:

                if g["status"] != "active":
                    continue

                try:

                    await speak(
                        f"Estoy evaluando el objetivo: {g['goal']}"
                    )

                    plan = create_plan(g["goal"])

                    workflow = plan_to_workflow(plan)

                    await speak(
                        f"He generado un plan para cumplir el objetivo."
                    )

                    await ws.broadcast({
                        "type": "nexus_goal_plan",
                        "goal": g["goal"],
                        "plan": plan,
                        "workflow": workflow
                    })

                except Exception as e:

                    logging.error(f"Goal planning error: {e}")

            # =========================
            # ESTADO GLOBAL DEL SISTEMA
            # =========================

            await ws.broadcast({
                "type": "nexus_state",
                "risk": risk,
                "health": health,
                "anomaly": anomaly,
                "snapshot": snapshot
            })

        except Exception as e:

            logging.error(f"Nexus autonomous loop error: {e}")

            await speak(
                "He encontrado un problema interno en mi ciclo autónomo.",
                "error"
            )

        # =========================
        # INTERVALO LOOP
        # =========================

        await asyncio.sleep(10)