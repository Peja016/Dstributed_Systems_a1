# Create Socket connection to server
# Create input/output streams
# Send message to server
# Wait for response
# Print server response
# Close connection

import os, socket

# Configuration retrieved from environment variables
HOST = os.getenv("APP") or "127.0.0.1"   # Default to localhost
PORT = 8080  # Port number for socket server

def run_test_case(test_name: str, payload: str, override_host=None, override_port=None):
    """
    Run a single test case with given payload.
    Focus only on socket-level errors (not payload validation).
    """
    host = override_host or HOST
    port = override_port or PORT

    print(f"\n--- {test_name} ---")
    try:
        # 1. Create socket and attempt connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"SUCCESS: Connection established to {host}:{port}")

        # 2. Send message (any string is accepted by server)
        print(f"Sending: {payload!r}")
        client_socket.send(payload.encode())

        # 3. Wait for server response
        try:
            response = client_socket.recv(1024).decode()
            print("Server response:", response)
        
        except ConnectionResetError:
            print("SOCKET ERROR: Connection was reset by the server.")
        except UnicodeDecodeError:
            print("SOCKET ERROR: Received non-decodable data from server.")

    # ----------------------------------------------------------------------
    # Socket-specific connection errors
    # ----------------------------------------------------------------------
    except ConnectionRefusedError:
        print(f"SOCKET ERROR: Connection refused at {host}:{port} (server down or port incorrect).")
    except socket.gaierror:
        print(f"SOCKET ERROR: Hostname resolution failed for '{host}'.")
    except Exception as e:
        print(f"SOCKET ERROR: Unexpected issue - {e}")

    # ----------------------------------------------------------------------
    # Ensure socket is always closed
    # ----------------------------------------------------------------------
    finally:
        if 'client_socket' in locals():
            try:
                client_socket.close()
                print("Connection closed.")
            except Exception:
                pass

if __name__ == "__main__":
    # testing list
    test_cases = [
        ("1. Normal Message", "hello server"),
        ("2. Empty String", ""),                      # send empty string, and check how server reponses
        ("3. Wrong Port (simulate ConnectionRefused)", "test", None, 9999),  # testing by useing a wrong port
        ("4. Bad Hostname (simulate gaierror)", "test", "no_such_host", 8080), # testing by useing a wrong host
    ]

    for case in test_cases:
        run_test_case(*case)


