# Synchronous Communication Patterns

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Design & Implementation](#system-design-&-implementation)
3. [Instructions](#instructions)
4. [Test Results](#test-results)
5. [Performance Comparison](#performance-comparison)
6. [Conclusion](#conclusion)
7. [References](#references)

---

## Project Overview

This project demonstrates **synchronous request-response communication** using three different technologies:

1. **Raw TCP Sockets** – low-level communication using Python’s built-in `socket` library.
2. **REST API** – synchronous HTTP communication implemented with Flask.
3. **gRPC** – modern, high-performance synchronous RPC framework with Protocol Buffers.

A **benchmarking module** is also included to compare REST vs gRPC performance in a controlled environment.

The entire system is containerized with **Docker** and orchestrated with **docker-compose** for easy testing and reproducibility.

## Project Structure

```
distributed-systems-a1/
├── python-socket-lab/          # Socket implementation
│   ├── server.py               # Socket server
│   ├── client.py               # Socket client(including tests)
│   ├── requirements.txt
│   └── Dockerfile
├── python-rest-lab/            # REST API implementation
│   ├── app.py                  # Flask application
│   ├── models.py               # User class
│   ├── requirements.txt
│   └── Dockerfile
├── python-grpc-lab/            # gRPC implementation
│   ├── proto/
│   │   └── user_service.proto  # Interface definition
│   ├── generated/              # Auto-generated code
│   │   └── __init__.py
│   │   └── user_service_pb2_grpc.py  # Auto-generated py file
│   │   └── user_service_pb2.py  # Auto-generated py file
│   ├── server.py               # gRPC server
│   ├── client.py               # gRPC client(including tests)
│   ├── requirements.txt
│   └── Dockerfile
├── benchmark.py                # Performance comparison
├── Dockerfile.benchmark        # dockerfile
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This document
```

---

## System Design & Implementation

This project adopts a classic client–server model, where all three implementations (Socket, REST, and gRPC) follow the same synchronous communication flow:

```
Client                          Server
  |                               |
  |-----> 1. Sends a request ---->|
  |                               | 2. Processes the request
  | (Waits until response)        |
  |<----- 3. Receives response ---|
  |                               |
  | 4. Continues execution        |
```

### 1. Socket Implementation

**Tech Stack:** Python `socket` library + TCP protocol

**Overview:**  
The socket implementation demonstrates **low-level synchronous communication** using Python’s built-in socket API.  
It employs a **request–response pattern**, where the server waits (blocks) for incoming connections and data, processes the message, and returns a response before accepting new requests.

**Features:**

- Raw TCP socket communication without external frameworks
- Simple message handling logic (text or JSON-like format)
- Sequential, synchronous processing for each client connection

**Briefly Code Example:**

```python
# --- Server side ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8080))
server_socket.listen(3)

client_socket, client_addr = server_socket.accept()  # Blocking: waits for connection
client_socket.settimeout(3.0)                        # wait for 3 secs
data = client_socket.recv(1024)                      # Blocking: waits for data
response = process_message(data)
client_socket.send(response)                         # Blocking: sends response

# --- Client side ---
HOST = os.getenv("APP") or "127.0.0.1"               # Default to localhost
PORT = 8080                                          # Port number for socket server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))                  # Blocking: establishes connection
client_socket.send(message.encode())                 # Sends data synchronously
response = client_socket.recv(1024).decode()         # Blocking: waits for server reply
```

**Code Rationale:**

#### Socket Server Logic (`server.py`)

This script implements a **basic synchronous TCP server** that continuously listens for incoming client connections, processes data, and responds before serving the next client.

**Key Steps:**

1. **Initialization:**

   - Creates a TCP/IP socket (`socket.AF_INET`, `socket.SOCK_STREAM`).
   - Binds to `0.0.0.0:8080`, allowing external connections from other hosts or containers.
   - Starts listening for up to three concurrent connection requests.

2. **Main Loop:**

   - Waits for a client connection (`accept()` → blocking call).
   - Once connected, the server sets a 3-second timeout and waits for data (`recv()`).
   - If data is received, it converts the text to uppercase and sends it back to the client.
   - If no data or timeout occurs, it sends a warning message instead.

3. **Error Handling:**

   - Handles socket-related exceptions such as timeouts, connection resets, or Unicode decoding errors.
   - Supports graceful shutdown via `Ctrl + C` (`KeyboardInterrupt`).

4. **Connection Lifecycle:**

   - Each client request is handled **synchronously**, meaning the server must complete one request–response cycle before moving on to another client.

5. **Summary:**  
   This implementation clearly demonstrates **synchronous, blocking request–response communication**,  
   where the server waits for each client to send, process, and respond before proceeding to the next connection.

---

#### Socket Client Logic (`client.py`)

The socket client is designed to **test and validate** the server’s synchronous communication behavior through multiple controlled scenarios.

**Key Steps:**

1. **Setup:**

   - Retrieves the host and port from environment variables (`APP`, `PORT`) or defaults to `127.0.0.1:8080`.
   - Defines a function `run_test_case()` that handles one complete send–receive cycle.

2. **Connection & Communication:**

   - Establishes a TCP connection using `socket.connect()`.
   - Sends a payload message (`send()`) and waits synchronously for a server response (`recv()`).
   - The client blocks until a response is received, ensuring predictable timing and order.

3. **Error Handling:**

   - Covers common socket-level errors:
     - `ConnectionRefusedError` → server offline or wrong port.
     - `socket.gaierror` → invalid or unresolved hostname.
     - `ConnectionResetError` → server closed the connection unexpectedly.
     - `UnicodeDecodeError` → response not readable as text.
   - Ensures every socket is properly closed within a `finally` block.

4. **Test Scenarios:**  
   The client automatically runs multiple test cases to verify server robustness:

   - Normal message exchange (`"hello server"`)
   - Empty string test (expecting a warning message)
   - Wrong port simulation (`ConnectionRefusedError`)
   - Invalid hostname simulation (`socket.gaierror`)

5. **Summary:**  
   This client script demonstrates **synchronous message exchange and structured error handling**.  
   Each request is blocking — the client waits for the server’s reply before executing the next test — providing a controlled, step-by-step demonstration of synchronous TCP communication.

**Synchronous Characteristics:**

- `accept()` → Blocks until a client connects.
- `recv()` → Blocks until data arrives from the client.
- `send()` → Performs synchronous data transmission (returns only after completion).

**Summary:**  
This implementation clearly exhibits **synchronous, blocking request–response communication**:  
each client must wait for the server to process and reply before proceeding to the next operation.

### 2. REST Implementation (Flask)

**Tech Stack:** Flask

**Overview:**  
The REST implementation demonstrates synchronous HTTP communication. Each REST endpoint (`GET`, `POST`, `PUT`, `DELETE`) blocks the client until the server completes the request and sends back a response.

**Features:**

- Standardized HTTP methods for CRUD operations
- JSON request and response format
- Error handling for invalid input or unsupported media type

**API Interface Design:**

| Method | Path            | Description       |
| ------ | --------------- | ----------------- |
| GET    | /api/users      | Get all users     |
| GET    | /api/users/{id} | Get specific user |
| POST   | /api/users      | Create new user   |
| PUT    | /api/users/{id} | Update user       |
| DELETE | /api/users/{id} | Delete user       |

- CRUD endpoints under `/api/users` for synchronous communication.
- Demonstrates HTTP-based request-response model.

**Briefly Code Example:**

```python
def user_required(f):
    @wraps(f)
    def wrapper(id, *args, **kwargs):
        user = User.findById(int(id))
        if not user:
            return jsonify({"error": "User not found"}), 404
        return f(user, *args, **kwargs)
    return wrapper

@app.before_request
def check_json_header():
    if request.method in ["POST", "PUT"]:
        if request.content_type != "application/json":
            return jsonify({
                "error": "Unsupported Media Type",
                "message": "The server only accepts 'Content-Type: application/json'"
            }), 415

@app.route('/api/users', methods=['GET'])
def get_users():
    users = [user.to_dict() for user in User.getAllUsers()]
    return jsonify(users)

@app.route('/api/users/<id>', methods=['GET'])
@user_required
def get_user(user):
    return jsonify(user.to_dict())

```

**Code Rationale:**

The REST API uses **Flask decorators** to enforce clean, consistent, and reusable validation logic before executing any route handler.

#### 1. `@user_required`

This custom decorator ensures that a user exists before executing user-specific routes such as `GET /api/users/<id>`, `PUT /api/users/<id>`, or `DELETE /api/users/<id>`.  
It retrieves the user object using the provided `id`.

- If the user is **not found**, the request is immediately terminated with a `404` JSON response.
- If found, the user instance is passed into the wrapped function, allowing the main handler to focus only on business logic.

This design prevents repetitive “user not found” checks across multiple endpoints and improves code readability and modularity.

#### 2. `@app.before_request`

This global Flask hook intercepts every incoming request **before it reaches any route handler**.  
It verifies that all `POST` and `PUT` requests use the proper `Content-Type: application/json` header.  
If the header is missing or incorrect, the server responds with a structured `415 Unsupported Media Type` error message.

This approach enforces consistent API behavior, improves robustness, and ensures all clients communicate in a

- All three implementations demonstrate **synchronous request-response behavior**.
- **Sockets** offer low-level control and minimal latency.
- **REST** provides simplicity and interoperability.
- **gRPC** offers the best performance and scalability.
- Docker ensures reproducibility across environments.

**Synchronous Behavior:**  
Each HTTP request (e.g., `POST /api/users`) is processed **sequentially** — the client waits for the server’s JSON response before continuing.

**Summary:**
This REST implementation also demonstrates synchronous, blocking request–response communication.
Each client sends an HTTP request and remains blocked until the Flask server fully processes the request and returns a JSON response.
Only after receiving the response does the client continue its execution, ensuring a clear one-to-one mapping between request and response.

### 3. gRPC Implementation

**Tech Stack:** Python gRPC (`grpcio`, `grpcio-tools`) + Protocol Buffers

**Overview:**  
The gRPC implementation uses strongly typed messages defined in a `.proto` file to handle synchronous RPC calls. The client sends a structured request to the server, which processes and returns a typed response.

**Briefly Code Example:**

```python
# --- Server side ---
class UserService(user_service_pb2_grpc.UserServiceServicer):
    # Implement GetUser
    def GetUser(self, request, context):
        for user in users:
            if user.id == request.id:
                return user
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server is running at port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

# --- Client side ---
def run():
    with grpc.insecure_channel(connect) as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)
        try:
            print("--- 3. CreateUser (SUCCESS) ---")
            new_user = stub.CreateUser(
                user_service_pb2.CreateUserRequest(name="Tan", email="Tan@example.com")
            )
            print("Created User:", new_user)

        except grpc.RpcError as e:
            handle_rpc_error(e, "CreateUser (SUCCESS)")
            print("FATAL: User creation failed. Cannot run further tests.")
            return
if __name__ == "__main__":
    run()
```

**Code Rationale:**

### Server (`server.py`)

This gRPC server implements a **synchronous request–response pattern** using Python’s `grpcio` library.  
It defines a `UserService` class that inherits from the auto-generated `UserServiceServicer` interface, providing concrete implementations for CRUD operations on an in-memory user list.

**Design Rationale:**

1. **Class-based Service Definition:**  
   The `UserService` class encapsulates all CRUD logic, aligning with gRPC’s service-oriented architecture.  
   Each RPC corresponds to a single business operation (`CreateUser`, `GetUser`, `UpdateUser`, `DeleteUser`), promoting modularity and readability.

2. **In-memory Storage:**  
   The global `users` list simulates a lightweight data store, making this implementation self-contained for demonstration purposes.  
   It highlights how gRPC can handle persistent-like operations without external dependencies.

3. **Synchronous Request Handling:**  
   Each incoming gRPC call (e.g., `CreateUser`) is processed sequentially and returns a response before the next call proceeds — ensuring a **synchronous RPC pattern**.  
   While the server supports multiple threads via `ThreadPoolExecutor(max_workers=10)`, each individual RPC remains blocking from the client’s perspective.

4. **Structured Error Handling:**  
   Instead of raising exceptions, the server uses `context.set_code()` and `context.set_details()` to return meaningful gRPC status codes such as:

   - `INVALID_ARGUMENT` → missing or invalid fields
   - `NOT_FOUND` → user ID does not exist  
     This ensures clear communication of errors to clients, aligning with gRPC’s standard error model.

5. **Threaded Server Initialization:**  
   The use of `futures.ThreadPoolExecutor` allows up to 10 concurrent requests, improving throughput while maintaining synchronous semantics at the client level.

6. **Server Lifecycle Management:**

   - `server.add_insecure_port('[::]:50051')` binds to all available interfaces for cross-container communication (e.g., in Docker).
   - `server.wait_for_termination()` keeps the server running indefinitely until manually stopped.

7. **Summary:**
   This server design provides a clean, modular, and synchronous gRPC service implementation — ideal for demonstrating how RPC frameworks can maintain blocking semantics while allowing scalable concurrent request handling.

---

### Client (`client.py`)

The client serves as a **comprehensive test harness** for the gRPC server, verifying both success and failure cases for all CRUD operations.  
It follows a step-by-step approach to illustrate **synchronous communication and error propagation** across the gRPC channel.

**Design Rationale:**

1. **Environment-based Configuration:**  
   The client dynamically determines the target server using the `APP` environment variable (e.g., `grpc-server:50051` in Docker) and defaults to `localhost:50051` for standalone runs.  
   This supports both containerized and local testing environments without code changes.

2. **Synchronous RPC Calls:**  
   Each stub call (e.g., `stub.CreateUser()`) is **blocking** — the client waits until the server finishes processing and returns a response.  
   This ensures deterministic behavior and clear demonstration of synchronous request–response flow.

3. **Structured Error Handling (`handle_rpc_error`):**

   - Centralizes exception handling for all gRPC calls.
   - Prints status codes (e.g., `NOT_FOUND`, `INVALID_ARGUMENT`) and detailed error messages.
   - Mirrors real-world client implementations that need robust fault tolerance.

4. **Comprehensive Test Coverage:**  
   The client simulates both **successful** and **failure** scenarios for each operation:

   - ✅ `CreateUser` success and invalid input test.
   - ✅ `GetUser` success and not-found test.
   - ✅ `UpdateUser` success and invalid ID test.
   - ✅ `DeleteUser` success and redundant deletion test.  
     These cases validate that the server correctly returns appropriate gRPC status codes for each situation.

5. **Graceful Connection Handling:**  
   The use of a context-managed channel (`with grpc.insecure_channel(connect) as channel:`) ensures automatic cleanup of network resources, even if errors occur.

6. **Isolation of Test Logic:**  
   The function `run_test_case()` allows reusable, parameterized testing, keeping the client modular and easy to extend for benchmarking or integration testing.

7. **Summary:**  
   This client implementation effectively demonstrates **synchronous RPC invocation, structured error handling, and end-to-end request–response validation** between a gRPC client and server.  
   It highlights how gRPC can provide **strong type safety, clear error semantics, and reliable synchronous communication** even across distributed systems.

**Synchronous Behavior:**  
Each gRPC call is **blocking** until the server responds or an error occurs. This ensures consistent request–response flow across services.

**Summary:**
This gRPC implementation clearly demonstrates synchronous, blocking request–response communication using remote procedure calls.
Each client call—such as CreateUser or GetUser—is executed synchronously: the client waits until the gRPC server completes the operation and returns a structured response message.
Although each call is blocking at the client level, multiple clients can still communicate with the server concurrently, as gRPC manages concurrent streams efficiently under the hood.

### 4. Benchmark

- `benchmark.py` measures total elapsed time for `N` `CreateUser` requests using both REST and gRPC.
- Reports latency, throughput, and speedup factor.

---

## Instructions

### 1. Build and Start Services

```bash
docker compose up --build
```

This starts:

- REST service → `http://localhost:5000`
- gRPC service → `localhost:50051`
- Socket server → `localhost:8080`

### 2. Testing

#### Run Clients

```bash
docker start grpc-client -> check the results in the docker log
docker compose run --rm socket-client -> check the results in the current terminal
docker start socket-client -> check the results in the docker log
docker compose run --rm grpc-client -> check the results in the current terminal
```

#### Rest API testing

```bash
1. Normal Tests
- Get All Users: curl -X GET http://localhost:5000/api/users
- Create a User: curl -X POST http://localhost:5000/api/users \
     -H "Content-Type: application/json" \
     -d '{"name": "Tan", "email": "tan@example.com"}'
- Get User by ID: curl -X GET http://localhost:5000/api/users/1
- Update a User: curl -X PUT http://localhost:5000/api/users/1 \
     -H "Content-Type: application/json" \
     -d '{"email": "updated@example.com"}'
- Delete a User: curl -X DELETE http://localhost:5000/api/users/1

2. Error Handling Tests
- Missing JSON Header: curl -X POST http://localhost:5000/api/users \
     -d '{"name": "Tan", "email": "tan@example.com"}'

- Invalid Body: curl -X POST http://localhost:5000/api/users \
     -H "Content-Type: application/json" \
     -d '{"name": ""}'
- User not found: curl -X DELETE http://localhost:5000/api/users/3345678
```

### 3. Run Benchmark

```bash
docker compose run --rm benchmark -> check the results in the docker log
docker start benchmark -> check the results in the current terminal
```

---

## Test Results

### Socket

```
--- 1. Normal Message ---
SUCCESS: Connection established to socket-server:8080
Sending: hello server
Server response: HELLO SERVER

socket-server | Received: hello server

--- 2. Empty String ---
SUCCESS: Connection established to socket-server:8080
Client: ''
Server Response: "You didn't send any data or sent an empty string"

socket-server | WARNING: Client ('172.18.0.6', 51580) timed out waiting for data.

--- 3. Wrong Port (simulate ConnectionRefused) ---
SOCKET ERROR: Connection refused at socket-server:9999 (server down or port incorrect).

--- 4. Bad Hostname (simulate gaierror) ---
SOCKET ERROR: Hostname resolution failed for 'no_such_host'.

```

### REST API

```
curl -X POST http://localhost:5000/api/users \
     -H "Content-Type: application/json" \
     -d '{"name": "Tan", "email": "tan@example.com"}'

response: {
  "email": "tan@example.com",
  "id": 101,
  "name": "Tan"
}

curl -X PUT http://localhost:5000/api/users/2 \
     -H "Content-Type: application/json" \
     -d '{"email": "updated@example.com"}'

response: {
  "message": "The user data has updated"
}

curl -X GET http://localhost:5000/api/users/2

response: {
  "email": "updated@example.com",
  "id": 2,
  "name": "user1"
}

curl -X POST http://localhost:5000/api/users \
     -d '{"name": "Tan", "email": "tan@example.com"}'

response: { "error": "Unsupported Media Type", "message": "The server only accepts 'Content-Type: application/json'" }

curl -X POST http://localhost:5000/api/users \
     -H "Content-Type: application/json" \
     -d '{"name": ""}'
response: { "error": "Invalid data" }

curl -X DELETE http://localhost:5000/api/users/3345678
response: { "error": "User not found" }
```

### gRPC

```
Attempting to connect to gRPC server at: grpc-server:50051

--- 1. CreateUser (SUCCESS) ---
Created User: id: "1"
name: "Tan"
email: "Tan@example.com"

--- 1b. CreateUser (ERROR: Missing Name) ---
SUCCESS: Server correctly returned INVALID_ARGUMENT for missing data.
RPC failed at CreateUser (ERROR)
Code: StatusCode.INVALID_ARGUMENT
Details: Name and email are required

--- 2. GetUser (SUCCESS) ---
Fetched User: id: "1"
name: "Tan"
email: "Tan@example.com"

--- 2b. GetUser (ERROR: Not Found) ---
SUCCESS: Server correctly returned NOT_FOUND for non-existent ID.
RPC failed at GetUser (ERROR)
Code: StatusCode.NOT_FOUND
Details: User not found

--- 3. UpdateUser (SUCCESS) ---
Updated User: id: "1"
name: "Hsuan-Yu Tan"
email: "Tan@new.com"

--- 3b. UpdateUser (ERROR: Not Found) ---
SUCCESS: Server correctly returned NOT_FOUND when updating non-existent user.
RPC failed at UpdateUser (ERROR)
Code: StatusCode.NOT_FOUND
Details: User not found

--- 4. DeleteUser (SUCCESS) ---
User deleted

--- 4b. DeleteUser (ERROR: Not Found) ---
SUCCESS: Server correctly returned NOT_FOUND when deleting an already deleted user.
RPC failed at DeleteUser (ERROR)
Code: StatusCode.NOT_FOUND
Details: User not found
```

---

## Performance Comparison

The example benchmark output:

```
=== REST vs gRPC Benchmark ===
Running 100 CreateUser calls for both REST and gRPC...
This test will measure total elapsed time for each approach.

REST Results:
  Average response time: 2.74 ms
  Min: 1.24 ms
  Max: 7.89 ms
  Standard deviation: 1.45 ms
  Total time: 273.91 ms
  Throughput: 365.1 requests/sec
  Errors: 0

gRPC Results:
  Average response time: 0.41 ms
  Min: 0.21 ms
  Max: 11.56 ms
  Standard deviation: 1.13 ms
  Total time: 40.59 ms
  Throughput: ~2464.0 requests/sec
  Errors: 0

REST 100 calls took: 273.9055 ms
gRPC 100 calls took: 40.5905 ms
gRPC is 6.75x faster than REST

---

### Performance Analysis

The benchmark results demonstrate a clear performance advantage of gRPC over REST in this synchronous communication test.
Although both approaches follow a blocking request–response pattern, their underlying protocols differ significantly:

REST uses HTTP/1.1 with human-readable JSON payloads.
This introduces additional overhead from header parsing, serialization, and text-based data formatting.

gRPC, on the other hand, is built on HTTP/2 and uses Protocol Buffers (binary serialization), which are more compact and efficient to encode and decode.

As a result:

The average response time for gRPC requests was approximately 0.41 ms, compared to 2.74 ms for REST — a 6.75× performance improvement.

The standard deviation is also lower in gRPC, indicating more stable and predictable response times.

Both implementations completed the same workload with zero errors, confirming functional correctness and consistency.

In summary, while REST offers simplicity and broader compatibility, gRPC delivers significantly better performance and lower latency, making it a preferred choice for high-throughput or real-time microservice communication.

---

## Conclusion

- All three implementations demonstrate **synchronous request-response behavior**.
- **Sockets** offer low-level control and minimal latency.
- **REST** provides simplicity and interoperability.
- **gRPC** offers the best performance and scalability.
- Docker ensures reproducibility across environments.

---

## References

- Python `socket` — https://docs.python.org/3/library/socket.html
- Flask — https://flask.palletsprojects.com/
- gRPC — https://grpc.io/docs/languages/python/quickstart/
- Docker Compose — https://docs.docker.com/compose/
```
