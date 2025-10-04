import grpc
from concurrent import futures

from generated import user_service_pb2, user_service_pb2_grpc 

users = []

class UserService(user_service_pb2_grpc.UserServiceServicer):
    # Implement GetUser
    def GetUser(self, request, context):
        for user in users:
            if user.id == request.id:
                return user
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return
    
    def CreateUser(self, request, context):
        if not request.name or not request.email:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Name and email are required")
            return
        
        new_user = user_service_pb2.User(
            id=str(len(users) + 1),
            name=request.name,
            email=request.email
        )

        users.append(new_user)

        return new_user
    
    def UpdateUser(self, request, context):
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Id are required")
            return
        for user in users:
            if user.id == request.id:
                if request.name:
                    user.name = request.name
                if request.email:
                    user.email = request.email
                return user
        
        #If not found
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return
    
    def DeleteUser(self, request, context):
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Id are required")
            return
        for user in users:
            if user.id == request.id:
                users.remove(user)
                return user_service_pb2.Empty()
        
        #If not found
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server is running at port 50051")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected — shutting down gracefully...")
        server.stop(0)  # terminate running
        print("gRPC server stopped.")

if __name__ == "__main__":
    serve()