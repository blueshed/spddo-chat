from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from tornado.concurrent import DummyExecutor
from faker import Factory
import pytest
from spddo.subs.actions.context import Context
from spddo.subs.actions.save_user import save_user
from spddo.subs.actions.save_group import save_group
from spddo.subs.actions.save_service import save_service
from blueshed.micro.orm import db_connection
from blueshed.micro.utils.utils import url_to_cors
from tornado import gen
from random import randint
from spddo.subs.actions.subscribe import subscribe
from spddo.subs.actions.make_payment import make_payment


def run_in_pool(method, context, *args, **kwargs):
    result = method(context, *args, **kwargs)
    return context, result


@pytest.fixture(scope="module")
def pool():
    db_connection.db_init("mysql+pymysql://root:root@localhost:8889/subs")
#     return DummyExecutor()
#     return ThreadPoolExecutor(4)
    return ProcessPoolExecutor(4)


@pytest.mark.gen_test(timeout=20)
def test_save(pool):
    fake = Factory.create()
    context = Context(-1, -1, None)
    users = yield gen.multi([
        pool.submit(run_in_pool,
                    save_user,
                    context=context,
                    name=fake.name(),
                    email=fake.email(),
                    password=fake.password()) for _ in range(1000)])
    groups = yield gen.multi([
        pool.submit(run_in_pool,
                    save_group,
                    context=context,
                    name=fake.company()) for _ in range(100)])

    jobs = []
    for _ in range(5):
        uri = fake.uri()
        cors = url_to_cors(uri)
        jobs.append(pool.submit(run_in_pool,
                                save_service,
                                context=context,
                                name=fake.ssn(),
                                description=fake.text(),
                                cost=fake.pyfloat(positive=True),
                                duration=randint(28, 365),
                                token_url=uri,
                                cors=cors))
    services = yield gen.multi(jobs)
    jobs = []
    for _, user in users:
        _, group = groups[randint(0, len(groups) - 1)]
        _, service = services[randint(0, len(services) - 1)]
        jobs.append(pool.submit(run_in_pool,
                                subscribe,
                                context=context,
                                user_id=user.get("id"),
                                group_id=group.get("id"),
                                service_id=service.get("id")))
    yield gen.multi(jobs)

    jobs = []
    for _, group in groups:
        jobs.append(pool.submit(run_in_pool,
                                make_payment,
                                context=context,
                                group_id=group.get("id")))

    yield gen.multi(jobs)

#     for broadcast in context.broadcasts:
#         print(broadcast)
#     assert False
