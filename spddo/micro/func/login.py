from pkg_resources import resource_filename  # @UnresolvedImport
from spddo.micro.func import model
from tornado.web import HTTPError
from blueshed.micro.utils import generate_templates
from blueshed.micro.mail.send_grid import send
import logging
from sqlalchemy.exc import IntegrityError


def login(context: 'micro-context', email: str, password: str) -> dict:
    ''' returns a user object on success '''
    with context.session as session:
        person = session.query(model.Person).\
            filter(model.Person.email == email,
                   model.Person.password == password).\
            first()
        if person is None:
            raise HTTPError(
                401,
                reason="<strong>Failed</strong> Email or password incorrect!")
        user = {
            "id": person.id,
            "email": person.email
        }
        context.set_cookie("current_user", user)
        return user


def forgotten_password(context: 'micro-context', email: str) -> dict:
    ''' emails your password to you '''
    with context.session as session:
        person = session.query(model.Person).filter_by(email=email).first()
        if person is None:
            raise HTTPError(
                400,
                reason="<strong>Failed</strong> Email not registered!")

        template_path = resource_filename('spddo.micro', "templates/email")
        html, body = generate_templates.generate(template_path,
                                                 "forgotten.html",
                                                 "forgotten.txt",
                                                 email=person.email,
                                                 password=person.password)
        result = send(person.email, "info@spddo.co.uk",
                      "welcome to spddo-chat", body, html)
        logging.info(result)
        return "email sent."


def register(context: 'micro-context', email: str, password: str) -> dict:
    ''' register your email and password to be able to login '''
    with context.session as session:
        try:
            person = model.Person(email=email, password=password)
            session.add(person)
            session.commit()
        except IntegrityError:
            raise HTTPError(
                400,
                reason="<strong>Failed</strong> Email already registered!")

        template_path = resource_filename('spddo.micro', "templates/email")
        html, body = generate_templates.generate(template_path,
                                                 "registered.html",
                                                 "registered.txt",
                                                 email=person.email,
                                                 password=person.password)
        result = send(person.email, "info@spddo.co.uk",
                      "welcome to spddo-chat", body, html)
        logging.info(result)
        return "an email has been sent to that address with your password."
