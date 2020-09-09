import json
import math
import os
import sys
from operator import itemgetter
import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Air_Quality_Prediction.settings import MEDIA_ROOT
from Home.calculate_aqi import calculate


# Create your views here.

# 返回全国全部站点的检测数据
@csrf_exempt
def get_china_aqi(request):
    path = os.path.join(MEDIA_ROOT, "data")
    file_list = os.listdir(path)
    file_path = os.path.join(MEDIA_ROOT, "data", max(file_list))
    # 读取json并进行分析
    with open(file_path, 'r') as load_f:
        load_dict = json.load(load_f)
    if load_f:
        datas = load_dict['data']
        results = []
        for data in datas:
            for d in data:
                if d['aqi']:
                    results.append(d)
        results = sorted(results, key=itemgetter('aqi'), reverse=True)
        return HttpResponse(json.dumps({'status': 0, 'data': results}))
    return HttpResponse(json.dumps({'status': 1}))


# 预测
@csrf_exempt
def predict(request):
    longitude = request.POST.get('longitude')
    latitude = request.POST.get('latitude')
    # print(longitude)
    station_path = os.path.join(MEDIA_ROOT, "station.json")
    with open(station_path, 'r') as station_f:
        station_dict = json.load(station_f)
    if station_f:
        # 找到离坐标最近的监测站
        p = np.array([float(latitude), float(longitude)])
        station_name = None
        station_code = None
        min_len = sys.maxsize
        for data in station_dict:
            p1 = np.array([data['latitude'], data['longitude']])
            p2 = p1 - p
            new_len = math.hypot(p2[0], p2[1])
            if min_len > new_len:
                min_len = new_len
                station_name = data['station']
                station_code = data['station_code']
        result_path = os.path.join(MEDIA_ROOT, "result", station_code + ".csv")
        before_path = os.path.join(MEDIA_ROOT, "before", station_code + ".csv")
        with open(result_path, 'r') as result_f:
            result_dict = pd.read_csv(result_f)
        with open(before_path, 'r') as before_f:
            before_dict = pd.read_csv(before_f)
        if result_f:
            air_quality = [{'AQI': calculate(before_dict['PM2.5'][23], before_dict['CO'][23] / 100),
                            'PM2.5': float(before_dict['PM2.5'][23]), 'PM10': float(before_dict['PM10'][23]),
                            'SO2': float(before_dict['SO2'][23]), 'NO2': float(before_dict['NO2'][23]),
                            'CO': float(before_dict['CO'][23] / 100), 'O3': float(before_dict['O3'][23])}]
            for i in range(0, 12):
                air_quality.append({'AQI': calculate(result_dict['PM2.5(t)'][i], result_dict['CO(t)'][i] / 100),
                                    'PM2.5': float(result_dict['PM2.5(t)'][i]), 'PM10': float(result_dict['PM10(t)'][i]),
                                    'SO2': float(result_dict['SO2(t)'][i]), 'NO2': float(result_dict['NO2(t)'][i]),
                                    'CO': float(result_dict['CO(t)'][i] / 100), 'O3': float(result_dict['O3(t)'][i])})
            return HttpResponse(json.dumps({'status': 0, 'data': {'airQuality': air_quality}}))
        else:
            return HttpResponse(json.dumps({'status': 1}))
    return HttpResponse(json.dumps({'status': 1}))
