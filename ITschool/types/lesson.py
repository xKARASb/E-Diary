from datetime import date
from . import *

class Lesson:
    def __init__(
            self,
            date: date,
            description: str,
            home_task: str,
            teacher: Worker,
            subject_short_name: str,
            room: int,
            lesson_shift: LessonTime 
    ):
        self.date = date
        self.descrption = description
        self.home_task = home_task
        self.teacher = teacher
        self.subject_short_name = subject_short_name
        self.room = room
        self.lesson_shift = lesson_shift
        self.score = Score

    async def get_date(self) -> str:
        return self.date.strftime('%Y-%m')
    