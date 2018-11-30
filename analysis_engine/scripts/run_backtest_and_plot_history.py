#!/usr/bin/env python

"""
A tool for showing how to build an algorithm and
run a backtest with an algorithm config dictionary

.. code-block:: python

    import analysis_engine.consts as ae_consts
    import analysis_engine.algo as base_algo
    import analysis_engine.run_algo as run_algo

    ticker = 'SPY'

    willr_close_path = (
        'analysis_engine/mocks/example_indicator_williamsr.py')
    willr_open_path = (
        'analysis_engine/mocks/example_indicator_williamsr_open.py')
    algo_config_dict = {
        'name': 'min-runner',
        'timeseries': timeseries,
        'trade_horizon': 5,
        'num_owned': 10,
        'buy_shares': 10,
        'balance': 10000.0,
        'commission': 6.0,
        'ticker': ticker,
        'algo_module_path': None,
        'algo_version': 1,
        'verbose': False,               # log in the algorithm
        'verbose_processor': False,     # log in the indicator processor
        'verbose_indicators': False,    # log all indicators
        'verbose_trading': True,        # log in the algo trading methods
        'positions': {
            ticker: {
                'shares': 10,
                'buys': [],
                'sells': []
            }
        },
        'buy_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'sell_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'indicators': [
            {
                'name': 'willr_-70_-30',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 80,
                'buy_below': -70,
                'sell_above': -30,
                'is_buy': False,
                'is_sell': False,
                'verbose': False  # log in just this indicator
            },
            {
                'name': 'willr_-80_-20',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 30,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_-90_-10',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 60,
                'buy_below': -90,
                'sell_above': -10,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_open_-80_-20',
                'module_path': willr_open_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_open_value': 0,
                'num_points': 80,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            }
        ],
        'slack': {
            'webhook': None
        }
    }

    class ExampleCustomAlgo(base_algo.BaseAlgo):
        def process(self, algo_id, ticker, dataset):
            if self.verbose:
                print(
                    'process start - {} '
                    'date={} minute={} close={} '
                    'high={} low={} open={} volume={}'
                    ''.format(
                        self.name, self.backtest_date, self.latest_min,
                        self.latest_close, self.latest_high,
                        self.latest_low, self.latest_open,
                        self.latest_volume))
        # end of process
    # end of ExampleCustomAlgo


    algo_obj = ExampleCustomAlgo(
        ticker=algo_config_dict['ticker'],
        config_dict=algo_config_dict)

    algo_res = run_algo.run_algo(
        ticker=algo_config_dict['ticker'],
        algo=algo_obj,
        raise_on_err=True)

    if algo_res['status'] != ae_consts.SUCCESS:
        print(
            'failed running algo backtest '
            '{} hit status: {} error: {}'.format(
                algo_obj.get_name(),
                ae_consts.get_status(status=algo_res['status']),
                algo_res['err']))
    else:
        print(
            'backtest: {} {} - plotting history'.format(
                algo_obj.get_name(),
                ae_consts.get_status(status=algo_res['status'])))
    # if not successful

"""

import os
import sys
import datetime
import json
import argparse
import analysis_engine.consts as ae_consts
import analysis_engine.algo as base_algo
import analysis_engine.run_algo as run_algo
import analysis_engine.plot_trading_history as plot_trading_history
import analysis_engine.build_publish_request as build_publish_request
import analysis_engine.run_custom_algo as run_custom_algo
import spylunking.log.setup_logging as log_utils


log = log_utils.build_colorized_logger(
    name='bt',
    log_config_path=ae_consts.LOG_CONFIG_PATH)


