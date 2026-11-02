import asyncio

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import jobs.manager as manager_module

from core.database import get_connection


WATCH_PATH = r"C:\Users\cdi40\Desktop"


class FolderHandler(FileSystemEventHandler):

    def on_created(self, event):

        # ignorar carpetas
        if event.is_directory:
            return

        print(f"📁 Nuevo archivo detectado: {event.src_path}")

        try:

            # =========================
            # CARGAR TRIGGERS
            # =========================
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT *
                FROM triggers
                WHERE enabled = TRUE
            """)

            triggers = cur.fetchall()

            conn.close()

            print(f"⚡ Triggers activos: {len(triggers)}")

            # =========================
            # EVALUAR TRIGGERS
            # =========================
            for trigger in triggers:

                config = trigger["config"] or {}

                ext = config.get("ext")

                if not ext:
                    continue

                print(f"🔍 Evaluando trigger: {ext}")

                # match extensión
                if event.src_path.lower().endswith(ext.lower()):

                    print(f"🔥 Trigger match: {ext}")

                    workflow_id = trigger["workflow_id"]

                    tenant_id = trigger["tenant_id"]

                    print(
                        f"🚀 Ejecutando workflow: {workflow_id}"
                    )

                    asyncio.run(
                        manager_module.manager.create_job(
                            workflow_id,
                            tenant_id
                        )
                    )

        except Exception as e:

            print(f"❌ Trigger error: {e}")


def start_folder_trigger():

    observer = Observer()

    observer.schedule(
        FolderHandler(),
        WATCH_PATH,
        recursive=False
    )

    observer.start()

    print(f"👀 Watching folder: {WATCH_PATH}")

    return observer