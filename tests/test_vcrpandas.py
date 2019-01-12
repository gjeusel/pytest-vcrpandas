from pathlib import Path
import pytest

# Check that the plugin has been properly installed before proceeding
assert pytest.config.pluginmanager.hasplugin("vcrpandas")


def test_jsonplaceholder_get_todos(testdir):
    testdir.copy_example("client_tester/test_jsonplaceholder.py")
    result = testdir.runpytest("-k", "test_get_todos", "--vcr-record", "new_episodes")

    for ext in [".yaml", ".pickle"]:
        fname = Path(testdir.tmpdir) / "fixtures/cassettes" / "random_bucket_name{}".format(ext)
        assert fname.exists()

    result.assert_outcomes(passed=1)

    result = testdir.runpytest("-k", "test_get_todos")
    result.assert_outcomes(passed=1)


def test_jsonplaceholder_otherpath_get_todos(testdir):
    testdir.copy_example("client_tester/test_jsonplaceholder.py")
    result = testdir.runpytest("-k", "test_otherpath_get_todos", "--vcr-record", "new_episodes")

    for ext in [".yaml", ".pickle"]:
        fname = Path(testdir.tmpdir) / "fixtures/myclient/cassettes" / "random_bucket_name{}".format(ext)
        assert fname.exists()

    result.assert_outcomes(passed=1)

    result = testdir.runpytest("-k", "test_otherpath_get_todos")
    result.assert_outcomes(passed=1)
