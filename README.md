# Python-Bot-Detector
The server and processing files for the Bot Detector Plugin

--README--
1. The files within this repo are used in conjunction with https://github.com/Ferrariic/bot-detector on RuneLite.

Workflow:
1. Player names are retrieved from Players (RuneLite Plugin Hub - https://github.com/Ferrariic/bot-detector)
2. Names are sent to the server and processed for machine readability. (https://github.com/Ferrariic/Python-Bot-Detector/blob/main/Web-Reciever.py)
3. Names are then scanned through the Hiscores and their stats are pulled. (https://github.com/Ferrariic/Python-Bot-Detector/blob/main/HiscoreNamePuller/HiscoreNamePuller.py)
4. Players are then categorized and evaluated. (https://github.com/Ferrariic/Python-Bot-Detector/blob/main/Main/V100_Main.py)
5. Players that meet criteria for being bot-like or suspicious are reported to tipoff@jagex.com

See what reviewers are saying about the plugin!

![Review 1](https://i.imgur.com/DfeeumQ.png)
![image](https://user-images.githubusercontent.com/5789682/109558682-b9c8be00-7aa7-11eb-9b19-996d2c91b273.png)
![image](https://user-images.githubusercontent.com/5789682/109558724-c77e4380-7aa7-11eb-9b2a-2ef36b232958.png)
