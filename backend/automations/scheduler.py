import schedule
import time
import threading
from automations.engine import run_steps


JOBS = []


def add_job(seconds, steps):

    def job():
        print("⏰ Ejecutando tarea programada...")
        run_steps(steps)

    schedule.every(seconds).seconds.do(job)
    JOBS.append(job)


def loop():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print("Scheduler crash:", e)
        time.sleep(1)


def start_scheduler():
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
