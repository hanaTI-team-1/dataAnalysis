import json
import pandas as pd
from geopy.distance import geodesic

# 전처리 함수 정의
def convert_new_bldgUsg(bldgUsg):
    if bldgUsg == '아파트':
        return 1
    elif bldgUsg == '연립다세대':
        return 2
    else:
        return 3  # 예외 처리

# 가장 가까운 지하철역의 거리를 계산하는 함수
def find_closest_station_distance(lat, lon, station_df):
    min_distance = float('inf')
    closest_station = None
    for _, station in station_df.iterrows():
        dist = geodesic((lat, lon), (station['Latitude'], station['Longitude'])).kilometers
        if dist < min_distance:
            min_distance = dist
            closest_station = station['name']
    return min_distance, closest_station

def convert_new_contract_type(contract_type):
    if contract_type == '신규':
        return 1
    elif contract_type == '갱신':
        return 0
    else:
        return None  # 예외 처리

def format_date(date_str):
    if len(date_str.split('.')[0]) == 2:
        return '20' + date_str
    return date_str

def count_nearby(lat, lon, df):
    count = 0
    for _, store in df.iterrows():
        dist = geodesic((lat, lon), (store['Latitude'], store['Longitude'])).km
        if dist <= 0.5:
            count += 1
    return count

def transfer(input_df):
    # 데이터 전처리 작업
    input_df.drop(columns='bfrRtfe', inplace=True)
    input_df.drop(columns='stdgNm', inplace=True)
    districts = ['강남구', '강서구', '관악구', '동작구', '송파구']
    for district in districts:
        input_df[f'자치구명_{district}'] = (input_df['cggNm'] == district).astype(int)
    input_df.drop(columns='lotnoSe', inplace=True)
    input_df.drop(columns='archYr', inplace=True)
    input_df.drop(columns='lotnoSeNm', inplace=True)
    input_df.drop(columns='bldgNm', inplace=True)
    input_df.drop(columns='rcptYr', inplace=True)
    input_df.drop(columns='rentSe', inplace=True)
    input_df['newUpdtYn'] = input_df['newUpdtYn'].apply(convert_new_contract_type)
    current = pd.to_datetime('now')
    input_df["ctrtDay"] = current - pd.to_datetime(input_df["ctrtDay"], format='%y%m%d')
    input_df["ctrtDay"] = input_df["ctrtDay"].dt.days
    input_df['시작일'] = input_df['ctrtPrd'].str.split('~').str[0]
    input_df['종료일'] = input_df['ctrtPrd'].str.split('~').str[1]
    input_df = input_df.dropna(subset=['시작일', '종료일'])
    input_df = input_df[~input_df['시작일'].str.startswith('.')]
    input_df = input_df[~input_df['종료일'].str.startswith('.')]
    input_df['시작일'] = input_df['시작일'].apply(format_date)
    input_df['종료일'] = input_df['종료일'].apply(format_date)
    input_df['시작일'] = pd.to_datetime(input_df['시작일'], format="%Y.%m")
    input_df['종료일'] = pd.to_datetime(input_df['종료일'], format="%Y.%m")
    input_df['ctrtDayMonth'] = (input_df['종료일'].dt.year - input_df['시작일'].dt.year) * 12 + (input_df['종료일'].dt.month - input_df['시작일'].dt.month)
    input_df.drop(columns=['시작일', '종료일', 'ctrtPrd'], inplace=True)
    input_df['bldgUsg'] = input_df['bldgUsg'].apply(convert_new_bldgUsg)
    input_df['ctrtUpdtUseYn'] = input_df['ctrtUpdtUseYn'].apply(lambda x: 1 if x == '○' else 0)
    input_df = input_df.dropna(subset=['newUpdtYn', 'bfrGrfe'])
    return input_df


