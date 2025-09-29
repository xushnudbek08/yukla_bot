from base import get_channels

async def check_subscription(bot, user_id, channels=None):
    if channels is None:
        channels = get_channels()

    unsubscribed = []  # obuna bo‘lmagan kanallarni yig‘amiz
    for ch_id, ch_link in channels:
        try:
            member = await bot.get_chat_member(ch_id, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                unsubscribed.append((ch_id, ch_link))
        except:
            unsubscribed.append((ch_id, ch_link))

    return unsubscribed  # agar [] bo‘lsa hammasiga obuna
