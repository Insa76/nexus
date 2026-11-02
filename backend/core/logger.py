import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):

        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }

        if hasattr(record, "extra_data"):
            log_record["data"] = record.extra_data

        return json.dumps(log_record)


logger = logging.getLogger("nexus")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger.addHandler(handler)