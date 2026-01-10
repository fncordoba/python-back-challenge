from dataclasses import dataclass
from decimal import Decimal
from src.domain.enums import Currency

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __le__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
             raise ValueError("Cannot compare different currencies")
        return self.amount <= other.amount
    
    def __lt__(self, other: 'Money') -> bool:
        if self.currency != other.currency:
             raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount
