class Score:
    def __init__(self, lesson_scores: dict):
        self.mark = None
        if lesson_scores:
            if lesson_scores["miss"]:
                self.mark = "Н"
            elif lesson_scores["scoreStr"] and lesson_scores["additionalScoreStr"]:
                self.mark = f"{lesson_scores['scoreStr']} {lesson_scores['additionalScoreStr']}"
            elif lesson_scores["scoreStr"]:
                self.mark = lesson_scores["scoreStr"]
            elif lesson_scores["additionalScoreStr"]:
                self.mark = lesson_scores["additionalScoreStr"]
        
    def __str__(self):
        return str(self.mark)