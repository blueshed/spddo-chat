from blueshed.micro.utils.date_utils import parse_date


def format_date(date: str, date_format: str='%b, %d %Y'):
    '''
        Expects date to be in the format: %Y-%m-%dT%H:%M:%S.%fZ
        or just: "%Y-%m-%d"
    '''
    date_value = parse_date(date)
    return date_value.strftime(date_format)
