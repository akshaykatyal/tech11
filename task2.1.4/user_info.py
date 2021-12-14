# This python file is for the storing the user data to the database
from flask_login import UserMixin

from data_db import user_get

# class for storing the user data
class Google_User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        # getting the id, name, email, and profile picture of the user login
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def user_get(user_id):
        # retrieving data from database
        db = user_get()
        # retrieving record from the user database
        user = db.execute(
            "SELECT * FROM user WHERE id = ?",(user_id,)
        ).fetchone()
        if not user:
            return None

        # storing the data in the variable using the Google user class
        user = Google_User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create_user(id_, name, email, profile_pic):
        # this is to store a new record in the database
        db = user_get()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, profile_pic),
        )
        db.commit()