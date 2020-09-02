from django.shortcuts import render
import json, os
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
    return HttpResponse(json.dumps({'status': 1}))
