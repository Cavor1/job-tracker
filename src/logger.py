import datetime

def log(l : str):
    with open("log.log","a") as f:
        f.write(f'{datetime.datetime.now()}\t{l}\n')