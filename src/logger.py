import datetime


def log(message: str):
    with open("log.log", "a") as f:
        f.write(f"{datetime.datetime.now()}\t{message}\n")
