# Importing Dependencies
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

import pickle
import os

app = FastAPI()


model_path = os.path.join(config.SAVE_MODEL_PATH,config.MODEL_NAME)
with open(model_path, 'rb') as f:
         rf_model = pickle.load(f)

 


@app.get('/')
def index():
    return {'message': 'Welcome to Churn Prediction App'}

# defining the function which will make the prediction using the data which the user inputs 
@app.post('/predict')
def predict_loan_status(churn_details:churn_pred_data):


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
    print(f"Details to prediction: {df}")
    # Make predictions
    prediction = rf_model.predict(df)
    print(f"Prediction:  {prediction}")
    

    # Interpret prediction
    pred = 'Stay' if prediction[0] == 1 else 'Leave'

    return {'Status of Churn for customer {}'.format(customerId): pred}

	



if __name__ == '__main__':
	  uvicorn.run(app, host='127.0.0.1', port=8000)