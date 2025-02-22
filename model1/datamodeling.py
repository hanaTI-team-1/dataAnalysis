# -*- coding: utf-8 -*-
"""datamodeling.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xj2hYh6NR5jYCfXwisSgA8V4WjC74dNt
"""

from google.colab import drive
drive.mount('/content/drive')

# import oracledb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import seaborn as sns
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
from matplotlib.ticker import StrMethodFormatter,FormatStrFormatter
pd.options.display.float_format = '{:.5f}'.format
plt.style.use("seaborn-whitegrid")
import seaborn as sns
from sklearn.preprocessing import KBinsDiscretizer
import datetime as dt
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

"""# data load"""

school_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/input_df_초중등.csv",encoding='utf-8')
bus_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/input_df_bus.csv",encoding='utf-8')
con_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/input_df_shop.csv",encoding='utf-8')
sub_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/지하철.csv",encoding='utf-8')
newdata=pd.read_csv("/content/drive/MyDrive/A하금티/jeonse_data_processed.csv",encoding='utf-8')

crime_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/crime.csv",encoding='utf-8')
police_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/police.csv",encoding='utf-8')

newdata.isnull().sum()

# newdata.drop(columns=['Unnamed: 0'],inplace=True)

"""## 데이터 전처리"""

input_df=newdata

# 신규계약구분을 1과 0으로 변환하는 함수
def convert_new_contract_type(contract_type):
    if contract_type == '신규':
        return 1
    elif contract_type == '갱신':
        return 0
    else:
        return None  # 예외 처리
# 날짜 형식을 통일하는 함수
def format_date(date_str):
    if len(date_str.split('.')[0]) == 2:
        return '20' + date_str
    return date_str

input_df=df

# bldgUsg 변환함수
def convert_new_bldgUsg(bldgUsg):
    if bldgUsg == '아파트':
        return 1
    elif bldgUsg == '연립다세대':
        return 2
    else:
        return 3  # 예외 처리

input_df['bldgUsg'] = input_df['bldgUsg'].apply(convert_new_bldgUsg)

def transfer(input_df):
  input_df.drop(columns='bfrRtfe',inplace=True)
  # 종전임대료 drop

  #자치구명 원핫 인코더
  # 자치구명 리스트
  districts = ['강남구', '강서구', '관악구', '동작구', '송파구']

  # 원핫 인코딩 컬럼 생성
  for district in districts:
      input_df[f'자치구명_{district}'] = (input_df['cggNm'] == district).astype(int)

  # input_df.drop(columns='rtfe',inplace=True)
  #임대료 drop
  input_df.drop(columns='lotnoSe',inplace=True) #지번구분 drop
  input_df.drop(columns='archYr',inplace=True) #건축년도 drop
  input_df.drop(columns='lotnoSeNm',inplace=True) #전월세 구분 drop 다 전세여서
  input_df.drop(columns='bldgNm',inplace=True)  # 건물명 drop
  # input_df.drop(columns='ctrtPrd',inplace=True)
  # ctrtPrd
  input_df.drop(columns='rcptYr',inplace=True)  # 계약기간 drop
  input_df.drop(columns='rentSe',inplace=True)  # rentSe drop

  # apply 함수를 사용하여 변환 적용
  input_df['newUpdtYn'] = input_df['newUpdtYn'].apply(convert_new_contract_type)

  #계약일 날짜로 변환
  current =  datetime.now()
  input_df["ctrtDay"] = current - pd.to_datetime(input_df["ctrtDay"],format='%Y%m%d')
  input_df["ctrtDay"] = input_df["ctrtDay"].dt.days

  input_df['시작일'] = input_df['ctrtPrd'].str.split('~').str[0]
  input_df['종료일'] = input_df['ctrtPrd'].str.split('~').str[1]

  input_df = input_df.dropna(subset=['시작일'])
  input_df = input_df.dropna(subset=['종료일'])

  # "."으로 시작하는 데이터 제거
  input_df = input_df[~input_df['시작일'].str.startswith('.')]
  input_df = input_df[~input_df['종료일'].str.startswith('.')]

  # 날짜 형식을 통일
  input_df['시작일'] = input_df['시작일'].apply(format_date)
  input_df['종료일'] = input_df['종료일'].apply(format_date)

  # 문자열을 datetime 형식으로 변환
  input_df['시작일'] = pd.to_datetime(input_df['시작일'], format="%Y.%m")
  input_df['종료일'] = pd.to_datetime(input_df['종료일'], format="%Y.%m")

  # 두 날짜 사이의 차이 계산 (월 단위)
  input_df['ctrtDayMonth'] = (input_df['종료일'].dt.year - input_df['시작일'].dt.year) * 12 + (input_df['종료일'].dt.month - input_df['시작일'].dt.month)
  input_df.drop(columns='시작일',inplace=True)
  input_df.drop(columns='종료일',inplace=True)
  input_df.drop(columns='ctrtPrd',inplace=True)
  input_df['ctrtDayMonth']

  input_df['ctrtUpdtUseYn'] = input_df['ctrtUpdtUseYn'].apply(lambda x: 1 if x == '○' else 0)
  input_df = input_df.dropna(subset=['newUpdtYn'])
  input_df = input_df.dropna(subset=['bfrGrfe'])
  return input_df

