from fitnessapp.models.models import Activity

def get_user_activities(user_id):
    return Activity.query.filter_by(user_id=user_id).order_by(Activity.date.desc()).all()

def get_user_activities_by_type(user_id, activity_type):
    return Activity.query.filter_by(user_id=user_id, activity_type=activity_type).order_by(Activity.date.asc()).all()

def get_user_activities_for_chart(user_id):
    return Activity.query.filter_by(user_id=user_id).order_by(Activity.date.asc()).all()

def get_user_activities_by_type_for_chart(user_id, activity_type):
    return Activity.query.filter_by(user_id=user_id, activity_type=activity_type).order_by(Activity.date.asc()).all()