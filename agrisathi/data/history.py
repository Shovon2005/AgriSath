"""
Historical Prediction Persistence Repository.
Stores, retrieves, and indexes past agronomic assessments in SQLite (data/history.db).
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from agrisathi.config import Config
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.data.history")


def get_db_connection() -> sqlite3.Connection:
    """Initialize SQLite database and return connection."""
    Config.ensure_directories()
    conn = sqlite3.connect(str(Config.HISTORY_DB_PATH))
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection):
    """Ensure predictions history table exists."""
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                location TEXT NOT NULL,
                season TEXT NOT NULL,
                crop TEXT NOT NULL,
                confidence REAL NOT NULL,
                fertility_class TEXT NOT NULL,
                soil_score INTEGER NOT NULL,
                irrigation_priority TEXT NOT NULL,
                farm_area REAL NOT NULL,
                input_json TEXT NOT NULL,
                advisory_json TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_crop ON predictions_history(crop)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_timestamp ON predictions_history(timestamp)
        """)


def save_prediction_record(
    farm_input: Dict[str, Any],
    prediction: Dict[str, Any],
    advisory: Dict[str, Any],
) -> int:
    """Save an agronomic prediction assessment into SQLite history."""
    try:
        conn = get_db_connection()
        ts = datetime.now(timezone.utc).isoformat()
        loc = str(farm_input.get("location") or "Local Farm")
        season = str(farm_input.get("season") or "Whole Year")
        crop = str(prediction.get("recommended_crop") or "Unknown").title()
        conf = float(prediction.get("confidence") or 0.0)

        soil = advisory.get("soil", {})
        fert_class = str(soil.get("fertility_class") or soil.get("status") or "Medium")
        score = int(soil.get("score") or 75)

        irrig = advisory.get("irrigation", {})
        irrig_prio = str(irrig.get("priority") or "Low")
        area = float(farm_input.get("farm_area") or 1.0)

        # Sanitize for JSON storage (remove non-serializable objects)
        clean_input = {k: v for k, v in farm_input.items() if isinstance(v, (str, int, float, bool, list, dict))}
        clean_advisory = {
            "crop": crop,
            "soil_fertility": fert_class,
            "soil_score": score,
            "irrigation_priority": irrig_prio,
            "irrigation_litres": irrig.get("water_quantity_litres", 0),
            "fertilizer": advisory.get("fertilizer", {}).get("recommendations", []),
            "risks": advisory.get("risks", {}).get("risks", []),
        }

        with conn:
            cur = conn.execute("""
                INSERT INTO predictions_history (
                    timestamp, location, season, crop, confidence,
                    fertility_class, soil_score, irrigation_priority, farm_area,
                    input_json, advisory_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts, loc, season, crop, conf, fert_class, score, irrig_prio, area,
                json.dumps(clean_input), json.dumps(clean_advisory)
            ))
            return cur.lastrowid
    except Exception as e:
        logger.error("Failed to persist prediction history: %s", e)
        return -1


def get_recent_predictions(limit: int = 20, crop_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent predictions, optionally filtered by crop name."""
    try:
        conn = get_db_connection()
        query = "SELECT * FROM predictions_history"
        params = []
        if crop_filter:
            query += " WHERE LOWER(crop) = LOWER(?)"
            params.append(crop_filter.strip())
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cur = conn.execute(query, params)
        rows = cur.fetchall()

        records = []
        for r in rows:
            rec = dict(r)
            try:
                rec["inputs"] = json.loads(rec["input_json"])
            except Exception:
                rec["inputs"] = {}
            try:
                rec["advisory_summary"] = json.loads(rec["advisory_json"])
            except Exception:
                rec["advisory_summary"] = {}
            records.append(rec)
        return records
    except Exception as e:
        logger.error("Failed to query prediction history: %s", e)
        return []


def get_prediction_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single historical prediction record by ID."""
    try:
        conn = get_db_connection()
        cur = conn.execute("SELECT * FROM predictions_history WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["inputs"] = json.loads(rec["input_json"])
        rec["advisory_summary"] = json.loads(rec["advisory_json"])
        return rec
    except Exception as e:
        logger.error("Failed to fetch prediction %s: %s", record_id, e)
        return None


def clear_history() -> bool:
    """Clear all records from prediction history."""
    try:
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM predictions_history")
        return True
    except Exception as e:
        logger.error("Failed to clear history: %s", e)
        return False
