# The Bot Detector Plugin Core Files
![GitHub](https://img.shields.io/github/license/Bot-Detector/Bot-Detector-Core-FIles)
![GitHub top language](https://img.shields.io/github/languages/top/Bot-Detector/Bot-Detector-Core-Files)
![Website](https://img.shields.io/website?down_color=lightgrey&down_message=down&up_color=green&up_message=up&url=https%3A%2F%2Fosrsbotdetector.com%2F)
![Discord](https://img.shields.io/discord/817916789668708384?label=discord)
![Twitter Follow](https://img.shields.io/twitter/follow/osrsbotdetector?style=social)
    
## How does it work?
The project is broken into 7 separate pieces:
* API ← You are here
* Database
* Hiscore scraper
* Machine Learning (ML)
* Discord Bot
* Twitter Bot
* Website
* Plugin

The API (core files) links all components with the database.

<!-- https://drive.google.com/file/d/16IO84vE3rJWRclbZAnOIEdKAmx5xAi3I/view?usp=sharing -->
![image](https://user-images.githubusercontent.com/40169115/153727141-0e39c6fe-1fdb-42f4-8019-2552bd127751.png)

## How can I request a new feature or report a bug?
To request a new feature or report a bug you should open an [issue](https://github.com/orgs/Bot-detector/repositories) on github. This way we can track new and interesting features recommended by users and developers of the plugin.

## How can I join the plugin community?
If you would like to join our community, get involved in development, join our clan, participate in events, and more -- you can join us on [our discord](https://discord.gg/3AB58CRmYs)!

## Can I get involved with development?
**Yes**. We're always welcoming new talent to the team. Many new faces like to join [our discord](https://discord.gg/3AB58CRmYs) to have a bit of guidance, however if that's not your cup of tea -- we've listed all of the steps necessary to start a development environment, and to help contribute to banning bots, below:

# Core Files Setup
This guide will take you through the necessary steps to start contributing to the server side components. 
This will include the following repositories:
* [API](https://github.com/Bot-detector/Bot-Detector-Core-Files)
* [Database](https://github.com/Bot-detector/Bot-Detector-Core-Files)
* [Scraper](https://github.com/Bot-detector/bot-detector-scraper)
* [Machine Learning](https://github.com/Bot-detector/bot-detector-ML)

You can find other relevant repositories in our [organization's github](https://github.com/Bot-detector).

### Install:
* [Docker](https://docs.docker.com/get-docker/)
*  [Github desktop](https://desktop.github.com/)
    * [Git windows](https://gitforwindows.org),  [Git unix](https://git-scm.com/download/linux) will also work.
* An integrated development environment (IDE).
    * We recommend [VSCode](https://code.visualstudio.com), but any IDE will work.

### Setup:
1. Open a terminal `cmd`
2. Navigate `cd` to where you want to save our code.
3. The command below will Create a folder `bot-detector` with two sub folders `remote` & `local` & download the remote repositories in the `remote` folder.
    * To add the repositories in github desktop, select `File` on the top left than click `Add local repository`, and navigate to the cloned repositories.
```
mkdir bot-detector\remote bot-detector\local && cd bot-detector\remote
git clone https://github.com/Bot-detector/Bot-Detector-Core-Files.git
git clone https://github.com/Bot-detector/bot-detector-mysql.git
git clone https://github.com/Bot-detector/bot-detector-ML.git
git clone https://github.com/Bot-detector/bot-detector-scraper.git
```
5. Now you can start the project, the command below will create the necessary docker containers, the first time might take a couple minutes. **Make sure docker desktop is running!**
```
cd Bot-Detector-Core-Files
docker-compose up -d
```
6. In the terminal you will now see `/usr/sbin/mysqld: ready for connections.` this means the database is ready.
7. Test the api's: 
    * Core api: ```http://localhost:5000/```
    * Machine learning: ```http://localhost:8000/```

adding /docs at the end will give return the swagger documentation for the components `/docs`

## What contributions are needed?
Features, and bugs are documented as issues in each repository. The project owners, review these, and select some as part of a [github project](https://github.com/orgs/Bot-detector/projects). 

## Merging your changes 
Changes to the project will have to submitted through the process of Merge Requests.  Github has good [documentation](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) outlining this process and how it works, but to summarize it here briefly:
1. Go to our repository and click `Fork`. ![image](https://user-images.githubusercontent.com/40169115/153728214-cd741e4e-b036-4d48-9f47-48c4dc9e99be.png)
2. Clone your newly created repository to your local machine (into the `bot-detector\local` folder)
3. Make your local changes. Test. Commit. And push to your own repo
4. Open a Merge Request

## The Development Workflow:
1. Make sure you are working in your fork. This will be a copy of the repository.
    - In github desktop, in the top left, you can click `Current repository`, select the repository under your name.
2. Create a branch, with a relative name, related to the issue.
    - In github desktop, on the top click `branch` or `current branch` than `new branch`.
3. Publish your branch.
    - In github desktop, blue button on the middle of your screen `Publish branch`
4. Create your commits (changes).
    - Small commits, defined scope are preferred.
    - Commit messages are desired.
5. Push your commits.
6. Create a Pull Request (PR)
    - In github desktop, blue button on the middle of your screen `Create Pull Request`
    - This will open your browser, make sure the base repository: `Bot-detector/` and base: `develop`

# What are the coding standards?
## General
Code must be well-understood by those willing to review it. Please add comments where necessary, if you find that the method used may be difficult to decipher in the future.

## Linting
Code must be linted prior to merging. We use `black`.

## Tests
Tests must be written where applicable.

## Naming conventions
- Variable: `snake_case`
- Function: `snake_case`
- Class: `camelCase`
- Table: `camelCase`
- Route: `kebab-case`

# How is my code approved?
We have automated workflows setup for assigning approvers based on their knowledge in each repository - this person will be the owner of Issue/Merge Request. If we have not seen your pull request in a 24 hour period, please notify us via our [our discord](https://discord.gg/3AB58CRmYs) or on github.
