# Program for Automating medium.com
The program parses users who liked a post on the platform via a given link and saves all the obtained information to a file.

Then, you can start the process of liking the posts of users from the generated file.

## Requirements
- Python 3.x
- Latest version of Google Chrome

## Installation
To install all necessary dependencies:
inside your virtual environment, use the command:

```
pip install -r src\requirements.txt
```

## Usage
To run the program, you need to use the command:

```
python run.py
```

When this command is executed, all necessary dependencies will be loaded and the program will start.

## Input Fields
- Proxy: you need to enter the proxy in the format **login:password@host:port**
- Email: your email address registered on Medium
- Password: application password generated in the Google account (for email interaction, to confirm the account)
  Here is a tutorial on how to get it: https://www.getmailbird.com/gmail-app-password
  It should be in the format: XXXX XXXX XXXX XXXX
- Link: the link to the post from which data needs to be parsed
- Working Directory: the directory used for saving the output files with users.
- User File: the file where the data of users who liked the post will be saved.

## Functions
- User Parsing:
  For this function, the fields: proxy, link, and working directory need to be filled.
  Records information about users who liked the post into a file.

- Liking Posts:
  For this function, the fields: proxy, email, password, and user file need to be filled.
  Likes the posts of users from the user file, on behalf of the account with the given email address.
