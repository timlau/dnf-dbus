from dnfdbus.client import DnfDbusClient, DnfDbusSignals
from dasbus.loop import EventLoop

if __name__ == "__main__":
    # Create listener that listen to signals from backend
    loop = EventLoop()
    listener = DnfDbusSignals(loop)
    # Start the event loop.
    loop.run()
