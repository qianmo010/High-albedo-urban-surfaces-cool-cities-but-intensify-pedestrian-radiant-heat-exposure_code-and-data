import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.weight'] = 'bold'     
plt.rcParams['axes.labelweight'] = 'bold' 
plt.rcParams['axes.titleweight'] = 'bold' 

def create_tmrt_plot(ax, density_df, group_name, city_name):

    tmrt0_mean = density_df['Tmrt00'].mean()
    tmrt_vertohor_mean = density_df['Tmrt0_vertohor'].mean()
    tmrt_grasscover_mean = density_df['Tmrt0_grasscover'].mean()
    tmrt_treecover_mean = density_df['Tmrt0_treecover'].mean()
    Tmrt_shortwave = density_df['Tmrt_shortwave'].mean()
    Tmrt_longwave = density_df['Tmrt_longwave'].mean()
    Tmrt_combined = density_df['Tmrt_combined'].mean()

    Eshort_mean = density_df['Eshort00'].mean()
    Elong_mean = density_df['Elong00'].mean()
    Etot = Eshort_mean + Elong_mean
    P_short = Eshort_mean / Etot
    P_long = Elong_mean / Etot

    deltas = {
        'bare land': tmrt0_mean,
        'building': tmrt_vertohor_mean - tmrt0_mean,
        'grasscover': tmrt_grasscover_mean - tmrt_vertohor_mean,
        'treecover': tmrt_treecover_mean - tmrt_grasscover_mean,
        'basic albedo': tmrt_treecover_mean,
        'basic-S': Tmrt_shortwave - tmrt_treecover_mean,
        'basic-S&L': Tmrt_combined - Tmrt_shortwave,
        'high albedo': Tmrt_combined
    }
    categories = list(deltas.keys())
    values = list(deltas.values())

    colors = [
        '#927661',  # wasteland 
        '#6E6F83',  # vertohor 
        '#AFDCCA',  # grasscover
        '#83AD7B',  # treecover
        '#AE727C',  # basic albedo
        '#A8A8D8',  # basic-S
        '#D9A7A9',  # basic-L
        '#79A8AB'   # high albedo
    ]

    color_short = '#C3C5C9' 
    color_long = "#E6E6E6"   

    # Calculate cumulative height
    cumulative_heights = [values[0]]
    
    for i in range(1, len(values)):
        if i in [4, 7]:  
            cumulative_heights.append(values[i])
        else:
            cumulative_heights.append(cumulative_heights[-1] + values[i])

    for i, (cat, val) in enumerate(zip(categories, values)):
        if i == 0:
            short_height = tmrt0_mean * P_short
            long_height = tmrt0_mean * P_long
            ax.bar(cat, short_height, color=color_short, edgecolor='none', width=0.8, label="Eshort")
            ax.bar(cat, long_height, bottom=short_height, color=color_long, edgecolor='none', width=0.8, label="Elong")
        elif i in [4, 7]:  
            ax.bar(cat, val, bottom=0, color=colors[i], edgecolor='none', width=0.8)
        else:
            if val >= 0:
                bottom = cumulative_heights[i-1]
                height = val
            else:
                bottom = cumulative_heights[i-1] + val
                height = -val
            ax.bar(cat, height, bottom=bottom, color=colors[i], edgecolor='none', width=0.8)

    for i in range(len(values)):
        val = values[i]
        if i == 0:
            short_height = tmrt0_mean * P_short
            long_height = tmrt0_mean * P_long

            ax.text(i, short_height/2, f"{P_short*100:.1f}%", ha='center', va='center',
            fontsize=30, color='black',fontweight='bold')
            ax.text(i, short_height + long_height/2, f"{P_long*100:.1f}%", ha='center', va='center',
            fontsize=30, color='black',fontweight='bold')

            y_pos = tmrt0_mean + 0.5
            ax.text(i, y_pos, f"{tmrt0_mean:.1f}", ha='center', va='bottom', fontsize=32, color='black',fontweight='bold')

        elif i in [4, 7]:
            y_pos = val + 0.5 if val >= 0 else val - 0.5
            va = 'bottom' if val >= 0 else 'top'
            ax.text(i, y_pos, f"{val:.1f}", ha='center', va=va, fontsize=32, color='black',fontweight='bold')
        else:
            current_height = cumulative_heights[i]
            y_pos = current_height + 0.5 if val >= 0 else current_height - 0.5
            va = 'bottom' if val >= 0 else 'top'
            ax.text(i, y_pos, f"{val:+.1f}", ha='center', va=va, fontsize=32, color='black',fontweight='bold')

    ax.set_title(f'{group_name}', fontsize=26, pad=26)
    if group_name == 'low':
        ax.set_ylabel('Tmrt (°C)', fontsize=50)
    ax.tick_params(axis='both', which='both', length=0, labelsize=34)

    ax.set_ylim(0, 90)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color('black')
    plt.setp(ax.get_xticklabels(), rotation=90, ha='right')

    
    # add legend
    if group_name == 'low':
        ax.legend(fontsize=26, frameon=False, loc="upper left",
                  bbox_to_anchor=(1.0, 0.95))


def create_simple_tmrt_plot(ax, density_df, group_name, city_name):
    create_tmrt_plot(ax, density_df, group_name, city_name)

def plot_all_density_groups(file_path, city_name):
    df = pd.read_csv(file_path)

    df['density_group'] = pd.qcut(
        df['blddensity'], 
        q=3,
        labels=['low', 'medium', 'high'],
        duplicates='drop'
    )

    # 创建3个子图
    fig, axes = plt.subplots(1, 3, figsize=(27, 7.5), sharey=True)
    for i, group_name in enumerate(['low', 'medium', 'high']):
        group_df = df[df['density_group'] == group_name]
        if len(group_df) > 0:
            if group_name == 'low':
                create_tmrt_plot(axes[i], group_df, group_name, city_name)
            else:
                create_simple_tmrt_plot(axes[i], group_df, group_name, city_name)
        else:
            axes[i].text(0.5, 0.5, f'No data for {group_name}', 
                        ha='center', va='center', transform=axes[i].transAxes)
            #axes[i].set_title(group_name, fontsize=40)
    
    # 设置整体标题
    #plt.suptitle(f'{city_name}', fontsize=24, y=0.98)
    plt.tight_layout()
    
    # 保存图像
    output_path = f".../{city_name}.svg"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()
    
    print(f"Saved: {city_name}")

def analyze_all_cities():
    city_names = ["澳门","保定","成都","大连","鄂尔多斯","佛山","广州","杭州","合肥","惠州",
              "济南","金华","昆明","拉萨","兰州","南宁","南通","宁波","青岛","泉州","三亚",
              "厦门","汕头","深圳","石家庄","苏州","台州","太原","唐山","芜湖","武汉",
              "西安","扬州","银川","郑州","中山","珠海","上海","北京","重庆","南京","长沙","东莞",
              "无锡","福州","贵阳","南昌","常州","嘉兴","徐州","海口"
              "绍兴","烟台","洛阳","西宁","天津","香港","哈尔滨","呼和浩特","长春","沈阳",]     


    for city_name in city_names:
        
        print(f"Processing: {city_name}")
        file_path = f".../data/figure3_data/{city_name}.csv"
        plot_all_density_groups(file_path, city_name)
# 运行分析
analyze_all_cities()