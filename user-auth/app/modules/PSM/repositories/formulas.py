from sqlalchemy import Numeric, and_, case, func, cast
from datetime import timedelta
TWE_SHOP = '66'
IMM_SHOP = '24'

efficiency_formulas = {
    1011 :  lambda breakdown, idle, total_time,schedule: ((total_time*60 - func.coalesce(schedule,0))/ (total_time*60 - func.coalesce(schedule,0) + func.coalesce(idle,0) + func.coalesce(breakdown,0)))*100,
    66 : lambda actual_prod,planned_prod : (actual_prod/planned_prod) * 100
}

sph_formulas = {
    1011 : lambda breakdown, idle, total_time,actual,schedule: func.coalesce(((actual*60.0) / (total_time*60 - func.coalesce(schedule,0) + func.coalesce(idle,0) + func.coalesce(breakdown,0))), 0)
}

def get_efficiency_by_shop_id(shop_id,breakdown,idle,total_time,schedule,in_minutes=False,actual_prod= None,planned_prod=None):
    if str(shop_id) == TWE_SHOP:
        if planned_prod == 0 or actual_prod == 0  :
            return 100
        if actual_prod is not None and planned_prod is not None:
            return  (actual_prod/planned_prod) * 100
        else:
            return 100

    formula = efficiency_formulas.get(shop_id)
    if in_minutes:
        return ((total_time - func.coalesce(schedule,0))/ (total_time - func.coalesce(schedule,0) + func.coalesce(idle,0) + func.coalesce(breakdown,0)))*100 
    if formula:
        return formula(breakdown, idle, total_time,schedule)
    else:
        return ((total_time*60 - func.coalesce(schedule,0))/ (total_time*60 - func.coalesce(schedule,0) + func.coalesce(idle,0) + func.coalesce(breakdown,0)))*100 
    
def get_sph_by_shop_id(shop_id,actual,total_time,idle,breakdown,schedule,rejection=0):
    if str(shop_id) == IMM_SHOP:
        return (actual-rejection)/((total_time-schedule)*60*60)
    formula = efficiency_formulas.get(shop_id)
    if formula:
        return formula(breakdown, idle, total_time,actual,schedule)
    else:
        return func.coalesce(((actual*60.0) / (total_time*60 - func.coalesce(schedule,0) + func.coalesce(idle,0) + func.coalesce(breakdown,0))), 0)