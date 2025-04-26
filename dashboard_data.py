import requests
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
import json
from keys import *

epap_model = "epd7in3f"

## color coding functions
def pollen_color(pollen_level, debug=False):
    if debug:
        if pollen_level.lower()=="low":
            color="green"
        elif pollen_level.lower()=="medium":
            color="yellow"
        elif pollen_level.lower()=="heavy":
            color="red"
        elif pollen_level.lower()=="extremely heavy":
            color="red"
        else:
            color="white"
    else:
        import epaper
        epd = epaper.epaper(epap_model).EPD()
        if pollen_level.lower()=="low":
            color=epd.GREEN
        elif pollen_level.lower()=="medium":
            color=epd.YELLOW
        elif pollen_level.lower()=="heavy":
            color=epd.RED
        elif pollen_level.lower()=="extremely heavy":
            color=epd.RED
        else:
            color=epd.WHITE
    return color

def aq_color(aq_code, debug=False):
    if debug:
        if aq_code is None:
            color="white"
        elif aq_code==1:
            color="green"
        elif aq_code==2:
            color="yellow"
        elif aq_code==3:
            color="orange"
        elif aq_code>=4:
            color="red"
        else:
            color="white"
    else:
        import epaper
        epd = epaper.epaper(epap_model).EPD()
        if aq_code is None:
            color=epd.WHITE
        elif aq_code==1:
            color=epd.GREEN
        elif aq_code==2:
            color=epd.YELLOW
        elif aq_code==3:
            color=epd.ORANGE
        elif aq_code>=4:
            color=epd.RED
        else:
            color=epd.WHITE
    return color

def uvi_color(uvi, debug=False):
    if debug:
        if uvi is None:
            return "black"
        elif uvi<0:
            return "black"
        else:
            pass
        uvi = round(uvi)
        if uvi<=2:
            color="green"
        elif uvi<=5:
            color="yellow"
        elif uvi<=7:
            color="orange"
        elif uvi>=8:
            color="red"
        else:
            color="black"
    else:
        import epaper
        epd = epaper.epaper(epap_model).EPD()
        if uvi is None:
            return epd.BLACK
        elif uvi<0:
            return epd.BLACK
        else:
            pass
        uvi = round(uvi)
        if uvi<=2:
            color=epd.GREEN
        elif uvi<=5:
            color=epd.YELLOW
        elif uvi<=7:
            color=epd.ORANGE
        elif uvi>=8:
            color=epd.RED
        else:
            color=epd.BLACK
    return color


## Current weather icons based on weather id
curr_weather_icons = {
    "clear": "./icons/sun.bmp",
    "clear_night": "./icons/night.bmp",
    "partly cloudy": "./icons/partly_cloudy.bmp",
    "partly cloudy night": "./icons/partly_cloudy_night.bmp",
    "mostly cloudy": "./icons/mostly_cloudy.bmp",
    "light rain": "./icons/light_rain.bmp",
    "rain": "./icons/rain.bmp",
    "thunderstorm": "./icons/thunder.bmp",
    "snow": "./icons/snow.bmp",
    "atmospheric": "./icons/atm.bmp",
}

def get_condition_icon(id, is_daytime, daily=False):
    id = str(id)
    if id == "800":
        if is_daytime or daily:
            icon  = curr_weather_icons["clear"]
        else:
            icon  = curr_weather_icons["clear_night"]
    elif id.startswith("2"):
        icon  = curr_weather_icons["thunderstorm"]
    elif id.startswith("3"):
        icon  = curr_weather_icons["light rain"]
    elif id.startswith("5"):
        icon  = curr_weather_icons["rain"]
    elif id.startswith("6"):
        icon  = curr_weather_icons["snow"]
    elif id.startswith("7"):
        icon  = curr_weather_icons["atmospheric"]
    elif id in ["801", "802"]:
        if is_daytime or daily:
            icon  = curr_weather_icons["partly cloudy"]
        else:
            icon  = curr_weather_icons["partly cloudy night"]
    elif id in ["803", "804"]:
        icon  = curr_weather_icons["mostly cloudy"]
    return icon



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## AIR QUALITY FUNCTIONS
## Get data from the AirNow API

