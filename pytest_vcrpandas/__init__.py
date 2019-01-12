from pathlib import Path

import pandas as pd
import pytest
import vcr


class BaseRecorder:
    """
    Context manager that will either record or replay requests call.
    It also proposes a send_object that will either save a DataFrame
    or compare with the saved DataFrame.

    """

    config = {
        'cassette_library_dir': 'fixtures/cassettes',
        # 'serializer': 'json',
        # 'match_on': ['uri', 'method'],
    }

    def __init__(self, bucket_name, record_mode='once', **kwargs):
        self.bucket_name = Path(bucket_name).stem
        self.record_mode = record_mode
        self.config.update(kwargs)
        self.vcr = vcr.VCR(**self.config)

    def __enter__(self):
        cassette_dir = Path(self.config['cassette_library_dir'])
        self.cm = self.vcr.use_cassette(
            "{}.yaml".format(cassette_dir / self.bucket_name),
            record=self.record_mode,
        )
        self.cm.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cm.__exit__()

    def __call__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError(
                'df is not a pandas.DataFrame instance: {}.'.format(df))

        cassette_dir = Path(self.config['cassette_library_dir'])
        pickle_path = cassette_dir / "{}.pickle".format(self.bucket_name)

        def dump(df):
            if not pickle_path.parent.exists():
                pickle_path.parent.mkdir(parents=True)
            df.to_pickle(pickle_path.absolute().as_posix())

        def compare(df):
            df_original = pd.read_pickle(pickle_path)
            pd.testing.assert_frame_equal(df, df_original)

        if self.record_mode == 'all':
            print("dumping pickle in {}".format(
                pickle_path.absolute().as_posix()))
            dump(df)

        elif self.record_mode in ['new_episodes', 'once']:
            if not pickle_path.exists():
                dump(df)
            else:
                compare(df)

        elif self.record_mode == 'none':
            if not pickle_path.exists():
                raise Exception("{} do not exists.".format(pickle_path))
            else:
                compare(df)


def pytest_addoption(parser):
    group = parser.getgroup('vcr')
    group.addoption(
        '--vcr-record',
        action='store',
        dest='vcr_record',
        default='none',
        choices=['once', 'new_episodes', 'none', 'all'],
        help='Set the recording mode for VCR')
    group.addoption(
        '--disable-vcr',
        action='store_true',
        dest='disable_vcr',
        help='Run tests without playing back VCR cassettes')


@pytest.fixture(scope='module')
def vcrpandas(request):
    record_mode = request.config.getoption('--vcr-record')

    kwargs = {}
    if request.config.getoption('--disable-vcr'):
        # Set mode to record but discard all responses to disable both recording and playback
        record_mode = 'new_episodes'
        kwargs['before_record_response'] = lambda *args, **kwargs: None

    class Recorder(BaseRecorder):
        def __init__(self, bucket_name):
            super().__init__(bucket_name, record_mode, **kwargs)

    return Recorder
