from aiohttp import ClientSession
import requests
from time import sleep

from .types import Lesson, Worker, LessonTime, Score
import datetime as dt
import threading as th
from ITschool.exceptions import ServerUnaccessible, UnrecognizedError

import logging
import json
import asyncio

from datetime import datetime
import mintotp
from time import sleep

learners = {}

class Learner:
    _instance = None
    
    def __init__(self, bot_token, notification_user_id, esia_password, esia_login, esia_totp_key):
        self.esia_passw = esia_password
        self.esia_login = esia_login
        self.bot_token = bot_token
        self.esia_totp_key = esia_totp_key
        self.notification_user_id = notification_user_id
        self.ediary_cookies = {
            "JSESSIONID": None
        }
        
    def send_notification(self, text):
        requests.get(f"https://api.telegram.org/bot{self.bot_token}/sendMessage&chat_id={self.notification_user_id}&text={text}")

    async def start_polling(self):
        self.is_ediary_running = True
        self.is_ediary_server = True

        if not self.update_jsession_cookie():
            return False
        self.session = ClientSession(cookies=self.ediary_cookies)
        
        self.loop = asyncio.get_running_loop()
        
        task = th.Thread(target=self.ping_ediary)
        task.start()
        await self.__get_periods_dates()

    async def stop_polling(self):
        logging.info("Stop pinging...")
        self.is_ediary_running = False
        await self.session.close()

    def ping_ediary(self):
        logging.info("Start pinging ediary")
        while self.is_ediary_running:
            resp = requests.get("https://school.edu-penza.ru/users/getprofile/", cookies=self.ediary_cookies, allow_redirects=False)
            
            self.is_ediary_server = True
            
            if resp.status_code == 302:
                if not self.update_jsession_cookie():
                    self.is_ediary_server = False
                    self.is_ediary_running = False
            elif resp.status_code > 400:
                self.is_ediary_server = False
                self.send_notification("Ediary server inaccessible")
                
            sleep(300)
        self.is_ediary_server = False
        self.send_notification("Stoped ping ediary server")
    
    def is_server_available(method: callable):
        def is_server_allowed(self, *args, **kwargs):
            if not self.is_ediary_server:
                raise ServerUnaccessible("Server is not available")
            else:
                return method(self, *args, **kwargs)
        return is_server_allowed
                
    async def __make_request(self, *args, **kwargs):
        resp = await self.session.get(*args, **kwargs)
        
        if resp.status == 302:
            if not self.update_jsession_cookie():
                raise UnrecognizedError("Couldn`t update jsession cookie")
            resp = await self.session.get(*args, **kwargs)
        elif resp.status > 400:
            self.is_ediary_server = False
            raise ServerUnaccessible("Server is not available")
        
        if (await resp.json())["message"] != "OK":
            raise UnrecognizedError((await resp.json())["message"])
        
        return await resp.json()
                
    def update_jsession_cookie(self):
        self.esia_session  = self.login_esia()
        session = self.get_jsessionid()
        
        if session:
            self.ediary_cookies["JSESSIONID"] = session
            logging.info(f"JSESSION: {session}")
            return True
        self.send_notification("Can not update JSESSIONID")
        return None

    def login_esia(self):
        logging.info("Start login esia")
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://esia.gosuslugi.ru",
            "Referer": "https://esia.gosuslugi.ru/login/",
            "Host": "esia.gosuslugi.ru",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        }
        param = {
            "ondate": datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        }
        req = requests.get("https://esia.gosuslugi.ru/rs/dscl", params=param, headers=headers)
        
        data = {
            'login': self.esia_login,
            'password': self.esia_passw
        }

        sleep(5)
        req = requests.post("https://esia.gosuslugi.ru/aas/oauth2/api/login", headers=headers, json=data, cookies=req.cookies)
        
        logging.info(req.status_code)
        cookies = {}
        cookies = req.cookies.get_dict()
                
        if req.status_code < 300:
            login_data = req.json()
            esia_session = req.cookies.get("ESIA_SESSION")
            logging.info(login_data)
            if login_data.get("failed"):
                logging.error(login_data)
                raise Exception
            match login_data["action"]:
                case "SOLVE_ANOMALY_REACTION":
                    match login_data["reaction_details"]["type"]:
                        case "О.ЗД1":
                            #Captcha
                            logging.info("0.3Д1 Капча")
                            req = requests.get("https://esia.gosuslugi.ru/captcha/api/public/v2/type", headers=headers, cookies=cookies)
                            data = req.json()
                            
                            captcha_session = data.get("captchaSession")
                            
                            cookies = req.cookies.get_dict()
                            captcha_headers = {
                                "Content-Type": "application/json",
                                "Origin": "https://esia.gosuslugi.ru",
                                "Referer": "https://esia.gosuslugi.ru/login/",
                                "Host": "esia.gosuslugi.ru",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                                "Captchasession": captcha_session,
                            }
                            
                            req = requests.get("https://esia.gosuslugi.ru/captcha/api/public/v2/image", headers=captcha_headers, cookies=cookies)
                            
                            with open(f"./data/{captcha_session}.png", "wb") as f:
                                f.write(req.content)
                            
                            self.send_notification("Капча")
                            self.send_notification(f"https://zoloto.net/E-diary/data/{captcha_session}.png")
                            
                            self.esia_login_data = {
                                "headers": captcha_headers,
                                "cookies": cookies,
                                "guid": login_data["guid"]
                            }
                            
                            # verify_data = {
                            #     "answer": captcha_answer,
                            #     "captchaType": "esiacaptcha"
                            # }
                            
                            # req = requests.post("https://esia.gosuslugi.ru/captcha/api/public/v2/verify", headers=captcha_headers, cookies=cookies, data=verify_data)

                            # verify_token = req.json()["verify_token"]
                            
                            # params = {
                            #     "guid": login_data["guid"],
                            #     "verify_token": verify_token
                            # }
                            
                            # req = requests.post("https://esia.gosuslugi.ru/aas/oauth2/api/anomaly/captcha/verify", params=params)
                            
                            self.wait_captcha = True
                            
                            while self.wait_captcha:
                                pass
                            
                        case "О.3И1":
                            #Question
                            logging.info("0.3И1")
                            question = requests.get(f"https://esia.gosuslugi.ru/anomaly-resolver/api/reaction/question?guid={login_data['reaction_details']['guid']}", headers=headers, cookies=cookies)
                            
                            match question.json()["question_code"]:
                                case "Q12":
                                    answ = "29"
                                case _:
                                    self.send_notification(f"{question.json()['question_code']}")
                                    self.send_notification(f"question:\n{question.json()['question_text']}")
                                    # answ = input(f"{question.json()['question_text']}: ")
                                    return 
                            req = requests.post("https://esia.gosuslugi.ru/aas/oauth2/api/anomaly/question/answer", json={"answer": answ, "guid": login_data["reaction_details"]["guid"]}, cookies=cookies, headers=headers)
                            
                        case _:
                            logging.info("No handler")
                            logging.info(login_data["reaction_details"]["type"])
                case "ENTER_MFA":
                    pass
                case _:
                    logging.info(login_data["action"])
                    raise Exception

        headers = {
            "Content-Type": "application/json",
            "Origin": "https://esia.gosuslugi.ru",
            "Referer": "https://esia.gosuslugi.ru/login/",
            "Host": "esia.gosuslugi.ru",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        }
        
        cookies = req.cookies
        logging.info(cookies)
        
        code = mintotp.totp(self.esia_totp_key)
        
        req = requests.post(f"https://esia.gosuslugi.ru/aas/oauth2/api/login/totp/verify?code={code}", cookies=cookies, headers=headers)
        
        if req.status_code == 200:
            return esia_session
        else:
            logging.info(req.json())
            raise Exception

    def get_jsessionid(self):
        cookies = {
            "ESIA_SESSION": self.esia_session
        }
        link_req = requests.get("https://school.edu-penza.ru/esia/auth/login", allow_redirects=False)
        req = requests.get(link_req.headers.get("Location"), cookies=cookies)
        return req.url.split("state=")[1]
    
    async def __get_periods_dates(self):
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

    @is_server_available
    async def get_week(self, person_id: int, date_start=dt.date.today(), date_end=dt.date.today(), sort_by = "subject") -> dict[str, list[Lesson]]:
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }
        
        resp = await self.__make_request("https://school.edu-penza.ru/android/scores/week", params=params, allow_redirects=False)

        lessons = {}
        if sort_by == "subject":
            for lesson in resp["returnedObject"]:
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
            for lesson in resp["returnedObject"]:
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


    @is_server_available
    async def get_period(self, person_id: int, date_start: dt.date = dt.date.today() - dt.timedelta(days=31), date_end: dt.date = dt.date.today()):
        params = {
            "childId": person_id,
            "dateStart": dt.datetime.strftime(date_start, "%Y-%m-%d"),
            "dateEnd": dt.datetime.strftime(date_end, "%Y-%m-%d")
        }

        resp = await self.__make_request("https://school.edu-penza.ru/android/scores/period", params=params, allow_redirects=False)
        
        return resp["returnedObject"]
 

    @is_server_available
    async def get_final(self, person_id: int) -> list[str]:
        params = {
            "childId": person_id
        }
        
        resp = await self.__make_request("https://school.edu-penza.ru/android/scores/result", params=params, allow_redirects=False)
        
        return resp["returnedObject"]
