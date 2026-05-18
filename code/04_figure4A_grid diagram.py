import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import jenkspy

plt.rcParams['font.serif'] = ['Arial']

shp_dir   = r"D:/script/data/04_urban morphology_shp/"
tmrt_dir  = r"D:/script/data/03_figure4_data/"

out_pic = ".../grid/"
out_shp = ".../shp/"

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

all_tmrt_values = []
all_cool_values = []

for city in city_names:
    merged  = pd.read_excel(f"{tmrt_dir}{city}.xlsx")
    
    merged = merged[merged['blddensity'] > 0.03]
    
    all_tmrt_values.extend(merged['ΔTmrt'].dropna().values)
    all_cool_values.extend(merged['ΔT_road'].dropna().values)

# ================= natural break =================
tmrt_breaks = jenkspy.jenks_breaks(np.array(all_tmrt_values), 3)
cool_breaks = jenkspy.jenks_breaks(np.array(all_cool_values), 3)

print("Tmrt breaks:", tmrt_breaks)
print("Cooling breaks:", cool_breaks)

# ================= Classification function =================
def classify_warming(value):
    if pd.isna(value) or value <= tmrt_breaks[1]:
        return 'low warming'
    elif value <= tmrt_breaks[2]:
        return 'middle warming'
    else:
        return 'high warming'

def classify_cooling(value):
    if pd.isna(value) or value >= cool_breaks[2]:
        return 'low cooling'
    elif value >= cool_breaks[1]:
        return 'middle cooling'
    else:
        return 'high cooling'

def map_category(warming_class, cooling_class):
    return f"{warming_class}-{cooling_class}"


category_config = {
    'low warming-low cooling': {'color': '#F5E5FF', 'alpha':1 },
    'low warming-middle cooling': {'color': '#84CEF3', 'alpha': 1},
    'low warming-high cooling': {'color': '#13B4E8', 'alpha': 1},
    
    'middle warming-low cooling': {'color': '#FB7381', 'alpha': 1},
    'middle warming-middle cooling': {'color': '#9E7DB4', 'alpha': 1},
    'middle warming-high cooling': {'color': '#386CB5', 'alpha': 1},
    
    'high warming-low cooling': {'color': '#FE0000', 'alpha': 1},
    'high warming-middle cooling': {'color': '#AF1440', 'alpha': 1},
    'high warming-high cooling': {'color': '#5D2681', 'alpha': 1}
}

# ================= Unified proportional range function =================
def analyze_city_extents(cities):
    xs, ys = [], []
    for city in cities:
        gdf = gpd.read_file(f"{shp_dir}{city}.shp")
        b = gdf.total_bounds
        xs.append(b[2]-b[0])
        ys.append(b[3]-b[1])
    return max(xs), max(ys)

max_x_range, max_y_range = analyze_city_extents(city_names)

for city in city_names:
    print(f"Processing {city}...")

    grid_gdf = gpd.read_file(f"{shp_dir}{city}.shp")
    merged  = pd.read_excel(f"{tmrt_dir}{city}.xlsx")

    merged = merged[merged['blddensity'] > 0.03]

    merged['warming_class'] = merged['ΔTmrt'].apply(classify_warming)
    merged['cool_class']    = merged['ΔT_road'].apply(classify_cooling)
    merged['grid_category'] = merged.apply(lambda x: map_category(x['warming_class'], x['cool_class']), axis=1)

    merged['color'] = merged['grid_category'].apply(lambda x: category_config[x]['color'])
    merged['alpha'] = merged['grid_category'].apply(lambda x: category_config[x]['alpha'])

    grid_gdf = grid_gdf.merge(merged[['Id','grid_category','color','alpha']], on='Id', how='inner')

    # ================= plot =================
    fig, ax = plt.subplots(figsize=(10,10))

    for idx, row in grid_gdf.iterrows():
        if row.geometry.geom_type == 'Polygon':
            x, y = row.geometry.exterior.xy
            ax.fill(x, y, color=row['color'], alpha=row['alpha'], edgecolor='grey', linewidth=0.3)
        elif row.geometry.geom_type == 'MultiPolygon':
            for polygon in row.geometry.geoms:
                x, y = polygon.exterior.xy
                ax.fill(x, y, color=row['color'], alpha=row['alpha'], edgecolor='grey', linewidth=0.3)

    bounds = grid_gdf.total_bounds
    x_center = (bounds[0] + bounds[2]) / 2
    y_center = (bounds[1] + bounds[3]) / 2
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    max_side = max(width, height)
    margin = 0.1 * max_side

    ax.set_xlim(x_center - max_side/2 - margin, x_center + max_side/2 + margin)
    ax.set_ylim(y_center - max_side/2 - margin, y_center + max_side/2 + margin)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    #plt.savefig(f"{out_pic}{city}.svg", dpi=300, bbox_inches='tight', transparent=True)
    plt.show()
    plt.close()

    #grid_gdf.to_file(f"{out_shp}{city}.shp", encoding='utf-8')

    print(f"{city} ")

print("All cities have been processed")