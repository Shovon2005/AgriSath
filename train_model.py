import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# 1. LOAD DATASET
# ==========================================

df = pd.read_csv("Crop_recommendationV2.csv")

print("Dataset shape:", df.shape)


# ==========================================
# 2. FEATURES
# ==========================================

features = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "soil_moisture",
    "soil_type",
    "sunlight_exposure",
    "wind_speed",
    "co2_concentration",
    "organic_matter",
    "irrigation_frequency",
    "crop_density",
    "pest_pressure",
    "fertilizer_usage",
    "growth_stage",
    "urban_area_proximity",
    "water_source_type",
    "frost_risk",
    "water_usage_efficiency"
]

X = df[features]
y = df["label"]


# ==========================================
# 3. CATEGORICAL FEATURES
# ==========================================

categorical_features = [
    "soil_type",
    "growth_stage",
    "water_source_type"
]

numeric_features = [
    feature for feature in features
    if feature not in categorical_features
]


# ==========================================
# 4. PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# ==========================================
# 5. RANDOM FOREST
# ==========================================

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 6. COMPLETE PIPELINE
# ==========================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ==========================================
# 7. TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==========================================
# 8. TRAIN
# ==========================================

print("\nTraining model...")

pipeline.fit(X_train, y_train)


# ==========================================
# 9. EVALUATION
# ==========================================

y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# ==========================================
# 10. CREATE MODEL FOLDER
# ==========================================

os.makedirs("model", exist_ok=True)


# ==========================================
# 11. SAVE PIPELINE
# ==========================================

joblib.dump(
    pipeline,
    "model/crop_model.pkl"
)

joblib.dump(
    features,
    "model/feature_info.pkl"
)

print("\n==============================")
print("MODEL SAVED SUCCESSFULLY")
print("==============================")
print("model/crop_model.pkl")
print("model/feature_info.pkl")