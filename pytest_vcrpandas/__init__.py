def pytest_addoption(parser):
    group = parser.getgroup('vcr')
    group.addoption(
        '--vcr-record',
        action='store',
        dest='vcr_record',
        default=None,
        choices=['once', 'new_episodes', 'none', 'all'],
        help='Set the recording mode for VCR'
    )
    group.addoption(
        '--disable-vcr',
        action='store_true',
        dest='disable_vcr',
        help='Run tests without playing back VCR cassettes'
    )
