import os
from datetime import datetime
from pandas import DataFrame, to_numeric

DEBIT = "Debit"
CREDIT = "Credit"
AMOUNT_IN_TRANSACTION_CURRENCY = "Amount in transaction currency"
DESCRIPTION = "Description"
CARD = "Card"
POSTING_DATE = "Posting date"
DATE_OF_TRANSACTION = "Date of transaction"


class Receipt:
    COLUMNS = [DATE_OF_TRANSACTION, POSTING_DATE, CARD, DESCRIPTION, AMOUNT_IN_TRANSACTION_CURRENCY, CREDIT,
               DEBIT]

    columns_parsers = {
        DATE_OF_TRANSACTION: lambda x: datetime.strptime(x, "%Y-%m-%d"),
        POSTING_DATE: lambda x: datetime.strptime(x, "%Y-%m-%d"),
        CARD: lambda x:x,
        DESCRIPTION: lambda x: x,
        AMOUNT_IN_TRANSACTION_CURRENCY: lambda x: x,
        CREDIT: lambda x: (None if x=="" else float(x)),
        DEBIT: lambda x: (None if x=="" else float(x)),
    }

    def __init__(self, columns, data):
        self.columns = columns
        self.data = data


    @staticmethod
    def define_borders(line, delimiters, borders_per_name={}):
        if len(borders_per_name.keys()) != 0:
            return borders_per_name

        left_borders = [line.find(delimiter) for delimiter in delimiters]
        right_borders = [left_borders[(i + 1) % len(delimiters)] for i in range(len(delimiters))]
        right_borders[-1] = -1

        for i in range(len(delimiters)):
            borders_per_name[delimiters[i]] = {"left": left_borders[i],
                                               "right": right_borders[i]}

        return borders_per_name


    @staticmethod
    def parse_line(line, borders, delimiters, columns_parsers):
        data = []
        for delimiter in delimiters:
            left = borders[delimiter]['left']
            right = borders[delimiter]['right']
            if right == -1:
                right = len(line)
            value_str = line[left: right].strip()
            data.append(columns_parsers[delimiter](value_str))
        return data

    @classmethod
    def read_receipt_from_file(cls, path_to_file):
        with open(path_to_file, 'r', encoding="utf-8") as inn:
            lines = inn.readlines()
        borders = cls.define_borders(lines[0], cls.COLUMNS)

        lines = lines[2:]
        rows = []
        for line in lines:
            if len(line.strip()) == 0:
                continue
            rows.append(cls.parse_line(line, borders, cls.COLUMNS, cls.columns_parsers))

        return cls(cls.COLUMNS, rows)

    def add_data_from_another_receipt(self, other):
        assert self.COLUMNS == other.COLUMNS
        self.data += other.data

    @classmethod
    def read_from_folder(cls, path_to_folder):
        files = [os.path.join(path_to_folder, file) for file in os.listdir(path_to_folder)]
        files = sorted(files)
        receipts = list(map(Receipt.read_receipt_from_file, files))
        receipt = receipts[0]
        for other_receipt in receipts[1:]:
            receipt.add_data_from_another_receipt(other_receipt)
        return receipt

    def to_DF(self):
        df = DataFrame(self.data, columns=self.columns)
        df[CREDIT] = df[CREDIT].apply(to_numeric)
        df[DEBIT] = df[DEBIT].apply(to_numeric)
        return df


if __name__ == "__main__":
    receipt = Receipt.read_from_folder("receipts").to_DF()
    print(receipt.head())
