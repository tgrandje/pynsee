# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 15:54:21 2023

@author: thomas.grandjean
"""

from requests_cache import CachedSession
import logging

logger = logging.getLogger(__name__)


def mock_pool(*args, **kwargs):
    class MockedPool:
        def __init__(
            self,
            processes=None,
            initializer=None,
            initargs=(),
            maxtasksperchild=None,
        ):
            self.initializer = initializer
            self.initargs = initargs

        def imap(self, func, iterable, chunksize=1):
            for args in iterable:
                if self.initializer:
                    self.initializer(*self.initargs)
                yield func(args)

        def __enter__(self, *args, **kwargs):
            return self

        def __exit__(self, *args, **kwargs):
            pass

    return MockedPool(*args, **kwargs)


class MockedSession(CachedSession):
    def __init__(self, *args, **kwargs):
        super().__init__(
            cache_name="pynsee-testing-cache",
            expire_after=3600 * 24 * 15,
            ignored_parameters=("Authorization", "access_token"),
            filter_fn=lambda session: "api.insee.fr/token" not in session.url,
            *args,
            **kwargs,
        )

    def get(self, *args, **kwargs):
        r = super().get(*args, **kwargs)
        print(f"{args[0]}, code={r.status_code}, from_cache={r.from_cache}")
        return r

    def post(self, *args, **kwargs):
        r = super().post(*args, **kwargs)
        print(f"{args[0]}, code={r.status_code}, from_cache={r.from_cache}")
        return r


def mock_requests_session(*args, **kwargs):
    return MockedSession(*args, **kwargs)


def mock_requests_get(*args, **kwargs):
    s = MockedSession()
    return s.get(*args, **kwargs)


def mock_requests_post(*args, **kwargs):
    s = MockedSession()
    return s.post(*args, **kwargs)
