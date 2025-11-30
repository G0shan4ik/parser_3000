from pprint import pprint

from botasaurus.browser_decorator import browser
from botasaurus_driver import Driver
from botasaurus_driver.user_agent import UserAgent

from bs4 import BeautifulSoup
import lxml

import re


all_links = ['https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_412_m_99_et._7327317712?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_96_m_617_et._4556659548?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_106_m_815_et._3495204480?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_797_m_217_et._7460847779?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_40_m_614_et._7524728402?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_125_m_1617_et._7494371490?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_427_m_1010_et._7460630195?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_2535_m_17_et._4646719202?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_62_m_27_et._7364297447?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_912_m_1010_et._7270582458?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_327_m_13_et._7483688107?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_70_m_1414_et._3939994353?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_31_m_1314_et._7259019921?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_82_m_217_et._7547119286?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_92_m_89_et._3884015000?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_793_m_1417_et._3388186136?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_69_m_614_et._7524941997?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_819_m_910_et._7563221895?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_34_m_99_et._7546295365?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_55_m_1617_et._7524640363?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_36_m_914_et._7516971034?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_42_m_29_et._7275949619?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_428_m_214_et._7526629109?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_47_m_59_et._7444292875?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_39_m_13_et._7534949329?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_57_m_59_et._4635478406?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_563_m_1520_et._7558380120?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_62_m_710_et._4244560337?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_42_m_1017_et._7393407238?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_768_m_69_et._7492405076?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_62_m_79_et._7556367165?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_91_m_1919_et._7494578448?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_39_m_210_et._7556068540?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_385_m_814_et._4287468746?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_36_m_611_et._7460944337?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_723_m_1314_et._4704210526?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_46_m_13_et._7529352907?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_49_m_310_et._7356716707?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_60_m_110_et._4779687905?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_90_m_317_et._4216259904?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_401_m_1414_et._1884162806?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_81_m_1717_et._7556037234?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_39_m_14_et._7421836258?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_947_m_920_et._7347098490?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_61_m_610_et._7537383682?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_58_m_618_et._7346255415?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_504_m_717_et._7402441451?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_58_m_1118_et._7346204703?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_537_m_99_et._7246882778?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_52_m_1621_et._7540730023?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiI5ak5SSTNzQzdzTzFHSnhZIjt9iXvpNz8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/dolya_v_3-k._kvartire_966_m_1417_et._7384062435?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_65_m_310_et._7268282346?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_397_m_1314_et._7481850709?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_794_m_517_et._7583604224?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_756_m_819_et._7434896761?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_107_m_520_et._3639612158?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_826_m_1117_et._4424489194?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/10_i_bolee-k._kvartira_300_m_1011_et._2156081177?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_545_m_99_et._7491137803?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_427_m_1010_et._7285353132?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_64_m_1420_et._7473375027?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_77_m_914_et._7479453722?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_796_m_510_et._4539603838?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_786_m_210_et._7320692214?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_69_m_410_et._3994741131?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_65_m_710_et._7502227850?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_773_m_1420_et._7528363070?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_414_m_59_et._7410931444?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_913_m_721_et._7607732088?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_335_m_99_et._4465611083?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_41_m_510_et._7358307439?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_276_m_13_et._4365337321?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_58_m_810_et._7542437226?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_276_m_23_et._4707707059?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_793_m_117_et._7541540150?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_356_m_1212_et._4362227187?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_40_m_1417_et._7553342398?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_1653_m_710_et._7410864387?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_61_m_110_et._7500812775?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_52_m_217_et._5121406164?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_1141_m_1017_et._7629374379?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_278_m_55_et._7573957319?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_982_m_1717_et._7419286536?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_51_m_1717_et._4181418533?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_58_m_39_et._7207129389?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_44_m_219_et._2830756502?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_54_m_410_et._4158952556?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_373_m_1217_et._7538773879?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_579_m_1017_et._7470443704?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_385_m_1010_et._7346573214?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_40_m_817_et._7386029605?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_70_m_910_et._3646981981?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_57_m_23_et._3949320896?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_43_m_1112_et._4155570481?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_107_m_1220_et._7482062299?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_367_m_44_et._7474670421?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_423_m_99_et._1485613169?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_2158_m_23_et._7253612288?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_132_m_311_et._7474705725?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_57_m_55_et._7262811472?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCdmF6ZWdERjZmNUxsM0QzIjt97uW1yT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_541_m_610_et._7500937106?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_388_m_710_et._7284719597?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_422_m_1317_et._7302573218?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_69_m_310_et._2258397530?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_426_m_1314_et._7280669343?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_45_m_59_et._4299659654?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_265_m_13_et._7330796793?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_426_m_1314_et._7322696582?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_100_m_214_et._4254197257?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_70_m_29_et._7410432996?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_65_m_110_et._7386379360?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_1928_m_119_et._3524487406?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_101_m_116_et._7359883884?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_469_m_57_et._7328887320?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_98_m_717_et._7334263809?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_725_m_1919_et._4476399640?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_749_m_1121_et._7536135591?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_58_m_720_et._3034726457?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_1011_m_310_et._7500119165?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_917_m_79_et._7337758711?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_40_m_1417_et._7258383625?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_40_m_612_et._3872699295?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/svob._planirovka_91_m_1919_et._7480344355?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_462_m_19_et._7419170398?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_47_m_13_et._7526111310?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_117_m_1317_et._7462368569?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_395_m_314_et._4490926387?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_98_m_417_et._4171137624?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_401_m_1114_et._4700119514?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_62_m_39_et._7339842717?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_345_m_33_et._4654347424?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_392_m_916_et._7562647581?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_756_m_821_et._7444768825?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_68_m_110_et._7534084280?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_932_m_710_et._4601343335?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_479_m_1214_et._7262751140?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_95_m_514_et._7547786699?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_110_m_1517_et._4348069031?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_795_m_217_et._7354573400?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_130_m_1011_et._7517251221?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_349_m_29_et._4581095764?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_606_m_110_et._4425985858?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_53_m_610_et._7450623711?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_992_m_914_et._4603528615?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_391_m_1017_et._7423653171?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_266_m_35_et._3829547428?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_35_m_1717_et._7482593480?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_221_m_67_et._7305581124?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_73_m_24_et._7393154136?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_371_m_710_et._7474919947?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJnY0NmWGxyRG5rQll2cGh4Ijt9cKgSAT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_811_m_1417_et._7534422758?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_90_m_25_et._7548878804?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_50_m_1114_et._7543055438?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_573_m_35_et._7245899043?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_462_m_317_et._4348861567?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_80_m_510_et._4407170817?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_622_m_910_et._7413491942?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_912_m_514_et._7431275812?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_267_m_23_et._7483161488?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_84_m_1019_et._4367444114?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_744_m_59_et._3846976491?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/svob._planirovka_723_m_1118_et._7436124239?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_1258_m_1919_et._4752085205?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_738_m_410_et._4044549597?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_984_m_311_et._7500347507?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_936_m_810_et._7517997889?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_799_m_910_et._7227728074?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_914_m_1619_et._7451997246?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_39_m_13_et._4256456239?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_797_m_1010_et._7535734699?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_602_m_512_et._7229676369?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/dolya_v_2-k._kvartire_663_m_510_et._7442044478?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_755_m_210_et._7405733005?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_69_m_614_et._7442832339?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_123_m_68_et._7436700013?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_753_m_1617_et._7445192096?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_51_m_59_et._7419525251?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_888_m_1414_et._4142193682?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_267_m_23_et._3759027766?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_48_m_49_et._7448180726?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_463_m_610_et._7539299335?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_1078_m_215_et._4148890547?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_625_m_1414_et._4794357000?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_606_m_79_et._7494304254?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_752_m_412_et._7522104386?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_97_m_1417_et._7404944535?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_796_m_45_et._4463165097?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_81_m_1417_et._7561744962?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_50_m_1919_et._7323929784?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_392_m_417_et._7430682669?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_415_m_99_et._4929974802?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_68_m_514_et._4590885420?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_81_m_517_et._4470063524?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_52_m_811_et._7404091403?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_121_m_99_et._4204875765?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_62_m_39_et._7551540697?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_383_m_59_et._7547290503?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_594_m_610_et._7540512733?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_39_m_1316_et._7521905512?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_786_m_210_et._7298286511?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJCWUlTaUlUWE9QWlZMWWFlIjt9wPXpfT8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_744_m_59_et._4266248846?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_93_m_514_et._4045852503?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_625_m_1617_et._7429831210?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_604_m_1717_et._7387237884?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_392_m_517_et._7483302298?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_79_m_1317_et._7482450379?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_1122_m_810_et._4723092417?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_718_m_510_et._7541796131?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_120_m_2020_et._7406355662?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_276_m_13_et._4578535882?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_353_m_210_et._7450673944?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_125_m_1419_et._7558544636?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_75_m_412_et._7444433081?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_98_m_417_et._7436173773?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_64_m_521_et._7317139162?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_753_m_1010_et._7374229230?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/kvartira-studiya_265_m_15_et._7330923420?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_674_m_110_et._7524549636?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_351_m_417_et._4359469862?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_56_m_24_et._7556726572?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_92_m_33_et._4276764442?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_721_m_710_et._7558389182?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_42_m_918_et._7340300803?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_531_m_59_et._7506099232?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_77_m_914_et._7444216656?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_514_m_13_et._7526224293?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_39_m_710_et._7276823459?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_263_m_55_et._4519059556?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_415_m_1017_et._7460319090?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_41_m_611_et._7494058096?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_594_m_69_et._7558142274?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_691_m_218_et._4550671942?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_595_m_29_et._7462900467?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_609_m_1010_et._7381197220?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_352_m_33_et._7526607529?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_92_m_33_et._7428801445?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_417_m_1717_et._7348097004?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_64_m_89_et._7500185211?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_576_m_210_et._7526790554?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_60_m_1414_et._4469310445?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_385_m_1010_et._7556379188?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_437_m_1112_et._7398552541?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_108_m_210_et._4582728649?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_68_m_79_et._4527259899?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_95_m_1820_et._7524289927?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_432_m_1117_et._7398900942?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_34_m_99_et._7500894678?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_392_m_1217_et._7300655069?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_60_m_79_et._7494270359?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_786_m_210_et._7308529025?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJqa3pQNm1nOWZOZHRWckxGIjt9k4fF3D8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_797_m_1010_et._7500216775?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_68_m_55_et._7334369310?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_60_m_1017_et._7460937475?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/4-k._kvartira_123_m_68_et._7500303848?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_572_m_110_et._4583347890?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_83_m_910_et._7500941078?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_69_m_614_et._7462342779?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_786_m_210_et._7398325123?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_51_m_49_et._2415751258?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_601_m_19_et._4077062428?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_795_m_217_et._7526525263?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_795_m_217_et._7540505475?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_78_m_210_et._7508472581?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_35_m_617_et._7494780829?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/1-k._kvartira_38_m_1114_et._7221096534?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/3-k._kvartira_98_m_416_et._7500810211?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_49_m_55_et._7218437133?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/2-k._kvartira_704_m_214_et._7398474350?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA',
             'https://www.avito.ru/ivanovo/kvartiry/6-k._kvartira_270_m_1516_et._7526341021?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJJeXBWdG84WnpTaGdaVHBDIjt9lxQexj8AAAA']


