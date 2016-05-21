from blueshed.micro.utils.date_utils import parse_date
from spddo.todo.actions.views import todo_view
from spddo.todo import model
import datetime


def save_todo(context: 'micro_context',
              description: str,
              done: datetime=None,
              todo_id: int=None) -> dict:
    '''
        creates or updates a todo
        broadcasts: SAVED_TODO
        returns: {
            id: int,
            person_id: int,
            description: str,
            created: datetime,
            done: datetime
        }
    '''
    with context.session as session:
        user = context.get_user(session)
        assert user, 'login required'
        if todo_id:
            todo = session.query(model.ToDo).get(todo_id)
        else:
            todo = model.ToDo(person=user,
                              created=datetime.datetime.now())
            session.add(todo)
        todo.description = description
        todo.done = parse_date(done)
        session.commit()
        return context.broadcast("SAVED_TODO",
                                 todo_view(todo))
