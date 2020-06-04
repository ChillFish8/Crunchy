

def has_voted(bot, user_id):
    has_voted_ = bot.cache.get("votes", user_id)
    if has_voted_ is not None:
        if has_voted_['expires'] is not None:
            return 1
        else:
            return 0
    else:
        has_voted_ = bot.database.get_vote(user_id)
        bot.cache.store("votes", user_id, has_voted)
        if has_voted_['expires'] is not None:
            return 1
        else:
            return 0
