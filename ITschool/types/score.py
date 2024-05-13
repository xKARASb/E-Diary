class Score:
    def __init__(self, lesson_scores: dict):
        self.mark = ""
        miss = ""
        score = ""
        additional_score = ""
        if lesson_scores:
            if lesson_scores["miss"]:
                miss = "Н"
            if lesson_scores["scoreStr"]:
                score = lesson_scores["scoreStr"]
            elif lesson_scores["additionalScoreStr"]:
                additional_score = lesson_scores["additionalScoreStr"]
        self.mark = " ".join([i for i in [miss, score, additional_score] if i])
    def __str__(self):
        return str(self.mark)