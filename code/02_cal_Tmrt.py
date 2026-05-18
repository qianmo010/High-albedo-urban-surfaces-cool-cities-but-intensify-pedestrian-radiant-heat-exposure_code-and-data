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



longitude_mapping = {
    "Dalian": 121, "Tangshan": 118, "Beijing": 116, "Tianjin": 117, "Baoding": 116, "Shijiazhuang": 114, "Taiyuan": 112, "Yantai": 121,
    "Jinan": 116, "Qingdao": 120, "Xuzhou": 117, "Zhengzhou": 113, "Luoyang": 111, "Xi'an": 108, "Lanzhou": 103, "Yangzhou": 119,
    "Nantong": 120, "Nanjing": 118, "Jiaxing": 121, "Changzhou": 119, "Shanghai": 121, "Wuhu": 118, "Hefei": 116, "Shaoxing": 120,
    "Wuxi": 120, "Suzhou": 120, "Hangzhou": 119, "Ningbo": 121, "Jinhua": 119, "Taizhou": 121, "Wenzhou": 120, "Nanchang": 115,
    "Fuzhou": 119, "Quanzhou": 118, "Xiamen": 118, "Wuhan": 114, "Changsha": 112, "Chongqing": 106, "Chengdu": 103, "Guiyang": 107,
    "Kunming": 102, "Nanning": 108, "Zhongshan": 113, "Foshan": 112, "Dongguan": 113, "Guangzhou": 113, "Macao": 113, "Shenzhen": 114,
    "Zhuhai": 113, "Huizhou": 114, "Hong Kong": 114, "Shantou": 116, "Haikou": 110, "Sanya": 109, "Ordos": 109, "Yinchuan": 106,
    "Lhasa": 91, "Xining": 101, "Hohhot": 111, "Changchun": 125, "Shenyang": 123, "Harbin": 126
}

latitude_mapping = {
    "Dalian": 39, "Tangshan": 39, "Beijing": 40, "Tianjin": 39, "Baoding": 40, "Shijiazhuang": 38, "Taiyuan": 37, "Yantai": 37,
    "Jinan": 36, "Qingdao": 36, "Xuzhou": 34, "Zhengzhou": 34, "Luoyang": 34, "Xi'an": 34, "Lanzhou": 36, "Yangzhou": 32,
    "Nantong": 32, "Nanjing": 31, "Jiaxing": 30, "Changzhou": 31, "Shanghai": 30, "Wuhu": 31, "Hefei": 31, "Shaoxing": 30,
    "Wuxi": 31, "Suzhou": 31, "Hangzhou": 29, "Ningbo": 29, "Jinhua": 28, "Taizhou": 28, "Wenzhou": 27, "Nanchang": 28,
    "Fuzhou": 26, "Quanzhou": 24, "Xiamen": 24, "Wuhan": 30, "Changsha": 28, "Chongqing": 29, "Chengdu": 30, "Guiyang": 27,
    "Kunming": 24, "Nanning": 22, "Zhongshan": 22, "Foshan": 22, "Dongguan": 22, "Guangzhou": 23, "Macao": 22, "Shenzhen": 22,
    "Zhuhai": 22, "Huizhou": 22, "Hong Kong": 22, "Shantou": 23, "Haikou": 19, "Sanya": 18, "Ordos": 39, "Yinchuan": 38,
    "Lhasa": 26, "Xining": 36, "Hohhot": 40, "Changchun": 43, "Shenyang": 41, "Harbin": 45
}

height_mapping = {
    "Dalian": 27, "Tangshan": 90, "Beijing": 40, "Tianjin": 3, "Baoding": 338, "Shijiazhuang": 30, "Taiyuan": 800, "Yantai": 68,
    "Jinan": 112, "Qingdao": 50, "Xuzhou": 50, "Zhengzhou": 108, "Luoyang": 464, "Xi'an": 974, "Lanzhou": 1530, "Yangzhou": 10,
    "Nantong": 4, "Nanjing": 28, "Jiaxing": 3.7, "Changzhou": 14, "Shanghai": 4, "Wuhu": 57, "Hefei": 75, "Shaoxing": 180,
    "Wuxi": 8, "Suzhou": 8, "Hangzhou": 12, "Ningbo": 4, "Jinhua": 316, "Taizhou": 141, "Wenzhou": 180, "Nanchang": 42,
    "Fuzhou": 258, "Quanzhou": 352, "Xiamen": 29, "Wuhan": 28, "Changsha": 180, "Chongqing": 318, "Chengdu": 500, "Guiyang": 1219,
    "Kunming": 2034, "Nanning": 76, "Zhongshan": 11, "Foshan": 8, "Dongguan": 20, "Guangzhou": 21, "Macao": 22, "Shenzhen": 28,
    "Zhuhai": 22, "Huizhou": 54, "Hong Kong": 1, "Shantou": 55, "Haikou": 40, "Sanya": 168, "Ordos": 1372, "Yinchuan": 1843,
    "Lhasa": 3650, "Xining": 3137, "Hohhot": 1050, "Changchun": 200, "Shenyang": 40, "Harbin": 140
}

city_names = [
    "Dalian", "Tangshan", "Beijing", "Tianjin", "Baoding", "Shijiazhuang", "Taiyuan", "Yantai",
    "Jinan", "Qingdao", "Xuzhou", "Zhengzhou", "Luoyang", "Xi'an", "Lanzhou", "Yangzhou",
    "Nantong", "Nanjing", "Jiaxing", "Changzhou", "Shanghai", "Wuhu", "Hefei", "Shaoxing",
    "Wuxi", "Suzhou", "Hangzhou", "Ningbo", "Jinhua", "Taizhou", "Wenzhou", "Nanchang",
    "Fuzhou", "Quanzhou", "Xiamen", "Wuhan", "Changsha", "Chongqing", "Chengdu", "Guiyang",
    "Kunming", "Nanning", "Zhongshan", "Foshan", "Dongguan", "Guangzhou", "Macao", "Shenzhen",
    "Zhuhai", "Huizhou", "Hong Kong", "Shantou", "Haikou", "Sanya", "Ordos", "Yinchuan",
    "Lhasa", "Xining", "Hohhot", "Changchun", "Shenyang", "Harbin"
]

for city_name in city_names:
    file_path = f"../{city_name}"
    output_folder_path = f".../{city_name}"
    longitude = longitude_mapping[city_name]
    latitude = latitude_mapping[city_name]
    altitude = height_mapping[city_name]

    calculate_Tmrt_mrged(city_name, file_path,longitude, latitude,altitude,output_folder_path)

