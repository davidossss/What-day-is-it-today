from bs4 import BeautifulSoup
from datetime import datetime
from json import load
from notifypy import Notify
from os import path
from platform import system
from random import shuffle
from requests import get
from sys import exit
from time import strftime
from windows_toasts import ToastDisplayImage, Toast, WindowsToaster 

operatingSystem = system()

timeStartup = int(strftime("%H"))

with open(path.abspath("resources/config.json"), encoding="utf-8") as file:
    config = load(file)

with open(path.abspath(f"resources/languages/{config["language"]}.json"), encoding="utf-8") as file:
    language = load(file)

def GetGreetings(time, language):
    if time >= 23:
        return language["good.night"]
    if time >= 18:
        return language["good.evening"]
    if time >= 12:
        return language["good.afternoon"]
    
    return language["good.morning"]

class Notification():
    def __init__(self, message, holiday):   
        holidayURL = holiday.replace(" ", "+")     
        pathIcon = path.abspath("resources/icon.png")

        match operatingSystem:
            case "Windows":
                self.notification = WindowsToaster(language["nameProgram"])

                self.notificationSettings = Toast()
                self.notificationSettings.text_fields = [language["nameProgram"], message + " «" + holiday + "»"]
                self.notificationSettings.AddImage(ToastDisplayImage.fromPath(pathIcon))
                self.notificationSettings.launch_action = f"https://www.google.com/search?q={holidayURL}"
            case _:
                self.notification = Notify()

                self.notification.title = language["nameProgram"]
                self.notification.message = message + " «" + holiday + "»" + "\n" + f"https://www.google.com/search?q={holidayURL}"
                self.notification.icon = pathIcon
        
        self.CallNotification()

    def CallNotification(self):
        match operatingSystem:
            case "Windows":
                self.notification.show_toast(self.notificationSettings)
            case _:
                self.notification.send(block=False)

class Holidays():
    def __init__(self):
        self.parsingHolidays = []
        self.customHolidays = []
        self.holidays = []

        self.GetParsingHolidays()
        self.GetCustomHolidays()
        self.GetHolidays()

    def GetParsingHolidays(self):
        url = 'https://какойсегодняпраздник.рф/'
        userAgent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 YaBrowser/21.6.0.616 Yowser/2.5 Safari/537.36',}
        response = get(url, headers = userAgent)
        beautifulSoup = BeautifulSoup(response.content, 'html.parser')
        
        items = beautifulSoup.find_all("div", itemprop="suggestedAnswer")
        for item in items:
            self.parsingHolidays.append(item.find("span", itemprop="text").get_text(strip=True))

        shuffle(self.parsingHolidays)

    def GetCustomHolidays(self):
        date = datetime.now()

        with open("resources/customholidays.txt", "r", encoding="utf-8") as customholidays:
            for line in customholidays.readlines():
                if line[0] not in ["#", "\n"]:
                    dataCustomHoliday = line.split(", ")
                    dataCustomHoliday[1] = dataCustomHoliday[1].replace("\n", "")
                    dateTimeCustomHoliday = (int(dataCustomHoliday[0].split(".")[0]), int(dataCustomHoliday[0].split(".")[1]))
                    
                    if dateTimeCustomHoliday == (date.day, date.month):
                        self.customHolidays.append(dataCustomHoliday[1])
        
        shuffle(self.customHolidays)

    def GetHolidays(self):
        try:
            self.holidays = []
            it = 0

            if len(self.customHolidays) != 0:
                while len(self.holidays) <= config["countHolidays"] and it < len(self.customHolidays):
                    self.holidays.append(self.customHolidays[it])
                    it += 1

            it = 0

            while len(self.holidays) <= config["countHolidays"] and it < len(self.parsingHolidays):
                self.holidays.append(self.parsingHolidays[it])
                it += 1
        except Exception:
            pass

if __name__ == '__main__':
    boolAgain = False

    print(f'{language["nameProgram"]} v{config["version"]}')

    while True:
        holidaysObject = Holidays()

        firstLine = GetGreetings(timeStartup, language) + " " + language["nameOfTheHoliday.first"] if boolAgain == False else language["nameOfTheHoliday.first"]

        notificationObjectFirst = Notification(firstLine, holidaysObject.holidays[0])
        notificationObjectSecond = Notification(language["nameOfTheHoliday.second"], holidaysObject.holidays[1])
        notificationObjectThird = Notification(language["nameOfTheHoliday.third"], holidaysObject.holidays[2])

        answer = str(input(language["tryAgain.first"] + "\n" + language["tryAgain.second"] + "\n>>> ")).lower()

        boolAgain = answer in [language["confirm"].lower(), language["confirm"][0].lower()]

        if boolAgain == False:
            exit()
