import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import joblib

def process_json(json_str):
    json_data = json.loads(json_str)
    input_df = pd.DataFrame([json_data])
    return input_df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python a.py 'json_data'")
        sys.exit(1)

    json_data_str = sys.argv[1]
    input_df = process_json(json_data_str)

    # model = load_model('final_model_pycaret')

    # predictions = predict_model(model, data=input_df)

    print(input_df[0])
