# Bot Detector
The core files for the Bot Detector Plugin.

Patreon: https://www.patreon.com/bot_detector

Workflow:

![image](https://user-images.githubusercontent.com/5789682/112380944-628dc600-8cc0-11eb-8924-4e5fa7ed2c45.png)

--README--
1. The files within this repo are used in conjunction with https://github.com/Ferrariic/bot-detector on RuneLite.

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

## api documentation
```
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```
## extra info
```
POST: to create data.
GET: to read data.
PUT: to update data.
DELETE: to delete data.
```

## setup
```
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
# for admin purposes saving & upgrading

```
venv\Scripts\activate
call pip freeze > requirements.txt
powershell "(Get-Content requirements.txt) | ForEach-Object { $_ -replace '==', '>=' } | Set-Content requirements.txt"
call pip install -r requirements.txt --upgrade
call pip freeze > requirements.txt
powershell "(Get-Content requirements.txt) | ForEach-Object { $_ -replace '>=', '==' } | Set-Content requirements.txt"
```
