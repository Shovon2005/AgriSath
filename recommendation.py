def soil_assessment(data):

    issues = []

    ph = data["ph"]
    organic_matter = data["organic_matter"]
    nitrogen = data["N"]
    phosphorus = data["P"]
    potassium = data["K"]

    # pH assessment
    if ph < 5.5:
        issues.append("Soil is relatively acidic.")
    elif ph > 8.0:
        issues.append("Soil is relatively alkaline.")
    else:
        issues.append("Soil pH is within the configured assessment range.")

    # Nutrient assessment
    if nitrogen < 30:
        issues.append("Nitrogen level is relatively low.")

    if phosphorus < 30:
        issues.append("Phosphorus level is relatively low.")

    if potassium < 30:
        issues.append("Potassium level is relatively low.")

    if organic_matter < 3:
        issues.append("Organic matter is relatively low.")

    if len(issues) <= 1:
        status = "Good"
    elif len(issues) <= 3:
        status = "Needs Attention"
    else:
        status = "Poor"

    return {
        "status": status,
        "issues": issues
    }


def irrigation_recommendation(data):

    moisture = data["soil_moisture"]
    temperature = data["temperature"]
    humidity = data["humidity"]
    rainfall = data["rainfall"]

    # Very dry soil
    if moisture < 15:

        if temperature > 30:
            return {
                "priority": "High",
                "message": "Irrigation is strongly recommended."
            }

        return {
            "priority": "Medium",
            "message": "Irrigation is recommended."
        }

    # Moderate moisture
    elif moisture < 22:

        if temperature > 30 and humidity < 50:
            return {
                "priority": "Medium",
                "message": "Monitor moisture and consider irrigation."
            }

        return {
            "priority": "Low",
            "message": "Monitor soil moisture."
        }

    # Good moisture
    else:

        if rainfall > 150:
            return {
                "priority": "Low",
                "message": "No immediate irrigation required."
            }

        return {
            "priority": "Low",
            "message": "Soil moisture is currently adequate."
        }


def fertilizer_recommendation(data):

    n = data["N"]
    p = data["P"]
    k = data["K"]

    recommendations = []

    if n < 30:
        recommendations.append(
            "Nitrogen level is relatively low."
        )

    if p < 30:
        recommendations.append(
            "Phosphorus level is relatively low."
        )

    if k < 30:
        recommendations.append(
            "Potassium level is relatively low."
        )

    if not recommendations:
        recommendations.append(
            "No major NPK deficiency detected under the configured rules."
        )

    return recommendations


def risk_assessment(data):

    risks = []

    frost = data["frost_risk"]
    pest = data["pest_pressure"]

    if frost > 70:
        risks.append("High frost-risk indicator.")

    if pest > 70:
        risks.append("High pest-pressure indicator.")

    if not risks:
        risks.append("No major environmental risk indicator detected.")

    return risks