from aiohttp import ClientSession
import requests
from time import sleep

from .types import Lesson, Worker, LessonTime, Score
import datetime as dt
import threading as th
from ITschool.exceptions import ServerUnaccessible

import logging
import json
import asyncio

learners = {}

class Learner:
    _instance = None
    
    def __init__(self, jsessionid: str):
        self.cookies = {
            "JSESSIONID": jsessionid
            }
        self.last_request = None
        self.server_allowed = False

    async def start_polling(self):
        self.session = ClientSession(cookies=self.cookies)
        
        self.ping_running = True
        self.server_available = True
        self.loop = asyncio.get_running_loop()
        
        task = th.Thread(target=self.ping)
        task.start()
        await self.__get_periods_dates()
        logging.info(self.periods)
    
    def server_is_available(method: callable):
        def is_server_allowed(self, *args, **kwargs):
            if self.server_available:
                return method(self, *args, **kwargs)
            else:
                raise ServerUnaccessible("Server is not available")
        return is_server_allowed
    
    def ping(self):
        logging.info("Start pinging")
        while self.ping_running:
            resp = requests.get("https://school.edu-penza.ru/users/getprofile/", cookies=self.cookies, allow_redirects=False)
            
            if resp.status_code != 200:
                self.server_available = False
                return {"error": "Sessionid expired"}
            sleep(300)
            
    async def stop_polling(self):
        logging.info("Stop pinging...")
        self.ping_running = False
        await self.session.close()
        logging.info("Stoped pinging")
                
    async def update_cookie(self, jsessionid: str):
        self.cookies["JSESSIONID"] = jsessionid 
        await self.session.close()
        self.session = ClientSession(cookies=self.cookies)
    
    @server_is_available
    async def get_week(self, person_id: int, date_start=dt.date.today(), date_end=dt.date.today(), sort_by = "subject") -> dict[str, list[Lesson]]:
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }
        
        req = await self.session.get("https://school.edu-penza.ru/android/scores/week", params=params, allow_redirects=False)


        if req.status > 300:
            logging.info(req.status_code)
            self.server_available = False
            raise ServerUnaccessible("Server is not available")
        
        req = await req.json()
        if req["message"] != "OK":
            return {"error": req["message"]}
        lessons = {}
        if sort_by == "subject":
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
        elif sort_by == "date":
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
                lessons[lsn.date.strftime("%Y-%m-%d")] = lessons.get(lsn.date.strftime("%Y-%m-%d"), []) + [lsn]
        return lessons

    @server_is_available
    async def get_period(self, person_id: int, date_start: dt.date = dt.date.today() - dt.timedelta(days=31), date_end: dt.date = dt.date.today()):
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }

        resp = await self.session.get("https://school.edu-penza.ru/android/scores/period", params=params, allow_redirects=False)

        if resp.status > 300:
            logging.info(resp.status_code)
            self.server_available = False
            raise ServerUnaccessible("Server is not available")
        resp = await resp.json()
        if resp["message"] != "OK":
            return {"error": resp["message"]}
        return resp["returnedObject"]
    
    async def __get_periods_dates(self):
        # resp = await (await self.session.get("https://school.edu-penza.ru/android/childs")).json()

        # if resp["message"] != "OK":
        #     return {"error": resp["message"]}
        # self.periods = resp["returnedObject"][0]["subperiods"]
        dates = """[
        {
            "guid": "067b299f-7405-41e7-9875-52fc2ad18e1e",
            "deleted": false,
            "id": 23892,
            "dateFrom": "2023-09-01",
            "dateTo": "2023-10-27",
            "dateExFrom": null,
            "dateExTo": null,
            "studyPeriod": {
                "guid": null,
                "deleted": false,
                "id": 1,
                "code": 1,
                "name": "I четверть",
                "group": 1
            }
        },
        {
            "guid": "b48fab2f-6704-4bc2-bfe7-05a3f3eafe4f",
            "deleted": false,
            "id": 23893,
            "dateFrom": "2023-11-07",
            "dateTo": "2023-12-22",
            "dateExFrom": null,
            "dateExTo": null,
            "studyPeriod": {
                "guid": null,
                "deleted": false,
                "id": 2,
                "code": 2,
                "name": "II четверть",
                "group": 1
            }
        },
        {
            "guid": "5b24f860-7655-4467-8c9d-b32afef1199a",
            "deleted": false,
            "id": 23894,
            "dateFrom": "2024-01-09",
            "dateTo": "2024-03-22",
            "dateExFrom": null,
            "dateExTo": null,
            "studyPeriod": {
                "guid": null,
                "deleted": false,
                "id": 3,
                "code": 3,
                "name": "III четверть",
                "group": 1
            }
        },
        {
            "guid": "430552a8-7098-40ac-97ee-43be875be817",
            "deleted": false,
            "id": 23895,
            "dateFrom": "2024-04-01",
            "dateTo": "2024-05-24",
            "dateExFrom": null,
            "dateExTo": null,
            "studyPeriod": {
                "guid": null,
                "deleted": false,
                "id": 4,
                "code": 4,
                "name": "IV четверть",
                "group": 1
            }
        }
    ]"""
        self.periods = json.loads(dates)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
        
