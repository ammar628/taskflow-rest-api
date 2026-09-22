from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum


class ResponseBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# start project validation class
class CreateProject(BaseModel):
    title:str
    description:str | None = None

class UpdateProject(BaseModel):
    title:str | None = None
    description: str | None = None


class ResponseProject(ResponseBase):
    id:int
    title:str
    description:str | None
# end project validation class

# start task validation class
class StatusEnum(Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class CreateTask(BaseModel):
    title:str
    description:str | None = None
    status:StatusEnum = StatusEnum.todo


class UpdateTask(BaseModel):
    title:str | None = None
    description:str | None = None
    status:StatusEnum | None = None


class ResponseTask(ResponseBase):
    id:int
    title:str
    description:str | None
    status:StatusEnum
# end task validation class

# start user validation class
class RegisterUser(BaseModel):
    username:str
    email:EmailStr
    password:str

class RolesUser(Enum):
    User = "user"
    Admin = "admin"

class ResponseUser(ResponseBase):
    id:int
    username:str
    email:EmailStr
    role:RolesUser
# end user validation class

