# YogaMerchant Trade system
The system allows to work with a broker IQ option, collect quotes, bet. 
The product analyzes the incoming and forms of these templates on which identifies more profitnye patterns, then bet the system

##Basic usage:

**Create new configuration file:**
```
python src/yogaMerchant/config/config.py -c config.json
python setup.py install && python src/yogaMerchant/config/config.py -c config.json
```

**Start IQ Option bot:**
```
python src/yogaMerchant/start_collector.py -c config.json
python setup.py install && python src/yogaMerchant/starter.py -c config.json
```

**Collect history:**
```
python setup.py install && python ./src/yogaMerchant/collect_history.py -c config.json -d 86400 -f 1479031838
```
Parameters:
`-d Duration
[-f] From timestamp - optional, default now`

**Check history:**
```
python setup.py install && python ./src/yogaMerchant/check_history.py -c config.json -f 1479459451 -t 1479031838
```
Parameters:
`-f From timestamp
[-t] To timestamp - optional, default now`


**Example config after generate:**
```
{
  "broker_settings": {
    "hostname": "iqoption.com",
    "password": "",
    "username": ""
  },
  "db_settings": {
    "postgres": {
      "database": "yogamerchant",
      "hostname": "localhost",
      "password": "",
      "port": "5432",
      "username": "postgres"
    },
    "redis": {
      "db": "0",
      "hostname": "localhost",
      "port": "6379"
    }
  }
}
```

# Documentation
The program works in a manner that would find itself working strategy (patterns). Search pattern occur for quite a number of intervals of past data and checks them summing up in the future put and call. These patterns are used on data in real time.

You can manage the configuration for the application.
Forecasts are generated when obtaining a new quote (time + time prediction). After the time of the forecast, the result update to pattern model. The pattern is checked whenever a new prediction in the next iteration analysis. If the pattern is suitable for the formation of a new configuration of the signal to be monitored in the field configuration of the trader

```
bid_times - Time allowed to the bets (for example +1 minute forward)
deep - Ignition sequence depth
min_deep - Minimal ignition sequence depth
interval - Real time Analyzer interval
prediction_expire - Life time prediction. If something came out new forecasts will be generated
prediction_delay_on_trend - Delay when the trend on repetitive Call Put the forecast
prediction_save_if_exists - Flag allows to analyze repeating during the forecast bets
candles_durations - Length of candles that will operate the Analyzer
chance - Minimum chance pattern with regard to Put/Call or Call/Put
repeats - The minimum number of consecutive trends when making bets
max_bids_for_expiration_time - The total number of bids allowed per time rates
```