airnow_host = "http://www.airnowapi.org"
airnow_zipsite_current = "/aq/observation/zipCode/current"
airnow_zipsite_forecast = "/aq/forecast/zipCode/"


def get_aq_current(airnow_api_key, zipcode="77008"):
    """
    Get the AirNow API response for current air quality.
    Defaulting to Houston Heights
    """
    payload = {}
    payload["zipCode"] = zipcode
    payload["format"] = "JSON"
    payload["api_key"] = airnow_api_key
    with requests.get(airnow_host+airnow_zipsite_current, params=payload) as response:
        return response

def get_ozone_current(**kwargs):
    """
    Parse the AirNow current air quality API response
    for Ozone value and level
    """
    ozone_value, ozone_level, ozone_code = None, None, None
    
    response = get_aq_current(**kwargs)
    if response.status_code in [404, 504]:
        return ozone_value, ozone_level, ozone_code
    aq = json.loads(response.text)
    
    for i in range(len(aq)):
        if aq[i]["ParameterName"]=="O3":
            try:
                ozone_value = aq[i]["AQI"]
            except:
                pass
            try:
                ozone_level = aq[i]["Category"]["Name"]
            except:
                pass
            try:
                ozone_code = aq[i]["Category"]["Number"]
            except:
                pass
    return ozone_value, ozone_level, ozone_code

def get_particulate_current(**kwargs):
    """
    Parse the AirNow current air quality API response
    for Particulate 2.5 value and level
    """
    part_value, part_level, part_code = None, None, None
    
    response = get_aq_current(**kwargs)
    if response.status_code in [404, 504]:
        return part_value, part_level, part_code
    aq = json.loads(response.text)
    
    for i in range(len(aq)):
        if aq[i]["ParameterName"]=="PM2.5":
            try:
                part_value = aq[i]["AQI"]
            except:
                pass
            try:
                part_level = aq[i]["Category"]["Name"]
            except:
                pass
            try:
                part_code = aq[i]["Category"]["Number"]
            except:
                pass
    return part_value, part_level, part_code

def get_aq_tomorrow(airnow_api_key, zipcode="77008"):
    """
    Get the AirNow API response for tomorrow's air quality.
    Defaulting to Houston Heights.
    """
    current_time = datetime.now()
    today = current_time.date()
    tomorrow = today + timedelta(days=1)
    payload = {}
    payload["zipCode"] = zipcode
    payload["format"] = "JSON"
    payload["api_key"] = airnow_api_key
    with requests.get(airnow_host+airnow_zipsite_forecast, params=payload) as response:
        return response

def get_ozone_forecast(**kwargs):
    """
    Parse the AirNow forecasted air quality API response
    for Ozone value and level
    """
    ozone_level, ozone_code = None, None
    
    response = get_aq_tomorrow(**kwargs)
    if response.status_code in [404, 504]:
        return ozone_level, ozone_code
    aq = json.loads(response.text)

    current_time = datetime.now()
    today = current_time.date()
    tomorrow = today + timedelta(days=1)
    
    for i in range(len(aq)):
        if aq[i]["ParameterName"]=="O3" and aq[i]["DateForecast"]==str(tomorrow):
            try:
                ozone_level = aq[i]["Category"]["Name"]
            except:
                pass
            try:
                ozone_code = aq[i]["Category"]["Number"]
            except:
                pass
    return ozone_level, ozone_code

def get_particulate_forecast(**kwargs):
    """
    Parse the AirNow forecasted air quality API response
    for Particulate 2.5 value and level
    """
    part_level, part_code = None, None
    
    response = get_aq_tomorrow(**kwargs)
    if response.status_code in [404, 504]:
        return part_level, part_code
    aq = json.loads(response.text)

    current_time = datetime.now()
    today = current_time.date()
    tomorrow = today + timedelta(days=1)
    
    for i in range(len(aq)):
        if aq[i]["ParameterName"]=="PM2.5" and aq[i]["DateForecast"]==str(tomorrow):
            try:
                part_level = aq[i]["Category"]["Name"]
            except:
                pass
            try:
                part_code = aq[i]["Category"]["Number"]
            except:
                pass
    return part_level, part_code


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## POLLEN FUNCTIONS
## Get data from the Houston Health Department

