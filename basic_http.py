import socket
import json
import random

from dice import Dice

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

PORT = 8081

# Bind the server socket to an IP address and port
server_socket.bind(('localhost', PORT))

# Start listening for incoming connections
server_socket.listen(1)
print(f"Server is listening on port {PORT}...")

# Accept incoming client connections
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")
    
    # Receive the HTTP request from the client
    request = client_socket.recv(1024).decode('utf-8')
    print(f"Request received ({len(request)}):")
    # print("*"*50)
    # print(request)
    # print("*"*50)

    # Check if the request is a GET request
    # if request.startswith("GET /myjson"):
    #     response_data = {
    #         "status": "success",
    #         "message": "Hello, KU!"
    #     } # JSON response example

    #     # Convert dictionary to JSON string
    #     response_json = json.dumps(response_data)

    #     # HTTP response with JSON content
    #     response = f"""HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_json}"""
    if request.startswith("GET"):
        # Prepare an HTTP response (basic HTML)
        response = request.split("\r\n\r\n")
        # print('-'*100)
        response_dict = json.loads(response[1])
        # print(response_dict)
        # print('-'*100)
        # print(type(response_dict))
        this_dice = Dice(response_dict['probabilities'], response_dict['number_of_random'])
        res_ = this_dice.roll()
        # print(res_)
        response_json = json.dumps(res_)
        response = f"""HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_json}"""
    else:
        # Respond with a 405 Method Not Allowed if not a GET request
        response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    client_socket.sendall(response.encode('utf-8')) # Send the HTTP response to the client

    client_socket.close() # Close the client connection
    
    print("Waiting for the next TCP request...")