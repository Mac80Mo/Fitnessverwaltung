from datetime import datetime, timedelta

# --- Zeiträume berechnen ---
def get_comparison_ranges(today=None):
    today = today or datetime.today().date()

    one_week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    first_day_this_month = today.replace(day=1)
    last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    end_last_month = first_day_this_month - timedelta(days=1)

    return {
        "today": today,
        "this_week": (one_week_ago, today),
        "prev_week": (two_weeks_ago, one_week_ago - timedelta(days=1)),
        "this_month": (first_day_this_month, today),
        "prev_month": (last_month, end_last_month),
    }

# --- Aktivitäten filtern ---
def filter_activities_by_range(activities, start, end):
    return [a for a in activities if start <= a.date.date() <= end]

# --- Summen berechnen ---
def sum_attr(data, attr):
    return sum(getattr(a, attr) or 0 for a in data)

# --- Prozentuale Änderung ---
def calc_change(new, old):
    if old == 0:
        return 100 if new > 0 else None
    return round((new - old) / old * 100, 1)

# --- Hauptfunktion für Dashboard-Auswertung ---
def calculate_dashboard_stats(user):
    activities = user.activities
    weights = sorted(user.weights, key=lambda e: e.date)
    today = datetime.today().date()
    ranges = get_comparison_ranges(today)

    # Gewicht & BMI
    last_weight = weights[-1].weight_kg if weights else None
    height_m = user.height_cm / 100
    bmi = round(last_weight / (height_m ** 2), 2) if last_weight else None

    # Aktivitäten heute
    today_acts = filter_activities_by_range(activities, today, today)
    duration_today = sum_attr(today_acts, 'duration_min')
    calories_today = sum_attr(today_acts, 'calories')
    distance_today = sum_attr(today_acts, 'distance_km')
    elevation_today = sum_attr(today_acts, 'elevation_gain')
    hr_today = [a.avg_heart_rate for a in today_acts if a.avg_heart_rate]
    avg_hr_today = round(sum(hr_today) / len(hr_today), 1) if hr_today else None

    # Woche / Monat: summieren & vergleichen
    def period_stats(attribute_name, period_name):
        return {
            'this': sum_attr(filter_activities_by_range(activities, *ranges[f'this_{period_name}']), attribute_name),
            'prev': sum_attr(filter_activities_by_range(activities, *ranges[f'prev_{period_name}']), attribute_name),
        }

    dur_week = period_stats('duration_min', 'week')
    cal_week = period_stats('calories', 'week')
    km_week = period_stats('distance_km', 'week')
    elev_week = period_stats('elevation_gain', 'week')

    dur_month = period_stats('duration_min', 'month')
    cal_month = period_stats('calories', 'month')
    km_month = period_stats('distance_km', 'month')
    elev_month = period_stats('elevation_gain', 'month')

    # Änderungen
    change_dur_week = calc_change(dur_week['this'], dur_week['prev'])
    change_cal_week = calc_change(cal_week['this'], cal_week['prev'])
    change_km_week = calc_change(km_week['this'], km_week['prev'])
    change_elev_week = calc_change(elev_week['this'], elev_week['prev'])

    change_dur_month = calc_change(dur_month['this'], dur_month['prev'])
    change_cal_month = calc_change(cal_month['this'], cal_month['prev'])
    change_km_month = calc_change(km_month['this'], km_month['prev'])
    change_elev_month = calc_change(elev_month['this'], elev_month['prev'])

    # Gesamtstatistik
    total_duration = sum_attr(activities, 'duration_min')
    total_calories = sum_attr(activities, 'calories')
    total_distance = sum_attr(activities, 'distance_km')
    total_elevation = sum_attr(activities, 'elevation_gain')
    all_hr = [a.avg_heart_rate for a in activities if a.avg_heart_rate]
    avg_heart_rate_all = round(sum(all_hr) / len(all_hr), 1) if all_hr else None

    # Zeitraum
    dates = [a.date.date() for a in activities]
    active_days = len(set(dates))

    if dates:
        first_date = min(dates)
        last_date = max(dates)
        num_days = (last_date - first_date).days + 1
        num_weeks = max(1, num_days // 7)
        num_months = max(1, (last_date.year - first_date.year) * 12 + (last_date.month - first_date.month + 1))

        avg_per_day = round(total_duration / num_days, 1)
        avg_per_week = round(total_duration / num_weeks, 1)
        avg_per_month = round(total_duration / num_months, 1)
        avg_km = round(total_distance / active_days, 2)
        avg_km_week = round(total_distance / num_weeks, 2)
        avg_km_month = round(total_distance / num_months, 2)
        avg_elev = round(total_elevation / active_days, 1)
        avg_elev_week = round(total_elevation / num_weeks, 1)
        avg_elev_month = round(total_elevation / num_months, 1)
    else:
        avg_per_day = avg_per_week = avg_per_month = avg_km = avg_km_week = avg_km_month = 0
        avg_elev = avg_elev_week = avg_elev_month = 0

    return {
        'user': user,
        'last_weight': last_weight,
        'bmi': bmi,
        'duration_today': duration_today,
        'calories_today': calories_today,
        'distance_today': distance_today,
        'elevation_today': elevation_today,
        'avg_hr_today': avg_hr_today,
        'total_duration': total_duration,
        'total_calories': total_calories,
        'total_distance': total_distance,
        'total_elevation': total_elevation,
        'active_days': active_days,
        'avg_per_day': avg_per_day,
        'avg_per_week': avg_per_week,
        'avg_per_month': avg_per_month,
        'avg_km': avg_km,
        'avg_elevation': avg_elev,
        'avg_km_week': avg_km_week,
        'avg_km_month': avg_km_month,
        'avg_elev_week': avg_elev_week,
        'avg_elev_month': avg_elev_month,
        'avg_heart_rate_all': avg_heart_rate_all,
        'change_dur_week': change_dur_week,
        'change_cal_week': change_cal_week,
        'change_km_week': change_km_week,
        'change_elev_week': change_elev_week,
        'change_dur_month': change_dur_month,
        'change_cal_month': change_cal_month,
        'change_km_month': change_km_month,
        'change_elev_month': change_elev_month
    }
