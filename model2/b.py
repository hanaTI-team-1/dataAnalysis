import logging
import json
import pandas as pd
import pickle
from pycaret.clustering import *
import sys
import os

if __name__ == "__main__":
    try:
        with open('kmeans_model_2.pkl', 'rb') as file:
          loaded_model = pickle.load(file)

        # 로드된 모델 사용
        #print(loaded_model)
        clustered_data=pd.read_csv("clustered_data.csv")

        json_data_str = sys.stdin.read()
        if not json_data_str:
            raise ValueError("no input")
        sampleData = json.loads(json_data_str)
        # sampleJson = '{"dongName":"신림동", "policeOffice":"1", "subway":"3", "school":"1", "mart":"1", "bus":"3", "price":"10000"}'
        # sampleData = json.loads(sampleJson)

        police = {"1":0,"2":1,"3":2}
        school = {"1":1,"2":3,"3":5}
        mart={"1":0,"2":1,"3":3}
        subway={"1":0.72,"2":0.5,"3":0.35}
        bus={"1":15,"2":30,"3":45}

        police_data = police[sampleData["policeOffice"]]
        school_data = school[sampleData["school"]]
        subway_data = subway[sampleData["subway"]]
        mart_data = mart[sampleData["mart"]]
        dong_data = sampleData["dongName"]
        price=int(sampleData["price"])
        bus_data = bus[sampleData["bus"]]

        columns = ['PRC', '500m_내_마트수', '500m_내_버스수','500m_내_경찰수', '500m_내_학교수', '가장가까운지하철거리']
        data=[[price, mart_data, bus_data, police_data, school_data, subway_data]]
        input_df = pd.DataFrame(data, columns=columns)

        clustering_setup = setup(data=clustered_data,
                                normalize=True,
                                ignore_features=['ATCLNO', '동', 'Cluster'],
                                session_id=123,
                                verbose=False
                                )

        # kmeans = create_model('kmeans', verbose=False)
        prd_df = predict_model(loaded_model,data=input_df)

        cluster = prd_df["Cluster"].values[0]
        clustered_data = clustered_data[clustered_data["동"] == dong_data]
        clustered_df = clustered_data[clustered_data["Cluster"] == prd_df["Cluster"].values[0]]


        # 정렬
        if sampleData["policeOffice"] == "3" :
          clustered_df.sort_values(by=["500m_내_경찰수"], inplace=True)
        if sampleData["school"] == "3" :
          clustered_df.sort_values(by=["500m_내_학교수"], inplace=True)
        if sampleData["subway"] == "3" :
          clustered_df.sort_values(by=["가장가까운지하철거리"], ascending=False, inplace=True)
        if sampleData["bus"] == "3" :
          clustered_df.sort_values(by=["500m_내_버스수"], inplace=True)
        if sampleData["mart"] == "3" :
          clustered_df.sort_values(by=["500m_내_마트수"], inplace=True)

        clustered_df = clustered_df[0:10]

        # json 변경
        json_data = clustered_df["ATCLNO"].values.tolist()

        json_data.append(cluster)

        result = {
            "data" : json_data
        }
        # clustered_data
        json_result = json.dumps(result)
        print(json_result)

    except Exception as e:
        print(f"Error in main function: {e}", file=sys.stderr)
        sys.exit(1)
