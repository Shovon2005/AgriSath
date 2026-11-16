"""
Backward-compatible wrapper for agronomic recommendation functions.
Delegates to agrisathi.advisory modules while preserving legacy signatures.
"""

from typing import Dict, Any, List
from agrisathi.advisory.soil import assess_soil_health
from agrisathi.advisory.irrigation import calculate_irrigation_advisory
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance
from agrisathi.advisory.risk import assess_environmental_risks


def soil_assessment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy soil assessment wrapper."""
    res = assess_soil_health(data)
    return {
        "status": res["status"],
        "issues": res["issues"],
    }


def irrigation_recommendation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy irrigation recommendation wrapper."""
    res = calculate_irrigation_advisory(data)
    return {
        "priority": res["priority"],
        "message": res["message"],
    }


def fertilizer_recommendation(data: Dict[str, Any]) -> List[str]:
    """Legacy fertilizer recommendation wrapper."""
    res = calculate_fertilizer_guidance(data)
    return res["recommendations"]


def risk_assessment(data: Dict[str, Any]) -> List[str]:
    """Legacy environmental risk assessment wrapper."""
    res = assess_environmental_risks(data)
    return res["risks"]
