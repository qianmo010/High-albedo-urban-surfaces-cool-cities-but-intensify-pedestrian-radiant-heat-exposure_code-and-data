import os
import pandas as pd
import re
import numpy as np
from cal_mrt import *

def generate_datetime_string( month, day, hour, year=2024,minute=30):
    if int(hour) == 24:
        hour = 0
    # Format the time string using f-string to ensure that the year, month, day, hour, and minute are two digits
    datetime_string = f"{int(year):04d}-{int(month):02d}-{int(day):02d} {int(hour):02d}:{int(minute):02d}"
    return datetime_string


def calculate_Tmrt_mrged(city_name, file_path,longitude, latitude,altitude,output_folder_path):
    
    # Read the tree coverage file
    for file in os.listdir(file_path):
        if file.startswith(f"{city_name}"):
            file_name = os.path.splitext(file)[0] 
            path = os.path.join(file_path, f'{file_name}.csv')
            merged_df = pd.read_csv(path)
    
            # 提取文件名中的albedo
            match = re.search(r"\(([\d.]+)\+([\d.]+)\+([\d.]+)\)", file_name)
            if match:
                albedo_road = float(match.group(1))  
                albedo_wall = float(match.group(2))  
                albedo_roof = float(match.group(3))  
            else:
                print(f"Pattern not found in {file_name}")


            if 'WallConf' in merged_df.columns:
                merged_df.rename(columns={'WallConf': 'wallconf'}, inplace=True)
            elif 'wallConf' in merged_df.columns:
                merged_df.rename(columns={'wallConf': 'wallconf'}, inplace=True)
           
            vectorized_datetime_string = np.vectorize(generate_datetime_string)

            # Generate a time character list using vectorization functions
            merged_df['time_str'] = vectorized_datetime_string(
                merged_df['month'], 
                merged_df['day'], 
                merged_df['hour'], 
                )
            results = merged_df.apply(lambda row: cal_Tmrt(time_str=row['time_str'],latitude=latitude,longitude=longitude,altitude=altitude,ground_albedo=albedo_road,
                                                          wall_albedo=albedo_wall,Ta=row['T_can'],RH=row['Rh_can'],TC=row['Total Sky Cover']/10,
                                                          groundtemp=row['T_road'],wall_temp=row['T_wall'],
                                                          SVF=row['wallconf'],treecover=row['treecover']), axis=1)
            combined = pd.concat([merged_df, pd.concat(results.tolist(), ignore_index=True)], axis=1).reset_index(drop=True)

            output_file_path = os.path.join(output_folder_path, f'{file_name}.csv')
            combined.to_csv(output_file_path, index=False)



longitude_mapping={
    "大连": 121, "唐山": 118, "北京": 116, "天津":117,"保定":116, "石家庄": 114, "太原": 112, "烟台": 121,
    "济南":116,  "青岛": 120, "徐州": 117, "郑州": 113,  "洛阳": 111, "西安": 108, "兰州": 103, "扬州": 119,
    "南通": 120, "南京": 118, "嘉兴": 121, "常州": 119,"上海": 121, "芜湖": 118, "合肥": 116, "绍兴": 120, 
    "无锡": 120, "苏州": 120, "杭州": 119, "宁波": 121, "金华": 119, "台州": 121, "温州": 120, "南昌": 115, 
    "福州": 119, "泉州": 118, "厦门": 118, "武汉": 114, "长沙": 112, "重庆":106, "成都": 103, "贵阳":107, 
    "昆明": 102, "南宁": 108, "中山":113,"佛山": 112, "东菀": 113, "广州": 113, "澳门": 113,"深圳": 114, 
    "珠海": 113,"惠州": 114, "香港": 114, "汕头": 116, "海口": 110,"三亚": 109,"鄂尔多斯": 109, "银川": 106,
    "拉萨": 91, "西宁": 101, "呼和浩特":111, "长春":125, "沈阳":123, "哈尔滨":126
}


latitude_mapping={
    "大连":39, "唐山":39, "北京": 40, "天津": 39,"保定": 40, "石家庄": 38, "太原":37, "烟台": 37,
    "济南": 36,  "青岛":36, "徐州": 34, "郑州":34,  "洛阳": 34, "西安": 34, "兰州": 36, "扬州": 32,
    "南通": 32, "南京": 31, "嘉兴":30, "常州": 31,"上海": 30, "芜湖": 31, "合肥": 31, "绍兴": 30, 
    "无锡": 31, "苏州": 31, "杭州": 29, "宁波": 29, "金华": 28, "台州": 28, "温州": 27, "南昌": 28, 
    "福州": 26, "泉州": 24, "厦门":24, "武汉":30, "长沙": 28, "重庆": 29, "成都": 30, "贵阳":27, 
    "昆明": 24, "南宁": 22, "中山": 22,"佛山": 22, "东菀": 22, "广州": 23, "澳门": 22,"深圳": 22, 
    "珠海": 22,"惠州": 22, "香港": 22, "汕头": 23, "海口": 19,"三亚":18,"鄂尔多斯": 39, "银川": 38,
    "拉萨": 26, "西宁": 36,"呼和浩特":40,"长春":43,"沈阳":41,"哈尔滨":45
}


height_mapping={
    "大连": 27, "唐山": 90, "北京": 40, "天津": 3,"保定": 338, "石家庄": 30, "太原": 800, "烟台": 68,
    "济南": 112,  "青岛": 50, "徐州": 50, "郑州": 108,  "洛阳": 464, "西安": 974, "兰州": 1530, "扬州": 10,
    "南通": 4, "南京": 28, "嘉兴": 3.7, "常州": 14,"上海": 4, "芜湖": 57, "合肥": 75, "绍兴": 180, 
    "无锡": 8, "苏州": 8, "杭州": 12, "宁波":4, "金华": 316, "台州": 141, "温州": 180, "南昌": 42, 
    "福州": 258, "泉州": 352, "厦门": 29, "武汉": 28, "长沙": 180, "重庆": 318, "成都": 500, "贵阳": 1219, 
    "昆明":2034, "南宁": 76, "中山": 11,"佛山": 8, "东菀": 20, "广州": 21, "澳门": 22,"深圳": 28, 
    "珠海": 22,"惠州": 54, "香港": 1, "汕头": 55, "海口": 40,"三亚": 168,"鄂尔多斯": 1372, "银川": 1843,
    "拉萨": 3650 ,"西宁":3137,"呼和浩特":1050,"长春":200,"沈阳":40,"哈尔滨":140
}

city_names = ["大连", "唐山", "北京", "天津","保定", "石家庄", "太原", "烟台",
    "济南",  "青岛", "徐州", "郑州",  "洛阳", "西安", "兰州", "扬州",
    "南通", "南京", "嘉兴", "常州","上海", "芜湖", "合肥", "绍兴", 
    "无锡", "苏州", "杭州", "宁波", "金华", "台州", "温州", "南昌", 
    "福州", "泉州", "厦门", "武汉", "长沙", "重庆", "成都", "贵阳", 
    "昆明", "南宁", "中山","佛山", "东菀", "广州", "澳门","深圳", 
    "珠海","惠州", "香港", "汕头", "海口","三亚","鄂尔多斯", "银川",
    "拉萨" ,"西宁","呼和浩特","长春","沈阳","哈尔滨"]

for city_name in city_names:
    file_path = f"../{city_name}"
    output_folder_path = f".../{city_name}"
    longitude = longitude_mapping[city_name]
    latitude = latitude_mapping[city_name]
    altitude = height_mapping[city_name]

    calculate_Tmrt_mrged(city_name, file_path,longitude, latitude,altitude,output_folder_path)

