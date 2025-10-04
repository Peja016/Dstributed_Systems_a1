class User:
    __userList = []
    def __init__(self, name, email):
        if User.__userList:  # check if the user list is empty
            last_id = User.__userList[-1].id
        else:
            last_id = 0
        self.__id = last_id + 1
        self.name = name
        self.email = email
        User.__userList.append(self)
    def __repr__(self):
        return f"id={self.__id}, name={self.name}, email={self.email}"
    @classmethod
    def getAllUsers(cls):
        return list(cls.__userList)
    @property
    def id(self):
        return self.__id
    @classmethod
    def findById(cls, user_id):
        for u in cls.__userList:
            if u.id == user_id:
                return u
        return None
    def delete(self):
        User.__userList.remove(self)
    
    def update_user(self, name=None, email=None):
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
    
    def to_dict(self):
        return {
            "id": self.__id,
            "name": self.name,
            "email": self.email
        }
    
    