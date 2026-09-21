import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object, load_numpy_array_data, evaluate_models

from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier

import mlflow


class ModelTrainer:

    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, best_model, classification_metric):

        with mlflow.start_run():

            mlflow.log_metric("f1_score", classification_metric.f1_score)
            mlflow.log_metric("precision_score", classification_metric.precision_score)
            mlflow.log_metric("recall_score", classification_metric.recall_score)

            mlflow.sklearn.log_model(best_model, "model")

    def train_model(self, x_train, y_train, x_test, y_test):

        models = {
            "Random Forest": RandomForestClassifier(random_state=42),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "KNN": KNeighborsClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(random_state=42),
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
            "AdaBoost": AdaBoostClassifier(random_state=42)
        }

        params = {
            "Random Forest": {
                "n_estimators": [50, 100, 200]
            },
            "Decision Tree": {
                "criterion": ["gini", "entropy", "log_loss"]
            },
            "KNN": {
                "n_neighbors": [5, 7, 9]
            },
            "Gradient Boosting": {
                "learning_rate": [0.1, 0.05, 0.01],
                "n_estimators": [50, 100, 150]
            },
            "Logistic Regression": {},
            "AdaBoost": {
                "learning_rate": [0.1, 0.01],
                "n_estimators": [50, 100, 150]
            }
        }

        model_report = evaluate_models(
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
            models=models,
            params=params
        )

        best_model_score = max(sorted(model_report.values()))

        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]

        best_model = models[best_model_name]

        logging.info(f"Best model found: {best_model_name}")
        logging.info(f"Best model score: {best_model_score}")

        y_train_pred = best_model.predict(x_train)

        classification_train_metric = get_classification_score(
            y_true=y_train,
            y_pred=y_train_pred
        )

        self.track_mlflow(best_model, classification_train_metric)

        y_test_pred = best_model.predict(x_test)

        classification_test_metric = get_classification_score(
            y_true=y_test,
            y_pred=y_test_pred
        )

        self.track_mlflow(best_model, classification_test_metric)

        preprocessor = load_object(
            file_path=self.data_transformation_artifact.transformed_object_file_path
        )

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)

        os.makedirs(model_dir_path, exist_ok=True)

        network_model = NetworkModel(
            preprocessor=preprocessor,
            model=best_model
        )

        save_object(
            self.model_trainer_config.trained_model_file_path,
            obj=network_model
        )

        save_object("final_model/model.pkl", network_model)

        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )

        logging.info(f"Model trainer artifact: {model_trainer_artifact}")

        return model_trainer_artifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:

        try:

            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train = train_arr[:, :-1]
            y_train = train_arr[:, -1]

            x_test = test_arr[:, :-1]
            y_test = test_arr[:, -1]

            model_trainer_artifact = self.train_model(
                x_train,
                y_train,
                x_test,
                y_test
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)