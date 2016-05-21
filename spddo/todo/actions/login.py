from pkg_resources import resource_filename  # @UnresolvedImport
from spddo.todo import model
from tornado.web import HTTPError
from blueshed.micro.utils import generate_templates
from blueshed.micro.mail.send_grid import send
import logging
from sqlalchemy.exc import IntegrityError
from spddo.todo.actions.views import user_view


def login(context: 'micro_context', email: str, password: str) -> dict:
    '''
        returns a user object on success
        broadcasts: MICRO_COOKIE_SET
    '''
    with context.session as session:
        user = session.query(model.User).\
            filter(model.User.email == email,
                   model.User.password == password).\
            first()
        if user is None:
            raise HTTPError(
                401,
                reason="<strong>Failed</strong> Email or password incorrect!")
        user = user_view(user)
        context.set_cookie("current_user", user)
        return user


def forgotten_password(context: 'micro_context', email: str) -> dict:
    '''
        emails your password to you
    '''
    with context.session as session:
        User = session.query(model.User).filter_by(email=email).first()
        if User is None:
            raise HTTPError(
                400,
                reason="<strong>Failed</strong> Email not registered!")

        template_path = resource_filename('spddo.micro', "templates/email")
        html, body = generate_templates.generate(template_path,
                                                 "forgotten.html",
                                                 "forgotten.txt",
                                                 email=User.email,
                                                 password=User.password)
        result = send(User.email, "info@spddo.co.uk",
                      "welcome to spddo-chat", body, html)
        logging.info(result)
        return "email sent."


def register(context: 'micro_context', email: str, password: str) -> dict:
    '''
        register your email and password to be able to login
    '''
    with context.session as session:
        try:
            User = model.User(email=email, password=password)
            session.add(User)
            session.commit()
        except IntegrityError:
            raise HTTPError(
                400,
                reason="<strong>Failed</strong> Email already registered!")

        template_path = resource_filename('spddo.micro', "templates/email")
        html, body = generate_templates.generate(template_path,
                                                 "registered.html",
                                                 "registered.txt",
                                                 email=User.email,
                                                 password=User.password)
        result = send(User.email, "info@spddo.co.uk",
                      "welcome to spddo-chat", body, html)
        logging.info(result)
        return "an email has been sent to that address with your password."
