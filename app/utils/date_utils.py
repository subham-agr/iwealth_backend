from datetime import timedelta
from dateutil.relativedelta import relativedelta

def generate_90_day_chunks(
    start_date,
    end_date,
):
    current = start_date

    while current <= end_date:

        chunk_end = min(
            current + timedelta(days=89),
            end_date,
        )

        yield current, chunk_end

        current = chunk_end + timedelta(days=1)

def generate_months(start_date, end_date):
    months = []
    current = start_date.replace(day=1)

    while current <= end_date:
        months.append(current.strftime("%m-%Y"))
        current += relativedelta(months=1)

    return months