def build_example_algo_config(
        ticker,
        timeseries='minute'):
    """build_example_algo_config

    helper for building an algorithm config dictionary

    :returns: algorithm config dictionary
    """
    willr_close_path = (
        'analysis_engine/mocks/example_indicator_williamsr.py')
    willr_open_path = (
        'analysis_engine/mocks/example_indicator_williamsr_open.py')
    algo_config_dict = {
        'name': 'backtest',
        'timeseries': timeseries,
        'trade_horizon': 5,
        'num_owned': 10,
        'buy_shares': 10,
        'balance': 10000.0,
        'commission': 6.0,
        'ticker': ticker,
        'algo_module_path': None,
        'algo_version': 1,
        'verbose': False,  # log in the algorithm
        'verbose_processor': False,  # log in the indicator processor
        'verbose_indicators': False,  # log all indicators
        'verbose_trading': False,  # log in the algo trading methods
        'inspect_datasets': False,  # log dataset metrics - slow
        'positions': {
            ticker: {
                'shares': 10,
                'buys': [],
                'sells': []
            }
        },
        'buy_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'sell_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'indicators': [
            {
                'name': 'willr_-70_-30',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 80,
                'buy_below': -70,
                'sell_above': -30,
                'is_buy': False,
                'is_sell': False,
                'verbose': False  # log in just this indicator
            },
            {
                'name': 'willr_-80_-20',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 30,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_-90_-10',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 60,
                'buy_below': -90,
                'sell_above': -10,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_open_-80_-20',
                'module_path': willr_open_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_open_value': 0,
                'num_points': 80,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            }
        ],
        'slack': {
            'webhook': None
        }
    }

    return algo_config_dict
# end of build_example_algo_config


class ExampleCustomAlgo(base_algo.BaseAlgo):
    """ExampleCustomAlgo"""

    def process(self, algo_id, ticker, dataset):
        """process

        Run a custom algorithm after all the indicators
        from the ``algo_config_dict`` have been processed and all
        the number crunching is done. This allows the algorithm
        class to focus on the high-level trade execution problems
        like bid-ask spreads and opening the buy/sell trade orders.

        **How does it work?**

        The engine provides a data stream from the latest
        pricing updates stored in redis. Once new data is
        stored in redis, algorithms will be able to use
        each ``dataset`` as a chance to evaluate buy and
        sell decisions. These are your own custom logic
        for trading based off what the indicators find
        and any non-indicator data provided from within
        the ``dataset`` dictionary.

        **Dataset Dictionary Structure**

        Here is what the ``dataset`` variable
        looks like when your algorithm's ``process``
        method is called (assuming you have redis running
        with actual pricing data too):

        .. code-block:: python

            dataset = {
                'id': dataset_id,
                'date': date,
                'data': {
                    'daily': pd.DataFrame([]),
                    'minute': pd.DataFrame([]),
                    'quote': pd.DataFrame([]),
                    'stats': pd.DataFrame([]),
                    'peers': pd.DataFrame([]),
                    'news1': pd.DataFrame([]),
                    'financials': pd.DataFrame([]),
                    'earnings': pd.DataFrame([]),
                    'dividends': pd.DataFrame([]),
                    'calls': pd.DataFrame([]),
                    'puts': pd.DataFrame([]),
                    'pricing': pd.DataFrame([]),
                    'news': pd.DataFrame([])
                }
            }

        .. tip:: you can also inspect these datasets by setting
            the algorithm's config dictionary key
            ``"inspect_datasets": True``

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a dictionary of identifiers (for debugging) and
            multiple pandas ``DataFrame`` objects.
        """
        if self.verbose:
            log.info(
                'process start - {} '
                'balance={} '
                'date={} minute={} close={} '
                'high={} low={} open={} volume={}'
                ''.format(
                    self.name,
                    self.balance,
                    self.backtest_date, self.latest_min,
                    self.latest_close, self.latest_high,
                    self.latest_low, self.latest_open,
                    self.latest_volume))
    # end of process

# end of ExampleCustomAlgo


