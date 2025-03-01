# LinkedIn_Liker
A Python-based script that will help you to like your colleague's posts on LinkedIn :D

## How does this app works
LinkedIn_Liker contains two modules:
- gmail handler,
- executive for chrome browser automation.

### gmail handler
Module **gmail** has a class **GmailBot**. This class contans three functions. First one for **credentials** creation. **Search_for_link** is looking in your mailbox for unread messages with specyfic title. when found, it saves them in a list. Function **search_for_verification** is used when selenium driver while loging into LinkedIn account will encounter PIN confirmation request that is send to the same gmail account. 

### executive module
Executive module is responsible for chrome automation using Selenium webdriver. **Login_to_inkedin** function in class **LinkHandling** gets data created with **search_for_links**. Before use the LinkedIn name and password need to be added to .env file.

### Make sure to have the same version of selenium webdriver as your chrome browser version downloaded and placed in *webdriver* folder

