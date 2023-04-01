Tracer TRX
========

Installations

```
pip3 uninstall --target=/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages tronpytool
pip3 install  --proxy 127.0.0.1:1087 --target=/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages tronpytool

pip3 install --target=/usr/lib/python3.8/site-packages --upgrade tronpytool
pip3 install --target=/usr/lib/python3.8/site-packages --upgrade trx_utils
pip3 install --target=/usr/lib/python3.8/site-packages --upgrade shutils


pip3 install --upgrade shutils
python3 --target=/usr/lib/python3.8/site-packages debug.py
python3 debug.py

```


### Useful for USDT marking and tracing

Run for simple USDT analysis given from the starting key address

```
    scan_on_address = "...."
    USDTApp().CollectionTransactionFromTronForUSDT(scan_on_address)
    Analysis().start(scan_on_address)
```

This will generate two files
1. report database for all the transactions
2. analysis for incoming and outgoing transactions for each address
