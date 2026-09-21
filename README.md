# Network Intrusion Detection System (NIDS) MLOps Pipeline

A production-ready machine learning project for detecting network intrusions from flow-based network telemetry using a modular MLOps pipeline. The solution combines data ingestion, validation, feature transformation, model training, experiment tracking, and deployment-ready inference into a single end-to-end workflow.

## Overview

This project builds a supervised intrusion detection model that classifies network traffic into different attack categories using network flow features such as packet counts, byte counts, timing metrics, flag counts, and session statistics. The system is designed to be extendable, reproducible, and suitable for real-world ML operations workflows.

The project follows an MLOps-oriented structure with:

- Automated data ingestion from a source CSV dataset
- Schema validation and drift monitoring
- Feature preprocessing with missing-value handling
- Model benchmarking and selection
- MLflow-based experiment tracking
- Model serialization and artifact management
- FastAPI-based prediction service
- Dockerized deployment ready for production use

## Problem Statement

Modern networks are exposed to a wide range of cyber threats, including DoS, probing, brute force, and malicious flow behaviors. Traditional rule-based detection systems often struggle to scale with dynamic and evolving attack patterns. This project addresses that challenge by applying machine learning to analyze network flow behavior and identify anomalous or malicious traffic patterns.

## Key Features

### Data Engineering
- CSV-based dataset ingestion from the network telemetry source
- Feature-store creation for traceable data storage
- Train/test split for robust evaluation
- Data cleaning and invalid value handling
- Support for artifact persistence and tracking

### Data Validation
- Column-level schema validation against a defined schema
- Dataset integrity checks for expected input format
- Drift detection using Kolmogorov-Smirnov 2-sample testing
- Automatic generation of drift reports in YAML format
- Validation artifacts used to gate downstream processing

### Feature Transformation
- KNN imputation for missing values
- Pipeline-based preprocessing workflow
- Label encoding for target classes
- Conversion of raw data into model-ready arrays
- Reusable preprocessing object for inference

### Model Training
- Multiple machine learning algorithms evaluated for comparison
- Candidate models include:
  - Random Forest
  - Decision Tree
  - K-Nearest Neighbors
  - Gradient Boosting
  - Logistic Regression
  - AdaBoost
- Best model selected using model evaluation metrics
- Model artifact generation and persistence
- Final model saved for deployment and inference

### Experiment Tracking and MLOps
- MLflow integration for metrics tracking
- Model metadata and metric logging
- Artifact synchronization with cloud storage using AWS S3 commands
- Structured pipeline configuration for reproducible runs
- Timestamped artifacts for versioned experimentation

### Inference API
- FastAPI application for REST-based serving
- CSV upload endpoint for prediction
- Automatic feature filtering and preprocessing
- Label decoding back to human-readable class names
- Output table rendered in HTML for quick inspection

### Deployment
- Docker support through a production-ready Dockerfile
- Service runs via Uvicorn on port 8000
- Ready to deploy in containerized environments or cloud infrastructure

## Tech Stack

### Core ML / Data Science
- Python
- pandas
- NumPy
- scikit-learn
- MLflow

### Web API / Serving
- FastAPI
- Uvicorn
- Jinja2 Templates
- Static file serving

### Data / Storage
- MongoDB integration via PyMongo
- CSV-based feature store
- YAML schema configuration
- AWS S3 sync for model and artifact storage

### MLOps & Pipeline Engineering
- Modular pipeline architecture
- Config and artifact entities
- Logging and exception handling
- Reproducible training workflows
- Versioned artifacts and final model packaging

### Deployment / Packaging
- Docker
- Python packaging with setuptools
- Environment variable management via dotenv

## Project Architecture

```text
NIDS_MLOps_Pipeline/
├── app.py                          # FastAPI application entry point
├── main.py                        # Manual pipeline execution entry point
├── Dockerfile                     # Container config for deployment
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Modern Python project metadata
├── setup.py                       # Package setup configuration
├── README.md                      # Project documentation
├── Network_Data/
│   └── nids.csv                  # Source network intrusion dataset
├── data_schema/
│   └── schema.yaml                # Expected dataset schema
├── networksecurity/
│   ├── cloud/
│   │   └── s3_syncer.py          # S3 artifact sync helper
│   ├── components/
│   │   ├── data_ingestion.py     # CSV ingestion and split logic
│   │   ├── data_validation.py    # Schema + drift validation
│   │   ├── data_transformation.py# Preprocessing pipeline
│   │   └── model_trainer.py      # Training and model persistence
│   ├── constant/
│   ├── entity/
│   ├── exception/
│   ├── logging/
│   ├── pipeline/
│   │   └── training_pipeline.py  # End-to-end orchestration
│   └── utils/
├── final_model/                   # Final serialized model artifacts
├── Artifacts/                     # Timestamped training artifacts
├── templates/                     # API HTML templates
├── static/                        # Frontend CSS/JS assets
└── prediction_output/             # Prediction output CSVs
```