def extract_int_from_string(s: str) -> int:
    # Ищем все цифры в строке
    digits = re.findall(r"\d+", s)
    # Склеиваем и преобразуем в число
    return int("".join(digits)) if digits else 0


@browser(
    user_agent=UserAgent.user_agent_98,
    add_arguments=['--disable-dev-shm-usage', '--no-sandbox'],
    profile='Avito'
)
def ddd(driver: Driver, url: str):
    try:
        driver.get(url)
        driver.sleep(2)
        driver.scroll()
        driver.scroll()
        driver.scroll()
        driver.scroll()
        driver.sleep(2)
        soup = BeautifulSoup(driver.page_html, 'lxml')
        # for item in soup.select_one('div.items-items-zOkHg').select('div[data-marker="item"]'):
        #     all_links.append(f"https://www.avito.ru{item.select_one('a').get('href')}")
        # print(len(all_links))

        year_house, house_made, rooms, area, floor, price, price_m = '-', '-', '-', '-', '-', '-', '-'

        first_data = soup.select_one('ul.HRzg1')
        second_data = soup.select('ul.HRzg1')[-1]

        for _item in first_data.select('li'):
            if 'Количество комнат:' in _item.text:
                _r = _item.text.replace('Количество комнат: ', '')
                rooms = f'{_r}К' if _r != 'студия' else 'СТ'
            if 'Общая площадь:' in _item.text:
                area = float(_item.text.replace('Общая площадь: ', '').replace('м²', ''))
            if 'Этаж:' in _item.text:
                floor = int(_item.text.replace('Этаж: ', '').split(' из ')[0])
        try:
            price = extract_int_from_string(soup.select_one('span[itemprop="price"]').text)
        except:
            ...

        for _item in second_data.select('li'):
            if 'Тип дома:' in _item.text:
                house_made = _item.text.replace('Тип дома: ', '')
            if 'Год постройки:' in _item.text:
                year_house = int(_item.text.replace('Год постройки: ', ''))

        if price != '-' and area != '-':
            price_m = round(float(price/area), 2)

        print({
            'Год постройки дома': year_house,
            'Материал дома': house_made,
            'Количество комнат в квартире': rooms,
            'Площадь квартиры': area,
            'Этаж': floor,
            'Цена квартиры': price,
            'Цена 1 м²': price_m,
            'link': url
        })

        return {
            'Год постройки дома': year_house,
            'Материал дома': house_made,
            'Количество комнат в квартире': rooms,
            'Площадь квартиры': area,
            'Этаж': floor,
            'Цена квартиры': price,
            'Цена 1 м²': price_m,
            'link': url
        }
    except:
        ...

# for num in range(1, 7):
#     ddd(f'https://www.avito.ru/ivanovo/kvartiry/prodam/vtorichka-ASgBAgICAkSSA8YQ5geMUg?context=H4sIAAAAAAAA_wEmANn_YToxOntzOjE6InkiO3M6MTY6IlpQUnhGQ1F2aHNwNHdOMVEiO30KOAPQJgAAAA&f=ASgBAgECAkSSA8YQ5geMUgFFxr4NF3siZnJvbSI6MjAxMCwidG8iOjIwMTh9&p={num}&presentationType=serp')

full_dict = []

for item in all_links:
    print(f'link №{all_links.index(item)+1} out of {len(all_links)}')
    full_dict.append(ddd(item))


def to_exel(mass: list[dict], prefix: str = '_Avito') -> str:
    import pandas as pd
    from datetime import datetime
    df = pd.DataFrame(mass)

    df.to_excel(f"all_exel/{datetime.now().date()}{prefix}.xlsx")
    return f'all_exel/{datetime.now().date()}{prefix}.xlsx'

print(full_dict)
to_exel(full_dict)


