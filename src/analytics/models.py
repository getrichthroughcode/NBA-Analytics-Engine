"""
NBA ML Models
=============
Machine learning models for NBA predictions.
"""

from typing import Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split

from ..utils.logger import get_logger

logger = get_logger(__name__)


class GameOutcomePredictor:
    """
    Predicts game outcomes (win/loss) based on team statistics.

    Features used:
    - Team offensive/defensive ratings
    - Recent form (last 10 games)
    - Home court advantage
    - Head-to-head record
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.is_trained = False
        logger.info("Game Outcome Predictor initialized")

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for model training/prediction.

        Args:
            data: Raw game data

        Returns:
            Feature DataFrame
        """
        features = pd.DataFrame()

        # Example features (expand based on available data)
        features["offensive_rating"] = data.get("offensive_rating", 0)
        features["defensive_rating"] = data.get("defensive_rating", 0)
        features["net_rating"] = data.get("net_rating", 0)
        features["is_home"] = data.get("is_home", 0).astype(int)
        features["recent_win_pct"] = data.get("recent_win_pct", 0.5)

        return features

    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the model.

        Args:
            X: Feature DataFrame
            y: Target variable (1 for win, 0 for loss)

        Returns:
            Training metrics
        """
        logger.info(f"Training model on {len(X)} samples")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        train_acc = accuracy_score(y_train, self.model.predict(X_train))
        test_acc = accuracy_score(y_test, self.model.predict(X_test))

        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5)

        self.is_trained = True

        metrics = {
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "cv_mean_accuracy": cv_scores.mean(),
            "cv_std_accuracy": cv_scores.std(),
        }

        logger.info(f"Training complete. Test accuracy: {test_acc:.3f}")
        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict game outcomes.

        Args:
            X: Feature DataFrame

        Returns:
            Predicted outcomes (1 for win, 0 for loss)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict win probabilities.

        Args:
            X: Feature DataFrame

        Returns:
            Win probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        return self.model.predict_proba(X)[:, 1]

    def save(self, filepath: str):
        """Save model to disk"""
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")

    def load(self, filepath: str):
        """Load model from disk"""
        self.model = joblib.load(filepath)
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")


class PlayerPerformancePredictor:
    """
    Predicts player performance (points, rebounds, assists) for upcoming games.
    """

    def __init__(self):
        self.points_model = GradientBoostingRegressor(random_state=42)
        self.rebounds_model = GradientBoostingRegressor(random_state=42)
        self.assists_model = GradientBoostingRegressor(random_state=42)
        self.is_trained = False
        logger.info("Player Performance Predictor initialized")

    def train(
        self,
        X: pd.DataFrame,
        y_points: pd.Series,
        y_rebounds: pd.Series,
        y_assists: pd.Series,
    ) -> Dict[str, Dict[str, float]]:
        """
        Train models for points, rebounds, and assists.

        Args:
            X: Feature DataFrame
            y_points: Target points
            y_rebounds: Target rebounds
            y_assists: Target assists

        Returns:
            Training metrics for each stat
        """
        logger.info(f"Training player performance models on {len(X)} samples")

        metrics = {}

        # Train points model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_points, test_size=0.2, random_state=42
        )
        self.points_model.fit(X_train, y_train)
        y_pred = self.points_model.predict(X_test)

        metrics["points"] = {
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        # Train rebounds model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_rebounds, test_size=0.2, random_state=42
        )
        self.rebounds_model.fit(X_train, y_train)
        y_pred = self.rebounds_model.predict(X_test)

        metrics["rebounds"] = {
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        # Train assists model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_assists, test_size=0.2, random_state=42
        )
        self.assists_model.fit(X_train, y_train)
        y_pred = self.assists_model.predict(X_test)

        metrics["assists"] = {
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        self.is_trained = True
        logger.info("Player performance models training complete")

        return metrics

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Predict player statistics.

        Args:
            X: Feature DataFrame

        Returns:
            Dictionary with predicted points, rebounds, assists
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")

        return {
            "points": self.points_model.predict(X),
            "rebounds": self.rebounds_model.predict(X),
            "assists": self.assists_model.predict(X),
        }
