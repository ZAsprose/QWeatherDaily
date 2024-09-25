# QWeatherDaily
[![English](https://img.shields.io/badge/lang-en-blue.svg)](#english)
[![中文](https://img.shields.io/badge/lang-cn-red.svg)](#中文)
[![Output](https://img.shields.io/badge/lang-en-blue.svg)](#DemoOutput)

Qinglong daily weather brief script for multiple cities using QWeather web api 
基于青龙面板的接入和风天气api的每日天气简报脚本

## 中文
需要的环境变量：
qweather_key：和风天气的web api key。需要在和风天气注册账号，并在控制台中新建项目并建立web api key。将key值保存在环境变量中。
city_list_str：一组由经纬度或城市（地区）信息构成的字符串，每个地点之间用英文引号分隔。
  经纬度：用英文逗号分隔的经度,纬度坐标
  信息：为了查找精确，本项目采取三段字符串，每个信息用英文逗号分隔。分别是“关键词,省份/上级行政区划,搜索范围（ISO 3166 所定义的国家代码）”
  详细说明在[和风天气GeoAPI文档](https://dev.qweather.com/docs/api/geoapi/city-lookup/)
  范例："茶陵,湖南,cn;melbourne,victoria,au;144.96,-37.82"

脚本内变量：
lang: 从api获取的信息语言，目前代码内设定为中文。相应[开发文档](https://dev.qweather.com/docs/resource/language/)
alarm_dic: 需要在信息开头进行提示的天气的关键字数组
hours_needed：需要获取天气的小时数。例如如果在6点开始定时项目，只关注今天的天气，则可设为18。脚本内设为24

脚本的通知是引用了青龙自带的notify方式发送。

## english
qinglong enviroment param needed:
qweather_key: web api key from qweather.com

## DemoOutput
【坏天气】茶陵 墨尔本 

【茶陵】小雨 
【墨尔本】小雨 


【茶陵】
温度: 22.0 - 24.0度
16:00 - 21:00: 多云
21:00 - 01:00: 小雨
16:00 - 21:00: 多云
21:00 - 01:00: 小雨
详细: https://www.qweather.com/weather/chaling-101250305.html

【墨尔本】
温度: 7.0 - 11.0度
18:00 - 20:00: 多云
20:00 - 23:00: 小雨
23:00 - 00:00: 多云
00:00 - 02:00: 小雨
02:00 - 03:00: 多云
18:00 - 20:00: 多云
20:00 - 23:00: 小雨
23:00 - 00:00: 多云
00:00 - 02:00: 小雨
02:00 - 03:00: 多云
详细: https://www.qweather.com/weather/melbourne-754D9.html
