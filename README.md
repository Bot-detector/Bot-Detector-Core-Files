# How can i request a new feature or improvment?
If you need help you can always go to our discord: https://discord.gg/3AB58CRmYs, our moderators, developers will help you.

To request a new feature or improvement you should make an issues, we have multiple repositories, make sure to select the correct repository before making the issue.

A list of our repositories can be found here: https://github.com/orgs/Bot-detector/repositories

# How is the project designed?
The diffrent repositories are related like this:
<!-- https://drive.google.com/file/d/16IO84vE3rJWRclbZAnOIEdKAmx5xAi3I/view?usp=sharing -->
![image](https://user-images.githubusercontent.com/40169115/153727141-0e39c6fe-1fdb-42f4-8019-2552bd127751.png)

# How do i run the project?
## requirements
Required & recommended programs:
- You must have an IDE installed, we recommend Visual Studio code: https://code.visualstudio.com/
- You must have docker installed: https://www.docker.com/products/docker-desktop
- We recommend using github desktop: https://desktop.github.com/

We recommend you create two folders:
- bot-detector-remote
- bot-detector-local

You must now download the key components (repositories), please follow this procedure: (for each key component)
1. Go to the component (repository).
2. Click the green "code" button, Click "Open with GitHub Desktop": ![image](https://user-images.githubusercontent.com/40169115/153727976-8196cbf1-e99c-4ac7-9d0a-d342c5e10337.png)
3. Make sure to select the bot-detector-remote folder: ![image](https://user-images.githubusercontent.com/40169115/153728043-181404df-df13-4a78-b2e6-8f3cf6ce3cbc.png)
4. Repeat for each component, see list below.

Our key components (repositories):
- https://github.com/Bot-detector/bot-detector-mysql
- https://github.com/Bot-detector/Bot-Detector-Core-Files
- https://github.com/Bot-detector/bot-detector-ML
- https://github.com/Bot-detector/bot-detector-scraper

if you want to contribute, the steps are slightly diffrent:
1. Go to the repository.
2. Click the "fork" button: ![image](https://user-images.githubusercontent.com/40169115/153728214-cd741e4e-b036-4d48-9f47-48c4dc9e99be.png)
3. Make sure to select the bot-detector-local folder.
4. Repeat for each component.

## running the project
We use docker compose to create the containers as if they were to run on our server, you can inspect the configuration, like the environment variables in the docker-compose.yaml file.

To run the project, do the following:
1. Open the Bot-Detector-Core-Files repository in your IDE
    - In github desktop, top left, "Current repository", select "Bot-Detector-Core-Files"
    - In github desktop, in the middel of your screeen "Open in Visual Studio Code"
2. In the Terminal, type: `docker-compose up --build`
3. Validate if the components are running.
    - Check command line
    - Check your browser: (you should see hello world)
        - Core api: http://127.0.0.1:5000
        - ML: http://127.0.0.1:8000
        - (tip adding /docs will show you the swagger documentation)
    

# How do i contribute?
If you want to contribute make sure to join our community: https://discord.gg/PK4mFgRWXE

## requirements
You must have setup the project, as described in  "How do i run the project", in particular you have to fork the repositories.

## What contributions are needed?
Features, and bugs are documented as issues in each repository, the project owners, review these, and select some as part of a github project: https://github.com/orgs/Bot-detector/projects.

In the github project you can find the refined github issues that we would like to see implemented.

## Development flow:
1. Make sure you are working in your fork. (copy of the repository)
    - On github desktop, in the top left, you can click "Current repository", select the repository under your name.
2. Create a branch, with a relative name, related to the issue.
    - In github desktop, on the top click "branch" or "current branch" > "new branch".
3. Publish your branch.
    - In github desktop, blue button on the middle of your screen "Publish branch"
4. Create your commits (changes).
    - Small commits, defined scope are preferd.
    - Commit messages are desired.
5. Push your commits.
6. Create a Pull Request (PR)
    - in github desktop, blue button on the middle of your screen "Create Pull Request"
    - this will open your browser, make sure the base repository: "Bot-detector/" and base:"develop"

# What are the coding standards?
During the development process it is desired to write tests.

We use black for linting, in Visual Studio code (vs code), you can right click "format document".

Naming conventions:
- Variable: "snake_case"
- Function: "snake_case"
- Class: "camelCase"
- Table: "camelCase"
- Routes: "kebab-case"

We are aware that we were not always consistent with naming, please suggest corrections.

# Who approves my code?
We have github workflows setup to assing approvers, this will be the owners of the project, with expertise in the area of the component.

# Who or how can i get into contact for help?
If you need help you can always go to our discord: https://discord.gg/3AB58CRmYs, our moderators, developers will help you.