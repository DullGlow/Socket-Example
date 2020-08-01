import socket  # Import socket module
import random
import datetime
import math
import threading


# Prints out all the services that are available
def print_functions():
    result = "Our available services include:\n"
    result += "[1] Echo\n"
    result += "[2] Sum\n"
    result += "[3] Multiply\n"
    result += "[4] Generate random number\n"
    result += "[5] Time\n"
    result += "[6] Date\n"
    result += "[7] Exit"
    return result


def date():
    return "Date: " + str(datetime.datetime.now().strftime("%Y-%m-%d"))


def time():
    return "Current time: " + str(datetime.datetime.now().strftime("%H:%M:%S"))


def generate_rand_num():
    return "Generated: " + str(random.randint(0, 10**9))


# Receives two integers from client and returns their multiple
def get_multiple(c):
    nums = []
    c.send("Multiply as many numbers as you will. Enter zero (0) to finish input.".encode())
    received = receive_int(c)
    while received != 0:
        nums.append(received)
        c.send("Please enter a number (zero to cancel): ".encode())
        received = receive_int(c)
    return "(" + (") * (".join([str(x) for x in nums])) + ") = " + str(math.prod(nums))


# Receives two integers from client and returns their sum
def get_sum(c):
    nums = []
    c.send("Sum as many numbers as you will. Enter zero (0) to finish input.".encode())
    received = receive_int(c)
    while received != 0:
        nums.append(received)
        c.send("Please enter a number (zero to cancel): ".encode())
        received = receive_int(c)
    return "(" + (") + (".join([str(x) for x in nums])) + ") = " + str(sum(nums))


# Sends received message back to client
def echo(c):
    c.send("Send us any message you want!".encode())
    received = receive(c)
    return 'Echo: "' + str(received) + '"'


# Redirect client to desired service
def function_switch(c):
    option = receive_int(c)
    if option == 1:
        return 0, echo(c)
    elif option == 2:
        return 0, get_sum(c)
    elif option == 3:
        return 0, get_multiple(c)
    elif option == 4:
        return 0, generate_rand_num()
    elif option == 5:
        return 0, time()
    elif option == 6:
        return 0, date()
    else:
        return 1, "Thank you for using our services!"


# Receive message from client. Accepts only integers
def receive_int(c):
    try:
        client_name = client_names[c]
    except KeyError:  # Shouldn't occur
        client_name = "Unknown"
    while True:
        try:
            received = int(c.recv(1024).decode())
            print(client_name + ": " + str(received))
            return received
        except ValueError:
            c.send("Provided input is not a number. Please try again.".encode())


# Receive message from client
def receive(c):
    try:
        client_name = client_names[c]
    except KeyError:  # User hasn't yet provided a name
        client_name = "Unknown"
    received = str(c.recv(1024).decode())
    print(client_name + ": " + received)
    return received


def handle_client(c, addr):
    global client_names
    try:
        print('Got connection from' + str(addr) + ":")
        c.send("Thank you for connecting\nWhat's your username?".encode())

        # Get name and update name table
        cname = receive(c)
        client_names[c] = cname

        c.send(("Hello, " + cname + ". How can we help you?\n" + print_functions()).encode())

        # Loop for function switch
        repeat, result = function_switch(c)
        while repeat == 0:  # 0 -> repeat  || 1 -> exit
            c.send((str(result) + "\nAnything else we can help you with?\n" + print_functions()).encode())
            repeat, result = function_switch(c)
        c.send(str(result).encode())

        # End connection
        c.close()
        del client_names[c]  # Remove the name from table
        print("Closed connection with " + str(addr) + ":" + cname)
    except BrokenPipeError:
        print("Connection to" + str(addr) + ":" + client_names[c] + " was disrupted.")
        try:
            del client_names[c]
        except KeyError:
            pass


print('Starting server...')

s = socket.socket()  # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 12345  # Reserve a port for your service.
s.bind((host, port))  # Bind to the port

client_names = {}  # All the sockets (key) will be associated with names (value)

print('Waiting for client...')
s.listen(5)  # Now wait for client connection.
while True:
    try:
        sock, address = s.accept()  # Establish connection with client.
        thread = threading.Thread(target=handle_client, args=(sock, address))
        thread.start()
    except KeyboardInterrupt:  # Force closing server
        print("Terminating program...")
        break
