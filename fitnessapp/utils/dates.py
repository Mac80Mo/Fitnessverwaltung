def get_month_ranges(today):
    from datetime import timedelta
    first_day_this_month = today.replace(day=1)
    end_last_month = first_day_this_month - timedelta(days=1)
    start_last_month = end_last_month.replace(day=1)
    return start_last_month, end_last_month