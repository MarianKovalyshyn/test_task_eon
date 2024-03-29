# Telegram Bot for test task from EON+

This is a Telegram bot built with Python and the aiogram library. 
The bot interacts with users, collects data through a series of questions, 
and generates a report based on the user's responses.

## Getting Started

These instructions will get you a copy of the project up and running on your 
local machine for development and testing purposes.
This project is intended to be used with Python 3.7.

### Libraries that are used in the project
- aiogram==2.25.1
- openai==1.10.0

## Installing using GitHub
Don't forget to create .env file with your API_KEY from OpenAI and your Telegram bot token.

```shell
git clone https://github.com/MarianKovalyshyn/test_task_eon.git
cd test_task_eon/
python -m venv venv
source venv/bin/activate (MacOS)
venv\Scripts\activate (Windows)
pip install -r requirements.txt
python main.py
```

## Usage
![img.png](img.png)