import json
import os

import pytest

from treeherder.etl.bugzilla import BzApiBugProcess
from treeherder.model.models import Bugscache


@pytest.fixture
def mock_bugzilla_api_request(monkeypatch):
    """Mock etl.common.fetch_json() to return a local sample file."""
    from treeherder.etl import common

    def _fetch_json(url, params=None):
        tests_folder = os.path.dirname(os.path.dirname(__file__))
        bug_list_path = os.path.join(
            tests_folder,
            "sample_data",
            "bug_list.json"
        )
        with open(bug_list_path) as f:
            return json.loads(f.read())

    monkeypatch.setattr(common,
                        'fetch_json',
                        _fetch_json)

    # TODO: Replace with responses


@pytest.mark.django_db(transaction=True)
def test_bz_api_process(mock_bugzilla_api_request):
    process = BzApiBugProcess()
    process.run()

    # the number of rows inserted should equal to the number of bugs
    assert Bugscache.objects.count() == 15

    # test that a second ingestion of the same bugs doesn't insert new rows
    process.run()
    assert Bugscache.objects.count() == 15
