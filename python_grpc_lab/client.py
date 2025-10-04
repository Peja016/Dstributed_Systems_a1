import grpc, os
from generated import user_service_pb2, user_service_pb2_grpc 
from typing import Optional

def handle_rpc_error(e: grpc.RpcError, context: str = ""):
    """
    Handles gRPC errors by printing the error code and details.
    This demonstrates the client's ability to catch server-side failures.
    """
    print(f"RPC failed at {context}" if context else "RPC failed")
    print("Code:", e.code())
    print("Details:", e.details(), "\n")

def run():
    # Retrieve connection string from environment variable (e.g., for Docker Compose)
    # If using Docker Compose, 'APP' should be set to 'grpc-server:50051'
    connect = os.getenv("APP")
    if not connect:
        # Fallback to localhost for direct execution outside of Docker
        connect = "localhost:50051"
    
    # Initialize new_user outside the try block to prevent UnboundLocalError 
    # if the first CreateUser call fails.
    new_user = None
    
    print(f"Attempting to connect to gRPC server at: {connect}\n")
    
    try:
        with grpc.insecure_channel(connect) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)

            # ----------------------------------------------------------------------
            # 1. CreateUser SUCCESS Case (Necessary for subsequent tests)
            # ----------------------------------------------------------------------
            try:
                print("--- 1. CreateUser (SUCCESS) ---")
                new_user = stub.CreateUser(
                    user_service_pb2.CreateUserRequest(name="Tan", email="Tan@example.com")
                )
                print("Created User:", new_user)

            except grpc.RpcError as e:
                handle_rpc_error(e, "CreateUser (SUCCESS)")
                print("FATAL: User creation failed. Cannot run further tests.")
                return # Exit if we cannot create the initial user

            # 1b. CreateUser ERROR Case (INVALID_ARGUMENT)
            # Test: Send a request with a missing required field (e.g., empty name/email)
            try:
                print("\n--- 1b. CreateUser (ERROR: Missing Name) ---")
                stub.CreateUser(
                    user_service_pb2.CreateUserRequest(name="", email="fail@example.com")
                )
                print("ERROR: Expected INVALID_ARGUMENT but call succeeded.")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                    print("SUCCESS: Server correctly returned INVALID_ARGUMENT for missing data.")
                handle_rpc_error(e, "CreateUser (ERROR)")


            # ----------------------------------------------------------------------
            # 2. GetUser SUCCESS Case
            # ----------------------------------------------------------------------
            try:
                print("\n--- 2. GetUser (SUCCESS) ---")
                user = stub.GetUser(user_service_pb2.UserRequest(id=new_user.id))
                print("Fetched User:", user)       

            except grpc.RpcError as e:
                handle_rpc_error(e, "GetUser (SUCCESS)")
                
            # 2b. GetUser ERROR Case (NOT_FOUND)
            # Test: Request a user ID that does not exist in the server's list.
            try:
                print("\n--- 2b. GetUser (ERROR: Not Found) ---")
                stub.GetUser(user_service_pb2.UserRequest(id="9999")) # Known non-existent ID
                print("ERROR: Expected NOT_FOUND but call succeeded.")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    print("SUCCESS: Server correctly returned NOT_FOUND for non-existent ID.")
                handle_rpc_error(e, "GetUser (ERROR)")


            # ----------------------------------------------------------------------
            # 3. UpdateUser SUCCESS Case
            # ----------------------------------------------------------------------
            try:
                print("\n--- 3. UpdateUser (SUCCESS) ---")
                updated_user = stub.UpdateUser(
                    user_service_pb2.UpdateUserRequest(id=new_user.id, name="Hsuan-Yu Tan", email="Tan@new.com")
                )
                print("Updated User:", updated_user)
            except grpc.RpcError as e:
                handle_rpc_error(e, "UpdateUser (SUCCESS)")
                
            # 3b. UpdateUser ERROR Case (NOT_FOUND)
            # Test: Attempt to update a user with a non-existent ID.
            try:
                print("\n--- 3b. UpdateUser (ERROR: Not Found) ---")
                stub.UpdateUser(
                    user_service_pb2.UpdateUserRequest(id="9999", name="Fail Name") 
                )
                print("ERROR: Expected NOT_FOUND but call succeeded.")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    print("SUCCESS: Server correctly returned NOT_FOUND when updating non-existent user.")
                handle_rpc_error(e, "UpdateUser (ERROR)")


            # ----------------------------------------------------------------------
            # 4. DeleteUser SUCCESS Case
            # ----------------------------------------------------------------------
            try:
                print("\n--- 4. DeleteUser (SUCCESS) ---")
                # Deleting the user created in step 3
                stub.DeleteUser(user_service_pb2.UserRequest(id=new_user.id)) 
                print("User deleted")
            except grpc.RpcError as e:
                handle_rpc_error(e, "DeleteUser (SUCCESS)")
                
            # 4b. DeleteUser ERROR Case (NOT_FOUND)
            # Test: Attempt to delete the same user again (which should now be gone).
            try:
                print("\n--- 4b. DeleteUser (ERROR: Not Found) ---")
                stub.DeleteUser(user_service_pb2.UserRequest(id=new_user.id))
                print("ERROR: Expected NOT_FOUND but call succeeded.")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    print("SUCCESS: Server correctly returned NOT_FOUND when deleting an already deleted user.")
                handle_rpc_error(e, "DeleteUser (ERROR)")

    except Exception as e:
        # Catch connection errors (e.g., if the server is not running)
        print(f"\nFATAL CONNECTION ERROR: {e}")
        print("Please ensure your gRPC server is running and the connection string is correct.")

if __name__ == "__main__":
    run()