from filters import filter_receip
from receipt import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
import numpy as np


def generate_monthes_startes(collection_of_dates):
    months_begins = set(map(lambda x: datetime.strptime(datetime.strftime(x, "%Y-%m"), "%Y-%m"), collection_of_dates))
    return sorted(list(months_begins))

def extract_month_data(df, month):
    begin = month
    end = month + relativedelta(months=1)
    cutted_from_begin = df[df[DATE_OF_TRANSACTION] >= begin]
    return cutted_from_begin[cutted_from_begin[DATE_OF_TRANSACTION] < end]


def main():
    receipt = Receipt.read_from_folder("receipts").to_DF()
    receipt = filter_receip(receipt)
    months_begins = generate_monthes_startes(receipt[DATE_OF_TRANSACTION])
    for begin in months_begins:
        with open(datetime.strftime(begin, "reports/%Y_%m.txt"), 'w') as report_file:
            month_data = extract_month_data(receipt, begin)
            print("Total month (%s) spending: " % datetime.strftime(begin, "%Y-%m"), month_data[DEBIT].sum(), file=report_file)
            print(file=report_file)
            valuable_columns = [DATE_OF_TRANSACTION, DESCRIPTION, DEBIT]
            month_data[DATE_OF_TRANSACTION] = month_data[DATE_OF_TRANSACTION].apply(lambda x: datetime.strftime(x, "%Y-%m-%d"))
            print(tabulate(month_data[valuable_columns].values.tolist(),
                           headers=valuable_columns,
                           tablefmt="plain",
                           ),
                  file=report_file)

    print(months_begins)
    print(receipt[DEBIT].sum() / len(months_begins))


if __name__ == "__main__":
    main()