import datetime

start = datetime.time(10, 0, 0)
end = datetime.time(18, 0, 0)
print(datetime.datetime.now().time())
print(start < datetime.datetime.now().time() < end)

