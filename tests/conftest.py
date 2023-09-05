# -*- coding: utf-8 -*-


def pytest_sessionstart(session):
    "Restore cached tests' web interactions from MinIO"
    try:
        # TODO : download
        pass
    except Exception:
        pass


def pytest_sessionfinish(session, exitstatus):
    "Store cached tests' web interactions on MinIO"
    try:
        # TODO : upload
        pass
    except Exception:
        pass
