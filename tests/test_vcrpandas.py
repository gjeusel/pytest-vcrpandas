import pytest

# Check that the plugin has been properly installed before proceeding
assert pytest.config.pluginmanager.hasplugin("vcrpandas")


def test_jsonplaceholder_get_todos(testdir):
    testdir.copy_example("jsonplaceholder.py")
    testdir.runpytest("-k", "test_get_todos")
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
