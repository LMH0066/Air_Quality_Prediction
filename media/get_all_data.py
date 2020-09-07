import ssl
import json
import re
import os
from urllib import request, parse
from datetime import datetime, timedelta
import urllib.request as urllib2
import pandas as pd

import numpy as np
import joblib

# 获取过去24小时天气记录索要用到的参数
API = "https://api.seniverse.com/v3/weather/hourly_history.json"
KEY = "S7m5R-CBepZLxPOAx"
UNIT = "c"
LANGUAGE = "zh-Hans"
getLocation = "beijing"
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

features = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP']
station_codes = ['1001A', '1002A', '1003A', '1004A', '1005A', '1006A', '1007A', '1008A', '1009A', '1010A', '1011A',
                 '1012A']


# 获取过去24小时天气
def fetch_weather(_location):
    params = parse.urlencode({
        'key': KEY,
        'location': _location,
        'language': LANGUAGE,
        'unit': UNIT
    })
    req = request.Request('{api}?{params}'.format(api=API, params=params))
    response = request.urlopen(req, context=gcontext).read().decode('UTF-8')
    return response


# 获取空气质量
def get_date(file_path, t):
    host = 'https://nairall.market.alicloudapi.com'
    path = '/api/v1/nation_air/station_realtime_list'
    method = 'GET'
    appcode = 'c294d756dbd346a791c53f73c8da931d'
    querys = 'pubtime=' + t
    bodys = {}
    url = host + path + '?' + querys

    request = urllib2.Request(url)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib2.urlopen(request, context=ctx)
    content = json.loads(response.read())
    if (content):
        data = open(file_path, 'w')
        json.dump(content, data)


# 初始化数据
def generate_dataset(data, labels, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = data
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.loc[:i - 1, :])
        names += [('%s(t-%d)' % (df.columns[j], i)) for j in range(n_vars)]

    # agg = pd.DataFrame(zip(cols))
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# 预测
def predict_12(_model, X, n_features):
    res = pd.DataFrame(
        columns=['PM2.5(t)', 'PM10(t)', 'SO2(t)', 'NO2(t)', 'CO(t)', 'O3(t)', 'TEMP(t)', 'PRES(t)', 'DEWP(t)'])
    for i in range(12):
        y_pred = _model.predict(np.array(X).reshape(1, -1))
        # drop late data
        X = X.shift(-n_features)
        # add predicted data
        X[X.index[-n_features:]] = y_pred.flatten()
        y_pred = pd.DataFrame(
            columns=['PM2.5(t)', 'PM10(t)', 'SO2(t)', 'NO2(t)', 'CO(t)', 'O3(t)', 'TEMP(t)', 'PRES(t)', 'DEWP(t)'],
            data=y_pred)
        res = res.append(y_pred)
    res.reset_index(inplace=True)
    return res


if __name__ == '__main__':
    location = getLocation
    weathers = json.loads(fetch_weather(location))
    path = os.getcwd()
    # 得到过去24小时天气数据
    time = re.split('T|\+', weathers['results'][0]['hourly_history'][0]['last_update'])
    S = datetime.strptime(time[0] + " " + time[1].split(':')[0] + ":00:00", '%Y-%m-%d %H:%M:%S')
    data_all = pd.DataFrame()
    for i in range(0, 24):
        t = (S - timedelta(hours=i)).strftime("%Y-%m-%d+%H:%M:%S")
        file_path = os.path.join(path, 'data', t + ".json")
        # 通过天气数据的时间获取空气质量数据并存储
        if not os.path.exists(file_path):
            get_date(file_path, t)
        # 将天气数据和空气质量数据合并
        datas = []
        with open(file_path, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            for data in json_data["data"]:
                for d in data:
                    if d["station_code"] >= "1001A" and d["station_code"] <= "1012A":
                        datas.append(d)
                    else:
                        break
        data_df = pd.DataFrame(datas)
        # data_df.rename(columns={'pm2_5':'PM2.5', 'pm10':'PM10', 'so2':'SO2', 'no2':'NO2', 'co':'CO', 'o3':'O3'})
        data_df['TEMP'] = weathers['results'][0]['hourly_history'][i]['temperature']
        data_df['PRES'] = weathers['results'][0]['hourly_history'][i]['pressure']
        # data_df['DEWP'] = weathers['results'][0]['hourly_history'][i]['dew_point']
        data_df['DEWP'] = 0
        data_all = data_all.append(data_df)
    data_all = data_all.rename(
        columns={'pm2_5': 'PM2.5', 'pm10': 'PM10', 'so2': 'SO2', 'no2': 'NO2', 'co': 'CO', 'o3': 'O3'})

    model = joblib.load('xgboost.model')
    for station_code in station_codes:
        df = data_all[data_all['station_code'] == station_code][features].copy().iloc[::-1]
        df.interpolate(inplace=True, limit_direction='both')
        df.reset_index(inplace=True)
        df = df[features].copy()
        before_path = os.path.join(path, 'before', station_code + ".csv")
        df.to_csv(before_path, sep=',', header=True, index=True)

        X_test = generate_dataset(df, n_in=24, n_out=12, labels=features)
        # print(X_test.iloc[0])
        result = predict_12(model, X_test.iloc[0], 9).drop(['index'], axis=1)
        result_path = os.path.join(path, 'result', station_code + ".csv")
        result.to_csv(result_path, sep=',', header=True, index=True)
        # print(result)

