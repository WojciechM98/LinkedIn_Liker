import gmail

if __name__ == '__main__':
    bot = gmail.GmailBot()
    bot.credentials()
    bot.search_for_link(20, 'Link')

