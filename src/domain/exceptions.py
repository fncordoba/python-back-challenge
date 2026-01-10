class DomainError(Exception):
    """Base exception for all domain errors."""
    pass

class BusinessRuleViolation(DomainError):
    """Raised when a business rule is violated."""
    pass

class EntityNotFound(DomainError):
    """Raised when an entity is not found."""
    pass

class PaymentExceedsDueAmount(BusinessRuleViolation):
    """Raised when payment amount exceeds the invoice remaining balance."""
    pass

class InvalidInvoiceStateTransition(BusinessRuleViolation):
    """Raised when attempting an invalid state transition."""
    pass

class OperationNotAllowed(BusinessRuleViolation):
    """Raised when an operation is not allowed on the current state."""
    pass