input_df=transfer(input_df)

input_df

school_df=transfer(school_df)
# newdata=transfer(newdata)

stdgNm=input_df[['stdgNm']]
stdgNm.to_csv("/content/drive/MyDrive/A하금티/data/stdgNm.csv")

input_df.to_csv("/content/drive/MyDrive/A하금티/newdata.csv")

"""정제된 본 데이터

### 추가 데이터 매핑
"""

sub_df.info()

newdata=input_df

newdata

newdata = newdata.reset_index(drop=True)
school_df = school_df.reset_index(drop=True)
school_df=transfer(school_df)
bus_df = bus_df.reset_index(drop=True)
con_df = con_df.reset_index(drop=True)
sub_df = sub_df.reset_index(drop=True)

# 데이터프레임 결합
df1 = pd.concat([newdata, school_df['500m_내_초중등수']], axis=1)
df1

df1 = df1.reset_index(drop=True)
df2=pd.concat([df1, bus_df['500m_내_bus수']], axis=1)
df2

df2 = df2.reset_index(drop=True)
df3 = pd.concat([df2, con_df['500m_내_마트수']], axis=1)
df3 = df3.reset_index(drop=True)
df4 = pd.concat([df3, sub_df['Closest_Station_Distance']], axis=1)
df4

input_df

crime_df=pd.read_csv("/content/drive/MyDrive/A하금티/data/crime.csv",encoding='utf-8')

# newdata=pd.read_csv("/content/drive/MyDrive/A하금티/jeonse_data_processed.csv",encoding='utf-8')

crime=input_df.merge(crime_df, how='left', left_on='cggNm', right_on='자치구별')
crime

input_df.columns

# newdata=transfer(newdata)
# crime=transfer(crime)
crime=crime[['발생','검거']]
crime

crime = crime.reset_index(drop=True)
df4 = df4.reset_index(drop=True)

df5=pd.concat([crime,df4],axis=1)
df5

df5.cggCd #넣는게 나을지 모르겠음

df5

newdata=pd.read_csv("/content/drive/MyDrive/A하금티/jeonse_data_processed.csv",encoding='utf-8')

newdata

newdata.ctrtDay.min()

inte_rate=pd.read_csv("/content/drive/MyDrive/A하금티/data/inte_rate.csv",encoding='cp949')
inte_rate=inte_rate[['TIME','value']]
inte_rate

newdata.ctrtDay

inte_rate=inte_rate.drop_duplicates(['TIME'], keep='first')

df6=newdata.merge(inte_rate, how='left', left_on='ctrtDay', right_on='TIME')
df6

df7=transfer(df6)
df7

