from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


"""
In our service when we did "todo = Todo(**new_todo.model_dump(), owner=user)"
it automatically sets the owner_id field to user.id
because of the foreign key relationship defined in the Todo model.

"owner: "User" = Relationship(back_populates="todos")" here:

- owner: "User": this means owner is a relationship field that refers to the User model, and when we do todo.owner it will return the associated User object.

- Relationship(back_populates="todos"): this means that the User model should have a field called "todos" that will hold the list of Todo objects associated with that user.

This is how SQLModel establishes a bidirectional relationship between the Todo and User models.

in our db though there are to "todos" and "owner" column because as when we try to access these, suppose we want to access user.todos then sqlmodel automatically knows that it should query the Todo table for all todos where owner_id matches the user's id(query will look something like: "SELECT * FROM todo WHERE owner_id = user.id").
"""


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="todos")
