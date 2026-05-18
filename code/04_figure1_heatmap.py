import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Rectangle

plt.rcParams['font.serif'] = ['Arial']

summer_file = r"C:\Users\HP\Desktop\summer.csv"
winter_file = r"C:\Users\HP\Desktop\winter.csv"
output_dir = ""
city_col = "city"
hour_col = "hour"

city_name_map = {
    "大连": "Dalian", "唐山": "Tangshan", "北京": "Beijing", "天津": "Tianjin",
    "保定": "Baoding", "石家庄": "Shijiazhuang", "太原": "Taiyuan", "烟台": "Yantai",
    "济南": "Jinan",  "青岛": "Qingdao", "徐州": "Xuzhou", "郑州": "Zhengzhou",  
    "洛阳": "Luoyang", "西安": "Xi'an", "兰州": "Lanzhou", "扬州": "Yangzhou",
    "南通": "Nantong", "南京": "Nanjing", "嘉兴": "Jiaxing", "常州": "Changzhou",
    "上海": "Shanghai", "芜湖": "Wuhu", "合肥": "Hefei", "绍兴": "Shaoxing", 
    "无锡": "Wuxi", "苏州": "Suzhou", "杭州": "Hangzhou", "宁波": "Ningbo", 
    "金华": "Jinhua", "台州": "Taizhou", "温州": "Wenzhou", "南昌": "Nanchang", 
    "福州": "Fuzhou", "泉州": "Quanzhou", "厦门": "Xiamen", "武汉": "Wuhan", 
    "长沙": "Changsha", "重庆": "Chongqing", "成都": "Chengdu", "贵阳": "Guiyang", 
    "昆明": "Kunming", "南宁": "Nanning", "中山": "Zhongshan","佛山": "Foshan", 
    "东莞": "Dongguan", "广州": "Guangzhou", "澳门": "Macao","深圳": "Shenzhen", 
    "珠海": "Zhuhai","惠州": "Huizhou", "香港": "Hong Kong", "汕头": "Shantou", 
    "海口": "Haikou","三亚": "Sanya",
    "鄂尔多斯": "Ordos", "银川": "Yinchuan",
    "拉萨": "Lhasa", "西宁": "Xining","哈尔滨":"Harbin","长春":"Changchun","沈阳":"Shenyang","呼和浩特":"Hohhot","温州":"Wenzhou"
}


df_summer = pd.read_csv(summer_file,encoding='gbk')
df_winter = pd.read_csv(winter_file,encoding='gbk')

value_cols = [c for c in df_summer.columns if c not in [city_col, hour_col]]
df_summer[value_cols] = df_summer[value_cols].apply(pd.to_numeric, errors="coerce")
df_winter[value_cols] = df_winter[value_cols].apply(pd.to_numeric, errors="coerce")

#os.makedirs(output_dir, exist_ok=True)

bounds = [-10, -5, -2, -1, -0.5, -0.1, 0, 0.1, 0.5, 2, 5, 10, 20]

colors = [
    "#305388",  # -10 ~ -5
    "#406FB5",    # -5~--2
    "#688FCA",    # -2 ~ -1
    "#86A6D5",    # -0.5 ~ -1  
    "#C3D2EA",    # -0.1~-0.5
    "#E1E8F4",    # -0.1 ~ 0  
    "#FFEEEB",    # 0 ~ 0.1
    "#FDD5AF",    # 0.1 ~ 0.5  
    "#F99462",    # 0.5 ~ 2
    "#FD5635",     # 2 ~ 5
    "#F42B03",    #5 ~ 10
    "#E70E02",      #10 ~ 20
]

group_names = ["ΔTs", "ΔCUHI", "ΔTmrt"]  

