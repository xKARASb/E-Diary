from aiohttp import ClientSession
import requests
from time import sleep

from .types import Lesson, Worker, LessonTime, Score
import datetime as dt
import threading as th

import logging

learners = {}

class Learner:
    def __init__(self, jsessionid: str):
        self.cookies = {
            "JSESSIONID": jsessionid
            }
        self.last_request = None
        self.server_allowed = False

    async def start_polling(self):
        self.session = ClientSession(cookies=self.cookies)
        
        self.ping_running = True
        task = th.Thread(target=self.ping)
        task.start()
        await self.__get_periods_dates()
        logging.info(self.periods)
    
    def ping(self):
        logging.info("Start pinging")
        while self.ping_running:
            resp = requests.get("https://school.edu-penza.ru/users/getprofile/", cookies=self.cookies, allow_redirects=False)
            
            if resp.status_code != 200:
                self.server_allowed = False
                return {"error": "Sessionid expired"}
            sleep(300)

    async def stop_polling(self):
        self.ping_running = False
        await self.session.close()
                
    async def update_cookie(self, jsessionid: str):
        self.cookies["JSESSIONID"] = jsessionid
        await self.session.close()
        self.session = ClientSession(cookies=self.cookies)
    
    async def get_week(self, person_id: int, date_start=dt.date.today(), date_end=dt.date.today()) -> dict[str, list[Lesson]]:
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }
        
        req = await (await self.session.get("https://school.edu-penza.ru/android/scores/week", params=params)).json()

        if req["message"] != "OK":
            return {"error": req["message"]}
        lessons = {}
        for lesson in req["returnedObject"]:
            lsn = Lesson(
                dt.datetime.strptime(lesson["date"], "%Y-%m-%d"),
                lesson["description"],
                lesson["previousHomeTask"],
                Worker(lesson["worker"]),
                lesson["subject"]["shortName"],
                lesson["room"]["number"],
                LessonTime(lesson["shiftsMode"]),
                Score(lesson["lessonScores"][0] if lesson["lessonScores"] else {}),
                )
            if lsn.score.mark:
                lessons[lsn.subject_short_name] = lessons.get(lsn.subject_short_name, []) + [lsn]
        return lessons

    async def get_period(self, person_id: int, date_start: dt.date = dt.date.today() - dt.timedelta(days=31), date_end: dt.date = dt.date.today()):
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }

        resp = await (await self.session.get("https://school.edu-penza.ru/android/scores/period", params=params)).json()

        if resp["message"] != "OK":
            return {"error": resp["message"]}
        return resp["returnedObject"]
    
    async def __get_periods_dates(self):
        resp = await (await self.session.get("https://school.edu-penza.ru/android/childs")).json()

        if resp["message"] != "OK":
            return {"error": resp["message"]}
        self.periods = resp["returnedObject"][0]["subperiods"]

    def __new__(cls, *args, **kwargs):
        print(args)
        _instance = None

        if not _instance:
            _instance = super().__new__(cls)
        return _instance
        