df7 = df7.reset_index(drop=True)
df7=df7[['value']]
df8=pd.concat([df7,df5],axis=1)
df8

df8.to_csv("/content/drive/MyDrive/A하금티/data/finaldf_최최종.csv")

"""# 찐 모델링"""

df9=pd.read_csv("/content/drive/MyDrive/A하금티/data/finaldf_최최종.csv",encoding='utf-8')

df9.columns

df9.drop(columns=['rtfe','Unnamed: 0','자치구명_동작구','자치구명_송파구','cggCd','stdgCd','ctrtUpdtUseYn','자치구명_강서구','자치구명_관악구','newUpdtYn','ctrtDayMonth','ctrtDay','bfrGrfe','자치구명_강남구'],inplace=True)
df9.columns

df9.to_csv("/content/drive/MyDrive/A하금티/data/finaldf_최최최최종.csv")

# df['bldgUsg'] = df['bldgUsg'].apply(convert_new_bldgUsg)

Y= df9[['grfe']]
X= df9.drop(columns=['grfe'])
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

"""## 회귀"""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# 선형 회귀 모델 학습
model = LinearRegression()
model.fit(X_train, Y_train)

from sklearn.metrics import mean_squared_error, r2_score,mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score
# 예측 수행
Y_pred = model.predict(X_test)

# 평가 지표 계산
mse = mean_squared_error(Y_test, Y_pred)
mae = mean_absolute_error(Y_test, Y_pred)
r2 = r2_score(Y_test, Y_pred)
# 교차 검증
cross_val_scores = cross_val_score(model, X, Y, scoring='neg_mean_squared_error', cv=5)

print(f'Mean Squared Error (Test Set): {mse}')
print(f'Mean Absolute Error (Test Set): {mae}')
print(f'R^2 Score (Test Set): {r2}')
print(f'Mean Squared Error (Cross-Validation): {-cross_val_scores.mean()}')
print(f'Standard Deviation (Cross-Validation): {cross_val_scores.std()}')

plt.figure(figsize=(10, 6))
sns.boxplot(x=df['grfe'])
plt.title('Box Plot for Feature Outliers Detection')
plt.xlabel('Features')
plt.ylabel('Values')
plt.show()

plt.figure(figsize=(10, 6))
sns.histplot(df['grfe'], bins=20, kde=True)
plt.title('Box Plot for 보증금')
plt.xlabel('grfe')
plt.ylabel('Values')
plt.show()

"""!pip uninstall scikit-learn -y
!pip uninstall tpot -y

!pip install scikit-learn==1.5.1
!pip install tpot==0.12.2
"""

pip install numpy scipy scikit-learn pandas joblib pytorch

pip install tpot --upgrade

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

from tpot import TPOTRegressor


# TPOTRegressor 설정 및 학습
tpot = TPOTRegressor(verbosity=2, generations=5, population_size=50)
tpot.fit(X_train, Y_train)

# 예측 및 평가
Y_pred = tpot.predict(X_test)
print(f"Mean Squared Error: {mean_squared_error(Y_test, Y_pred)}")
print(f"R^2 Score: {r2_score(Y_test, Y_pred)}")

# 베스트 파이프라인 코드 출력
tpot.export('best_model_pipeline.py')

!pip install pycaret

!pip install numpy scipy scikit-learn cython pandas

!pip install auto-sklearn

!sudo apt-get update -y
!sudo apt-get install python3.9

!pip install scikit-learn==0.24.2 --no-build-isolation

!pip uninstall imbalanced-learn -y
!pip uninstall mlxtend -y
!pip uninstall yellowbrick -y

!apt-get install swig
!pip install cython numpy
!pip install auto-sklearn

pip install numba --upgrade

!pip install autosklearn

!apt-get install -y build-essential swig
!pip install Cython numpy

!pip install scikit-learn==0.24.2

!pip install --upgrade pip

import autosklearn.regression


