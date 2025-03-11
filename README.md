# CS130-SWEats

## Living Documents
1. [PRD](https://docs.google.com/document/d/1jvmDcy5BvK7oRuoCHL4rN7Vr4UHbwxqwlw8ncNZxmbI/edit?usp=sharing)
2. [DD](https://docs.google.com/document/d/1xZnrjl_DweEybGai-yuaf5lxHyyDiGRB6irLnSPqaI4/edit?usp=sharing)

## Description
Trivia website that generates quiz bowl style questions ([for reference](https://www.naqt.com/samples/hsnct.pdf)) from Wikipedia articles using a LLM. The UI is staying sleek and 
minimalistic with options to choose category preferences. It also generates unique questions while also having sub-second question generation and answer processing. Finally, it 
stores users' historical answers and points for correct answers, etc. for review. 

Well that's the goal at least. Refer to Living Documents for updates

## Organization
This is the relevant directory organization (omitting ignore files etc.).
```
./
|-cache/
|-db/
|-frontend/
|-gamemaster/
|-question_gen/
|-docker-compose.yml
|-.env
```
Each folder holds the source/dependency files, Dockerfile, test files, and other miscellaneous files depending on the service.
**NOTE:** Define the following environment variables. Users can rename the .env.example file and fill in:
```
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
OPENAI_API_KEY=...
OPENAI_USER_AGENT=...
```
**NOTE** Setting OPENAI_USER_AGENT to "DUMMY" will make the question generator return dummy questions

## Running
To run this project:
1. Make sure cwd is root of this project
2. Enter `docker-compose up --build`
3. Once all containers are running, access web app from browser at `http://localhost:80`
4. To take down project, either use docker desktop to remove all containers or use `docker-compose down`
