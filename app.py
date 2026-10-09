from flask import Flask, render_template, request
import joblib

from recommendation import (
    soil_assessment,
    irrigation_recommendation,
    fertilizer_recommendation,
    risk_assessment
)

from explain import explain_prediction

app = Flask(__name__)

model = joblib.load("model/crop_model.pkl")
features = joblib.load("model/feature_info.pkl")

# Categorical columns
categorical_features = [
    "soil_type",
    "growth_stage",
    "water_source_type"
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    data = {}

    for feature in features:

        value = request.form[feature]

        # Keep categorical values as text
        if feature in categorical_features:
            data[feature] = value

        # Convert numerical values to float
        else:
            data[feature] = float(value)

    # AI prediction
    result = explain_prediction(data)

    crop = result["prediction"]

    # Other recommendations
    soil = soil_assessment(data)
    irrigation = irrigation_recommendation(data)
    fertilizer = fertilizer_recommendation(data)
    risks = risk_assessment(data)

    return render_template(
        "result.html",
        crop=crop,
        soil=soil,
        irrigation=irrigation,
        fertilizer=fertilizer,
        risks=risks,
        important_features=result["important_features"].to_dict("records"),
        probabilities=result["probabilities"].head(5).to_dict("records"),
        input_data=data
    )


if __name__ == "__main__":
    app.run(debug=True)