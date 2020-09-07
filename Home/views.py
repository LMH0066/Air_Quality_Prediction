from django.shortcuts import render
import json, os, sys, math, csv
import numpy as np
from Air_Quality_Prediction.settings import MEDIA_ROOT, MEDIA_URL
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

# 返回全国全部站点的检测数据
@csrf_exempt
def get_china_aqi(request):
    path = os.path.join(MEDIA_ROOT, "data.json")
    # 读取json并进行分析
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    if load_f:
        datas = load_dict['data']
        results = []
        for data in datas:
            for d in data:
                if d['aqi']:
                    results.append(d)
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
        with open(result_path, 'r') as result_f:
            result_dict = csv.reader(result_f)
            column = [row[1] for row in result_dict]
        if result_f:
            return HttpResponse(json.dumps({'status': 0, 'data': {
                'station': station_name,
                'forecast': column[1:]}}))
            # for data in result_dict:
            #     if data['station'][0] == station_name:
            #         return HttpResponse(json.dumps({'status': 0, 'data': {'station' : station_name, 'forecast' : data['data']}}))
        else:
            return HttpResponse(json.dumps({'status': 1}))
    return HttpResponse(json.dumps({'status': 1}))
