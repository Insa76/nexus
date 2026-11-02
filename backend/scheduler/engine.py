import asyncio
from datetime import datetime
from croniter import croniter

from core.database import get_connection
from jobs.manager import manager


class Scheduler:

    def __init__(self):
        asyncio.create_task(self.loop())

    # =========================
    # LOOP PRINCIPAL
    # =========================

    async def loop(self):

        while True:
            try:
                await self.check_schedules()
            except Exception as e:
                print("🔥 Scheduler loop error:", e)

            await asyncio.sleep(5)

    # =========================
    # CHECK SCHEDULES
    # =========================

    async def check_schedules(self):

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT * FROM schedules WHERE enabled = TRUE AND tenant_id = %s", ("default",))
            rows = cur.fetchall()
        except Exception as e:
              print("⏳ Scheduler DB error:", e)
              return   

        finally:
            try:
                conn.close()
            except:
                pass

        now = datetime.utcnow()

        for row in rows:

            try:

                if row["type"] == "interval":
                    await self.check_interval(row, now)

                elif row["type"] == "cron":
                    await self.check_cron(row, now)

            except Exception as e:
                print("🔥 Scheduler check error:", e)

    # =========================
    # INTERVAL
    # =========================

    async def check_interval(self, row, now):

        interval = int(row["expression"])

        if not row["last_run"]:
            await self.run_schedule(row)
            return

        last = self.parse_datetime(row["last_run"])

        if not last:
            await self.run_schedule(row)
            return

        if (now - last).total_seconds() >= interval:
            await self.run_schedule(row)

    # =========================
    # CRON
    # =========================

    async def check_cron(self, row, now):

        expr = row["expression"]

        base = self.parse_datetime(row["last_run"]) or now

        itr = croniter(expr, base)
        next_run = itr.get_next(datetime)

        if now >= next_run:
            await self.run_schedule(row)

    # =========================
    # RUN
    # =========================

    async def run_schedule(self, row):

        try:

            await manager.create_job(row["workflow"])

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE schedules
                SET last_run = %s
                WHERE id = %s
            """, (
                datetime.utcnow(),
                row["id"]
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print("🔥 Scheduler run error:", e)

    # =========================
    # HELPERS
    # =========================

    def parse_datetime(self, value):

        try:
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(str(value))
        except Exception:
            return None


# =========================
# INIT
# =========================

