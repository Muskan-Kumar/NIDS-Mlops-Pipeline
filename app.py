import sys,os
import certifi
ca=certifi.where()

from dotenv import load_dotenv
load_dotenv()

mongo_db_url=os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)

import pymongo
import pandas as pd

from fastapi import FastAPI,File,UploadFile,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.constant.training_pipeline import TARGET_COLUMN,DATA_INGESTION_DATABASE_NAME,DATA_INGESTION_COLLECTION_NAME

client=pymongo.MongoClient(mongo_db_url,tlsCAFile=ca)

database=client[DATA_INGESTION_DATABASE_NAME]
collection=database[DATA_INGESTION_COLLECTION_NAME]

app=FastAPI()
origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

templates=Jinja2Templates(directory="./templates")

@app.get("/",tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is Successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)

@app.post("/predict")
async def predict_route(request:Request,file:UploadFile=File(...)):
    try:
        df=pd.read_csv(file.file)

        network_model=load_object("final_model/model.pkl")
        label_encoder=load_object("final_model/label_encoder.pkl")

        df=df.drop(columns=[TARGET_COLUMN,"Timestamp"],errors="ignore")

        y_pred=network_model.predict(df)
        y_pred=label_encoder.inverse_transform(y_pred.astype(int))

        df["predicted_column"]=y_pred

        os.makedirs("prediction_output",exist_ok=True)
        df.to_csv("prediction_output/output.csv",index=False)

        table_html=df.to_html(classes="table table-striped",index=False)

        return templates.TemplateResponse(
            "table.html",
            {
                "request":request,
                "table":table_html
            }
        )

    except Exception as e:
        raise NetworkSecurityException(e,sys)

if __name__=="__main__":
    app_run(app,host="localhost",port=8000)

    