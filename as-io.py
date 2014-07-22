import asyncio

@asyncio.coroutine
def factorial(name, number):
    f = 1
    for i in range(2, number+1):
        print("Task %s: compute factorial (%s)" % (name, i))
        yield from asyncio.sleep(1)
        f *= i
    print("Task %s: factorial(%s) = %s" % (name, number, f))

loop = asyncio.get_event_loop()

tasks = [
    asyncio.Task(factorial("A",5)),
    asyncio.Task(factorial("B",2)),
    asyncio.Task(factorial("C",3)),
]

try:
    loop.run_until_complete(asyncio.wait(tasks))
finally:
    loop.close()
