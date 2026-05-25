import pandas as pd
import numpy as np
import pvlib
from datetime import datetime, timedelta

#1. calculate solarparam
def calc_solarparam(time_str, latitude, longitude, altitude, groundalbedo=0.18, human=True, TC=0, time_str_end=None):
    """ This function uses PVLib to calculate solar parameters. 
    Returns a DataFrame of solar vector, solar view factor, 
    direct solar radiation intensity, and diffuse solar radiation 
    intensities from the sky and the ground """
    if time_str_end is None:
        time_str_end = time_str

    # using Asia/Shanghai timezone
    thistime = pd.date_range(start=time_str, end=time_str_end, freq='1min', tz='Asia/Shanghai')

    thisloc = pvlib.location.Location(latitude, longitude, tz='Asia/Shanghai', altitude=altitude, name=None)

    # Solar position and the vector components 
    solpos = thisloc.get_solarposition(thistime) 
    sunpz = np.sin(np.radians(solpos.elevation[0])); 
    hyp = np.cos(np.radians(solpos.elevation[0]))
    sunpy = hyp*np.cos(np.radians(solpos.azimuth[0]))
    sunpx = hyp*np.sin(np.radians(solpos.azimuth[0]))
    # Solar position angles (Zenith and Azimuth)


    solar_pmt =  thisloc.get_clearsky(thistime,model='ineichen') 
    E_sol= solar_pmt['dni'][0] #direct normal solar irradiation  [W/m^2] for clear sky  
    E_totalglobalradiation = solar_pmt['ghi'][0]   # total global radiation
    E_dhi = solar_pmt['dhi'][0]   # total global radiation

    """ Estimation of solar radiation based on total cloud cover (TC) by Luo et al 2010"""
    """ TC takes a value between 0 and 0.8. """ 
    """ E0_Ec is the ratio of observed solar radiation to clear-sky solar radiation """ 
    TC=0.8*(TC-0)/(1-0)
    E0_Ec=1.0-1.9441*TC**3+2.8777*TC**2-2.2023*TC 
    N=1.0-E0_Ec
    E_sol=E_sol*(1.0-N)

    Ground_Diffuse = pvlib.irradiance.get_ground_diffuse(surface_tilt=90, ghi=solar_pmt['ghi'], albedo=groundalbedo)[0]#Diffuse radiation received on the vertical human body based on reflected solar radiation from the ground [W/m^2]
    Sky_Diffuse =  pvlib.irradiance.isotropic(90, solar_pmt['dhi'])[0] #Diffuse Solar Irradiation [W/m^2].        
    
    """ Formula 9 in Huang et. al. 2014 1966 from Underwood and Ward  for a standing person, 
    largely independent of gender, body shape and size. For a sitting person, approximately 0.25 """ 
    if human:
        solarvf=abs(0.0355*np.sin(solpos.elevation[0])+2.33*np.cos(solpos.elevation[0])*(0.0213*np.cos(solpos.azimuth[0])**2+0.00919*np.sin(solpos.azimuth[0])**2)**(0.5)); 
    else:
        solarvf=0.25 # In case calculations are done for a sensor instead of a human 
        
    results = pd.DataFrame({
    'solarvector':[(sunpx,sunpy,sunpz)],
    'solarviewfactor':[solarvf],
    'direct_sol':[E_sol],
    'diffuse_frm_sky':[Sky_Diffuse],
    'diffuse_frm_ground':[Ground_Diffuse],
    'E_ghi':[E_totalglobalradiation],
    'E_dhi':[E_dhi],
    })    
    return results


# 3.Calculate longwave radiation from the sky
def calc_Esky_emis(Ta,RH,TC=0):
    """ returns scalar of longwave radiation from the sky, that needs to be factored by SVF  """
    sigma =5.67*10**(-8)
    TaK =  Ta+273.15
    """ Estimation of solar radiation based on total cloud cover (TC) by Luo et al 2010"""
    """ TC takes a value between 0 and 0.8. """ 
    """ E0_Ec is the ratio of observed solar radiation to clear-sky solar radiation """ 
    E0_Ec=1.0-1.9441*TC**3+2.8777*TC**2-2.2023*TC 
    N=1.0-E0_Ec
    """ Sky emissivity Idso and Jackson (1969) considering cloud cover based on the comparison of Finch and Best 2004"""
    skyemis=N+(1-N)*(1.0-0.261*np.exp(-7.77*10**(-4)*(273.16-TaK)**2)) #Idso and Jackson 1096
    Esky = sigma*(TaK**4)*skyemis
    return Esky


# 4. Calculate the shortwave and longwave radiation of the wall
def calc_radiation_from_values(SurfTemp,Eswall):
    """ List of values for visibele surface parameters. returns long and shortwave radiative components. Assumes that lists are in order and of the same length"""
    sigma =5.67*10**(-8)
    emissivity=0.9
    Elwall = emissivity*sigma*SurfTemp**4
    Eswall = Eswall
    return Elwall, Eswall


def meanradtemp(Esky,Elwall, Elground,Eswall, solarparam, SVF, GVF,  pedestrian_albedo, pedestrian_emiss=0.97, shadow=0):
    """ calculates Stefan-Boltzmann equation for mean radiant temperature, from different sources of radiation in the urban environment """
    sigma =5.67*10**(-8)
    Eshort =  solarparam.diffuse_frm_sky[0]*SVF/2 + solarparam.diffuse_frm_ground[0]*GVF + solarparam.direct_sol[0]*solarparam.solarviewfactor[0]*(1 - shadow)+ Eswall*SVF
  #  Elong = Esky*SVF/2+Elwall+Elground
    Elong = Esky*SVF/2+Elwall*SVF+Elground*GVF

    t_mrt= ((Eshort*(1-pedestrian_albedo)+Elong)/sigma/pedestrian_emiss)**(1/4.) - 273.15  
    
    return t_mrt, Eshort, Elong


def cal_Tmrt(time_str,latitude,longitude,altitude,ground_albedo,wall_albedo,Ta,RH,TC,groundtemp,wall_temp,SVF,treecover):
    solarparam = calc_solarparam(time_str,latitude,longitude,altitude, groundalbedo=ground_albedo,human=True, TC=TC,time_str_end=None)
    ghi = solarparam.E_ghi[0]

    Esky = calc_Esky_emis(Ta,RH,TC=TC) 


    SurfTemp = wall_temp + 273.15 
    Eswall=SVF*wall_albedo*ghi
    Elwall, Eswall = calc_radiation_from_values(SurfTemp,Eswall)

    ground_emissivity = 0.95
    sigma = 5.67*10**(-8)
    groundtemp_K = groundtemp + 273.15
    gvf=0.5
    Elground = ground_emissivity*sigma*groundtemp_K**4 

    tmrt,Eshort, Elong = meanradtemp(Esky,Elwall, Elground,Eswall, solarparam, SVF, GVF=0.5,  pedestrian_albedo=0.3, pedestrian_emiss=0.95, shadow=treecover)

    results = pd.DataFrame({
        'direct_sol': [solarparam.direct_sol[0]],
        'diffuse_frm_sky': [solarparam.diffuse_frm_sky[0]],
        'diffuse_frm_ground': [solarparam.diffuse_frm_ground[0]],
        'Esky':[Esky],
        'Eswall': [Eswall],
        'Elwall': [Elwall],
        'Eground':[Elground],
        'Eshort': [Eshort],
        'Elong': [Elong],
        'Tmrt': [tmrt],
    })
    return results 