def run_backtest_and_plot_history(
        config_dict):
    """run_backtest_and_plot_history

    Run a derived algorithm with an algorithm config dictionary

    :param config_dict: algorithm config dictionary
    """

    log.debug('start - sa')

    parser = argparse.ArgumentParser(
        description=(
            'stock analysis tool'))
    parser.add_argument(
        '-t',
        help=(
            'ticker'),
        required=True,
        dest='ticker')
    parser.add_argument(
        '-e',
        help=(
            'file path to extract an '
            'algorithm-ready datasets from redis'),
        required=False,
        dest='algo_extract_loc')
    parser.add_argument(
        '-l',
        help=(
            'show dataset in this file'),
        required=False,
        dest='show_from_file')
    parser.add_argument(
        '-H',
        help=(
            'show trading history dataset in this file'),
        required=False,
        dest='show_history_from_file')
    parser.add_argument(
        '-E',
        help=(
            'show trading performance report dataset in this file'),
        required=False,
        dest='show_report_from_file')
    parser.add_argument(
        '-L',
        help=(
            'restore an algorithm-ready dataset file back into redis'),
        required=False,
        dest='restore_algo_file')
    parser.add_argument(
        '-f',
        help=(
            'save the trading history dataframe '
            'to this file'),
        required=False,
        dest='history_json_file')
    parser.add_argument(
        '-J',
        help=(
            'plot action - after preparing you can use: '
            '-J show to open the image (good for debugging)'),
        required=False,
        dest='plot_action')
    parser.add_argument(
        '-b',
        help=(
            'run a backtest using the dataset in '
            'a file path/s3 key/redis key formats: '
            'file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
            's3://algoready/SPY-latest.json or '
            'redis:SPY-latest'),
        required=False,
        dest='backtest_loc')
    parser.add_argument(
        '-B',
        help=(
            'optional - broker url for Celery'),
        required=False,
        dest='broker_url')
    parser.add_argument(
        '-C',
        help=(
            'optional - broker url for Celery'),
        required=False,
        dest='backend_url')
    parser.add_argument(
        '-w',
        help=(
            'optional - flag for publishing an algorithm job '
            'using Celery to the analysis_engine workers'),
        required=False,
        dest='run_on_engine',
        action='store_true')
    parser.add_argument(
        '-k',
        help=(
            'optional - s3 access key'),
        required=False,
        dest='s3_access_key')
    parser.add_argument(
        '-K',
        help=(
            'optional - s3 secret key'),
        required=False,
        dest='s3_secret_key')
    parser.add_argument(
        '-a',
        help=(
            'optional - s3 address format: <host:port>'),
        required=False,
        dest='s3_address')
    parser.add_argument(
        '-Z',
        help=(
            'optional - s3 secure: default False'),
        required=False,
        dest='s3_secure')
    parser.add_argument(
        '-s',
        help=(
            'optional - start date: YYYY-MM-DD'),
        required=False,
        dest='start_date')
    parser.add_argument(
        '-n',
        help=(
            'optional - end date: YYYY-MM-DD'),
        required=False,
        dest='end_date')
    parser.add_argument(
        '-u',
        help=(
            'optional - s3 bucket name'),
        required=False,
        dest='s3_bucket_name')
    parser.add_argument(
        '-G',
        help=(
            'optional - s3 region name'),
        required=False,
        dest='s3_region_name')
    parser.add_argument(
        '-g',
        help=(
            'Path to a custom algorithm module file '
            'on disik. This module must have a single '
            'class that inherits from: '
            'https://github.com/AlgoTraders/stock-ana'
            'lysis-engine/blob/master/'
            'analysis_engine/algo.py Additionally you '
            'can find the Example-Minute-Algorithm here: '
            'https://github.com/AlgoTraders/stock-anal'
            'ysis-engine/blob/master/analysis_engine/mocks/'
            'example_algo_minute.py'),
        required=False,
        dest='run_algo_in_file')
    parser.add_argument(
        '-p',
        help=(
            'optional - s3 bucket/file for trading history'),
        required=False,
        dest='algo_history_loc')
    parser.add_argument(
        '-o',
        help=(
            'optional - s3 bucket/file for trading performance report'),
        required=False,
        dest='algo_report_loc')
    parser.add_argument(
        '-r',
        help=(
            'optional - redis_address format: <host:port>'),
        required=False,
        dest='redis_address')
    parser.add_argument(
        '-R',
        help=(
            'optional - redis and s3 key name'),
        required=False,
        dest='keyname')
    parser.add_argument(
        '-m',
        help=(
            'optional - redis database number (0 by default)'),
        required=False,
        dest='redis_db')
    parser.add_argument(
        '-x',
        help=(
            'optional - redis expiration in seconds'),
        required=False,
        dest='redis_expire')
    parser.add_argument(
        '-c',
        help=(
            'optional - algorithm config_file path for setting '
            'up internal algorithm trading strategies and '
            'indicators'),
        required=False,
        dest='config_file')
    parser.add_argument(
        '-v',
        help=(
            'set the Algorithm to verbose logging'),
        required=False,
        dest='verbose_algo',
        action='store_true')
    parser.add_argument(
        '-P',
        help=(
            'set the Algorithm\'s IndicatorProcessor to verbose logging'),
        required=False,
        dest='verbose_processor',
        action='store_true')
    parser.add_argument(
        '-I',
        help=(
            'set all Algorithm\'s Indicators to verbose logging '
            '(note indivdual indicators support a \'verbose\' key '
            'that can be set to True to debug just one '
            'indicator)'),
        required=False,
        dest='verbose_indicators',
        action='store_true')
    parser.add_argument(
        '-V',
        help=(
            'inspect the datasets an algorithm is processing - this'
            'will slow down processing to show debugging'),
        required=False,
        dest='inspect_datasets',
        action='store_true')
    parser.add_argument(
        '-j',
        help=(
            'run the algorithm on just this specific date in the datasets '
            '- specify the date in a format: YYYY-MM-DD like: 2018-11-29'),
        required=False,
        dest='run_this_date')
    parser.add_argument(
        '-d',
        help=(
            'debug'),
        required=False,
        dest='debug',
        action='store_true')
    args = parser.parse_args()

    ticker = ae_consts.TICKER
    use_balance = 10000.0
    use_commission = 6.0
    use_start_date = None
    use_end_date = None
    use_config_file = None
    debug = False
    verbose_algo = None
    verbose_processor = None
    verbose_indicators = None
    inspect_datasets = None
    history_json_file = None
    run_this_date = None

    ssl_options = ae_consts.SSL_OPTIONS
    transport_options = ae_consts.TRANSPORT_OPTIONS
    broker_url = ae_consts.WORKER_BROKER_URL
    backend_url = ae_consts.WORKER_BACKEND_URL
    path_to_config_module = ae_consts.WORKER_CELERY_CONFIG_MODULE
    include_tasks = ae_consts.INCLUDE_TASKS
    load_from_s3_bucket = None
    load_from_s3_key = None
    load_from_redis_key = None
    load_from_file = None
    load_compress = False
    load_publish = True
    load_config = None
    report_redis_key = None
    report_s3_bucket = None
    report_s3_key = None
    report_file = None
    report_compress = False
    report_publish = True
    report_config = None
    history_redis_key = None
    history_s3_bucket = None
    history_s3_key = None
    history_file = None
    history_compress = False
    history_publish = True
    history_config = None
    extract_redis_key = None
    extract_s3_bucket = None
    extract_s3_key = None
    extract_file = None
    extract_save_dir = None
    extract_compress = False
    extract_publish = True
    extract_config = None
    s3_enabled = True
    s3_access_key = ae_consts.S3_ACCESS_KEY
    s3_secret_key = ae_consts.S3_SECRET_KEY
    s3_region_name = ae_consts.S3_REGION_NAME
    s3_address = ae_consts.S3_ADDRESS
    s3_bucket_name = ae_consts.S3_BUCKET
    s3_key = None
    s3_secure = ae_consts.S3_SECURE
    redis_enabled = True
    redis_address = ae_consts.REDIS_ADDRESS
    redis_key = None
    redis_password = ae_consts.REDIS_PASSWORD
    redis_db = ae_consts.REDIS_DB
    redis_expire = ae_consts.REDIS_EXPIRE
    redis_serializer = 'json'
    redis_encoding = 'utf-8'
    publish_to_s3 = True
    publish_to_redis = True
    publish_to_slack = True
    slack_enabled = False
    slack_code_block = False
    slack_full_width = False

    dataset_type = ae_consts.SA_DATASET_TYPE_ALGO_READY
    serialize_datasets = ae_consts.DEFAULT_SERIALIZED_DATASETS
    compress = False
    encoding = 'utf-8'
    debug = False
    run_on_engine = False

    auto_fill = True
    timeseries = 'minute'
    trade_strategy = 'count'

    if args.s3_access_key:
        s3_access_key = args.s3_access_key
    if args.s3_secret_key:
        s3_secret_key = args.s3_secret_key
    if args.s3_region_name:
        s3_region_name = args.s3_region_name
    if args.s3_address:
        s3_address = args.s3_address
    if args.s3_secure:
        s3_secure = args.s3_secure
    if args.redis_address:
        redis_address = args.redis_address
    if args.redis_db:
        redis_db = args.redis_db
    if args.redis_expire:
        redis_expire = args.redis_expire
    if args.history_json_file:
        history_json_file = args.history_json_file
    if args.ticker:
        ticker = args.ticker.upper()
    if args.debug:
        debug = True
    if args.verbose_algo:
        verbose_algo = True
    if args.verbose_processor:
        verbose_processor = True
    if args.verbose_indicators:
        verbose_indicators = True
    if args.inspect_datasets:
        inspect_datasets = True
    if args.run_this_date:
        run_this_date = args.run_this_date
    if args.start_date:
        try:
            use_start_date = '{} 00:00:00'.format(
                str(args.start_date))
            datetime.datetime.strptime(
                args.start_date,
                ae_consts.COMMON_DATE_FORMAT)
        except Exception as e:
            msg = (
                'please use a start date formatted as: {}'
                '\n'
                'error was: {}'.format(
                    ae_consts.COMMON_DATE_FORMAT,
                    e))
            log.error(msg)
            sys.exit(1)
        # end of testing for a valid date
    # end of args.start_date
    if args.end_date:
        try:
            use_end_date = '{} 00:00:00'.format(
                str(args.end_date))
            datetime.datetime.strptime(
                args.end_date,
                ae_consts.COMMON_DATE_FORMAT)
        except Exception as e:
            msg = (
                'please use an end date formatted as: {}'
                '\n'
                'error was: {}'.format(
                    ae_consts.COMMON_DATE_FORMAT,
                    e))
            log.error(msg)
            sys.exit(1)
        # end of testing for a valid date
    # end of args.end_date
    algo_mod_path = None
    if args.run_algo_in_file:
        if not os.path.exists(args.run_algo_in_file):
            log.error(
                'missing algorithm module file: {}'.format(
                    args.run_algo_in_file))
            sys.exit(1)
        algo_mod_path = args.run_algo_in_file
    if args.config_file:
        use_config_file = args.config_file
        if not os.path.exists(use_config_file):
            log.error(
                'Failed: unable to find config file: -c {}'.format(
                    use_config_file))
            sys.exit(1)
        config_dict = json.loads(open(use_config_file).read())
        algo_mod_path = config_dict.get(
            'algo_path',
            algo_mod_path)
        if not os.path.exists(algo_mod_path):
            log.error(
                'missing algorithm module file from config: {}'.format(
                    algo_mod_path))
            sys.exit(1)

    """
    Finalize the algo config
    """

    config_dict['ticker'] = ticker
    config_dict['balance'] = use_balance
    config_dict['commission'] = use_commission

    if verbose_algo:
        config_dict['verbose'] = verbose_algo
    if verbose_processor:
        config_dict['verbose_processor'] = verbose_processor
    if verbose_indicators:
        config_dict['verbose_indicators'] = verbose_indicators
    if inspect_datasets:
        config_dict['inspect_datasets'] = inspect_datasets
    if run_this_date:
        config_dict['run_this_date'] = run_this_date

    """
    Run a custom algo module from disk
    """
    if algo_mod_path:

        if args.backtest_loc:
            backtest_loc = args.backtest_loc
            if ('file:/' not in backtest_loc and
                    's3://' not in backtest_loc and
                    'redis://' not in backtest_loc):
                log.error(
                    'invalid -b <backtest dataset file> specified. '
                    '{} '
                    'please use either: '
                    '-b file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-b s3://algoready/SPY-latest.json or '
                    '-b redis://SPY-latest'.format(
                        backtest_loc))
                sys.exit(1)
            if 's3://' in backtest_loc:
                load_from_s3_bucket = backtest_loc.split('/')[-2]
                load_from_s3_key = backtest_loc.split('/')[-1]
            elif 'redis://' in backtest_loc:
                load_from_redis_key = backtest_loc.split('/')[-1]
            elif 'file:/' in backtest_loc:
                load_from_file = backtest_loc.split(':')[-1]
            load_publish = True
        # end of parsing supported transport - loading an algo-ready

        if args.algo_history_loc:
            algo_history_loc = args.algo_history_loc
            if ('file:/' not in algo_history_loc and
                    's3://' not in algo_history_loc and
                    'redis://' not in algo_history_loc):
                log.error(
                    'invalid -b <backtest dataset file> specified. '
                    '{} '
                    'please use either: '
                    '-p file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-p s3://algoready/SPY-latest.json or '
                    '-p redis://SPY-latest'.format(
                        algo_history_loc))
                sys.exit(1)
            if 's3://' in algo_history_loc:
                history_s3_bucket = algo_history_loc.split('/')[-2]
                history_s3_key = algo_history_loc.split('/')[-1]
            elif 'redis://' in algo_history_loc:
                history_redis_key = algo_history_loc.split('/')[-1]
            elif 'file:/' in algo_history_loc:
                history_file = algo_history_loc.split(':')[-1]
            history_publish = True
        # end of parsing supported transport - trading history

        if args.algo_report_loc:
            algo_report_loc = args.algo_report_loc
            if ('file:/' not in algo_report_loc and
                    's3://' not in algo_report_loc and
                    'redis://' not in algo_report_loc):
                log.error(
                    'invalid -b <backtest dataset file> specified. '
                    '{} '
                    'please use either: '
                    '-o file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-o s3://algoready/SPY-latest.json or '
                    '-o redis://SPY-latest'.format(
                        algo_report_loc))
                sys.exit(1)
            if 's3://' in algo_report_loc:
                report_s3_bucket = algo_report_loc.split('/')[-2]
                report_s3_key = algo_report_loc.split('/')[-1]
            elif 'redis://' in algo_report_loc:
                report_redis_key = algo_report_loc.split('/')[-1]
            elif 'file:/' in algo_report_loc:
                report_file = algo_report_loc.split(':')[-1]
            report_publish = True
        # end of parsing supported transport - trading performance report

        if args.algo_extract_loc:
            algo_extract_loc = args.algo_extract_loc
            if ('file:/' not in algo_extract_loc and
                    's3://' not in algo_extract_loc and
                    'redis://' not in algo_extract_loc):
                log.error(
                    'invalid -b <backtest dataset file> specified. '
                    '{} '
                    'please use either: '
                    '-e file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-e s3://algoready/SPY-latest.json or '
                    '-e redis://SPY-latest'.format(
                        algo_extract_loc))
                sys.exit(1)
            if 's3://' in algo_extract_loc:
                extract_s3_bucket = algo_extract_loc.split('/')[-2]
                extract_s3_key = algo_extract_loc.split('/')[-1]
            elif 'redis://' in algo_extract_loc:
                extract_redis_key = algo_extract_loc.split('/')[-1]
            elif 'file:/' in algo_extract_loc:
                extract_file = algo_extract_loc.split(':')[-1]
            extract_publish = True
        # end of parsing supported transport - extract algorithm-ready

        if args.run_on_engine:
            run_on_engine = True
            if verbose_algo:
                log.info('starting algo on the engine')

        use_name = config_dict.get(
            'name',
            'missing-algo-name')
        auto_fill = config_dict.get(
            'auto_fill',
            auto_fill)
        timeseries = config_dict.get(
            'timeseries',
            timeseries)
        trade_strategy = config_dict.get(
            'trade_strategy',
            trade_strategy)

        algo_res = run_custom_algo.run_custom_algo(
            mod_path=algo_mod_path,
            ticker=config_dict['ticker'],
            balance=config_dict['balance'],
            commission=config_dict['balance'],
            name=use_name,
            start_date=use_start_date,
            end_date=use_end_date,
            auto_fill=auto_fill,
            config_dict=config_dict,
            load_from_s3_bucket=load_from_s3_bucket,
            load_from_s3_key=load_from_s3_key,
            load_from_redis_key=load_from_redis_key,
            load_from_file=load_from_file,
            load_compress=load_compress,
            load_publish=load_publish,
            load_config=load_config,
            report_redis_key=report_redis_key,
            report_s3_bucket=report_s3_bucket,
            report_s3_key=report_s3_key,
            report_file=report_file,
            report_compress=report_compress,
            report_publish=report_publish,
            report_config=report_config,
            history_redis_key=history_redis_key,
            history_s3_bucket=history_s3_bucket,
            history_s3_key=history_s3_key,
            history_file=history_file,
            history_compress=history_compress,
            history_publish=history_publish,
            history_config=history_config,
            extract_redis_key=extract_redis_key,
            extract_s3_bucket=extract_s3_bucket,
            extract_s3_key=extract_s3_key,
            extract_file=extract_file,
            extract_save_dir=extract_save_dir,
            extract_compress=extract_compress,
            extract_publish=extract_publish,
            extract_config=extract_config,
            publish_to_slack=publish_to_slack,
            publish_to_s3=publish_to_s3,
            publish_to_redis=publish_to_redis,
            dataset_type=dataset_type,
            serialize_datasets=serialize_datasets,
            compress=compress,
            encoding=encoding,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            redis_encoding=redis_encoding,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_address=s3_address,
            s3_bucket=s3_bucket_name,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            dataset_publish_extract=extract_publish,
            dataset_publish_history=history_publish,
            dataset_publish_report=report_publish,
            run_on_engine=run_on_engine,
            auth_url=broker_url,
            backend_url=backend_url,
            include_tasks=include_tasks,
            ssl_options=ssl_options,
            transport_options=transport_options,
            path_to_config_module=path_to_config_module,
            timeseries=timeseries,
            trade_strategy=trade_strategy,
            verbose=verbose_algo)

        show_label = 'algo.name={}'.format(
            use_name)
        show_extract = '{}'.format(
            algo_extract_loc)
        show_history = '{}'.format(
            algo_history_loc)
        show_report = '{}'.format(
            algo_report_loc)
        base_label = (
            'load={} '
            'extract={} '
            'history={} '
            'report={}'.format(
                args.run_algo_in_file,
                show_extract,
                show_history,
                show_report))
        show_label = (
            '{} running in engine task_id={} {}'.format(
                ticker,
                algo_res['rec'].get(
                    'task_id',
                    'missing-task-id'),
                base_label))
        if not run_on_engine:
            algo_trade_history_recs = algo_res['rec'].get(
                'history',
                [])
            show_label = (
                '{} algo.name={} {} trade_history_len={}'.format(
                    ticker,
                    use_name,
                    base_label,
                    len(algo_trade_history_recs)))
        if args.debug:
            log.info(
                'algo_res={}'.format(
                    algo_res))
            if algo_res['status'] == ae_consts.SUCCESS:
                log.info(
                    '{} - done running {}'.format(
                        ae_consts.get_status(status=algo_res['status']),
                        show_label))
            else:
                log.error(
                    '{} - done running {}'.format(
                        ae_consts.get_status(status=algo_res['status']),
                        show_label))
        else:
            if algo_res['status'] == ae_consts.SUCCESS:
                log.info(
                    '{} - done running {}'.format(
                        ae_consts.get_status(status=algo_res['status']),
                        show_label))
            else:
                log.error(
                    'run_custom_algo returned error: {}'.format(
                        algo_res['err']))
                sys.exit(1)
        # end of running the custom algo handler
    # end if running a custom algorithm module

    if args.backtest_loc:
        backtest_loc = args.backtest_loc
        if ('file:/' not in backtest_loc and
                's3://' not in backtest_loc and
                'redis://' not in backtest_loc):
            log.error(
                'invalid -b <backtest dataset file> specified. '
                '{} '
                'please use either: '
                '-b file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                '-b s3://algoready/SPY-latest.json or '
                '-b redis://SPY-latest'.format(
                    backtest_loc))
            sys.exit(1)

        load_from_s3_bucket = None
        load_from_s3_key = None
        load_from_redis_key = None
        load_from_file = None

        if 's3://' in backtest_loc:
            load_from_s3_bucket = backtest_loc.split('/')[-2]
            load_from_s3_key = backtest_loc.split('/')[-1]
        elif 'redis://' in backtest_loc:
            load_from_redis_key = backtest_loc.split('/')[-1]
        elif 'file:/' in backtest_loc:
            load_from_file = backtest_loc.split(':')[-1]
        # end of parsing supported transport - loading an algo-ready

        load_config = build_publish_request.build_publish_request(
            ticker=ticker,
            output_file=load_from_file,
            s3_bucket=load_from_s3_bucket,
            s3_key=load_from_s3_key,
            redis_key=load_from_redis_key,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            s3_address=s3_address,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            verbose=debug,
            label='load-{}'.format(
                backtest_loc))
        if load_from_file:
            load_config['output_file'] = load_from_file
        if load_from_redis_key:
            load_config['redis_key'] = load_from_redis_key
            load_config['redis_enabled'] = True
        if load_from_s3_bucket and load_from_s3_key:
            load_config['s3_bucket'] = load_from_s3_bucket
            load_config['s3_key'] = load_from_s3_key
            load_config['s3_enabled'] = True

    if debug:
        log.info('starting algo')

    algo_obj = ExampleCustomAlgo(
        ticker=config_dict['ticker'],
        config_dict=config_dict)

    algo_res = run_algo.run_algo(
        ticker=ticker,
        algo=algo_obj,
        start_date=use_start_date,
        end_date=use_end_date,
        raise_on_err=True)

    if algo_res['status'] != ae_consts.SUCCESS:
        log.error(
            'failed running algo backtest '
            '{} hit status: {} error: {}'.format(
                algo_obj.get_name(),
                ae_consts.get_status(status=algo_res['status']),
                algo_res['err']))
        return
    # if not successful

    log.info(
        'backtest: {} {}'.format(
            algo_obj.get_name(),
            ae_consts.get_status(status=algo_res['status'])))

    trading_history_dict = algo_obj.get_history_dataset()
    history_df = trading_history_dict[ticker]
    if not hasattr(history_df, 'to_json'):
        return

    if history_json_file:
        log.info(
            'saving history to: {}'.format(
                history_json_file))
        history_df.to_json(
            history_json_file,
            orient='records',
            date_format='iso')

    log.info('plotting history')

    first_date = history_df['date'].iloc[0]
    end_date = history_df['date'].iloc[-1]
    title = (
        'Trading History {} for Algo {}\n'
        'Backtest dates from {} to {}'.format(
            ticker,
            trading_history_dict['algo_name'],
            first_date,
            end_date))
    use_xcol = 'date'
    use_as_date_format = '%d\n%b'
    if config_dict['timeseries'] == 'minute':
        use_xcol = 'minute'
        use_as_date_format = '%d %H:%M:%S\n%b'
    xlabel = 'Dates vs {} values'.format(
        trading_history_dict['algo_name'])
    ylabel = 'Algo {}\nvalues'.format(
        trading_history_dict['algo_name'])
    df_filter = (history_df['close'] > 0.01)

    # set default hloc columns:
    blue = None
    green = None
    orange = None

    red = 'close'
    blue = 'balance'

    if debug:
        for i, r in history_df.iterrows():
            log.debug('{} - {}'.format(
                r['minute'],
                r['close']))

    plot_trading_history.plot_trading_history(
        title=title,
        df=history_df,
        red=red,
        blue=blue,
        green=green,
        orange=orange,
        date_col=use_xcol,
        date_format=use_as_date_format,
        xlabel=xlabel,
        ylabel=ylabel,
        df_filter=df_filter,
        show_plot=True,
        dropna_for_all=True)

# end of run_backtest_and_plot_history


def start_backtest_with_plot_history():
    """start_backtest_with_plot_history

    setup.py helper for kicking off a backtest
    that will plot the trading history using
    seaborn and matplotlib showing
    the algorithm's balance vs the closing price
    of the asset
    """
    run_backtest_and_plot_history(
        config_dict=build_example_algo_config(
            ticker='SPY',
            timeseries='minute'))
# end of start_backtest_with_plot_history


if __name__ == '__main__':
    start_backtest_with_plot_history()
