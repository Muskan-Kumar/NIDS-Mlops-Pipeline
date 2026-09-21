import sys,os
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from networksecurity.constant.training_pipeline import TARGET_COLUMN,DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import DataTransformationArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object

class DataTransformation:
    def __init__(self,data_validation_artifact:DataValidationArtifact,data_transformation_config:DataTransformationConfig):
        try:
            self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
            self.data_transformation_config:DataTransformationConfig=data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def get_data_transformer_object(self)->Pipeline:
        logging.info('Entered get_data_transformer method of Transformation class')
        try:
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"initiate KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            processor:Pipeline=Pipeline([('imputer',imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_transformaion(self)->DataTransformationArtifact:
        logging.info('Entered initiate_data_transformation method of DataTransformation class')
        try:
            logging.info('Starting data transformation')
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            train_df=train_df.replace([np.inf,-np.inf],np.nan)
            test_df=test_df.replace([np.inf,-np.inf],np.nan)

            inpute_feature_train_df=train_df.drop(columns=[TARGET_COLUMN,"Timestamp"])
            target_feature_train_df=train_df[TARGET_COLUMN]

            inpute_feature_test_df=test_df.drop(columns=[TARGET_COLUMN,"Timestamp"])
            target_feature_test_df=test_df[TARGET_COLUMN]

            label_encoder=LabelEncoder()
            target_feature_train_df=label_encoder.fit_transform(target_feature_train_df)
            target_feature_test_df=label_encoder.transform(target_feature_test_df)

            preprocessor=self.get_data_transformer_object()
            preprocessor_object=preprocessor.fit(inpute_feature_train_df)
            transformed_input_train_feature=preprocessor_object.transform(inpute_feature_train_df)
            transformed_input_test_feature=preprocessor_object.transform(inpute_feature_test_df)

            train_arr=np.c_[transformed_input_train_feature,target_feature_train_df]
            test_arr=np.c_[transformed_input_test_feature,target_feature_test_df]

            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_object)
            save_object("final_model/preprocessing.pkl",preprocessor_object)
            save_object("final_model/label_encoder.pkl",label_encoder)

            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)