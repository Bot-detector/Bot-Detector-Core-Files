![Discord](https://img.shields.io/discord/817916789668708384?label=discord&style=plastic)
![Twitter Follow](https://img.shields.io/twitter/follow/osrsbotdetector?style=social)

![GitHub repo size](https://img.shields.io/github/repo-size/Bot-detector/Bot-Detector-Core-Files?style=plastic)
![Lines of code](https://img.shields.io/tokei/lines/github/Bot-detector/Bot-Detector-Core-Files?style=plastic)

# How does it work?
The project is broken into 7 separate pieces:
* API
* Database
* Highscores scraper
* Machine Learning (ML)
* Discord/Twitter bot
* Website
* plugin

The API (core files) links all components with the database.

<!-- https://drive.google.com/file/d/16IO84vE3rJWRclbZAnOIEdKAmx5xAi3I/view?usp=sharing -->
![image](https://user-images.githubusercontent.com/40169115/153727141-0e39c6fe-1fdb-42f4-8019-2552bd127751.png)

# How can I request a new feature or report a bug?
To request a new feature or report a bug you should [open an Issue](https://github.com/orgs/Bot-detector/repositories) on Github.

[Our discord](https://discord.gg/3AB58CRmYs) is also a viable option, but we prefer to be able to track feature requests, so Github is preferred.  However the Discord is perfect for small questions, or just to chat.


# Can I get involved with development?
Yes, you can start contributing in less than 10 minutes!

Follow this guide to start contributing to the server side components (API, (database), scraper, machine learning)

For the other components, look at the relevant [repository](https://github.com/Bot-detector)

## requirements
* You must have [Docker](https://docs.docker.com/get-docker/) installed.
* You must have git installed.
    * We recommend [Github desktop](https://desktop.github.com/)
    * [Git windows](https://gitforwindows.org),  [Git unix](https://git-scm.com/download/linux) will also work.
* You must have an integrated development environment (IDE).
    * We recommend [VSCode](https://code.visualstudio.com), but any IDE will work.


Once that is installed, we can begin downloading the code.

Open up a terminal (cmd) & navigate (cd) to where you want to save our code.

We will create a folder `bot-detector` with two sub folders `remote` & `local`, we will download the remote repositories in the `remote` folder.

```sh
mkdir bot-detector\remote bot-detector\local && cd bot-detector\remote
git clone https://github.com/Bot-detector/Bot-Detector-Core-Files.git
git clone https://github.com/Bot-detector/bot-detector-mysql.git
git clone https://github.com/Bot-detector/bot-detector-ML.git
git clone https://github.com/Bot-detector/bot-detector-scraper.git
```
To add the repositories in github desktop, select `File` on the top left than click `Add local repository`, and navigate to the cloned repositories.


Now you can start the project, the command below will create the necessary docker containers, the first time might take a couple minutes. *Make sure docker desktop is running!
```powershell
cd 'Bot-Detector-Core-Files'
docker-compose up -d
```

In the terminal you will now see `/usr/sbin/mysqld: ready for connections.` this means the database is ready.

To test the api type: 
```sh
http://localhost:5000/
```
to test the ml type:
```sh
http://localhost:8000/
```
`adding /docs at the end will give return the swagger documentation for the components`

## What contributions are needed?
Features, and bugs are documented as issues in each repository, the project owners, review these, and select some as part of a [github project](https://github.com/orgs/Bot-detector/projects).

## Opening Merge Requests
Changes to the project will have to submitted through the process of Merge Requests.  Github has good [documentation](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) outlining this process and how it works, but to summarize it here briefly:
1. Go to our repository and click `Fork`. ![image](https://user-images.githubusercontent.com/40169115/153728214-cd741e4e-b036-4d48-9f47-48c4dc9e99be.png)
2. Clone your newly created repository to your local machine (into the `bot-detector\local` folder)
3. Make your local changes. Test. Commit. And push to your own repo
4. Open a Merge Request

## The development workflow:
1. Make sure you are working in your fork. (copy of the repository)
    - On github desktop, in the top left, you can click `Current repository`, select the repository under your name.
2. Create a branch, with a relative name, related to the issue.
    - In github desktop, on the top click `branch` or `current branch` than `new branch`.
3. Publish your branch.
    - In github desktop, blue button on the middle of your screen `Publish branch`
4. Create your commits (changes).
    - Small commits, defined scope are preferd.
    - Commit messages are desired.
5. Push your commits.
6. Create a Pull Request (PR)
    - in github desktop, blue button on the middle of your screen `Create Pull Request`
    - this will open your browser, make sure the base repository: `Bot-detector/` and base: `develop`

# What are the coding standards?
During the development process it is desired to write tests.

We use black for linting, in Visual Studio code (vs code), you can right click "format document".

Naming conventions:
- Variable: "snake_case"
- Function: "snake_case"
- Class: "camelCase"
- Table: "camelCase"
- Route: "kebab-case"

We are aware that we were not always consistent with naming, please suggest corrections.

# Who approves my code?
We have automated workflows setup for assigning approvers based on their knowledge in ths project - this person will be the owner of Issue/Merge Request.
