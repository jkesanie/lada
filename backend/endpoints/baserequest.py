import socket

lcdURL = "h224.it.helsinki.fi"
lcdPort = 8080

class BaseRequest(object):

    def __init__(self, datamanager):
        self.dm = datamanager


    def checkForConnection(self):
        try:
            socket.create_connection((lcdURL, lcdPort))
            return True
        except:
            pass
        return False
