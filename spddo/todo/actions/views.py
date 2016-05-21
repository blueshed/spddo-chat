

def todo_view(todo):
    return {
        "id": todo.id,
        "description": todo.description,
        "created": todo.created,
        "done": todo.done
    }


def user_view(user):
    return {
        "id": user.id,
        "email": user.email
    }
