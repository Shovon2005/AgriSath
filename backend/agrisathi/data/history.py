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
    conn = sqlite3.connect(str(Config.HISTORY_DB_PATH), timeout=10.0)
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
    conn = None
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
            "soil_details": {
                "status": str(soil.get("status") or "Good"),
                "fertility_class": fert_class,
                "score": score,
                "ph": soil.get("ph"),
                "electrical_conductivity": soil.get("electrical_conductivity"),
                "organic_carbon": soil.get("organic_carbon"),
                "organic_matter": soil.get("organic_matter"),
                "soil_texture": soil.get("soil_texture"),
                "deficiencies": soil.get("deficiencies", []),
                "excesses": soil.get("excesses", []),
                "corrective_actions": soil.get("corrective_actions", []),
            },
            "irrigation_details": {
                "priority": irrig_prio,
                "irrigation_required": irrig.get("irrigation_required", "Scheduled"),
                "next_irrigation_time": irrig.get("next_irrigation_time", "Within 48 hours"),
                "daily_water_requirement_mm": irrig.get("daily_water_requirement_mm", 0.0),
                "water_quantity_litres": irrig.get("water_quantity_litres", 0),
                "water_quantity_m3": irrig.get("water_quantity_m3", 0.0),
                "recommended_actions": irrig.get("recommended_actions", []),
            },
            "fertilizer_details": {
                "recommendations": advisory.get("fertilizer", {}).get("recommendations", []),
                "commercial_fertilizers": advisory.get("fertilizer", {}).get("commercial_fertilizers", {}),
                "total_farm_requirements": advisory.get("fertilizer", {}).get("total_farm_requirements", {}),
                "organic_alternatives": advisory.get("fertilizer", {}).get("organic_alternatives", {}),
                "application_schedule": advisory.get("fertilizer", {}).get("application_schedule", []),
                "deficits": advisory.get("fertilizer", {}).get("deficits", {}),
            },
            "crop_comparison": advisory.get("crop_comparison", {}),
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
    finally:
        if conn is not None:
            conn.close()


def _hydrate_record(row: sqlite3.Row) -> Dict[str, Any]:
    """Hydrate a database row into a dictionary with deserialized JSON subdocuments."""
    rec = dict(row)
    for key, json_col in (("inputs", "input_json"), ("advisory_summary", "advisory_json")):
        try:
            rec[key] = json.loads(rec[json_col])
        except Exception:
            rec[key] = {}
    return rec


def get_recent_predictions(limit: int = 20, crop_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent predictions, optionally filtered by crop name."""
    conn = None
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
        return [_hydrate_record(r) for r in cur.fetchall()]
    except Exception as e:
        logger.error("Failed to query prediction history: %s", e)
        return []
    finally:
        if conn is not None:
            conn.close()


def get_prediction_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single historical prediction record by ID."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.execute("SELECT * FROM predictions_history WHERE id = ?", (record_id,))
        row = cur.fetchone()
        return _hydrate_record(row) if row else None
    except Exception as e:
        logger.error("Failed to fetch prediction %s: %s", record_id, e)
        return None
    finally:
        if conn is not None:
            conn.close()


def clear_history() -> bool:
    """Clear all records from prediction history."""
    conn = None
    try:
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM predictions_history")
        return True
    except Exception as e:
        logger.error("Failed to clear history: %s", e)
        return False
    finally:
        if conn is not None:
            conn.close()
