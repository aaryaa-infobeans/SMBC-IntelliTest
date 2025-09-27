import random
import re

import allure
import pytest

from TestDataCommon.test_data import test_data
from Utilities.TestUtils.test_metadata import annotate_test_metadata


@allure.epic("Account Registration")
class TestAccountRegistrationFlow:
    """Contains all test cases for the Account Registration Flow module."""

    @annotate_test_metadata
    @pytest.mark.xray("MYS-29", defects=["MYS-55"])
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-29", name="Jira MYS-29")
    def test_verify_successful_registration_with_valid_data(self):
        """Test successful registration with valid data."""
        self.login_helper.login(
            test_data["login"]["valid_credentials"]["username"], test_data["login"]["valid_credentials"]["password"]
        )
        self.login_helper.verify_page_title("Swag Labs")
        assert random.choice([True, False]), "Random failure: Successful registration"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-30")
    def test_validate_error_for_duplicate_email_registration(self):
        """Test duplicate email registration."""
        assert random.randint(1, 10) > 2, "Random failure: Duplicate email error"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-31")
    def test_password_strength_validation(self):
        """Test password strength requirements."""
        password = "SecurePass123!"  # nosec - This is a test password for validation only
        assert len(password) >= 8, "Password should be at least 8 characters"
        assert any(c.isupper() for c in password), "Password should contain uppercase"
        assert any(c.isdigit() for c in password), "Password should contain a number"
        assert any(not c.isalnum() for c in password), "Password should contain a special char"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-32")
    # @pytest.mark.skip("Skipping OTP verification test")
    def test_check_otp_verification_during_registration(self):
        """Test OTP verification during registration."""
        assert random.choice([True, False]), "Random failure: OTP verification"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-33")
    def test_verify_mandatory_fields_are_enforced(self):
        """Test mandatory fields enforcement."""
        assert random.random() > 0.1, "Random failure: Mandatory fields"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-34")
    def test_social_media_registration_google_facebook(self):
        assert random.choice(["google", "facebook"]) == "google", "Random failure: Social media registration"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-35")
    def test_check_mobile_number_verification(self):
        assert random.randint(0, 1) == 1, "Random failure: Mobile verification"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-36")
    def test_validate_error_for_invalid_email_format(self):
        """Test for invalid email format."""
        invalid_email = "invalid-email.com"
        # This should fail the regex match, so the assertion should be for None
        assert (
            re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", invalid_email) is None
        ), "Should correctly identify an invalid email format"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-37")
    def test_verify_email_confirmation_sent_post_registration(self):
        """Test email confirmation post registration."""
        assert random.choice([True, False]), "Random failure: Email confirmation"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-38")
    def test_check_redirection_to_dashboard_post_signup(self):
        """Test redirection to dashboard post signup."""
        assert random.randint(1, 5) != 1, "Random failure: Redirect to dashboard"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-39")
    def test_terms_and_conditions_checkbox_validation(self):
        """Test terms and conditions checkbox validation."""
        assert random.choice([True, False]), "Random failure: T&C checkbox"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-40")
    def test_check_back_button_functionality_on_signup(self):
        """Test back button functionality on signup."""
        assert random.random() > 0.3, "Random failure: Back button"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-41")
    def test_registration_with_referral_code(self):
        """Test registration with referral code."""
        assert 150 + 10 == random.choice([160, 161]), "Random failure: Referral code"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-42")
    # @pytest.mark.skip("Skipping username uniqueness test")
    def test_validate_username_uniqueness_check(self):
        """Test username uniqueness check."""
        assert random.choice([True, False]), "Random failure: Username uniqueness"

    @annotate_test_metadata
    @pytest.mark.xray("MYS-43")
    def test_check_registration_date_saved_correctly(self):
        """Test registration date saved correctly."""
        assert random.randint(1, 10) > 1, "Random failure: Registration date"