for city in df_summer[city_col].unique():
    summer_df = df_summer[df_summer[city_col] == city].set_index(hour_col)[value_cols]
    winter_df = df_winter[df_winter[city_col] == city].set_index(hour_col)[value_cols]
    
    city_english = city_name_map.get(city, city)  
    heatmap_data_list = []
    row_labels = []
    season_labels = []  
    for var in value_cols:
        if var in summer_df.columns:
            heatmap_data_list.append(summer_df[[var]].T)
            row_labels.append(f"{var}_summer")
            season_labels.append("S")
        if var in winter_df.columns:
            heatmap_data_list.append(winter_df[[var]].T)
            row_labels.append(f"{var}_winter")
            season_labels.append("W")

    heatmap_data = pd.concat(heatmap_data_list, axis=0)
    heatmap_data.index = row_labels

    desired_order = []
    season_order = []
    for var in value_cols:
        desired_order.append(f"{var}_summer")
        season_order.append("S")
        desired_order.append(f"{var}_winter")
        season_order.append("W")
    heatmap_data = heatmap_data.reindex(desired_order)
    season_labels = season_order

    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bounds, len(colors), extend="neither")
    plt.figure(figsize=(6, len(heatmap_data)*0.5))
    ax = sns.heatmap(
        heatmap_data,
        cmap=cmap,
        norm=norm,
        linewidths=0.7,
        linecolor='white',
        annot=False,
        cbar=False
    )

    ax.set_yticks([])
    ax.set_yticklabels([])

    hours = heatmap_data.columns.astype(int)
    xtick_positions = [i + 0.5 for i, h in enumerate(hours) if h % 3 == 0]
    xtick_labels = [str(h) for h in hours if h % 3 == 0]
    ax.set_xticks(xtick_positions)
    ax.set_xticklabels(xtick_labels, fontsize=14)

    # ==== colorbar ====
    fig = plt.gcf()
    im = ax.collections[0]
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.05, pad=0.3, aspect=40)
    cbar.set_label("Changes in temperatures",fontsize=14)

    n_rows = heatmap_data.shape[0]

    left_margin = -2
    for i, label_text in enumerate(season_labels):
        y_center = i + 0.5
        t = ax.text(left_margin + 1.5, y_center, label_text, ha='center', va='center', fontsize=14)
        rect_width = 1
        rect_height = 1
        rect_x = left_margin+1
        rect_y = i
        rect = Rectangle(
            (rect_x, rect_y),
            rect_width,
            rect_height,
            linewidth=0.7,
            edgecolor='black',
            facecolor='none',
            transform=ax.transData,
            clip_on=False
        )
        ax.add_patch(rect)

    group_width = 4
    for j, group_name in enumerate(group_names):
        start_row = j*2
        if start_row >= n_rows:
            break
        end_row = min(start_row + 2, n_rows)
        rect_y = start_row
        rect_height = end_row - start_row
        rect_x = left_margin+1 - group_width
        group_rect = Rectangle(
            (rect_x, rect_y),
            group_width,
            rect_height,
            linewidth=0.7,
            edgecolor='black',
            facecolor='none',
            transform=ax.transData,
            clip_on=False
        )
        ax.add_patch(group_rect)
        ax.text(rect_x + group_width/2, rect_y + rect_height/2, group_name,
                ha='center', va='center', fontsize=14)

    n_cols = heatmap_data.shape[1]
    outer_rect = Rectangle(
        (0, 0), n_cols, n_rows,
        linewidth=0.7,
        edgecolor='black',
        facecolor='none',
        transform=ax.transData,
        clip_on=False
    )
    ax.add_patch(outer_rect)
    
    for i in range(2, n_rows, 2):
        ax.hlines(i, xmin=0, xmax=n_cols, colors='black', linewidth=1)
    
    
    group_width = -29  
    city_rect_height = 1  
    city_rect_y = n_rows-7  
    city_rect_x = left_margin -3 - group_width  

    city_top_rect = Rectangle(
    (city_rect_x, city_rect_y),
    group_width,
    city_rect_height,
    linewidth=0.7,
    edgecolor='black',
    facecolor='none',
    transform=ax.transData,
    clip_on=False
    )
    ax.add_patch(city_top_rect)

    ax.text(city_rect_x + group_width/2, city_rect_y + city_rect_height/2,
        city_english, ha='center', va='center', fontsize=16, fontweight='bold')
    plt.xlabel("hour", fontsize=16)
    plt.tight_layout()

    output_path = os.path.join(output_dir, f"{city_english}.svg")
    #plt.savefig(output_path,)
    plt.show()
    print(f"Saved: {output_path}")
