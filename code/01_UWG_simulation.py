from uwg import UWG
import pandas as pd
import os

def generate_file(epw_path,dtsim,number,city_name, urban_path,new_epw_dir,excel_path,month,day,nday,zone,albroad,albwall,albroof):
    df = pd.read_excel(urban_path)
    n = number
    for bldheight, blddensity, vertohor,grasscover,treecover in zip(df["bldheight"], df["blddensity"], df["vertohor"],df["grasscover"],df["treecover"]):
        n += 1
        if blddensity > 0.03:
        # # Initialize the UWG model by passing parameters as arguments, or relying on defaults
            model = UWG.from_param_args(bldheight=bldheight, blddensity=blddensity, vertohor=vertohor, grasscover=grasscover,
                                        treecover=treecover, zone=zone, month=month, day=day, nday=nday, dtsim=dtsim,
                                        dtweather=3600, bld=(('largeoffice', 'pst80', 0.4),
                                                             ('midriseapartment', 'pst80', 0.6)), autosize=0,
                                        h_mix=1, sensocc=100, latfocc=0.3, radfocc=0.2, radfequip=0.5,
                                        radflight=0.7, charlength=1000, albroad=albroad,
                                        droad=0.5, kroad=1.0, croad=1600000, rurvegcover=0.9, vegstart=4, vegend=10,
                                        albveg=0.25, latgrss=0.4, lattree=0.6, sensanth=20,
                                        schtraffic=(
                                            (0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.7, 0.9, 0.9, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 0.8,
                                             0.9, 0.9, 0.8, 0.8, 0.7, 0.3, 0.2, 0.2),  # Weekday
                                            (0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.6, 0.7,
                                             0.7, 0.7, 0.7, 0.5, 0.4, 0.3, 0.2, 0.2),  # Saturday
                                            (0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4,
                                             0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.2, 0.2)), h_ubl1=1000, h_ubl2=80, h_ref=150,
                                        h_temp=2, h_wind=10, c_circ=1.2, c_exch=1, maxday=150,
                                        maxnight=20, windmin=1, h_obs=0.1, epw_path=epw_path,
                                        new_epw_dir = new_epw_dir, new_epw_name=f"{city_name}{n}.epw", ref_bem_vector=None,
                                        ref_sch_vector=None)
            model.albwall = albwall
            model.albroof = albroof
            model.generate()
            model.simulate()
            model.new_epw_path
            model.write_epw()

            UCM_data = model.UCMData
            UBL_data = model.UBLData
            Weather_data = model.WeatherData

            T_rur = [ Weather_data_i.__dict__['temp']-273.15 for Weather_data_i in Weather_data ]
            T_can = [ UCM_data_i.__dict__['canTemp']-273.15 for UCM_data_i in UCM_data ]
            T_road = [ UCM_data_i.__dict__['roadTemp']-273.15 for UCM_data_i in UCM_data ]
            T_wall = [ UCM_data_i.__dict__['wallTemp']-273.15 for UCM_data_i in UCM_data ]
            T_roof = [ UCM_data_i.__dict__['roofTemp']-273.15 for UCM_data_i in UCM_data ]
            UHI = [T_can - T_rur for T_can, T_rur in zip(T_can, T_rur)]

            Rh_can = [ UCM_data_i.__dict__['canRHum'] for UCM_data_i in UCM_data ]
            Rh_rur = [ Weather_data_i.__dict__['rHum'] for Weather_data_i in Weather_data ]
            wind_can = [ UCM_data_i.__dict__['canWind'] for UCM_data_i in UCM_data ]
            wind_rur = [ Weather_data_i.__dict__['wind'] for Weather_data_i in Weather_data ]

            wallconf = [UCM_data_i.__dict__['wallConf'] for UCM_data_i in UCM_data ]
            roadConf = [UCM_data_i.__dict__['roadConf'] for UCM_data_i in UCM_data ]


            data={'T_rur':T_rur,'T_can':T_can,'T_road':T_road,'T_wall':T_wall,'T_roof':T_roof,'UHI':UHI,
                  'Rh_can':Rh_can,'Rh_rur':Rh_rur,'wind_can':wind_can,'wind_rur':wind_rur,'wallconf':wallconf,
                  }
            df=pd.DataFrame(data)
            path = os.path.join(excel_path,f"{city_name}{n}.xlsx")
            df.to_excel(path)




city_name = ...
# urban morphology data
urban_path = f".../data/urban morpholog/{city_name}.xlsx"

month = ...
day = ...
nday = ...
zone = ...
part = ...

albroad = 0.1
albwall = 0.3
albroof = 0.3

# rural epw file
epw_path = ...

# output epw file path
new_epw_dir = ...
# output excel file path
excel_path = ...

generate_file(epw_path,300,0,city_name, 
            urban_path,new_epw_dir,excel_path,
            month,day,nday,zone,
            albroad,albwall,albroof)