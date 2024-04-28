from aiohttp import ClientSession
from .types import Lesson, Worker, LessonTime, Score
import datetime as dt

class Learner:
    def __init__(self, jsessionid: str):
        self.cookies = {
            "JSESSIONID": jsessionid
            }
        self.last_request = None

    async def start_polling(self):
        self.session = ClientSession(cookies=self.cookies)
    
    async def stop_polling(self):
        await self.session.close()
                
    async def update_cookie(self, jsessionid: str):
        self.cookies["JSESSIONID"] = jsessionid
        await self.session.close()
        self.session = ClientSession(cookies=self.cookies)
    
    async def get_week(self, person_id: int, date_start=dt.date.today(), date_end=dt.date.today()):
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }
        
        req = self.session.get("https://school.edu-penza.ru/android/scores/week", params=params).json()

        if req["message"] != "OK":
            return {"error": req["message"]}
        return [
            Lesson(
                dt.datetime.strptime(lesson["date"], "%Y-%m-%d"),
                lesson["description"],
                lesson["previousHomeTask"],
                Worker(lesson["worker"]),
                lesson["subject"]["shortName"],
                lesson["room"]["number"],
                LessonTime(lesson["shiftsMode"]),
                Score(lesson["score"])
                )
            for lesson in req["returnedObject"]
            ]

    async def get_period(self, person_id: int, date_start: dt.date = dt.date.today() - dt.timedelta(days=31), date_end: dt.date = dt.date.today()):
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }

        resp = self.session.get("https://school.edu-penza.ru/android/scores/period", params=params).json()

        if resp["message"] != "OK":
            return {"error": resp["message"]}
        return resp["returnedObject"]
    
    async def __get_periods_dates(self):
        resp = self.session.get("https://school.edu-penza.ru/android/childs").json()

        if resp["message"] != "OK":
            return {"error": resp["message"]}
        return  resp["returnedObject"][0]["periods"]
    
