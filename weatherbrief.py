import requests, json ,re, os
from datetime import datetime
import notify

# qinglong env var qweatherkey to fetech api key
qweatherkey = os.getenv("qweather_key")

# qinglong env var city_list_str to fetch city name by city,state,countrycode or longtitude,latitude
city_list_str = os.getenv("city_list_str")
# test string for city_list_str
# city_list_str = "茶陵,湖南,cn;melbourne,victoria,au;144.96,-37.82"

# language setting for notify text
lang = "zh"

# alarm dictionary, an arr contains keywords that you want to alarm, align with lang
alarm_dic = ["雨", "雪", "雹", "雷", "暴", "霾"]

# time start to fetch weather report
# say if your task starts at 8 am, the api would fetch the following 24h data from 9 am to 7pm tomorrow, so only 9am to 24:00, overall 15 data is needed for today's notification
# this can be set to 24, if 24h data is need
# also, if you don't need that much, you can set it to the amount of data you need
hours_needed = 24

# define City to store all information for each city
class City:
    # Define the attributes (data members) of the class
    def __init__(self, name, locationid, weathers, disasteralarm, rainsnowalarm, fxLink):
        self.name = name
        self.locationid = locationid
        self.weathers = weathers
        self.disasteralarm = disasteralarm
        self.rainsnowalarm = rainsnowalarm
        self.fxLink = fxLink

    # Define a method (function) that prints the person's details
    def print_details(self):
        print(f"Name: {self.name}")
        print(f"locationid: {self.locationid}")
        print(f"rainsnowalarm: {self.rainsnowalarm}")
        print(f"fxLink: {self.fxLink}")
        if self.weathers != None:
            for var in self.weathers:
                var.print_details()
        if self.disasteralarm != None:
            for var in self.disasteralarm:
                var.print_details()

# define Disaster to store disaster alarm info
class Disaster:
    # Define the attributes (data members) of the class
    def __init__(self, title, severity, text):
        self.title = title
        self.severity = severity
        self.text = text

    # Define a method (function) that prints the person's details
    def print_details(self):
        print(f"title: {self.title}")
        print(f"severity: {self.severity}")
        print(f"text: {self.text}")

# define Weather to store hourly weather info
class Weather:
    # Define the attributes (data members) of the class
    def __init__(self, text, temp, txTime):
        self.text = text
        self.temp = temp
        self.txTime = txTime

    # Define a method (function) that prints the person's details
    def print_details(self):
        print(f"text: {self.text}")
        print(f"temp: {self.temp}")
        print(f"txTime: {self.txTime}")

# add param to url to fetch in certain language with a valid deve key
def build_url(url):
    return url + f"&key={qweatherkey}&lang={lang}"

# check if a string is a valid coordinate value defined by qweather
def if_coordinate(input):
    if len(re.split(",", input)) == 2 and input.count(".") < 3:
        try:
            float(input.replace('.', '', 1).replace('+', '').replace('-', '').replace(',', ''))
            return True
        except ValueError:
            return False
    else:
        return False

# build city info strcut based on input str attr or coordinate
def create_city_info_struct_from_str(input):
    cityinfo_attr = re.split(",", input)
    len_cityinfo_attr = len(cityinfo_attr)
    if len_cityinfo_attr == 0:
        return None
    elif len_cityinfo_attr > 3 or len_cityinfo_attr == 1:
        print("invalid grammar for: " + input)
        return None
    else:
        if if_coordinate(cityinfo):
            url = f"https://geoapi.qweather.com/v2/city/lookup?location={input}&key={qweatherkey}&lang={lang}"
        else:
            url = f"https://geoapi.qweather.com/v2/city/lookup?location={cityinfo_attr[0]}&adm={cityinfo_attr[1]}&range={cityinfo_attr[2]}"
        r = requests.get(build_url(url))

        if r.status_code == 200:
            city = json.loads(r.text)['location']
            if len(city) != 1:
                print("there is ambiguity when fetching the city, can't get exact weather")
                return None
            else:
                # print(city[0])
                disasters = get_disaster_alarm_by_locationid(city[0]['id'])
                weathers = get_24_weather_report_by_locationid(city[0]['id'])
                rainsnowalarm = check_if_alarm_rainsnow(weathers)
                return City(city[0]['name'], city[0]['id'], weathers, disasters, rainsnowalarm, city[0]['fxLink'])

        else:
            print("invalid city_list_str leads to error when fetch city info: " + r.text)
            return None

# build disaster alarm info arr for a city
# use arr in case there are multiple for a city
def get_disaster_alarm_by_locationid(locationid):
    r = requests.get(build_url(f"https://devapi.qweather.com/v7/warning/now?location={locationid}"))
    if r.status_code == 200:
        disasters = []
        try:
            warnings = json.loads(r.text)['warning']
            for warning in warnings:
                print(warning)
                disasters.append(Disaster(warning[0]['title'], warning[0]['severity'], warning[0]['text']))
        except:
            print("error when fetch disasters: " + r.text)
        finally:
            if len(disasters) > 0:
                return disasters
            else:
                return None
    else:
        return None

