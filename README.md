# opencritic_bot
Simple score aggregator bot for r/Games with OpenCritic and MetaCritic support.

# r/Games score aggregation bot

Simple score aggregator bot for r/Games with OpenCritic and MetaCritic support. Scans r/Games for review threads and
replies with a reddit formated visualization of the OpenCritic/MetaCritic review scores.

## Getting Started

This guide uses [anaconda](https://www.anaconda.com/distribution/) which contains *pip* and numerous other packages. File locations in this guide may vary, depending on your current set up.

### Prerequisites

Use pip to install following packages:
* praw
* numpy (included in anaconda)
* beautifulsoup4 

```
pip install <package-name>
```

You can also simply execute the make.bat in the root folder.

### Set Up

#### 1. Get reddit credentials
Make sure you have a working [reddit](reddit.com) account with 2FA disabled. 
Create a reddit app as shown [here](https://www.pythonforengineers.com/build-a-reddit-bot-part-1/).

#### 2. Configure praw.ini
Edit the *praw.ini* in the *praw* package folder according to the [guide above](https://www.pythonforengineers.com/build-a-reddit-bot-part-1/). It is located in *Anaconda3\Lib\site-packages\praw*, if you are using anaconda 3.
Use the following configuration name and add your credentials:

```
[opencritic_bot]
client_id=
client_secret=
password=
username=
user_agent=
```

#### 3. Run the program
Open your commandline in the project source folder. Run `python main.py` to execute the program.

## Authors

* **lebeli** - *Initial work* - [lebeli](https://github.com/lebeli)

## Disclaimer

* This simple bot is a work in progress. 
