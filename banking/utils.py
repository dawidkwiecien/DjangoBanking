import random


def generateAccount():
        while True:
            bank_code = f"{random.randint(0, 99999999):08d}"
            account_number = f"{random.randint(0, 10**16 - 1):016d}"
            check_digits = 98 - int(
                f"{bank_code}{account_number}252100"  # P=25, L=21, 00
            ) % 97
            return f"{check_digits:02d}{bank_code}{account_number}"