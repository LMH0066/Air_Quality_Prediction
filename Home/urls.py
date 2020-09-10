from django.urls import path
from . import views

app_name = 'Home'
urlpatterns = [
    path('getChinaAqi', views.get_china_aqi),
    path('predict', views.predict),
    path('predict_test', views.predict_test)
]
