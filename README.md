# PoE Trade Ledger v0.0.2

This tool is designed to continuously collect data from Path of Exile's public APIs (Exchange, Search and Public Stash) and apply transformations to properly curate the data before sinking it to a specified storage. In other words, it's intended to support ETL operations on specified topics of interest respecting "X-Rate" rules upon each request. It's primarily designed for Data Scientists and Analysts looking for some alternatives to tap information from the public APIs aforementioned.

Currently, this tool is being designed to run as a server-side application. However, it should work just fine on any standalone client (for ad-hoc collection or similar).

All of the development and testing is being done on UNIX-based OS, specifically CentOs 7 and AmazonLinux 2. At the moment, It's likely that this tool works on different platforms, such as MacOs and Windows.

## Requirements

* Multithreading support
* Python 3.6+ or above
    * Virtualenv

## Installing

1. You can either clone this repository or download it's latest version:

```bash
git clone https://github.com/gustavo-hsm/PoE_TradeLedger
cd PoE_TradeLedger
``` 

or 

```bash
wget https://github.com/gustavo-hsm/PoE_TradeLedger/archive/master.zip
unzip master.zip
cd PoE_TradeLedger-master
``` 

2. Ensure you have either Python 3.6+ or Python3-pip available:

```bash
sudo yum install python3-pip
pip3 install virtualenv --user
```

3. Run the makefile. It will initialize a virtual environment and basic directories:

```bash
make
```

4. Activate the virtual environment and install dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

And we're good to go. You can start the application running the command below:

```bash
python src/main.py
```

### Execution tips and suggestions

You can deactivate the virtual environment at any time using the command:

```bash
deactivate
```

You can set it as a background process using the 'nohup' command:

```bash
nohup python src/main.py >> logs/nohup.log &
```

Errors, exceptions and inline "prints" are going to be redirected to "nohup.log" file. You can keep track of the execution by watching the "main" log:

```bash
tail -f logs/main.log
```

## Customizing data sources

The [main.py](src/main.py) file contains a few samples of data sources to browse the Exchange API. You can use that as an example to adjust your topics of interest:

```python
# Browse Mirror sellers asking for Exalted Orb
exalt_to_mirror = ExchangeItem(want='mirror', have='exalted')

# Browse Mirror sellers asking for Exalted Orb with a fixed minimum stock of 10 Mirrors
high_stock_exalt_to_mirror = ExchangeItem(want='mirror', have='exalted',
                                          minimum_stock=10,
                                          allow_adjust_minimum_stock=False)

# Browse Exalted Orb sellers asking for Chaos Orb
chaos_to_exalt = ExchangeItem(want='exalted', have='chaos')

# Browse Ancient Orb sellers asking for Chaos Orb with a minimum stock of 16 Ancient Orbs
chaos_to_ancient = ExchangeItem(want='ancient-orb', have='chaos',
                                minimum_stock=16)
```

You can find all item tags [here](https://www.pathofexile.com/trade/about) to adjust your wants/haves accordingly.

## Developing and requesting

I'm currently developing new features for this project, as well as keeping my own servers running on AWS to collect data for my studies. If you'd like to request a specific dataset, or need assistance developing customized features, feel free to contact me at anytime!