## AI Money

This is a personal finance expense tracker. This works on top of transactions in [beancount](https://beancount.github.io/) file format.
The app converts an uploaded csv of credit card statement into a beacnount file and categorizes the expenses with an AI agent.

### Features
- Categorize transactions using AI

![AI money categorize demo](ai-money-categorize.png)

### Setup

#### Backend
- Install the python version specified in pyproject.toml
- cd backend
- pip install poetry
- poetry install

#### Frontend
This is a [Next.js](https://nextjs.org) app bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

Install
- Node.js (version 22.x or later recommended)
- npm (comes with Node.js)
- cd frontend
- npm install

### Run

**Backend**
- Start the backend with
```
cd backend
poetry shell
ANTHROPIC_API_KEY=<your Anthropic API key>
python -m uvicorn app:app --reload
```

**Frontend**
```
cd frontend
npm run dev
```

And visit localhost:3000

**Sample CC statement**

A sample statement is available in backend/statements. Currently, the application supports only this statement format. To use this application, ensure your statements are converted to this CSV format.


### Dashboard

[Paisa](https://paisa.fyi/) is a dashboard tool to visualize the transactions. To visualiase the transactions you can use that.
