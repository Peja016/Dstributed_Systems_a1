# Import socket library
# Create TCP/IP socket
# Bind to localhost:8080
# Listen for connections
# While True:
# - Accept client connection
# - Receive data from client
# - Process data
# - Send response back
# - Close connection

import socket
import time

try:
    # 1. Create TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 2. Bind to all available network interfaces (so other containers/hosts can connect)
    server_socket.bind(("0.0.0.0", 8080))

    # 3. Listen for incoming connections
    server_socket.listen(3)
    print("Server listening on port 8080")
except OSError as e:
    print(f"FATAL ERROR during startup: {e}")
    print("Check if port 8080 is already in use or if you have permission.")
    exit(1)

# 4. Accept connections in a loop
while True:
    try:
        # - Accept client connection
        client_socket, client_addr = server_socket.accept()
        print(f"Connection from {client_addr}")

        # - Receive data from client
        client_socket.settimeout(3.0)  # wait for 3 secs
        warning_msg = "You didn't send any data or sent an empty string" # create a warining message if the client didn't sent data or sent an empty sting.
        try:
            data = client_socket.recv(1024).decode()

            if not data:
                print(f"WARNING: Client {client_addr} sent nothing (closed connection).")
                client_socket.send(warning_msg.encode())
                continue
            else:
                print(f"Received: {data}")
                response = data.upper()
                client_socket.send(response.encode())

        except socket.timeout:
            print(f"WARNING: Client {client_addr} timed out waiting for data.")
            client_socket.send(warning_msg.encode())
        except ConnectionResetError:
            print(f"WARNING: Client {client_addr} forcibly closed the connection.")
        except UnicodeDecodeError:
            print(f"WARNING: Received data from {client_addr} was not valid text (UnicodeDecodeError).")
        except Exception as e:
            print(f"ERROR handling client {client_addr}: {e}")

        finally:
            # Add delay to prevent race condition/ConnectionResetError
            time.sleep(0.1)
            # - Close connection
            client_socket.close()

    except KeyboardInterrupt:
        # press Ctrl+C to terminate the server
        print("\nServer shutdown requested.")
        break
    except Exception as e:
        # handle the other error except for accept() 
        print(f"Unexpected error in main loop: {e}")
        break

server_socket.close()
print("Server shut down cleanly.")