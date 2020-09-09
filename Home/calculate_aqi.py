def cal_linear(iaqi_lo, iaqi_hi, bp_lo, bp_hi, cp):
    # 线性缩放
    iaqi = (iaqi_hi - iaqi_lo) * (cp - bp_lo) / (bp_hi - bp_lo) + iaqi_lo
    return iaqi


def cal_pm_iaqi(pm_val):
    # 计算PM2.5的IAQI
    if 0 <= pm_val < 36:
        iaqi = cal_linear(0, 50, 0, 35, pm_val)
    elif 36 <= pm_val < 76:
        iaqi = cal_linear(50, 100, 35, 75, pm_val)
    elif 76 <= pm_val < 116:
        iaqi = cal_linear(100, 150, 75, 115, pm_val)
    elif 116 <= pm_val < 151:
        iaqi = cal_linear(150, 200, 115, 150, pm_val)
    elif 151 <= pm_val < 251:
        iaqi = cal_linear(200, 300, 150, 250, pm_val)
    elif 251 <= pm_val < 351:
        iaqi = cal_linear(300, 400, 250, 350, pm_val)
    elif 351 <= pm_val < 501:
        iaqi = cal_linear(400, 500, 350, 500, pm_val)
    else:
        iaqi = 0
    return iaqi


def cal_co_iaqi(co_val):
    # 计算co的IAQI
    if 0 <= co_val < 3:
        iaqi = cal_linear(0, 50, 0, 2, co_val)
    elif 3 <= co_val < 5:
        iaqi = cal_linear(50, 100, 2, 4, co_val)
    elif 5 <= co_val < 15:
        iaqi = cal_linear(100, 150, 4, 14, co_val)
    elif 15 <= co_val < 25:
        iaqi = cal_linear(150, 200, 14, 24, co_val)
    elif 25 <= co_val < 37:
        iaqi = cal_linear(200, 300, 24, 36, co_val)
    elif 37 <= co_val < 49:
        iaqi = cal_linear(300, 400, 36, 48, co_val)
    elif 49 <= co_val < 61:
        iaqi = cal_linear(400, 500, 48, 60, co_val)
    else:
        iaqi = 0
    return iaqi


def cal_aqi(param_list):
    # AQI计算
    pm_val = param_list[0]
    co_val = param_list[1]

    pm_iaqi = cal_pm_iaqi(pm_val)
    co_iaqi = cal_co_iaqi(co_val)

    iaqi_list = []
    iaqi_list.append(pm_iaqi)
    iaqi_list.append(co_iaqi)

    AQI = max(iaqi_list)
    return AQI


def calculate(pm_val, co_val):
    para_list = [float(pm_val), float(co_val)]
    aqi_val = cal_aqi(para_list)
    return aqi_val
