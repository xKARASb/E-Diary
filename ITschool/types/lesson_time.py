import datetime as dt

class LessonTime:
    day_of_week: int
    num: int
    start_time: dt.datetime
    end_time: dt.datetime

    def __init__(self, shifts_mode: dict):
        self.days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        self.day_of_week = shifts_mode["dayWeek"]
        self.num = shifts_mode["num"]
        self.start_time = dt.datetime.strptime(shifts_mode["timeBegin"], "%H:%M:%S")
        self.end_time = dt.datetime.strptime(shifts_mode["timeEnd"], "%H:%M:%S")
    
    def __str__(self):
        return f"{self.days[self.day_of_week - 1]} {self.num} урок {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    