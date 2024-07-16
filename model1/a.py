# !pip install pycaret
import json
import pandas as pd
from geopy.distance import geodesic
from pycaret.regression import load_model, predict_model
import sys

jeonsePrice = None
school = None
publicSecurity = None
busStop = None
subway = None
mart = None

# 전처리 함수 정의
def convert_new_bldgUsg(bldgUsg):
    if bldgUsg == '아파트':
        return 1
    elif bldgUsg == '연립다세대':
        return 2
    else:
        return 3  # 예외 처리
# "atclCfmYmd" 값을 "20240709" 형식으로 변환하는 함수
def convert_date(date_str):
    parts = date_str.split('.')
    year = "20" + parts[0]
    month = parts[1].zfill(2)
    day = parts[2].zfill(2)
    return year + month + day

# 가장 가까운 지하철역의 거리를 계산하는 함수
def find_closest_station_distance(lat, lon, station_df):
  min_distance = float('inf')
  for i, station in station_df.iterrows():
    dist = geodesic((lat, lon), (station['Latitude'], station['Longitude'])).kilometers
    if dist < min_distance:
      min_distance = dist
  return min_distance

def convert_new_contract_type(contract_type):
    if contract_type == '신규':
        return 1
    elif contract_type == '갱신':
        return 0
    else:
        return None

def format_date(date_str):
    if len(date_str.split('.')[0]) == 2:
        return '20' + date_str
    return date_str

def count_nearby(lat, lon, df):
    count = 0
    for _, dff in df.iterrows():
        dist = geodesic((lat, lon), (dff['Latitude'], dff['Longitude'])).km
        if dist <= 0.5:
            count += 1
    return count

  # 주소에서 구, 본번, 부번 추출하는 함수 정의
def extract_address_parts(address):
    address_parts = address.split()
    gu = address_parts[1]
    dong = address_parts[2]
    main_number_subnumber = address_parts[-1]  # '본번-부번'
    main_number, sub_number = main_number_subnumber.split('-')
    return gu, dong,main_number, sub_number


def transfer(input_df):
  input_df['flrInfo'] = input_df['flrInfo'].apply(lambda x: int(x.split('/')[0]))
  input_df=input_df[['rletTpNm','flrInfo','prc','spc1','lat','lng','address','atclCfmYmd']]
  input_df[['cggNm', 'stdgNm','mno', 'sno']] = input_df['address'].apply(lambda x: pd.Series(extract_address_parts(x)))

  input_df.rename(columns={
      'flrInfo':'flr',
      'spc1':'rentArea',
      'prc' :'grfe',
      'rletTpNm':'bldgUsg'
  }, inplace=True)

  current = pd.to_datetime('now')
  inte_rate=pd.read_csv("inte_rate.csv",encoding='cp949')
  inte_rate=inte_rate.drop_duplicates(['TIME'], keep='first')
  input_df['atclCfmYmd'] = input_df['atclCfmYmd'].apply(convert_date)

  input_df['atclCfmYmd'] = input_df['atclCfmYmd'].astype(str)
  inte_rate['TIME'] = inte_rate['TIME'].astype(str)
  input_df=input_df.merge(inte_rate, how='left', left_on='atclCfmYmd', right_on='TIME')
  input_df['bldgUsg'] = input_df['bldgUsg'].apply(convert_new_bldgUsg)

  return input_df


def infra(newdata):
  school_df=pd.read_csv("school_filtered.csv",encoding='utf-8')
  bus_df=pd.read_excel("bus_seoul_filtered.xlsx")
  shop_df=pd.read_csv("market.csv",encoding='utf-8')
  sub_df=pd.read_csv("station.csv",encoding='utf-8')
  sub_df.dropna(subset=['Latitude'],inplace=True)

  crime_df=pd.read_csv("crime.csv",encoding='utf-8')
  police_df=pd.read_csv("police_add_lo.csv",encoding='utf-8')


  desired_gu = ['관악구', '송파구', '강서구', '강남구', '동작구']
  crime_df = crime_df[crime_df['자치구별'].isin(desired_gu)]


    # 인프라 계산 및 입력 데이터프레임에 추가
  newdata['Closest_Station_Distance'] = find_closest_station_distance(newdata['lat'].iloc[0], newdata['lng'].iloc[0], sub_df)
  newdata['500m_내_마트수'] = count_nearby(newdata['lat'].iloc[0], newdata['lng'].iloc[0], shop_df)
  newdata['500m_내_초중등수'] = count_nearby(newdata['lat'].iloc[0], newdata['lng'].iloc[0], school_df)
  newdata['500m_내_bus수'] = count_nearby(newdata['lat'].iloc[0], newdata['lng'].iloc[0], bus_df)
  newdata['500m_내_경찰서수'] = count_nearby(newdata['lat'].iloc[0], newdata['lng'].iloc[0], police_df)
  newdata = newdata.merge(crime_df, how='left', left_on='cggNm', right_on='자치구별')

  selected_features = ['value', '발생', '검거', 'cggNm', 'stdgNm', 'mno', 'sno', 'flr', 'rentArea',
       'grfe', 'bldgUsg', 'lat', 'lng', '500m_내_초중등수', '500m_내_bus수',
       '500m_내_마트수', 'Closest_Station_Distance']
  newdata = newdata[selected_features]

  return newdata

def process_json(json_str):
  json_data = json.loads(json_str)
  input_df = pd.DataFrame([json_data])
  input_df = transfer(input_df)
  return input_df

# 예측 함수
def predict(input_df):

    # 모델 로드
    model = load_model('final_lgbm_pycaret')

    input_df.rename(columns={'lng':'lon'}, inplace=True)
    Y= input_df[['grfe']]
    X= input_df.drop(columns=['grfe'])
    # 모델 예측
    predictions = predict_model(model, data=X)
    predicted_label = predictions['prediction_label'].iloc[0]

    result = {
            "jeonsePrice": float(predicted_label),
            "infrastructureScore": {
                "school": int(input_df['500m_내_초중등수'].iloc[0]),
                "publicSecurity": int(input_df['발생'].iloc[0]),
                "busStop": int(input_df['500m_내_bus수'].iloc[0]),
                "subway": int(input_df['Closest_Station_Distance'].iloc[0]),
                "mart": int(input_df['500m_내_마트수'].iloc[0]),
            }
        }
    json_result = json.dumps(result)

    return json_result



if __name__ == "__main__":
    try:
        # Read input from stdin
        json_data_str = sys.stdin.read()
        print("Received JSON data:", json_data_str)

        input_df = process_json(json_data_str)
        input_df = infra(input_df)
        predictions = predict(input_df)
        '''
        predicted_labels = predictions['prediction_label'].iloc[0]
        print("Prediction: ",predicted_labels)

        result = {
            "jeonsePrice": float(predicted_labels),
            "infrastructureScore": {
                "school": int(input_df['500m_내_초중등수'].iloc[0]),
                "publicSecurity": int(input_df['발생'].iloc[0]),
                "busStop": int(input_df['500m_내_bus수'].iloc[0]),
                "subway": int(input_df['Closest_Station_Distance'].iloc[0]),
                "mart": int(input_df['500m_내_마트수'].iloc[0])
            }
        }
        json_result = json.dumps(result)
'''
        # 결과 출력

        print(predictions)
        return predictions

    except Exception as e:
        print(f"Error in main function: {e}", file=sys.stderr)
        sys.exit(1)
