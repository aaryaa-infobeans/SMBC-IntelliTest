"""
Singleton Faker class for generating dynamic test data throughout the framework.
This ensures a single instance of Faker is used, providing consistent and efficient data generation.
"""

from typing import Any, Optional

from faker import Faker


class FakerSingleton:
    """
    Singleton class for Faker instance.
    Ensures only one instance of Faker is created and used throughout the framework.
    """

    _instance: Optional["FakerSingleton"] = None
    _faker: Optional[Faker] = None

    def __new__(cls) -> "FakerSingleton":
        """
        Override __new__ to implement singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._faker = Faker()
        return cls._instance

    @classmethod
    def get_instance(cls) -> "FakerSingleton":
        """
        Get the singleton instance of FakerSingleton.

        Returns:
            FakerSingleton: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def faker(self) -> Faker:
        """
        Get the Faker instance.

        Returns:
            Faker: The Faker instance
        """
        if self._faker is None:
            self._faker = Faker()
        return self._faker

    def set_locale(self, locale: str) -> None:
        """
        Set the locale for the Faker instance.

        Args:
            locale: The locale string (e.g., 'en_US', 'fr_FR')
        """
        self._faker = Faker(locale)

    def set_seed(self, seed: Optional[int] = None) -> None:
        """
        Set the seed for reproducible data generation.

        Args:
            seed: The seed value for random generation
        """
        Faker.seed(seed)

    # Convenience methods for common test data generation
    def first_name(self) -> str:
        """Generate a random first name."""
        return self.faker.first_name()

    def last_name(self) -> str:
        """Generate a random last name."""
        return self.faker.last_name()

    def full_name(self) -> str:
        """Generate a random full name."""
        return self.faker.name()

    def email(self) -> str:
        """Generate a random email address."""
        return self.faker.email()

    def phone_number(self) -> str:
        """Generate a random phone number."""
        return self.faker.phone_number()

    def address(self) -> str:
        """Generate a random address."""
        return self.faker.address()

    def city(self) -> str:
        """Generate a random city name."""
        return self.faker.city()

    def country(self) -> str:
        """Generate a random country name."""
        return self.faker.country()

    def date(self, pattern: str = "%Y-%m-%d") -> str:
        """Generate a random date."""
        return self.faker.date(pattern=pattern)

    def date_time(self) -> str:
        """Generate a random datetime."""
        return str(self.faker.date_time())

    def text(self, max_nb_chars: int = 200) -> str:
        """Generate random text."""
        return self.faker.text(max_nb_chars=max_nb_chars)

    def random_int(self, min_int: int = 0, max_int: int = 9999) -> int:
        """Generate a random integer."""
        return self.faker.random_int(min=min_int, max=max_int)

    def random_float(self, min_float: float = 0, max_float: float = 9999, right_digits: int = 2) -> float:
        """Generate a random float."""
        return round(self.faker.random.uniform(min_float, max_float), right_digits)

    def boolean(self) -> bool:
        """Generate a random boolean."""
        return self.faker.boolean()

    def pystr(self, min_chars: int = 8, max_chars: int = 8) -> str:
        """Generate a random string."""
        return self.faker.pystr(min_chars=min_chars, max_chars=max_chars)

    def __getattr__(self, name: str) -> Any:
        """
        Delegate any other method calls to the underlying Faker instance.
        This allows access to all Faker methods not explicitly defined here.

        Args:
            name: The method name to call on Faker

        Returns:
            The method from the Faker instance
        """
        return getattr(self.faker, name)


# Create a global instance for easy import
FAKER_SINGLETON = FakerSingleton.get_instance()
