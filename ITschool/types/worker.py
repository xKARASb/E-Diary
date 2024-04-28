class Worker:
    def __init__(self, worker: dict):
        self.full_namename = worker["person"]["fullName"]
        self.short_name = worker["person"]["shortName"]
    