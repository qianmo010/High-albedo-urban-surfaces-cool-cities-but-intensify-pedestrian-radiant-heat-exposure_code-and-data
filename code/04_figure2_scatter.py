import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['font.serif'] = ['Arial']
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['ytick.direction'] = 'out'

RESULT_FOLDER = r"\data\02_figure2_data"

city_name_mapping = {
    "哈尔滨":"Harbin","北京": "Beijing", "上海": "Shanghai", "拉萨": "Lhasa",
    "昆明": "Kunming", "武汉":"Wuhan","广州": "Guangzhou","海口": "Haikou",
}
chinese_city_names = list(city_name_mapping.keys())
english_city_names = [city_name_mapping[c] for c in chinese_city_names]

y_variables = ["ΔTs", "ΔCUHI", "ΔTmrt"]
x_variables = ["vertohor", "blddensity", "bldheight"]

all_data = []

# 遍历读取指定文件夹内各城市结果表
for city_name in chinese_city_names:
    file_path = f"{RESULT_FOLDER}{city_name}.csv"
    print(f"读取文件: {file_path}")
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 宽表转长表，适配原有绘图结构
    for x_col in x_variables:
        # ΔTmrt
        tmp1 = df[["Id", x_col, "ΔTmrt"]].rename(columns={x_col:"x_value", "ΔTmrt":"diff"})
        tmp1["city"] = city_name
        tmp1["x_variable"] = x_col
        tmp1["indicator"] = "ΔTmrt"
        tmp1["period"] = "noon"
        all_data.append(tmp1)

        # ΔTs
        tmp2 = df[["Id", x_col, "ΔTs"]].rename(columns={x_col:"x_value", "ΔTs":"diff"})
        tmp2["city"] = city_name
        tmp2["x_variable"] = x_col
        tmp2["indicator"] = "ΔTs"
        tmp2["period"] = "noon"
        all_data.append(tmp2)

        # ΔUHI → 匹配原字段名ΔCUHI
        tmp3 = df[["Id", x_col, "ΔUHI"]].rename(columns={x_col:"x_value", "ΔUHI":"diff"})
        tmp3["city"] = city_name
        tmp3["x_variable"] = x_col
        tmp3["indicator"] = "ΔCUHI"
        tmp3["period"] = "noon"
        all_data.append(tmp3)

all_data = pd.concat(all_data, ignore_index=True)
noon_data = all_data.copy()
# 保留你原有异常值过滤
noon_data = noon_data[~((noon_data["indicator"] == "ΔCUHI") & (noon_data["diff"] < -0.6))]

# ---------- 以下绘图代码完全原样保留，无任何改动 ----------
city_colors = {
    "Beijing": "#6090C1", "Shanghai": "#ACD2E5", "Harbin": "#FEE395",
    "Lhasa": "#D7312D", "Haikou": "#F2724D", "Wuhan": "#F79015",
    "Kunming": "#FB8275", "Guangzhou": "#8F69C5",
}
x_label_mapping = {
    "vertohor": "vertical-to-horizontal aspect ratio",
    "blddensity": "building coverage",
    "bldheight": "building height"
}

y_limits = {}
for y_var in y_variables:
    y_vals = noon_data[noon_data["indicator"] == y_var]["diff"]
    y_min, y_max = y_vals.min(), y_vals.max()
    y_range = y_max - y_min
    y_limits[y_var] = (y_min - 0.1 * y_range, y_max + 0.1 * y_range)

fig, axs = plt.subplots(3, 3, figsize=(18, 12))

for row, y_var in enumerate(y_variables):
    y_data = noon_data[noon_data["indicator"] == y_var]
    for col, x_var in enumerate(x_variables):
        sub = y_data[y_data["x_variable"] == x_var]
        ax = axs[row, col]

        for chinese_city, english_city in zip(chinese_city_names, english_city_names):
            city_data = sub[sub["city"] == chinese_city].sort_values("x_value")
            x, y = city_data["x_value"].values, city_data["diff"].values
            ax.scatter(x, y, color=city_colors[english_city], alpha=0.1, s=30)

            if len(x) >= 3:
                try:
                    coeffs, cov = np.polyfit(x, y, deg=2, cov=True)
                    poly = np.poly1d(coeffs)
                    x_smooth = np.linspace(x.min(), x.max(), 200)
                    y_smooth = poly(x_smooth)

                    X = np.column_stack([x**2, x, np.ones_like(x)])
                    X_smooth = np.column_stack([x_smooth**2, x_smooth, np.ones_like(x_smooth.T)])
                    se = np.sqrt(np.diag(X_smooth @ cov @ X_smooth.T))
                    t_val = stats.t.ppf(0.975, len(x) - 3)
                    confidence = t_val * se

                    ax.plot(x_smooth, y_smooth,
                            color=city_colors[english_city], lw=3, label=english_city)
                    ax.fill_between(x_smooth,
                                    y_smooth - confidence,
                                    y_smooth + confidence,
                                    color=city_colors[english_city], alpha=0.2)
                except (np.linalg.LinAlgError, ValueError):
                    coeffs = np.polyfit(x, y, deg=2)
                    poly = np.poly1d(coeffs)
                    x_smooth = np.linspace(x.min(), x.max(), 200)
                    y_smooth = poly(x_smooth)
                    residuals = y - poly(x)
                    stderr = np.std(residuals)
                    confidence = 1.96 * stderr
                    ax.plot(x_smooth, y_smooth,
                            color=city_colors[english_city], lw=3, label=english_city)
                    ax.fill_between(x_smooth,
                                    y_smooth - confidence,
                                    y_smooth + confidence,
                                    color=city_colors[english_city], alpha=0.2)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)  
        ax.spines['bottom'].set_linewidth(1.5)  

        ax.set_ylim(y_limits[y_var])
        ax.tick_params(axis='both', labelsize=16)

        if row == 2:
            ax.set_xlabel(x_label_mapping.get(x_var, x_var), fontsize=20)
        else:
            ax.tick_params(axis='x', labelbottom=False)

        if col == 0:
            ax.set_ylabel(f"{y_var} (℃)", fontsize=20)
        else:
            ax.tick_params(axis='y', labelleft=False)

plt.subplots_adjust(wspace=0.1, hspace=0.15)

handles, labels = axs[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=8, fontsize=16,
           bbox_to_anchor=(0.5, -0.02), frameon=False)  

plt.tight_layout(rect=[0, 0.05, 1, 0.98])
#plt.savefig(r"C:/Users/scatter.jpg", bbox_inches='tight', dpi=300)
plt.show()