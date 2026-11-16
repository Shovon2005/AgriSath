"""
Machine learning pipeline definition.
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from agrisathi.core.schemas import CATEGORICAL_FEATURES, NUMERIC_FEATURES


KNOWN_CATEGORIES = {
    "soil_type": ["Clay", "Loamy", "Sandy"],
    "growth_stage": ["Flowering", "Maturity", "Seedling", "Vegetative"],
    "water_source_type": ["Canal", "Groundwater", "Rainwater", "River"],
}


def build_pipeline(
    n_estimators: int = 300,
    random_state: int = 42,
    max_depth: int = None,
) -> Pipeline:
    """Build production scikit-learn pipeline."""
    categories_list = [
        KNOWN_CATEGORIES[col] for col in CATEGORICAL_FEATURES
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    categories=categories_list,
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        max_depth=max_depth,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
