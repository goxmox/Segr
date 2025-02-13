from datetime import datetime, timezone

from engine.models.hmm import HMMLearn
from engine.transformers.returns import Returns
from engine.models.target_processor import StandardScaler
from engine.transformers.candles_processing import RemoveZeroActivityCandles
from api.broker_list import t_invest
from engine.candles.candles_uploader import LocalCandlesUploader

LocalCandlesUploader.broker = t_invest

from main import main
from engine.strategies.state_based import AvgState


if __name__ == '__main__':
    t = datetime(year=2024, month=12, day=2, hour=6, minute=59).replace(tzinfo=timezone.utc)

    tickers_collection = ['SBER']

    model = HMMLearn(
        n_components=10,
        covariance_type='full',
    )

    candle_to_price = 'two_way'

    pipe = [
        RemoveZeroActivityCandles(),
        Returns(keep_overnight=False, day_number=False, candle_to_price=candle_to_price, keep_vol=False),
        StandardScaler(with_mean=False),
        model,
    ]

    mock_client_config = {
        'period': t,
        'bid_orderbook_price': 'open',
        'ask_orderbook_price': 'open',
        'market_order_price': 'open',
        'buy_price_end_period': 'low',
        'sell_price_end_period': 'high',
    }

    strategies = [
        AvgState(
            pipeline=pipe,
            cash_share=0.9,
            num_of_averaging=1,
            t_threshold=1.1,
            model_metadata={'returns_type': candle_to_price},
            states_from_train_data=False
        )
    ]

    #redetermine_states(model)
    #print(model.states_map)

    main(
        strategies=strategies,
        mock_client_config=mock_client_config,
        tickers_collection=tickers_collection,
    )

