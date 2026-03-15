#### get_kline:
- endpoint: /market/klines
- method: GET
- parameters:
  - query parameters:
    - symbol (required): trading pair symbol, e.g. `BTCUSDT`, `ETHUSDT`
    - interval (required): kline interval. Supported values: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`
    - exchange (required): exchange name. Supported values: `Binance`, `Hyper`, `Aster`, `Grvt`, `StandX`, `Lighter`
    - start_time (optional): start time in Unix milliseconds. If omitted together with end_time, returns the latest 100 klines.
    - end_time (optional): end time in Unix milliseconds. If omitted together with start_time, returns the latest 100 klines.
- response (example below in json format):
  ```json
  {
    "base_response": {
      "status_code": 200,
      "status_msg": "success",
      "trace_id": "trace tracking id"
    },
    "klines": [
      {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "exchange": "Binance",
        "open_time": 1709251200000,
        "close_time": 1709254800000,
        "open": "62345.50",
        "high": "62890.00",
        "low": "62100.00",
        "close": "62780.30",
        "volume": "1234.567",
        "quote_volume": "77012345.89",
        "trades_count": 45678
      }
    ]
  }
  ```
- notes:
  - Maximum 100 klines per response. If the query range contains more, only the latest 100 are returned.
  - Price and volume fields are returned as strings to preserve decimal precision.

#### check_account

- endpoint: /auth/autopilot/positions
- method: GET
- parameters:
  - query parameters:
     - user_id: taco user id
     - trader_id: taco ai trader id
- response(example below in json format):
  ```json
  {
    "available_balance": 4976.69597582,
    "base_response": {
        "status_code": 200,
        "status_msg": "success",
        "trace_id": "trace tracking id"
    },
    "margin_used": 34.85004,
    "margin_used_pct": 0.69538661076795,
    "positions": [
        {
            "entry_price": 87094.9,
            "leverage": 5,
            "liquidation_price": 2582567.83656375,
            "mark_price": 87125.1,
            "position_size": 174.2502,
            "quantity": 0.002,
            "side": "Short",
            "symbol": "BTCUSDT",
            "unrealized_pnl": -0.0604
        }
    ],
    "total_equity": 5011.60641582
  }
  ```

#### open_position
- endpoint: /auth/autopilot/position/open
- method: POST
- parameters:
  - query parameters:
     - user_id: taco user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "trader_id": "target taco ai trader id",
         "exchange": "Binance",
         "symbol": "BTCUSDT",
         "notional_position": 123.456,
         "long": true,
         "leverage": 3.0,
         "sl_price": 30000.0,
         "tp_price": 90000.0
       }
       ```

#### close_position
- endpoint: /auth/autopilot/position/close
- method: POST
- parameters:
  - query parameters:
     - user_id: taco user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "trader_id": "target taco ai trader id",
         "exchange": "Binance",
         "symbol": "BTCUSDT",
         "notional_position": 123.456,
         "long": true
       }
       ```

#### update_position_triggering
- endpoint: /auth/autopilot/position/triggering
- method: POST
- parameters: 
  - query parameters: 
     - user_id: taco user id
  - request body (in json format as below example):
       ```json
       {
         "api_token": "please use taco api key same as authentication bearer token in header",
         "user_id": "same as in query parameter",
         "trader_id": "target taco ai trader id",
         "exchange": "Binance",
         "symbol": "BTCUSDT",
         "price": 123.456,
         "take_profit": true
       }
       ```
	   