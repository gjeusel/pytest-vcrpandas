import pytest

import vcr


class RecorderBase:
    """
    Context manager that will either record or replay requests call.
    It also proposes a send_object that will either save a DataFrame
    or compare with the saved DataFrame.

    """

    def __init__(self, bucket_name, mode='none'):
        self.bucket_name = bucket_name
        self.mode = mode

    def __enter__(self):
        self.rec = self.recorder.use_cassette(
            self.bucket_name,
            record=self.mode,
        )
        self.rec.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rec.stop()

    def send_dataframe(self, df):
        if not isinstance(df, pd.DataFrame):
            raise NotImplementedError('Recorder Only works for pandas.DataFrame.')

        if df.empty:
            raise ValueError('DataFrame is empty')

        pickle_path = SAMPLES_DIR / "{}.pickle".format(self.bucket_name)
        csv_path = SAMPLES_DIR / "{}.csv".format(self.bucket_name)

        def dump(df):
            df.to_pickle(pickle_path)
            df.to_csv(csv_path)

        def compare(df):
            df_original = pd.read_pickle(pickle_path)
            assert_frame_equal(df, df_original)

        if self.mode == 'all':
            dump(df)
        elif self.mode == 'once':
            if not pickle_path.exists():
                dump(df)
        elif self.mode == 'none':
            compare(df)



def recorder_pandas(df, bucket_name, dir_cassette, mode):
    cassette_path = dir_cassette / bucket_name
    pickle_df_path = cassette_path.parent / "{}.{}".format(cassette_path.stem, "pkl")
    with vcr.use_cassette(cassette_path.as_posix()):
        df_expected = pd.read_pickle(pickle_df_path)


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


@pytest.fixture
def vcrpandas():
    obj = Object()
    return obj
