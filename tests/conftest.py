import pytest

# Check that the plugin has been properly installed before proceeding
assert pytest.config.pluginmanager.hasplugin("vcrpandas")
