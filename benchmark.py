import time
import statistics
import requests
import grpc
import os

from python_grpc_lab.generated import user_service_pb2, user_service_pb2_grpc

import statistics

# Read host from environment variable, fallback to localhost
REST_HOST = os.getenv("REST_HOST", "localhost")
GRPC_HOST = os.getenv("GRPC_HOST", "localhost")

REST_URL = f"http://{REST_HOST}:5000/api/users"
GRPC_TARGET = f"{GRPC_HOST}:50051"

# Number of requests to send for benchmarking
N = 100 

def summarize_results(label, times, errors=0):
    """
    Summarize and print benchmark results.

    Args:
        label (str): A label for the test, e.g. "REST" or "gRPC".
        times (list): A list of response times (in milliseconds).
        errors (int): Number of failed requests.

    Returns:
        float: The average response time (ms), or None if no data.
    """
    if not times:
        print(f"\n{label} Results: No data")
        return None

    # Compute descriptive statistics
    avg_time = statistics.mean(times)   # average response time
    min_time = min(times)               # fastest response
    max_time = max(times)               # slowest response
    std_dev = statistics.stdev(times) if len(times) > 1 else 0  # variability
    total_time = sum(times)             # total time for all requests

    # Print results in a nice format
    print(f"\n{label} Results:")
    print(f"  Average response time: {avg_time:.2f} ms")
    print(f"  Min: {min_time:.2f} ms")
    print(f"  Max: {max_time:.2f} ms")
    print(f"  Standard deviation: {std_dev:.2f} ms")
    print(f"  Total time: {total_time:.2f} ms")
    print(f"  Throughput: {(N / total_time) * 1000:.2f} requests/sec")
    print(f"  Errors: {errors}")

    return total_time 

def benchmark_rest():
    """
    Benchmark REST API by sending N POST requests to /api/users.
    Records individual response times and errors for analysis.
    """
    times = []   # store each request's response time (ms)
    errors = 0   # count failed requests

    for i in range(N):
        start = time.time()  # start timer for this request
        try:
            # Send a POST request to create a new user
            resp = requests.post(
                REST_URL,
                json={"name": f"user{i}", "email": f"user{i}@example.com"}
            )
            resp.raise_for_status()  # raise error if status_code != 200
        except Exception:
            errors += 1
        end = time.time()  # stop timer

        # Convert seconds to milliseconds and store
        times.append((end - start) * 1000)

    # Summarize statistics for REST benchmark
    return summarize_results("REST", times, errors)


def benchmark_grpc():
    """
    Benchmark gRPC API by sending N CreateUser RPC calls.
    Records individual response times and errors for analysis.
    """
    times = []   # store each RPC's response time (ms)
    errors = 0   # count failed calls

    # Create a gRPC channel and stub (client proxy)
    channel = grpc.insecure_channel(GRPC_TARGET)
    stub = user_service_pb2_grpc.UserServiceStub(channel)

    for i in range(N):
        start = time.time()  # start timer for this call
        try:
            # Call gRPC CreateUser RPC with test data
            stub.CreateUser(
                user_service_pb2.CreateUserRequest(
                    name=f"user{i}",
                    email=f"user{i}@example.com"
                )
            )
        except Exception:
            errors += 1
        end = time.time()  # stop timer

        # Convert seconds to milliseconds and store
        times.append((end - start) * 1000)

    # Summarize statistics for gRPC benchmark
    return summarize_results("gRPC", times, errors)


if __name__ == "__main__":
    print("=== REST vs gRPC Benchmark ===")
    print(f"Running {N} CreateUser calls for both REST and gRPC...")
    print("This test will measure total elapsed time for each approach.\n")
    # Run benchmarks
    rest_time = benchmark_rest()
    grpc_time = benchmark_grpc()

    # Print results
    print(f"REST {N} calls took: {rest_time:.4f} ms")
    print(f"gRPC {N} calls took: {grpc_time:.4f} ms")

    if grpc_time < rest_time:
        # gRPC is faster
        print(f"gRPC is {(rest_time/grpc_time):.2f}x faster than REST")
    elif rest_time < grpc_time:
        # REST is faster
        print(f"REST is {(grpc_time/rest_time):.2f}x faster than gRPC")
    else:
        # Tie (very rare, but safe to handle)
        print("REST and gRPC took the same time")