def get_last_friday():
    """
    Return date of preceeding Friday. To be used
    if current date is a Saturday or Sunday when
    pollen data is not available
    """
    d = {0:3,1:4,2:5,3:6,4:0,5:1,6:2}
    last_friday = datetime.today()-timedelta(days=d[datetime.today().weekday()])
    return last_friday

def make_payload_addition(use_yesterday=False):
    """
    Create the end tag of the url based on the date.
    """
    if date.today().strftime('%A') in ["Saturday", "Sunday"]:
        use_date = get_last_friday()
    else:
        use_date = date.today()

    if use_yesterday:
        use_date = date.today() - timedelta(days=1)

    year = str(use_date.year)
    month = use_date.strftime('%B').lower()
    day_name = use_date.strftime('%A').lower()
    day_number = str(use_date.day)

    tmp_lst = [day_name, month, day_number, year]
    payload_addition = "-".join(p for p in tmp_lst)
    
    return payload_addition

def get_pollen_data():
    """
    Query the Houston Health Department for pollen/allergen
    data. Only available Monday-Friday, so return the recent Friday
    data if it is currently the weekend.

    Add some fixes because COH keeps fucking up the url
    """
    url_base = "https://www.houstonhealth.org/services/pollen-mold/"
    payload_base = "houston-pollen-mold-count-"
    payload_addition = make_payload_addition()
    payload = payload_base+payload_addition
    url = url_base + payload
    page = requests.get(url)

    if page.status_code == 404:
        payload_addition = make_payload_addition(use_yesterday=True)
        payload = payload_base+payload_addition
        url = url_base + payload
        page = requests.get(url)

        if page.status_code == 404:
            ## because they fat finger the second hyphen
            payload_addition = make_payload_addition()
            idx = payload_addition.rfind("-")
            payload_addition = payload_addition[:idx] + payload_addition[idx+1:]
            payload = payload_base+payload_addition
            url = url_base + payload
            page = requests.get(url)

            if page.status_code == 404:
                ## because they fat finger the second hyphen
                payload_addition = make_payload_addition(use_yesterday=True)
                idx = payload_addition.rfind("-")
                payload_addition = payload_addition[:idx] + payload_addition[idx+1:]
                payload = payload_base+payload_addition
                url = url_base + payload
                page = requests.get(url)
    
    soup = BeautifulSoup(page.content, "html.parser")
    tmp = soup.find_all("p", class_="text-align-center")
    page.close()
    
    pollen_data = {}
    for i in tmp:
        tmp_data = str(i)[37:].replace("</strong><br/><strong>", " ").split()
        pollen_type = ' '.join([tmp_data[0], tmp_data[1]])
        pollen_level = tmp_data[2]
        if tmp_data[3].lower() == "heavy": #needed for houston
            pollen_level = "extremely heavy"
        pollen_type = pollen_type.replace("<br/>", "")
        pollen_level = pollen_level.replace("<br/>", "")
        pollen_data[pollen_type] = pollen_level

    return pollen_data



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## WEATHER FUNCTIONS
## Get data from the OpenWeatherMap API


def get_weather(weather_api_key, latitude, longitude):
    """
    Get the current and forecasted weather and conditions
    """
    base = "https://api.openweathermap.org/data/3.0/onecall?"
    lat_str = "lat="+latitude
    long_str = "&lon="+longitude
    api_str = "&appid="+weather_api_key
    with requests.get(base+lat_str+long_str+api_str) as response:
        return response

def kelvin_to_farenheit(temp_K):
    """
    Convert temperature in Kelvin to
    degrees Farenheit
    """
    temp_f = (temp_K - 273.15) * 9/5 + 32
    temp_f = round(temp_f)
    return temp_f


