def sum_attr(data, attr):
    return sum(getattr(a, attr) or 0 for a in data)

def calc_change(new, old):
    if old == 0:
        return 100 if new > 0 else None
    return round((new - old) / old * 100, 1)