# 학습 데이터와 테스트 데이터 분리
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Auto-sklearn Regressor 설정 및 학습
automl = autosklearn.regression.AutoSklearnRegressor(time_left_for_this_task=3600, per_run_time_limit=360)
automl.fit(X_train, Y_train)

# 예측 및 평가
Y_pred = automl.predict(X_test)
print(f"Mean Squared Error: {mean_squared_error(Y_test, Y_pred)}")
print(f"R^2 Score: {r2_score(Y_test, Y_pred)}")

# 최적 모델과 하이퍼파라미터 출력
print(automl.show_models())

pip install pycaret

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

pip install numba --upgrade

"""## pytoch"""

!pip uninstall sklearn -y
!pip install --upgrade sklearn
!pip install scikit-learn==0.23.2 --user

!pip install --upgrade scipy

import sklearn
sklearn.__version__

pip install pycaret

from pycaret.regression import *

Y= df[['grfe']]
X= df.drop(columns=['Unnamed: 0', 'grfe'])
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

from pycaret.regression import setup, compare_models, tune_model, finalize_model, predict_model

# 데이터프레임 결합
train_data = X_train.copy()
# train_data.drop(columns=['Unnamed: 0.1'],inplace=True)
train_data['Label'] = Y_train

# PyCaret 설정
reg_setup = setup(data=train_data, target='Label', session_id=42,normalize = True)

#전처리된 trian data 확인
reg_setup.train_transformed

# 모델 비교
best_model1 = compare_models(sort ='RMSE',fold=3,n_select = 3)

best_model1

best_model1[0]

best_model1[1]

best_model1[2]

# 모델 튜닝
et_model = create_model('et',fold=3)

tuned_lgbm = tune_model(best_model1[2],fold=3,n_iter=5,optimize='RMSE')
tuned_lgbm

# 최종 모델 선택
final_lgbm = finalize_model(tuned_lgbm)

# 모델 저장
save_model(final_lgbm, '/content/drive/MyDrive/A하금티/data/final_lgbm_pycaret')

finalize_model

prediction = predict_model(final_lgbm, data = X_test)
prediction

# 최종 모델을 훈련 데이터에 맞춰 훈련
final_lgbm.fit(X_train, Y_train)

# 테스트 데이터로 예측
predictions = final_lgbm.predict(X_test)

# 성능 평가
from sklearn.metrics import mean_squared_error
rmse = mean_squared_error(Y_test, predictions, squared=False)
print(f"최종 모델 RMSE: {rmse}")

from sklearn.metrics import mean_squared_error, r2_score,mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score
# 평가 지표 계산
mse = mean_squared_error(Y_test, predictions)
mae = mean_absolute_error(Y_test, predictions)
r2 = r2_score(Y_test, predictions)
# 교차 검증
cross_val_scores = cross_val_score(final_lgbm, X, Y, scoring='neg_mean_squared_error', cv=5)

print(f'Mean Squared Error (Test Set): {mse}')
print(f'Mean Absolute Error (Test Set): {mae}')
print(f'R^2 Score (Test Set): {r2}')
print(f'Mean Squared Error (Cross-Validation): {-cross_val_scores.mean()}')
print(f'Standard Deviation (Cross-Validation): {cross_val_scores.std()}')

evaluate_model(final_lgbm)

"""### 상위3개"""

tuned_xgb = tune_model(best_model1[0],fold=3,n_iter=5,optimize='RMSE')
tuned_xgb

final_xgb= finalize_model(tuned_xgb)
final_xgb

save_model(final_xgb, '/content/drive/MyDrive/A하금티/data/final_xgb')

prediction.columns

evaluate_model(final_xgb)

"""### ~"""

blended_models = blend_models(best, fold=3)
blended_models



prediction = predict_model(final_model, data = x_test)
prediction

evaluate_model(blended_models)

blended_models = finalize_model(blended_models)

# 모델 저장
save_model(final_model, 'final_model_pycaret')

et = create_model('et',fold=3)
tuned_et = tune_model(et)
tuned_et