def convert_utc(utc, offset=-18000):
    """
    Convert the UTC time stamp to a datetime
    object. Offset defaults to US Central.
    """
    stamp = utc + offset
    stamp = datetime.utcfromtimestamp(stamp)
    return stamp


def current_conditions(response):
    """
    Return the current 'feels like' temperature
    in degrees F, current humidity, current
    UVI, current condition id, and day[true] night[false]
    """
    conditions = {}
    conditions["temp_f"] = None
    conditions["humidity"] = None
    conditions["uvi"] = None
    conditions["id"] = None
    conditions["daytime"] = False
    try:
        resp = json.loads(response.text)
    except:
        return conditions
    temp_K = resp['current']['feels_like']
    temp_f = kelvin_to_farenheit(temp_K)

    humidity = resp['current']['humidity']

    uvi = resp['current']['uvi']

    id = resp["current"]["weather"][0]["id"]

    if resp["current"]["sunrise"] < resp["current"]["dt"] < resp["current"]["sunset"]:
        conditions["daytime"] = True

    conditions["temp_f"] = temp_f
    conditions["humidity"] = humidity
    conditions["uvi"] = uvi
    conditions["id"] = id
    
    return conditions


def hourly_forecast(response, hours=8):
    """
    Return the hourly forecasted 'feels like' temperature
    and weather id
    """

    hourly_forecast  = []
    try:
        resp = json.loads(response.text)
    except:
        for i in range(hours):
            tmp_dict = {}
            tmp_dict[str(i)]["temp_f"] = None
            tmp_dict[str(i)]["id"] = None
            hourly_forecast.append(tmp_dict)
        return hourly_forecast

    forecast = resp["hourly"][:hours]
    for f in forecast:
        time = f["dt"]
        hour = convert_utc(time).hour
        if hour > 12:
            hour = hour-12
        if hour == 0:
            hour = 12

        temp_K = f["feels_like"]
        temp_f = kelvin_to_farenheit(temp_K)

        id = f["weather"][0]["id"]

        tmp_dict = {}
        tmp_dict[str(hour)] = {}
        tmp_dict[str(hour)]["temp_f"] = temp_f
        tmp_dict[str(hour)]["id"] = id
        hourly_forecast.append(tmp_dict)

    return hourly_forecast

def daily_forecast(response, days=5):
    """
    Return the daily forecasted min/max temperatures
    and weather id
    """

    daily_forecast  = []
    try:
        resp = json.loads(response.text)
    except:
        for i in range(days):
            tmp_dict = {}
            tmp_dict[str(i)]["max_temp"] = None
            tmp_dict[str(i)]["min_temp"] = None
            tmp_dict[str(i)]["id"] = None
            daily_forecast.append(tmp_dict)
        return daily_forecast

    forecast = resp["daily"][:days]
    for f in forecast:
        day = f["dt"]
        day  = convert_utc(day).weekday()
        day_list = ["MON", "TUE","WED", "THU", "FRI", "SAT", "SUN"]
        day = day_list[day]

        max_temp = f["temp"]["max"]
        max_temp = kelvin_to_farenheit(max_temp)

        min_temp = f["temp"]["min"]
        min_temp = kelvin_to_farenheit(min_temp)

        id = f["weather"][0]["id"]

        tmp_dict = {}
        tmp_dict[str(day)] = {}
        tmp_dict[str(day)]["max_temp"] = max_temp
        tmp_dict[str(day)]["min_temp"] = min_temp
        tmp_dict[str(day)]["id"] = id
        daily_forecast.append(tmp_dict)

    return daily_forecast

def make_weather_data(**kwargs):
    """
    Create dictionary of current and forecasted weather conditions
    """
    weather_data = {}
    
    response = get_weather(**kwargs)

    current_weather = current_conditions(response)
    hourly_weather = hourly_forecast(response, hours=8)
    daily_weather = daily_forecast(response, days=5)

    weather_data["current"] = current_weather
    weather_data["hourly"] = hourly_weather
    weather_data["daily"] = daily_weather

    return weather_data
