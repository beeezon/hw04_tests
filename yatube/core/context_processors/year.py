from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    today = date.today().year
    return {'year': today}
