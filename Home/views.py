import json
import math
import os
import sys
from datetime import datetime, timedelta
from django.core import serializers
from operator import itemgetter
import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Air_Quality_Prediction.settings import MEDIA_ROOT
from Home.calculate_aqi import calculate


# Create your views here.

def add_header(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Max-Age'] = '1000'
    response['Access-Control-Allow-Headers'] = '*'
    return response


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
                    results.append({'province': d['province'], 'city': d['city'],
                                    'city_code': d['city_code'], 'station': d['station'],
                                    'aqi': d['aqi'], 'no2': d['no2'], 'so2': d['so2'], 'co': d['co'],
                                    'o3': d['o3'], 'pm2_5': d['pm2_5'], 'pm10': d['pm10']})
        results = sorted(results, key=itemgetter('aqi'), reverse=True)
        return add_header(HttpResponse(json.dumps({'status': 0, 'data': {'station': results}})))
    return add_header(HttpResponse(json.dumps({'status': 1})))


# 预测
@csrf_exempt
def predict(request):
    longitude = request.GET.get('longitude')
    latitude = request.GET.get('latitude')
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
            air_quality = [{'AQI': round(calculate(before_dict['PM2.5'][23], before_dict['CO'][23] / 1000)),
                            'PM2.5': round(float(before_dict['PM2.5'][23])),
                            'PM10': round(float(before_dict['PM10'][23])),
                            'SO2': round(float(before_dict['SO2'][23])),
                            'NO2': round(float(before_dict['NO2'][23])),
                            'CO': round(float(before_dict['CO'][23] / 1000), 1),
                            'O3': round(float(before_dict['O3'][23]))}]
            for i in range(0, 12):
                air_quality.append({'AQI': round(calculate(result_dict['PM2.5(t)'][i], result_dict['CO(t)'][i] / 1000)),
                                    'PM2.5': round(float(result_dict['PM2.5(t)'][i])),
                                    'PM10': round(float(result_dict['PM10(t)'][i])),
                                    'SO2': round(float(result_dict['SO2(t)'][i])),
                                    'NO2': round(float(result_dict['NO2(t)'][i])),
                                    'CO': round(float(result_dict['CO(t)'][i] / 1000), 1),
                                    'O3': round(float(result_dict['O3(t)'][i]))})

            pm_25 = []
            for i in range(0, 24):
                t = datetime.strptime(before_dict['pubtime'][i], "%Y-%m-%d %H:%M:%S")
                pm_25.append([t.strftime("%H:%M"), round(float(before_dict['PM2.5'][i]), 1)])
            before_time = datetime.strptime(before_dict['pubtime'][23], "%Y-%m-%d %H:%M:%S")
            for i in range(0, 12):
                before_time = before_time + timedelta(hours=1)
                pm_25.append([before_time.strftime("%H:%M"), round(float(result_dict['PM2.5(t)'][i]), 1)])
            # pm_25 = serializers.serialize("json", pm_25)
            return add_header(HttpResponse(json.dumps({'status': 0, 'data': {'PM2.5': pm_25, 'airQuality': air_quality}})))
        else:
            return add_header(HttpResponse(json.dumps({'status': 1})))
    return add_header(HttpResponse(json.dumps({'status': 1})))


# 预测
@csrf_exempt
def predict_test(request):
    before_path = os.path.join(MEDIA_ROOT, "before", "1001A.csv")
    with open(before_path, 'r') as before_f:
        before_dict = pd.read_csv(before_f)
    air_quality = [{'AQI': round(calculate(0, 0)), 'PM2.5': round(float(0)), 'PM10': round(float(0)),
                    'SO2': round(float(0)), 'NO2': round(float(0)), 'CO': round(float(0), 1), 'O3': round(float(0))}]
    for i in range(0, 12):
        num = (i + 1) * 30
        air_quality.append({'AQI': round(calculate(num, num / 100)), 'PM2.5': round(float(num)), 'PM10': round(float(num)),
                            'SO2': round(float(num)), 'NO2': round(float(num)), 'CO': round(float(num / 100), 1),
                            'O3': round(float(num))})

    pm_25 = []
    for i in range(0, 24):
        t = datetime.strptime(before_dict['pubtime'][i], "%Y-%m-%d %H:%M:%S")
        pm_25.append([t.strftime("%H:%M"), round(float(0), 1)])
    before_time = datetime.strptime(before_dict['pubtime'][23], "%Y-%m-%d %H:%M:%S")
    for i in range(0, 12):
        before_time = before_time + timedelta(hours=1)
        pm_25.append([before_time.strftime("%H:%M"), round(float((i + 1) * 30), 1)])
    # pm_25 = serializers.serialize("json", pm_25)
    return add_header(HttpResponse(json.dumps({'status': 0, 'data': {'PM2.5': pm_25, 'airQuality': air_quality}})))