# fetch 24h weather report for a city
def get_24_weather_report_by_locationid(locationid):
    r = requests.get(build_url(f"https://devapi.qweather.com/v7/weather/24h?location={locationid}"))
    if r.status_code == 200:
        # print(r.text)
        weathers = []
        hourlys = json.loads(r.text)['hourly']
        for i, hourly in enumerate(hourlys):
            if i == hours_needed:
                break
            # print(f"{i}: {hourly}")
            weathers.append(Weather(hourly['text'], hourly['temp'], hourly['fxTime']))
        return weathers
    else:
        return None

# check if a city needs alarm for keywords in alarm_dic
def check_if_alarm_rainsnow(weathers):
    alarm_text = ""
    dic = {}
    for weather in weathers:
        for alarm in alarm_dic:
            if alarm in weather.text:
                dic[weather.text] = weather.text
    print(dic)
    for alarm in dic:
        alarm_text += (alarm + " ")
    if alarm_text == None or alarm_text.strip() == "":
        return None
    else:
        return alarm_text

# build message header including disaster alarm and rain or snow alarm
def build_message_header_for_disaster_rainsnow(city_struct_arr):
    overall_disaster_alarm_str = "【灾害预警】"
    overall_rainsnow_alarm_str = "【坏天气】"
    if_alarm_rain_snow = False
    if_alarm_disaster = False
    disaster_alarms =[]
    rainsnow_alarms =[]
    disaster_strs =[]
    rainsnow_strs = []
    for city in city_struct_arr:
        if city.disasteralarm != None:
            if_alarm_disaster = True
            overall_disaster_alarm_str += (f'{city.name} ')
            for disasteralarm in city.disasteralarm:
                disaster_alarms.append(f'{disasteralarm.title}\n{disasteralarm.severity}\n{disasteralarm.text}')
            disaster_str = f'【{city.name}】{connect_strs(disaster_alarms, "\n")}'
            disaster_strs.append(disaster_str)

        if city.rainsnowalarm != None:
            if_alarm_rain_snow = True
            overall_rainsnow_alarm_str += (city.name + " ")
            rainsnow_str = f'【{city.name}】{city.rainsnowalarm}'
            rainsnow_strs.append(rainsnow_str)

    print(f'if_alarm_rain_snow: {if_alarm_rain_snow}')
    print(f'if_alarm_disaster: {if_alarm_disaster}')

    header = ""
    if if_alarm_rain_snow and if_alarm_disaster:
        header = f'{overall_disaster_alarm_str}\n{overall_rainsnow_alarm_str}\n\n{connect_strs(disaster_alarms, "\n")}\n\n{connect_strs(rainsnow_strs, "\n")}'
    elif if_alarm_rain_snow:
        header = f'{overall_rainsnow_alarm_str}\n\n{connect_strs(rainsnow_strs, "\n")}'
    elif if_alarm_disaster:
        header =f'{overall_disaster_alarm_str}\n\n{connect_strs(disaster_alarms, "\n")}'

    if header.strip() != "":
        return header
    else:
        return None

# build brief of weather for a city including temperature range, weather, and link to details
def build_24h_weather_brief(city_attr):
    weather_cur = city_attr.weathers[0].text
    starttime = city_attr.weathers[0].txTime
    weather_str_attr = []
    temperature = []
    for i, weather in enumerate(city_attr.weathers):
        temperature.append(weather.temp)
        if weather.text != weather_cur:
            endtime = weather.txTime
            weather_str_attr.append([weather_cur, starttime, endtime])
            starttime = weather.txTime
            weather_cur = weather.text
    weather_str_attr.append([weather_cur, starttime, city_attr.weathers[len(city_attr.weathers) - 1].txTime])
    weather_str = build_24h_weather_str(weather_str_attr)

    float_temperature = list(map(float, temperature))
    max_temp = max(float_temperature)
    min_temp = min(float_temperature)
    context = f'温度: {min_temp} - {max_temp}度\n{weather_str}'

    return f'【{city_attr.name}】\n{context}\n{weather_str}\n详细: {city_attr.fxLink}'

# build string of weather in 24h in format of "starttime-endtime: weather"
def build_24h_weather_str(weather_str_attr):
    # print(weather_str_attr)
    str_attr = []
    for str in weather_str_attr:
        str_attr.append(f'{parse_time(str[1])} - {parse_time(str[2])}: {str[0]}')
    return connect_strs(str_attr, "\n")

# parse time from %Y-%m-%dT%H:%M%z to
def parse_time(time):
    dt = datetime.strptime(time, "%Y-%m-%dT%H:%M%z")
    formatted_time = dt.strftime("%H:%M")
    return formatted_time

# connect a list of string to one string using specific connector
def connect_strs(strs, connector):
    return connector.join(strs)

# main
city_list = re.split(";", city_list_str)
city_struct_arr = []

for cityinfo in city_list:
    city_strut = create_city_info_struct_from_str(cityinfo)
    if city_strut != None:
        city_struct_arr.append(city_strut)

print("=============== end of data fetch for qweather ==============")

header = build_message_header_for_disaster_rainsnow(city_struct_arr)

weather_briefs = []
for city in city_struct_arr:
    city.print_details()
    print("\n")
    weather_brief = build_24h_weather_brief(city)
    if weather_briefs != None:
        weather_briefs.append(weather_brief)

if len(weather_briefs) > 0:
    context = connect_strs(weather_briefs, "\n\n")
    if header != None:
        context  = header + "\n\n\n" + context

    print("=============== result ==============")
    print(context)
    notify.send("今日天气简报", context)
