from datetime import date


def increment_daily_learning(
    user,
):  # this is related to data collected from the user not to sm2

    today = date.today()

    stat, created = ShowCardDailyStat.objects.get_or_create(user=user, date=today)

    if not created:
        stat.count = F("count") + 1
    else:
        stat.count = 1  # First time today, set count to 1

    stat.save(update_fields=["count"])
    stat.refresh_from_db()

    return stat
