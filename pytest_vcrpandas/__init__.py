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

    def __init__(self,
                 bucket_name,
                 record_mode='once',
                 cassette_library_dir='fixtures/cassettes',
                 **kwargs):
        self.bucket_name = Path(bucket_name).stem
        self.record_mode = record_mode
        self.cassette_library_dir = Path(cassette_library_dir)

        self.vcr = vcr.VCR(
            # serializer='json',
            cassette_library_dir=cassette_library_dir,
            record_mode=record_mode,
            match_on=['uri', 'method'],
            **kwargs)

    def __enter__(self):
        self.cm = self.vcr.use_cassette(
            "{}.yaml".format(self.cassette_library_dir / self.bucket_name),
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

        pickle_path = self.cassette_library_dir / "{}.pickle".format(self.bucket_name)

        def dump(df):
            df.to_pickle(pickle_path)

        def compare(df):
            df_original = pd.read_pickle(pickle_path)
            pd.testing.assert_frame_equal(df, df_original)

        if self.record_mode == 'all':
            dump(df)
        elif self.record_mode in ['once', 'new_episodes']:
            if not pickle_path.exists():
                dump(df)
        elif self.record_mode == 'none':
            if not pickle_path.exists():
                dump(df)
            else:
                compare(df)


def pytest_addoption(parser):
    group = parser.getgroup('vcr')
    group.addoption(
        '--vcr-record',
        action='store',
        dest='vcr_record',
        default=None,
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
