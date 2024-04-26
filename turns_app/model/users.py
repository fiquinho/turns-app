from dataclasses import dataclass

from turns_app.utils.dataclass_utils import BaseDataclass


@dataclass
class NamedUser(BaseDataclass):
    id: str
    name: str


# TODO: Validate the email and phone fields
@dataclass
class User(NamedUser):
    email: str
    phone: str
    activity: str

    def get_named_user(self) -> NamedUser:
        return NamedUser(self.id, self.name)


class UserExistsError(Exception):
    pass


class MongoUsersManager:
    def __init__(self, mongo_config):
        self.mongo_config = mongo_config
        self.collection = self.mongo_config.db.users

    def get_by_id(self, user_id: str) -> User | None:
        user_dict = self.collection.find_one({"id": user_id})
        return User.from_dict(user_dict) if user_dict else None

    def get_users(self) -> list[User]:
        return [User.from_dict(user) for user in self.collection.find()]

    def create_user(self, user: User) -> None:
        if self.get_by_id(user.id):
            raise UserExistsError(f"The user with idx {user.id} already exists")

        self.collection.insert_one(user.to_dict())
