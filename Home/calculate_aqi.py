def cal_linear(iaqi_lo, iaqi_hi, bp_lo, bp_hi, cp):
    """
        范围缩放
    """
    iaqi = (iaqi_hi - iaqi_lo) * (cp - bp_lo) / (bp_hi - bp_lo) + iaqi_lo
    return iaqi


def cal_pm_iaqi(pm_val):
    """
        计算PM2.5的IAQI
    """
    if 0 <= pm_val < 35:
        iaqi = cal_linear(0, 50, 0, 35, pm_val)
    elif 35 <= pm_val < 75:
        iaqi = cal_linear(50, 100, 35, 75, pm_val)
    elif 75 <= pm_val < 115:
        iaqi = cal_linear(100, 150, 75, 115, pm_val)
    else:
        iaqi = 0

    return iaqi


def cal_co_iaqi(co_val):
    """
        计算CO的IAQI
    """
    if 0 <= co_val < 3:
        iaqi = cal_linear(0, 50, 0, 3, co_val)
    elif 3 <= co_val < 5:
        iaqi = cal_linear(50, 100, 2, 4, co_val)
    else:
        iaqi = 0

    return iaqi


def cal_aqi(para_list):
    """
        AQI计算
    """
    pm_val = para_list[0]
    co_val = para_list[1]

    pm_iaqi = cal_pm_iaqi(pm_val)
    co_iaqi = cal_co_iaqi(co_val)

    iaqi_list = []
    iaqi_list.append(pm_iaqi)
    iaqi_list.append(co_iaqi)

    aqi = max(iaqi_list)
    return aqi


def calculate(pm_val, co_val):
    para_list = [pm_val, co_val]
    aqi_val = cal_aqi(para_list)
    return aqi_val
