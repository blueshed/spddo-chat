from spddo.todo import model
from sqlalchemy.sql.expression import and_
from spddo.todo.actions.views import todo_view


def filter_todos(context: 'micro_context',
                 term: str='', offset: int=0, limit: int=10) -> list:
    '''
        filters the todos by term on description
        returns: [{
            id: int,
            person_id: int,
            description: str,
            created: datetime,
            done: datetime
        }]
    '''
    with context.session as session:
        user = context.get_user(session)
        assert user, 'login required'

        term = "{}%".format(term)
        items = session.query(model.ToDo).\
            filter(and_(model.ToDo.description.like(term),
                        model.ToDo.person == user)).\
            offset(offset).\
            limit(limit)

        return [todo_view(item) for item in items]
