import hpfeeds
import sys


HOST = 'localhost'
PORT = 10000

CHANNELS = [
    "cowrie.sessions",
    "snort.alerts",
    "agave.events",     # for drupot
    "wordpot.events"
]

IDENT = 'collector'
SECRET = 'collector'


def main():
    hpc = hpfeeds.new(HOST, PORT, IDENT, SECRET)
    print("connected to " + hpc.brokername)

    def on_message(identifier, channel, payload):
        print ('msg:\n', identifier, channel, payload)
        print ('payload type --> ' + str(type(payload)))
        print("\n")

    def on_error(payload):
        hpc.stop()

    hpc.subscribe(CHANNELS)
    hpc.run(on_message, on_error)
    hpc.close()
    return 0


main()