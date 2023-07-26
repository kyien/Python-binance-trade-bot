from classes import Bot
from threading import Thread

bot1 = Bot("BTCUSDT",0.001,5,1,1)
bot2 = Bot("ETHUSDT",0.01,5,1,1)


def b1():
    bot1.run()


def b2():
    bot2.run()


t1 = Thread(target=b1)
t2 = Thread(target=b2)

t1.start()
t2.start()