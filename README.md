# Python-Bot-Detector
The server and processing files for the Bot Detector Plugin

--BEHOLD PRETTY CHARTS TO LURE YOU IN--

(n = 6445) [Attack, Runecrafting, Strength][x, y, z]


![image](https://user-images.githubusercontent.com/5789682/109563187-707b6d00-7aad-11eb-9303-941bb29b7ceb.png)
![image](https://user-images.githubusercontent.com/5789682/109563206-74a78a80-7aad-11eb-86a2-54c61a5c3c01.png)
![image](https://user-images.githubusercontent.com/5789682/109563212-76714e00-7aad-11eb-9ace-5db5d3aaa38b.png)

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

FAQ:

Q: "Why do you need my IP?"

A: I don't, and it's not stored anywhere. But we live in the year 2021 and computers have to talk to eachother so unfortunately your IP comes along for the ride with the Data.


Q: "This plugin is worthless"

A: Not really a question - but hopefully it'll help Jagex a little bit in solving their botting crisis - and maybe even repair the OSRS economy.


Q: "How can I help contribute to the plugin?"

A: "Fork and pull request, I'll approve if it's not malicious"


Q: "My bots got banned because of this plugin"

A: "Yay!"


Q: "Is this plugin malicious? How can I be sure that it's not malicious?"

A: The only part that connects to your RuneLite client is the RuneLite plugin which is available here: https://github.com/Ferrariic/bot-detector. The RuneLite developers won't allow anything that's even mildly suspect to enter the Plugin Hub - which is pretty great.


Q: "I still don't understand why you need to use a RuneLite client plugin to capture OSRS names, what's the point?"

A: If I could have access to the OSRS database for Hiscores - this would take far less time. However, the API for Jagex's Hiscore pulling system calls only every 1-3 seconds, which means it would take over 600 days to process every single name through the API. Basically, by the time OSRS 2 and RS4 came out we'd have only scratched the surface of processing the names into a usable format - nevermind even doing the math and other nonsense to detect who is a bot.


Q: "So, how do you detect who is a bot?"

A: Well, we could use a variety of different methods - the one that I chose was to group every player together that has similar stats, and if that group gets banned more frequently than other groups then it's probably likely that the rest of the group is pretty bot-like or suspicious. This could also include gold-farmers, RWTers, etc. Any group with a high ban rate is suspicious and would be reported to Tipoff@Jagex.com

Q: "Your code looks like trash"

A: I'm a medical student that's doing this as a hobby, I'm learning as I go :(
