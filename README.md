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
