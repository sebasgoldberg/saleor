from enum import Enum

from django.utils.translation import pgettext_lazy


class PaymentError(Exception):
    def __init__(self, message):
        super(PaymentError, self).__init__(message)
        self.message = message


class GatewayError(IOError):
    pass


class CustomPaymentChoices:
    MANUAL = "manual"

    CHOICES = [(MANUAL, pgettext_lazy("Custom payment choice type", "Manual"))]


class OperationType(Enum):
    PROCESS_PAYMENT = "process_payment"
    AUTH = "authorize"
    CAPTURE = "capture"
    VOID = "void"
    REFUND = "refund"
    CONFIRM = "confirm"


class TransactionError(Enum):
    """Represents a transaction error."""

    INCORRECT_NUMBER = "incorrect_number"
    INVALID_NUMBER = "invalid_number"
    INCORRECT_CVV = "incorrect_cvv"
    INVALID_CVV = "invalid_cvv"
    INCORRECT_ZIP = "incorrect_zip"
    INCORRECT_ADDRESS = "incorrect_address"
    INVALID_EXPIRY_DATE = "invalid_expiry_date"
    EXPIRED = "expired"
    PROCESSING_ERROR = "processing_error"
    DECLINED = "declined"


class TransactionKind:
    """Represents the type of a transaction.

    The following transactions types are possible:
    - AUTH - an amount reserved against the customer's funding source. Money
    does not change hands until the authorization is captured.
    - VOID - a cancellation of a pending authorization or capture.
    - CAPTURE - a transfer of the money that was reserved during the
    authorization stage.
    - REFUND - full or partial return of captured funds to the customer.
    """

    AUTH = "auth"
    CAPTURE = "capture"
    VOID = "void"
    REFUND = "refund"
    CONFIRM = "confirm"
    WAIT_FOR_AUTH = "wait" # Wait for payment confirmation.
    REJECT = "reject" # Reject a payment when is waiting a confirmation.
    CANCEL = "cancel" # Cancel a payment when is already captured.
    CHOICES = [
        (AUTH, pgettext_lazy("transaction kind", "Authorization")),
        (REFUND, pgettext_lazy("transaction kind", "Refund")),
        (CAPTURE, pgettext_lazy("transaction kind", "Capture")),
        (VOID, pgettext_lazy("transaction kind", "Void")),
        (CONFIRM, pgettext_lazy("transaction kind", "Confirm")),
        (WAIT_FOR_AUTH, pgettext_lazy("transaction kind", "Wait Confirmation")),
        (REJECT, pgettext_lazy("transaction kind", "Reject")),
        (CANCEL, pgettext_lazy("transaction kind", "Cancel")),
    ]


class ChargeStatus:
    """Represents possible statuses of a payment.

    The following statuses are possible:
    - NOT_CHARGED - no funds were take off the customer founding source yet.
    - PARTIALLY_CHARGED - funds were taken off the customer's funding source,
    partly covering the payment amount.
    - FULLY_CHARGED - funds were taken off the customer founding source,
    partly or completely covering the payment amount.
    - PARTIALLY_REFUNDED - part of charged funds were returned to the customer.
    - FULLY_REFUNDED - all charged funds were returned to the customer.
    """

    NOT_CHARGED = "not-charged"
    PARTIALLY_CHARGED = "partially-charged"
    FULLY_CHARGED = "fully-charged"
    PARTIALLY_REFUNDED = "partially-refunded"
    FULLY_REFUNDED = "fully-refunded"
    WAITING_FOR_AUTH = "wait-auth" # Is waiting for a confirmation.
    REJECTED = "rejected" # Was rejected after wait for a confirmation.
    PARTIALLY_CANCELLED = "partially-cancelled" # Partially cancelled a previously captured payment.
    FULLY_CANCELLED = "fully-cancelled" # Fully cancelled a previously captured payment.

    CHOICES = [
        (NOT_CHARGED, pgettext_lazy("payment status", "Not charged")),
        (PARTIALLY_CHARGED, pgettext_lazy("payment status", "Partially charged")),
        (FULLY_CHARGED, pgettext_lazy("payment status", "Fully charged")),
        (PARTIALLY_REFUNDED, pgettext_lazy("payment status", "Partially refunded")),
        (FULLY_REFUNDED, pgettext_lazy("payment status", "Fully refunded")),
        (WAITING_FOR_AUTH, pgettext_lazy("transaction kind", "Wait Confirmation")),
        (REJECTED, pgettext_lazy("transaction kind", "Rejected")),
        (PARTIALLY_CANCELLED, pgettext_lazy("transaction kind", "Partially cancelled")),
        (FULLY_CANCELLED, pgettext_lazy("transaction kind", "Fully cancelled")),
    ]
