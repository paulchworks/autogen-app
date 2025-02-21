# Autogen with FastApi backend and React frontend

This is a simple implementation of Autogen Agents using FastApi as backend and a frontend client using React

1. **FastApi Backend**: A FastApi application running autogen.
2. **Webapp**: React webapp using websocket to communicate with FastApi.

## Running demo

1. **Clone this repo**
```
git clone
cd autogen-app
```
2. **Configure backend**

Configure python deps
```
cd backend
pip install -r ./requirements.txt 
```

Add your Openai key to .env inside src folder
```
cd backend/src (edit .env and add your key)
```

Start backend server inside src folder
```
python main.py
```
You should see

```
INFO:     Started server process [85614]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

2. **Configure frontend**

Open a new terminal and go to the react-frontend folder (you need to have nodejs installed and npm >= v14 )
```
cd autogenwebdemo/react-frontend
npm install
npm run dev
```
Open you browser on http://localhost:5173/ or the port shown 

Try doing a web search by typing "What are the top news in AI today?"

**Groupchat** if you want to use Groupchat take a look at autogen_group_chat.py


