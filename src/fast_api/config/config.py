import pathlib
import os
import fast_api


PACKAGE_ROOT = pathlib.Path(fast_api.__file__).resolve().parent



result_columns = ['TotalCharges','Month-to-month','One year','Two year','PhoneService','tenure']
pre_processing_columns = ['customerID','TotalCharges','Contract','PhoneService','tenure']


alias_to_attr_map = {
            'Month-to-month': 'Month_to_month',
            'One year': 'One_year',
            'Two year': 'Two_year'
}





MODEL_NAME = 'churn_model.pickle'
SAVE_MODEL_PATH = os.path.join(PACKAGE_ROOT,'trained_model')