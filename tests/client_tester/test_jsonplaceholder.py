import pandas as pd
import pytest
import requests


class JsonPlaceHolderClient():
    baseurl = "https://jsonplaceholder.typicode.com{route}"

    def __init__(self, session=None):
        if not session:
            session = requests.Session()
        self.session = session

    def _format_url(self, route):
        return self.baseurl.format(route=route)

    def get_todos(self, n=None):
        if n:
            route = "/todos/{}".format(n)
        else:
            route = "/todos"

        resp = self.session.get(url=self._format_url(route))
        df = pd.DataFrame(resp.json())
        return df


CL = JsonPlaceHolderClient()


def test_get_todos(vcrpandas):
    with vcrpandas("random_bucket_name") as recorder:
        recorder(CL.get_todos())


@pytest.fixture
def vcrpandas_otherpath(vcrpandas):
    vcrpandas.config.update({
        'cassette_library_dir': 'fixtures/myclient/cassettes',
    })
    return vcrpandas


def test_otherpath_get_todos(vcrpandas_otherpath):
    with vcrpandas_otherpath("random_bucket_name") as recorder:
        recorder(CL.get_todos())
