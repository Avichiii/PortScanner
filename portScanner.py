from socket import * 
import threading
import logging
import argparse
import datetime
import time

DATA_SEGMENT = 1024

logging.basicConfig(level = logging.DEBUG, filename='portscanner.log', filemode='w', format='[%(asctime)s] [%(process)s] [%(levelname)s] [%(message)s]')
logg = logging.getLogger(__name__)

class TimeDate:
    getTime = datetime.datetime.now()
    formatTime = getTime.strftime(f'%Y-%m-%d %H:%M IST')


class ConnectionThread:
    def __init__(self, host:str, port:int, increaseWait, scanResult:list):
        self.host = host
        self.port = port
        self.increaseWait = increaseWait
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.scanResult = scanResult 
    
    def run(self):
        try:
            if self.increaseWait:
                self.clientSocket.settimeout(3)
            
            if self.clientSocket.connect_ex((self.host, self.port)) == 0:
                serviceName = self.getServiceName(self.port)

                if serviceName:
                    self.scanResult.append('%d/tcp open %s' % (self.port, serviceName))
                else:
                    self.scanResult.append('%d/tcp open' % (self.port))

                self.clientSocket.close()

        except Exception as e:
            logg.info(e)
        
    @staticmethod
    def getServiceName(port:int) -> str:
        try:
            return getservbyport(port)
    
        except OSError as error:
            logg.info(f'service error: {error}')


class InitClient:
    def __init__(self,options):
        self.host = options.host
        self.startPort = options.startPort
        self.endingPort = options.endPort
        self.increaseWait = options.increaseWait
        print(f'Starting Port Scanner at {TimeDate.formatTime}')
        print(f'Scan report for ({self.host})')
        print('PORT   STATE SERVICE')
        
    def start(self):
        try:
            start = time.perf_counter()

            threads = []
            scanResult = []
            
            for port in range(self.startPort, self.endingPort + 1):
                thread = threading.Thread(target=ConnectionThread(self.host, port, self.increaseWait, scanResult).run)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            sortedResult = sorted(scanResult, key= lambda x: int(x.split('/')[0]))
            for result in sortedResult:
                print(result)

            finish = time.perf_counter()

            print(f'\ntime took {round(finish-start, 2)} s')
        
        except OSError as os:
            if os.errno > 65536:
                print('To many Open files!')
                exit(0)
            logg.info(os)

        except KeyboardInterrupt:
            print('Keyboard interrupt!')
            exit(0)


if __name__ == "__main__":
    desc = 'Python Port Scanner - Multithreaded'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-n', type=str, default=gethostbyname(gethostname()),
                        dest='host',
                        help='enter the host IP %(default)s')
    parser.add_argument('-p', type=int, default=1,
                        dest='startPort',
                        help='specify the starting port address %(default)s')
    parser.add_argument('-',type=int, default=1024,
                        dest='endPort',
                        help='specify the ending port address %(default)s')
    parser.add_argument('-Pn', action='store_true', dest='increaseWait',
                        help='wait for 3s before before determining that socket is closed.') 
    options = parser.parse_args()

    if hasattr(options, '-h'):
        parser.print_help()
    
    init = InitClient(options)
    init.start()