## End-to-End ML Pipeline

The project follows a standard MLOps lifecycle:

1. Data Ingestion
   - Load the raw network dataset
   - Store it in a feature store
   - Perform train/test split

2. Data Validation
   - Check schema consistency
   - Validate expected column structure
   - Detect concept drift using statistical checks
   - Save drift report for monitoring

3. Data Transformation
   - Replace invalid values and infinities with NaN
   - Apply KNN imputation
   - Encode target labels
   - Convert to numeric arrays for model training

4. Model Training
   - Train multiple classification models
   - Compare performance across models
   - Choose the best-performing model
   - Track evaluation metrics in MLflow

5. Model Packaging
   - Save preprocessing pipeline
   - Save label encoder
   - Save the final model wrapper object
   - Publish model to final_model directory

6. Deployment / Inference
   - Expose the model through FastAPI endpoints
   - Accept uploaded CSV files
   - Run preprocessing + prediction
   - Return output table to the user

## Model Training Strategy

The project evaluates several conventional machine learning classifiers and selects the strongest one based on scoring metrics. This allows for a transparent comparison of model behavior on intrusion detection data.

The training module calculates classification metrics such as:

- Precision
- Recall
- F1-score

These metrics are logged using MLflow to make model comparisons easier and more reproducible.

## API Usage

### Start the application

```bash
python app.py
```

or with Uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Routes

- GET / : Landing page
- GET /train : Runs the full training pipeline
- POST /predict : Upload a CSV file and receive predictions

### Prediction flow

1. User uploads a network traffic CSV file
2. Server reads the uploaded dataset
3. Unwanted columns are removed where necessary
4. Model and label encoder are loaded
5. The trained pipeline predicts traffic class labels
6. Results are saved to prediction_output/output.csv
7. HTML prediction table is returned in the response

## Environment Setup

### Prerequisites
- Python 3.11+
- pip or uv
- Optional: Docker
- AWS CLI configured if using S3 sync features
- MongoDB connection details if using database-backed ingestion flows

### Install dependencies

```bash
pip install -r requirements.txt
```

or using the project metadata:

```bash
pip install -e .
```

### Environment variables

Create a .env file in the project root with the required configuration, such as:

```env
MONGODB_URL_KEY=your_mongo_connection_string
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=your_region
```

## Docker Deployment

```bash
docker build -t nids-mlops-pipeline .
docker run -p 8000:8000 nids-mlops-pipeline
```

The service is exposed on port 8000 and can be integrated into production deployment environments such as Kubernetes, ECS, or Docker Compose.

## Example Workflow

```bash
# Run training pipeline
python main.py

# Or start the app for inference
python app.py
```

Then open the browser at:

```text
http://localhost:8000/
```

## Why This Project Matters

This project demonstrates a practical end-to-end machine learning lifecycle for network security analytics. It is not just a notebook experiment; it reflects real-world engineering practices such as:

- modular code organization
- configuration-driven execution
- validation gates
- artifact tracking
- reusable preprocessing logic
- model deployment through a web API
- cloud-ready storage integration

## Future Enhancements

- Support for additional intrusion classes and modern datasets
- Hyperparameter tuning with Optuna or RandomizedSearchCV
- Model explainability with SHAP or feature importance analysis
- Model monitoring and alerting for drift and performance decay
- CI/CD pipeline for automated retraining and deployment
- Cloud-native deployment with Kubernetes and container orchestration

## License

This project is intended for learning, experimentation, and deployment prototyping in cybersecurity and MLOps workflows. If you plan to use it in a production or organization context, review the licensing and compliance requirements applicable to your environment.

## Contact

For questions, collaboration, or improvements, please reach out through the project repository or contact the repository maintainer.

---

Built for intelligent network security monitoring, automated model lifecycle management, and scalable ML operations.
