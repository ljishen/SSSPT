full trim + 75% seq fill, then 3x30min Fixed/Random LBAs runs


```bash
$ fio -v
fio-3.8

$ sudo blkerasediscard.sh /dev/sdb
$ sudo fio wipc.fio --output-format=json+ --output=wipc.sdb.fio
$ iostat -dktxyzH -g sdb /dev/sdb 3 | tee dynamic_seed.sdb.iostat.3
$ sudo fio pre-conditioning.fio.wdpc.ssd --output-format=json+ --output=dynamic_seed.sdb.fio.3
$ ./extract_throughput.py dynamic_seed.sdb.iostat.3
```

Then change the seed number from 101 to 208 in file `wdpc.fio.fixed_seed`
