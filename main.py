# Importing Dependencies
import sys
import os

# Add the src directory to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

from fastapi import FastAPI
from pydantic import BaseModel, conint
import uvicorn
import numpy as np
import pandas as pd
import pickle
# Correct: importing the specific class from the module
from fast_api.data.churn_pred_data import churn_pred_data
from fast_api.data import internal_churn_pred_data

from fast_api.processing import preprocessing as pp
from fast_api.config import config
from prometheus_fastapi_instrumentator import Instrumentator

import pickle
import logging

port = int(os.environ.get("PORT", 8000))
app = FastAPI()


model_path = os.path.join(config.SAVE_MODEL_PATH,config.MODEL_NAME)
with open(model_path, 'rb') as f:
         rf_model = pickle.load(f)

    
  
logging.basicConfig(
    filename=config.LOGGING_FILENAME,
    filemode=config.LOGGING_FILEMODE,
    level=getattr(logging, config.LOGGING_LEVEL),  # Convert string level to logging constant
    format=config.LOGGING_FORMAT
)
logger = logging.getLogger(__name__)         

 


@app.get('/')
def index():
    return {'message': 'Welcome to Churn Prediction App'}

# defining the function which will make the prediction using the data which the user inputs 
@app.post('/predict')
def predict_churn_status(churn_details:churn_pred_data):


    data = churn_details.model_dump()
    customerId = data['customerID']
    # Create a DataFrame from the input data for preprocessing
    preprocess_df = pd.DataFrame([data], columns=config.pre_processing_columns)
    
    # Apply the preprocessing pipeline
    transformed_df = pp.pipeline.transform(preprocess_df)
    
    # Extract the transformed data into a dictionary
    result = transformed_df.to_dict(orient='records')[0]


    internal_data = internal_churn_pred_data.dict_to_pydantic({
       
        'Contract': result.get('Contract'),
        'tenure': result.get('tenure'),
        'PhoneService': result.get('PhoneService'),
        'TotalCharges': result.get('TotalCharges'),
        'Month-to-month': result.get('Contract_Month-to-month', 0),
        'One year': result.get('Contract_One year', 0),
        'Two year': result.get('Contract_Two year', 0)
    })
    
    # Extract features for prediction using the internal Pydantic model
    features = [getattr(internal_data, config.alias_to_attr_map.get(column, column)) for column in config.result_columns]
    
    # Create DataFrame for prediction
    df = pd.DataFrame([features], columns=config.result_columns)
    logger.debug("Details to prediction: %s ",df)
    print(f"Details to prediction: {df}")
    # Make predictions
    prediction = rf_model.predict(df)
    logger.debug("Prediction: %s ",prediction)
    print(f"Prediction:  {prediction}")
    

    # Interpret prediction
    pred = 'Stay' if prediction[0] == 1 else 'Leave'

    return {'Status of Churn for customer {}'.format(customerId): pred}

	
if __name__== "__main__":
    uvicorn.run("main:app", host="0.0.0.0",port=port,reload=False,log_config=None)

Instrumentator().instrument(app).expose(app)


#if __name__ == '__main__':
#	 uvicorn.run(app, host='0.0.0.0', port=8000)
   