def infra(newdata):

  school_df = pd.read_csv("schooldf_경로", encoding='cp949')
  newdata = pd.read_csv("newdata_경로", encoding='cp949')
  bus_df = pd.read_csv("bus_df_경로", encoding='cp949')
  bus_df = bus_df[['X좌표', 'Y좌표']]
  shop_df = pd.read_csv("shop_df_경로", encoding='cp949')
  sub_df = pd.read_csv("sub_df_경로", encoding='cp949')
  con_df = pd.read_csv("con_df_경로", encoding='cp949')
  police_df = pd.read_csv("police_df_경로", encoding='cp949')
  crime_df = pd.read_csv("crime_df_경로", encoding='cp949')

    # 자치구명 필터링
  desired_gu = ['관악구', '송파구', '강서구', '강남구', '동작구']
  crime_df = crime_df[crime_df['자치구별'].isin(desired_gu)]

    # 각 데이터 전처리
  school_df = transfer(school_df)
  # newdata = transfer(newdata)

    # 인프라 계산 및 입력 데이터프레임에 추가
  newdata['500m_내_편의점_수'] = newdata.apply(lambda row: count_nearby(row['lat'], row['lon'], shop_df), axis=1)
  newdata['Closest_Station_Distance'] = newdata.apply(lambda row: find_closest_station_distance(row['lat'], row['lon'], sub_df)[0], axis=1)
  newdata['500m_내_마트수'] = newdata.apply(lambda row: count_nearby(row['lat'], row['lon'], shop_df), axis=1)
  newdata['500m_내_초중등수'] = newdata.apply(lambda row: count_nearby(row['lat'], row['lon'], school_df), axis=1)
  input_df['500m_내_bus수'] = input_df.apply(lambda row: count_nearby(row['lat'], row['lon'], bus_df), axis=1)
  input_df = input_df.merge(crime_df, how='left', left_on='자치구명', right_on='자치구별')
  input_df['500m_내_경찰서수'] = input_df.apply(lambda row: count_nearby(row['lat'], row['lon'], police_df), axis=1)
def process_json(json_str):
    json_data = json.loads(json_str)
    input_df = pd.DataFrame([json_data])
    input_df = transfer(input_df)
    return input_df

# 모델 로드 함수
def load_model(model_path):
    # 모델 로드 코드 (여기서는 생략)

# 예측 함수
def predict(input_df):
    # 모델 로드
    model = load_model('final_model_pycaret.pkl')

    # 데이터 전처리
    input_df = transfer(input_df)

    # 특성 선택 (모델에 맞게 수정 필요)
    selected_features = ['bldgUsg', 'newUpdtYn', 'ctrtDay', 'ctrtDayMonth', '500m_내_편의점_수', 'Closest_Station_Distance']

    # 선택된 특성만 사용
    input_df = input_df[selected_features]

    # 모델 예측
    predictions = model.predict(input_df)

    return predictions

if __name__ == "__main__":
    # JSON 데이터가 첫 번째 인자로 전달됨을 가정
    json_data_str = """
    {
        "atclNo": "2433784438",
        "cortarNo": "1150010500",
        "atclNm": "마곡일성트루엘플래닛",
        "atclStatCd": "R0",
        "rletTpCd": "A02",
        "uprRletTpCd": "A02",
        "rletTpNm": "오피스텔",
        "tradTpCd": "A1",
        "tradTpNm": "매매",
        "vrfcTpCd": "OWNER",
        "flrInfo": "13/14",
        "prc": 41000,
        "rentPrc": 0,
        "hanPrc": "4억 1,000",
        "spc1": "96",
        "spc2": "42.86",
        "direction": "남향",
        "atclCfmYmd": "24.07.09.",
        "repImgUrl": "/20240709_33/land_naver_1720508229484uxIok_JPEG/20200728_182536_1.jpg",
        "repImgTpCd": "10",
        "repImgThumb": "f130_98",
        "lat": 37.568732,
        "lng": 126.825344,
        "atclFetrDesc": "마곡코엑스 인근. 실입주가능. 로얄호수 1.5룸",
        "tag1": "10년이내",
        "tag2": "역세권",
        "tag3": "화장실한개",
        "bildNm": "A동",
        "minute": "0",
        "sameAddrCnt": 2,
        "sameAddrDirectCnt": 1,
        "cpid": "bizmk",
        "cpNm": "매경부동산",
        "cpCnt": 2,
        "rltrNm": "마곡보타닉공인중개사사무소",
        "sellrNm": "",
        "directTradYn": "N",
        "minMviFee": 0,
        "maxMviFee": 0,
        "etRoomCnt": 0,
        "tradePriceHan": "",
        "tradeRentPrice": 0,
        "tradeCheckedByOwner": "false",
        "cpLinkVO": "",
        "dtlAddrYn": "N",
        "dtlAddr": "",
        "address": "서울 강서구 마곡동 758-2"
    }
    """

    # JSON 데이터를 처리하여 DataFrame으로 변환
    input_df = process_json(json_data_str)

    # 예측 수행
    predictions = predict(input_df)

    # 예측 결과 출력
    print(predictions.tolist())
