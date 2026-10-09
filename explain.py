import joblib
import pandas as pd


# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load("model/crop_model.pkl")
features = joblib.load("model/feature_info.pkl")


# ==========================================
# CLEAN FEATURE NAME
# ==========================================

def clean_feature_name(name):

    # Remove pipeline prefixes
    name = name.replace("numeric__", "")
    name = name.replace("categorical__", "")

    feature_names = {

        "N": "Nitrogen (N)",
        "P": "Phosphorus (P)",
        "K": "Potassium (K)",

        "temperature": "Temperature",
        "humidity": "Humidity",
        "ph": "Soil pH",
        "rainfall": "Rainfall",

        "soil_moisture": "Soil Moisture",
        "soil_type": "Soil Type",

        "sunlight_exposure": "Sunlight Exposure",
        "wind_speed": "Wind Speed",

        "co2_concentration": "CO₂ Concentration",
        "organic_matter": "Organic Matter",

        "irrigation_frequency": "Irrigation Frequency",
        "crop_density": "Crop Density",
        "pest_pressure": "Pest Pressure",

        "fertilizer_usage": "Fertilizer Usage",
        "growth_stage": "Growth Stage",

        "urban_area_proximity": "Urban Area Proximity",
        "water_source_type": "Water Source",

        "frost_risk": "Frost Risk",
        "water_usage_efficiency": "Water Usage Efficiency"
    }

    # Handle categorical encoded values
    for key, value in feature_names.items():

        if name.startswith(key + "_"):
            category = name.replace(key + "_", "")

            return f"{value}: {category}"

    return feature_names.get(
        name,
        name.replace("_", " ").title()
    )


# ==========================================
# EXPLAIN PREDICTION
# ==========================================

def explain_prediction(data):

    # Create DataFrame
    input_df = pd.DataFrame(
        [data],
        columns=features
    )


    # ==========================================
    # CROP PREDICTION
    # ==========================================

    prediction = model.predict(input_df)[0]


    # ==========================================
    # PREDICTION PROBABILITY
    # ==========================================

    probabilities = model.predict_proba(input_df)[0]

    classes = model.classes_

    probability_df = pd.DataFrame({

        "crop": classes,
        "probability": probabilities

    })

    probability_df = probability_df.sort_values(
        by="probability",
        ascending=False
    )


    # ==========================================
    # FEATURE IMPORTANCE
    # ==========================================

    rf_model = model.named_steps["model"]

    preprocessor = model.named_steps["preprocessor"]

    transformed_features = (
        preprocessor.get_feature_names_out()
    )

    feature_importance = (
        rf_model.feature_importances_
    )


    importance = pd.DataFrame({

        "feature": transformed_features,
        "importance": feature_importance

    })


    importance = importance.sort_values(
        by="importance",
        ascending=False
    )


    # ==========================================
    # CLEAN FEATURE NAMES
    # ==========================================

    importance["feature"] = (
        importance["feature"]
        .apply(clean_feature_name)
    )


    # ==========================================
    # TOP 5
    # ==========================================

    top_features = importance.head(5).copy()


    # ==========================================
    # RETURN RESULT
    # ==========================================

    return {

        "prediction": prediction,

        "probabilities": probability_df,

        "important_features": top_features

    }