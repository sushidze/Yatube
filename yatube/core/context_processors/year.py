from datetime import datetime


def year(request):
    date = datetime.now().year
    return {'year': date}
