import random

import allure
import pytest


@allure.epic("Account Transactions")
class TestCurrentAndSavingsAccountsTransactions:
    """Contains all test cases for the Current and Savings Accounts Transactions module."""

    @pytest.mark.xray("MYS-44")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Money Transfer")
    @allure.title("MYS-44: Verify that money transfer between own accounts works correctly.")
    @allure.description("Verify that money transfer between own accounts works correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-44", name="Jira MYS-44")
    def test_verify_money_transfer_between_own_accounts(self):
        """Test money transfer between own accounts."""
        assert random.choice([True, False]), "Random failure: Money transfer"

    @pytest.mark.xray("MYS-45")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Transaction History")
    @allure.title("MYS-45: Verify that transaction history is accurate.")
    @allure.description("Verify that transaction history is accurate.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-45", name="Jira MYS-45")
    def test_check_transaction_history_accuracy(self):
        """Test transaction history accuracy."""
        assert random.randint(1, 10) > 3, "Random failure: Transaction history"

    @pytest.mark.xray("MYS-46")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Account Balance")
    @allure.title("MYS-46: Verify that account balance is calculated correctly after a transaction.")
    @allure.description("Verify that account balance is calculated correctly after a transaction.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-46", name="Jira MYS-46")
    def test_account_balance_after_transaction(self):
        """Test balance calculation after a transaction."""
        initial_balance = 1000
        transaction_amount = 150
        expected_balance = 850
        new_balance = initial_balance - transaction_amount
        assert new_balance == expected_balance, "Balance calculation is incorrect"

    @pytest.mark.xray("MYS-47")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify IMPS Transfer")
    @allure.title("MYS-47: Verify that IMPS transfer functionality works correctly.")
    @allure.description("Verify that IMPS transfer functionality works correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-47", name="Jira MYS-47")
    def test_imps_transfer_functionality(self):
        """Test IMPS transfer functionality."""
        assert random.choice([True, False]), "Random failure: IMPS transfer"

    @pytest.mark.xray("MYS-48")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Withdrawal Limit Enforcement")
    @allure.title("MYS-48: Verify that withdrawal limit enforcement works correctly.")
    @allure.description("Verify that withdrawal limit enforcement works correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-48", name="Jira MYS-48")
    def test_check_withdrawal_limit_enforcement(self):
        """Test withdrawal limit enforcement."""
        daily_limit = 10000
        withdrawal_amount = 5000
        assert withdrawal_amount <= daily_limit, "Withdrawal should be within the daily limit"

    @pytest.mark.xray("MYS-49")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Deposit Transaction Logging")
    @allure.title("MYS-49: Verify that deposit transaction logging works correctly.")
    @allure.description("Verify that deposit transaction logging works correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-49", name="Jira MYS-49")
    def test_deposit_transaction_logging(self):
        """Test deposit transaction logging."""
        assert random.randint(0, 1) == 1, "Random failure: Deposit logging"

    @pytest.mark.xray("MYS-50")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Mini Statement Generation")
    @allure.title("MYS-50: Verify that mini statement generation works correctly.")
    @allure.description("Verify that mini statement generation works correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-50", name="Jira MYS-50")
    def test_verify_mini_statement_generation(self):
        """Test mini statement generation."""
        assert "success" in random.choice(["success", "failed"]), "Random failure: Mini statement"

    @pytest.mark.xray("MYS-51")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Overdraft Limit Warnings")
    @allure.title("MYS-51: Verify that overdraft limit warnings are displayed correctly.")
    @allure.description("Verify that overdraft limit warnings are displayed correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-51", name="Jira MYS-51")
    def test_check_overdraft_limit_warnings(self):
        """Test overdraft limit warnings."""
        assert random.choice([True, False]), "Random failure: Overdraft warning"

    @pytest.mark.xray("MYS-52")
    @allure.feature("Account Transactions")
    @allure.tag("smoke", "regression")
    @allure.story("Verify Failed Transaction Due to Downtime")
    @allure.title("MYS-52: Verify that failed transaction due to downtime is handled correctly.")
    @allure.description("Verify that failed transaction due to downtime is handled correctly.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("owner", "swapnil")
    @allure.link("https://sauce1100.atlassian.net/browse/MYS-52", name="Jira MYS-52")
    def test_failed_transaction_due_to_downtime(self):
        """Test failed transaction due to downtime."""
        assert random.randint(1, 5) != 1, "Random failure: Failed transaction"
