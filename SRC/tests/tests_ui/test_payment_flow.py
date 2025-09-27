"""
Test cases for the Payment Flow UI module.
"""

import random

import pytest

from Utilities.GenericUtils.retry_utils import retry
from Utilities.TestUtils.test_metadata import annotate_test_metadata


class TestPaymentFlowOnUI:
    """Contains all test cases for the Payment Flow UI module."""

    @annotate_test_metadata
    @pytest.mark.xray("MYS-14")
    def test_verify_successful_payment_with_valid_card_details(self):
        """Test successful payment processing with valid card details."""
        assert random.choice([True, False]), "Random failure: Successful payment"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-15")
    def test_validate_error_on_expired_card_entry(self):
        """Test that expired card entry shows appropriate error message."""
        assert random.randint(1, 10) > 3, "Random failure: Expired card error"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-16")
    def test_validate_error_on_invalid_card_entry(self):
        """Test payment decline when card has insufficient funds."""
        assert "success" not in random.choice(["success", "decline", "error"]), "Random failure: Insufficient funds"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-17")
    def test_validate_cvv_check_during_payment(self):
        """Test CVV validation for length."""
        cvv = "123"
        assert len(cvv) == 3, "CVV should be 3 digits"
        assert cvv.isdigit(), "CVV should only contain digits"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-18")
    def test_verify_currency_change_updates_payment_amount(self):
        """Test that changing currency updates the payment amount correctly."""
        assert 100 * 1.1 == random.choice([110, 110.0, 111]), "Random failure: Currency change"

    @pytest.mark.skip("Skipping UPI payment integration test")
    def test_upi_payment_integration_flow(self):
        """Test UPI payment integration and flow functionality."""
        assert random.choice([True, False]), "Random failure: UPI integration"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-20")
    def test_validate_saved_card_autofill_functionality(self):
        """Test that saved card details are automatically filled in payment form."""
        assert random.randint(0, 1) == 1, "Random failure: Card autofill"

    @annotate_test_metadata
    @retry(max_attempts=3, delay=1)
    @pytest.mark.xray("MYS-21")
    def test_verify_success_message_post_successful_transaction(self):
        """Test that success message is displayed after successful payment transaction."""
        assert "Success" in random.choice(["Payment Success", "Payment Failed"]), "Random failure: Success message"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-22")
    @pytest.mark.skip("Skipping cancel payment test")
    def test_cancel_payment_redirects_to_cart(self):
        """Test that canceling payment redirects user back to cart page."""
        assert random.choice([True, False]), "Random failure: Cancel payment"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-23")
    @retry(max_attempts=3, delay=1)
    def test_check_promo_code_application_in_payment(self):
        """Test promo code discount calculation."""
        price = 100
        discount = 30
        final_price = price - discount
        assert final_price == 90, "Promo code discount not applied correctly"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-19")
    def test_verify_retry_mechanism_on_network_error(self):
        """Test that payment retry mechanism works correctly on network errors."""
        assert random.choice([True, False]), "Random failure: Retry mechanism"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-25")
    @pytest.mark.skip("Skipping 3D secure authentication test")
    def test_validate_3d_secure_authentication(self):
        """Test 3D Secure authentication process for card payments."""
        assert random.randint(1, 5) != 1, "Random failure: 3D secure"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-26")
    def test_international_card_payment(self):
        """Test payment processing with international credit/debit cards."""
        assert random.choice([True, False]), "Random failure: International card"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-24")
    @pytest.mark.skip("Skipping email receipt test")
    def test_verify_email_receipt_sent_after_payment(self):
        """Test that email receipt is sent to customer after successful payment."""
        assert random.random() > 0.1, "Random failure: Email receipt"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-27")
    def test_validate_payment_breakdown_with_tax_and_discount(self):
        """Test that payment breakdown correctly calculates tax and discount amounts."""
        assert 100 + 10 - 5 == random.choice([105, 104]), "Random failure: Payment breakdown"
