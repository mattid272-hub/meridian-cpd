"""The files in this folder are stand-alone scripts (python3 tests/test_x.py): each one sets
its environment, imports the app, patches it in place and asserts as it goes. This file
lets `python -m pytest -q` (from the webhook folder) run them as well: every script is
collected as one test, and before each one runs the app modules are forgotten, the
environment is put back as it was and the stand-ins the scripts put on the shared httpx
and stripe modules are undone, so the scripts stay independent of each other."""
import os
import runpy
import sys

import httpx
import pytest
import stripe

_APP_MODULES = ("main", "email_sender", "outreach", "news", "settings", "certificate_generator")
_ENV = dict(os.environ)
# Attributes the scripts replace on shared third-party modules, with their originals.
_SHARED = {
    (httpx, "AsyncClient"): httpx.AsyncClient,
    (stripe.Webhook, "construct_event"): stripe.Webhook.__dict__["construct_event"],
    (stripe.Subscription, "list"): stripe.Subscription.__dict__["list"],
    (stripe.Subscription, "retrieve"): stripe.Subscription.__dict__["retrieve"],
    (stripe.Customer, "list"): stripe.Customer.__dict__["list"],
    (stripe.Customer, "retrieve"): stripe.Customer.__dict__["retrieve"],
    (stripe.Customer, "modify"): stripe.Customer.__dict__["modify"],
    (stripe.billing_portal.Session, "create"): stripe.billing_portal.Session.__dict__["create"],
    (stripe.checkout.Session, "retrieve"): stripe.checkout.Session.__dict__["retrieve"],
    (stripe.checkout.Session, "list_line_items"): stripe.checkout.Session.__dict__["list_line_items"],
}


def _isolate() -> None:
    os.environ.clear()
    os.environ.update(_ENV)
    for (owner, attr), original in _SHARED.items():
        setattr(owner, attr, original)
    for name in _APP_MODULES:
        sys.modules.pop(name, None)


class ScriptItem(pytest.Item):
    def runtest(self):
        _isolate()
        runpy.run_path(str(self.path), run_name="pytest")

    def reportinfo(self):
        return self.path, 0, self.name


class ScriptFile(pytest.File):
    def collect(self):
        yield ScriptItem.from_parent(self, name=self.path.stem)


class _NotAModule(pytest.Module):
    """Stands in for pytest's own module collector so a script named on the command line
    is not imported a second time at collection."""
    def collect(self):
        return []


def pytest_collect_file(parent, file_path):
    if file_path.suffix == ".py" and file_path.name.startswith("test_"):
        return ScriptFile.from_parent(parent, path=file_path)
    return None


def pytest_pycollect_makemodule(module_path, parent):
    return _NotAModule.from_parent(parent, path=module_path)
