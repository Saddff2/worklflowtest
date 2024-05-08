from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import random


class BankAccount:
    admin_password = "1234"
    accounts = {}
    commision_rate = 0.05
    filename = "accounts.json"

    def __init__(self, id, owner_name, initial_balance=0):
        self.id = id
        self.owner_name = owner_name
        self.balance = initial_balance
        self.transactions = []
        self.accounts[id] = self

    @classmethod
    def create_account(cls, id, owner_name, initial_balance=0):
        if id in cls.accounts:
            raise HTTPException(status_code=400, detail="Account ID already exists")
        account = cls(id, owner_name, initial_balance)
        cls.save_accounts(cls.filename)
        return account

    def deposit(self, amount):
        x = random.randint(0, 10)
        if x == 5:
            print(
                "Hahahaha you won by 1/10 chance now your deposit will be transferred to the CEO of Leumi"
            )
        else:
            self.balance += amount
            self.transactions.append(f"Deposit: +{amount}")
            BankAccount.save_accounts(BankAccount.filename)

    def widthdraw(self, amount):
        commision = amount * BankAccount.commision_rate
        total_widthdrawal = amount + commision
        if total_widthdrawal <= self.balance:
            self.balance -= total_widthdrawal
            self.transactions.append(
                f"Withdrawal: -{total_widthdrawal} includes {commision} commission"
            )
            BankAccount.save_accounts(BankAccount.filename)
        else:
            raise HTTPException(
                status_code=400, detail="Insufficient funds for the operation"
            )

    def dump(self):
        print("/-\\" * 20)
        print(f"Your identification number is: {self.id}")
        print(f"Your name is: {self.owner_name}")
        print(f"Your balance is: {self.balance}")
        print("Transaction history:")
        for transaction in self.transactions:
            print(transaction)

    def __str__(self):
        return f"{self.owner_name}, balance is {self.balance}, identification number is {self.id}"

    @staticmethod
    def save_accounts(filename):
        with open(filename, "w") as f:
            data = {
                id: {
                    "owner_name": account.owner_name,
                    "balance": account.balance,
                    "transactions": account.transactions,
                }
                for id, account in BankAccount.accounts.items()
            }
            json.dump(data, f, indent=4)

    @staticmethod
    def load_accounts(filename):
        try:
            with open(filename) as f:
                data = json.load(f)
            for id, account_data in data.items():
                account = BankAccount(
                    id, account_data["owner_name"], account_data["balance"]
                )
                account.transactions = account_data.get("transactions", [])

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")


app = FastAPI()


def load_accounts_from_file():
    try:
        with open(BankAccount.filename) as f:
            data = json.load(f)
        for id, account_data in data.items():
            account = BankAccount(
                id, account_data["owner_name"], account_data["balance"]
            )
            account.transactions = account_data.get("transactions", [])
    except FileNotFoundError:
        print(f"Error: File '{BankAccount.filename}' not found.")


@app.on_event("startup")
async def startup_event():
    load_accounts_from_file()


class CreateAccountRequest(BaseModel):
    id: str
    owner_name: str
    initial_balance: float = 0.0


@app.post("/create_account/")
async def create_account(request: CreateAccountRequest):
    return BankAccount.create_account(
        request.id, request.owner_name, request.initial_balance
    )


class DepositRequest(BaseModel):
    id: str
    amount: float


@app.post("/deposit/")
async def deposit(request: DepositRequest):
    account = BankAccount.accounts.get(request.id)
    if account:
        account.deposit(request.amount)
        return {"message": "Deposit successful!"}
    else:
        raise HTTPException(status_code=404, detail="Account not found")


class WithdrawRequest(BaseModel):
    id: str
    amount: float


@app.post("/withdraw/")
async def withdraw(request: WithdrawRequest):
    account = BankAccount.accounts.get(request.id)
    if account:
        account.widthdraw(request.amount)
        return {"message": "Withdrawal successful!"}
    else:
        raise HTTPException(status_code=404, detail="Account not found")


class AccountInfo(BaseModel):
    id: str
    owner_name: str
    balance: float
    transactions: list


@app.get("/account/{id}")
async def get_account_info(id: str):
    account = BankAccount.accounts.get(id)
    if account:
        return AccountInfo(
            **{
                "id": account.id,
                "owner_name": account.owner_name,
                "balance": account.balance,
                "transactions": account.transactions,
            }
        )
    else:
        raise HTTPException(status_code=404, detail="Account not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
