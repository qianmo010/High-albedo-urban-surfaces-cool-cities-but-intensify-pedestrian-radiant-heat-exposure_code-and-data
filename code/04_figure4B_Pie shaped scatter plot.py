import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import to_rgba
import jenkspy  

plt.rcParams['font.serif'] = ['Arial']
plt.rcParams['font.family'] = 'Arial'

GLOBAL_ALPHA = 1

# ================= file path =================
tmrt_dir = r"...\data\03_figure4_data"
bld_file = r"...\data\all_cities_blddensity.xlsx"
height_file = r"...\data\all_cities_bldheight.xlsx"

# ================= city names (英文) =================
city_names_en = [
    "Macao", "Baoding", "Chengdu", "Dalian", "Ordos", "Foshan", "Guangzhou", "Hangzhou", "Hefei", "Huizhou",
    "Jinan", "Jinhua", "Kunming", "Lhasa", "Lanzhou", "Nanning", "Nantong", "Ningbo", "Qingdao", "Quanzhou", "Sanya",
    "Xiamen", "Shantou", "Shenzhen", "Shijiazhuang", "Suzhou", "Taizhou", "Taiyuan", "Tangshan", "Wuhu", "Wuhan",
    "Xi'an", "Yangzhou", "Yinchuan", "Zhengzhou", "Zhongshan", "Zhuhai", "Shanghai", "Beijing", "Chongqing", "Nanjing",
    "Changsha", "Dongguan", "Wuxi", "Fuzhou", "Guiyang", "Nanchang", "Changzhou", "Jiaxing", "Xuzhou",
    "Shaoxing", "Yantai", "Haikou", "Luoyang", "Xining", "Tianjin", "Hong Kong", "Harbin", "Hohhot", "Changchun", "Shenyang"
]

all_tmrt_values = []
all_cool_values = []

for city in city_names_en:
    m_path = os.path.join(tmrt_dir, f"{city}.xlsx")
    m = pd.read_excel(m_path)  
    m = m[m['blddensity'] > 0.03]
    all_tmrt_values.extend(m['ΔTmrt'].dropna().values)
    all_cool_values.extend(m['ΔT_road'].dropna().values)

# ================= natural break =================
tmrt_breaks = jenkspy.jenks_breaks(np.array(all_tmrt_values), 3)
cool_breaks = jenkspy.jenks_breaks(np.array(all_cool_values), 3)

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

def map_category(warming, cooling):
    return f"{warming}-{cooling}"

# ================= color =================
color_dict = {
    'low warming-low cooling':'#F5E5FF',
    'low warming-middle cooling':'#84CEF3',
    'low warming-high cooling':'#13B4E8',
    'middle warming-low cooling':'#FB7381',
    'middle warming-middle cooling':'#9E7DB4',
    'middle warming-high cooling':'#386CB5',
    'high warming-low cooling':'#FE0000',
    'high warming-middle cooling':'#AF1440',
    'high warming-high cooling':'#5D2681'
}
ordered_categories = list(color_dict.keys())

records = []
for city in city_names_en:
    m_path = os.path.join(tmrt_dir, f"{city}.xlsx")
    m = pd.read_excel(m_path)
    m = m[m['blddensity'] > 0.03]

    m['warming'] = m['ΔTmrt'].apply(classify_warming)
    m['cooling'] = m['ΔT_road'].apply(classify_cooling)
    m['Category'] = m.apply(lambda x: map_category(x['warming'], x['cooling']), axis=1)

    counts = m['Category'].value_counts(normalize=True)
    for cat in ordered_categories:
        records.append({
            'city': city,  # 直接使用英文名
            'Category': cat,
            'Proportion': counts.get(cat, 0)
        })

plot_df = pd.DataFrame(records)

# ================= building data =================
bld_df = pd.read_excel(bld_file)
bld_df['city'] = bld_df['city'].str.replace('.xlsx', '', regex=False)  # 直接使用英文名，不需要map

height_df = pd.read_excel(height_file)
height_df['city'] = height_df['city'].str.replace('.xlsx', '', regex=False)  # 直接使用英文名

density_raw = bld_df.set_index('city')['mean_blddensity']
height_raw = height_df.set_index('city')['mean_bldheight']

city_abbr = {
    'Harbin': 'HRB', 'Beijing': 'BJ', 'Shanghai': 'SH', 'Wuhan': 'WH',
    'Guangzhou': 'GZ', 'Kunming': 'KM', 'Lhasa': 'LXA', 'Haikou': 'HK'
}

# ================= plot =================
fig, ax = plt.subplots(figsize=(10, 5))

x_min, x_max = height_raw.min(), height_raw.max()
y_min, y_max = density_raw.min(), density_raw.max()
x_range = x_max - x_min
pie_size = 0.06

def draw_city_pie(city_name):
    if city_name not in height_raw or city_name not in density_raw:
        return
    x = height_raw[city_name]
    y = density_raw[city_name]

    city_data = plot_df[plot_df['city'] == city_name]
    if city_data.empty:
        return

    sizes = []
    colors_with_alpha = []
    for cat in ordered_categories:
        val = city_data[city_data['Category'] == cat]['Proportion'].values[0]
        sizes.append(val)
        colors_with_alpha.append(to_rgba(color_dict[cat], GLOBAL_ALPHA))

    width = x_range * pie_size
    height_ax = (y_max - y_min) * pie_size * (fig.get_size_inches()[0] / fig.get_size_inches()[1])

    pie_ax = ax.inset_axes([x - width/2, y - height_ax/2, width, height_ax], transform=ax.transData)

    z = 20 if city_name in city_abbr else 2
    wedges, _ = pie_ax.pie(sizes, colors=colors_with_alpha, wedgeprops={'edgecolor': 'none'})
    pie_ax.set_aspect('equal')
    pie_ax.axis('off')
    pie_ax.set_zorder(z)

    if city_name in city_abbr:
        circle = plt.Circle((0, 0), 1, transform=pie_ax.transData, fill=False, edgecolor='black', linewidth=0.4, zorder=25)
        pie_ax.add_artist(circle)

for city in density_raw.index:
    if city not in city_abbr:
        draw_city_pie(city)
for city in city_abbr.keys():
    draw_city_pie(city)

ax.set_xlim(x_min - x_range * 0.05, x_max + x_range * 0.05)
ax.set_ylim(y_min - (y_max - y_min) * 0.05, y_max + (y_max - y_min) * 0.05)

ax.set_xlabel("Building height (m)", fontsize=16)
ax.set_ylabel("Building coverage", fontsize=16)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1)
ax.spines['bottom'].set_linewidth(1)
ax.tick_params(axis='both', labelsize=16)

plt.tight_layout()
#plt.savefig(".../pie.svg", bbox_inches='tight', facecolor='white')
plt.show()

print("Completed")