"""
Auto Healer Utility for Playwright Test Automation
This utility provides AI-powered element location healing when standard locators fail.
"""

import os
import time
from typing import Any, Dict, Optional

from openai import AzureOpenAI
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page

from Utilities.ReportUtils.logger import get_logger

_client = None


def get_client():
    """Return a singleton OpenAI client, initialized on first use."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        api_end_point = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        _client = AzureOpenAI(
            api_key=api_key,  # from portal
            api_version="2024-05-01-preview",  # check docs for latest
            azure_endpoint=api_end_point
        )
    return _client


logger = get_logger()


class AutoHealer:
    """

    This class provides intelligent element location with fallback mechanisms using AI agents
    to suggest alternative locators when the primary ones fail.
    """

    def __init__(self, page: Page):
        """
        Initialize the AutoHealer with a Playwright page instance.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.last_dom_snapshot = ""
        self.healing_attempts = 0
        self.max_healing_attempts = 3

    def getElement(self, locator: str, description: str = "element") -> Optional[Locator]:
        """
        Get element using locator with AI-powered healing fallback.

        This method tries to find an element using the provided locator. If it fails,
        it uses AI to suggest alternative locators. It also handles Playwright strict mode
        errors when multiple elements are found.

        Args:
            locator: The CSS selector, XPath, or other locator string
            description: Human-readable description of the element for AI context

        Returns:
            Playwright Locator object if found, None if not found after all attempts

        Raises:
            Exception: If element cannot be found after all healing attempts
        """
        logger.info(f"Attempting to locate element: {description} using locator: {locator}")

        try:
            # First attempt: Try the normal way of searching the locator
            element = self.page.locator(locator)

            # Check if element exists and is visible
            if element.count() > 0:
                logger.info(f"Successfully found element using original locator: {locator}")
                return element
            else:
                logger.warning(f"Element not found with locator: {locator}")
                # Directly call AI healing instead of raising exception
                return self._attempt_ai_healing(locator, description, f"Element not found: {locator}")

        except PlaywrightError as e:
            error_message = str(e)
            logger.error(f"Playwright error occurred: {error_message}")

            # Handle strict mode error (multiple elements found)
            if "strict mode violation" in error_message.lower() or "multiple elements" in error_message.lower():
                logger.warning(f"Strict mode violation detected for locator: {locator}")
                return self._handle_strict_mode_error(locator, description, error_message)

            # Handle element not found error
            elif "not found" in error_message.lower() or "timeout" in error_message.lower():
                logger.warning(f"Element not found, attempting AI healing for: {description}")
                return self._attempt_ai_healing(locator, description, error_message)

            else:
                # Other Playwright errors
                logger.error(f"Unhandled Playwright error: {error_message}")
                return self._attempt_ai_healing(locator, description, error_message)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            return self._attempt_ai_healing(locator, description, str(e))

    def _handle_strict_mode_error(
        self, original_locator: str, description: str, error_message: str
    ) -> Optional[Locator]:
        """
        Handle Playwright strict mode violations by asking AI for more specific locators.

        Args:
            original_locator: The original locator that caused strict mode violation
            description: Description of the element
            error_message: The error message from Playwright

        Returns:
            More specific Locator if found, None otherwise
        """
        logger.info(f"Handling strict mode error for: {description}")

        try:
            # Get current page context for AI
            page_context = self._get_page_context()

            # Ask AI for a more specific locator
            ai_prompt = f"""
            The locator '{original_locator}' for element '{description}' is matching multiple elements (strict mode violation).
            Error: {error_message}
            
            Page context: {page_context}
            
            Please provide a more specific locator that will match only one element.
            Return only the locator string, no explanation.
            """

            specific_locator = self._get_command_from_ai(ai_prompt, "specific_locator")

            if specific_locator:
                logger.info(f"AI suggested specific locator: {specific_locator}")
                try:
                    element = self.page.locator(specific_locator)
                    if element.count() == 1:
                        logger.info(f"Successfully resolved strict mode with AI locator: {specific_locator}")
                        return element
                    else:
                        logger.warning(f"AI locator still has strict mode issues: {specific_locator}")

                except PlaywrightError as e:
                    logger.error(f"AI suggested locator failed: {str(e)}")

        except Exception as e:
            logger.error(f"Error in strict mode handling: {str(e)}")

        return None

    def _attempt_ai_healing(self, original_locator: str, description: str, error_message: str) -> Optional[Locator]:
        """
        Attempt to heal the locator using AI suggestions.

        Args:
            original_locator: The original locator that failed
            description: Description of the element
            error_message: The error message that occurred

        Returns:
            Healed Locator if found, None otherwise
        """
        if self.healing_attempts >= self.max_healing_attempts:
            logger.error(f"Maximum healing attempts ({self.max_healing_attempts}) reached for: {description}")
            return None

        self.healing_attempts += 1
        logger.info(f"AI healing attempt {self.healing_attempts} for: {description}")

        try:
            # Save current DOM snapshot for AI analysis
            self._save_dom_snapshot(description)

            # Get page context
            page_context = self._get_page_context()

            # Prepare AI prompt - use your original engineered prompt here
            ai_prompt = self._build_locator_healing_prompt(original_locator, description, error_message, page_context)

            # Get AI suggestion
            ai_locator = self._get_command_from_ai(ai_prompt, "alternative_locator")

            if ai_locator:
                logger.info(f"AI suggested alternative locator: {ai_locator}")

                try:
                    # Test the AI suggested locator
                    element = self.page.locator(ai_locator)

                    if element.count() > 0:
                        logger.info(f"Successfully healed element using AI locator: {ai_locator}")
                        return element
                    else:
                        logger.warning(f"AI suggested locator found no elements: {ai_locator}")

                        # If AI suggested a specific element type in XPath, try with wildcard
                        wildcard_locator = self._try_wildcard_variation(ai_locator)
                        if wildcard_locator and wildcard_locator != ai_locator:
                            logger.info(f"Trying wildcard variation: {wildcard_locator}")
                            wildcard_element = self.page.locator(wildcard_locator)
                            if wildcard_element.count() > 0:
                                logger.info(f"Successfully healed element using wildcard variation: {wildcard_locator}")
                                return wildcard_element

                except PlaywrightError as e:
                    logger.error(f"AI suggested locator failed: {str(e)}")

                    # If AI locator also has strict mode issues, handle recursively
                    if "strict mode violation" in str(e).lower():
                        return self._handle_strict_mode_error(ai_locator, description, str(e))

        except Exception as e:
            logger.error(f"Error in AI healing attempt: {str(e)}")

        # If this attempt failed, try again (up to max attempts)
        return self._attempt_ai_healing(original_locator, description, error_message)

    def _try_wildcard_variation(self, locator: str) -> Optional[str]:
        """
        Try to create a wildcard variation of the locator.

        This method converts specific element XPaths to wildcard versions.
        For example: //button[contains(text(), 'Logout')] -> //*[contains(text(), 'Logout')]

        Args:
            locator: The original locator to create variation for

        Returns:
            Wildcard variation of the locator or None if not applicable
        """
        try:
            # Handle XPath locators with specific element types
            if locator.startswith("//") and "[" in locator:
                # Extract the element type and the condition
                parts = locator.split("[", 1)
                if len(parts) == 2:
                    xpath_start = parts[0]  # e.g., "//button"
                    condition = "[" + parts[1]  # e.g., "[contains(text(), 'Logout')]"

                    # Check if it's a specific element type (not already wildcard)
                    if not xpath_start.endswith("*"):
                        # Convert to wildcard
                        wildcard_locator = "//*" + condition
                        logger.debug(f"Created wildcard variation: {locator} -> {wildcard_locator}")
                        return wildcard_locator

            # Handle CSS selectors with specific element types
            elif not locator.startswith("//") and not locator.startswith("/"):
                # For CSS selectors like "button.class" -> "*.class" or ".class"
                if "." in locator and not locator.startswith("."):
                    # Check if it starts with an element type
                    parts = locator.split(".", 1)
                    if len(parts) == 2 and parts[0] and not parts[0].startswith("["):
                        wildcard_locator = "." + parts[1]
                        logger.debug(f"Created CSS wildcard variation: {locator} -> {wildcard_locator}")
                        return wildcard_locator

                # For CSS selectors like "button[attr='value']" -> "*[attr='value']" or "[attr='value']"
                elif "[" in locator and not locator.startswith("["):
                    parts = locator.split("[", 1)
                    if len(parts) == 2 and parts[0] and parts[0] not in ["*", ""]:
                        wildcard_locator = "[" + parts[1]
                        logger.debug(f"Created CSS attribute wildcard: {locator} -> {wildcard_locator}")
                        return wildcard_locator

            return None

        except Exception as e:
            logger.error(f"Error creating wildcard variation for {locator}: {str(e)}")
            return None

    def _build_locator_healing_prompt(
        self, original_locator: str, description: str, error_message: str, page_context: Dict[str, Any]
    ) -> str:
        """
        Build the AI prompt for locator healing using the original engineered prompt.

        Uses the comprehensive system prompt with robust locator-finding rules,
        modified to return only the locator string instead of full JSON command.

        Args:
            original_locator: The original locator that failed
            description: Description of the element
            error_message: The error message that occurred
            page_context: Current page context information

        Returns:
            The AI prompt string with engineered locator-finding logic
        """

        system_prompt = """You are an expert QA automation engineer using Playwright. Your task is to analyze the failed locator and suggest a better CSS selector or XPath that can be used with page.locator().

**CRITICAL RULES**:
1. **Be Precise**: Your selectors MUST target exactly one element.
2. **Return CSS Selectors or XPath**: Only return selectors that work with page.locator(), NOT getByRole() or other Playwright methods.

**PREFERRED LOCATOR STRATEGIES** (in order of preference):
1. **Test IDs and Data Attributes** (most reliable):
   - `[data-testid='submit-btn']`
   - `[data-test='login-button']`
   - `[data-cy='username-input']`

2. **Semantic HTML attributes**:
   - `[aria-label='Submit form']`
   - `[title='Close dialog']`
   - `input[placeholder='Enter username']`
   - `img[alt='Company logo']`

3. **ID and Name attributes**:
   - `#submit-button`
   - `input[name='username']`
   - `form[id='login-form']`

4. **Class-based selectors** (be specific):
   - `.submit-btn.primary`
   - `.form-input.username`
   - `button.btn-primary`

5. **Attribute combinations**:
   - `input[type='password'][name='password']`
   - `button[type='submit'][class*='primary']`
   - `a[href*='login'][class='nav-link']`

6. **Text-based CSS selectors**:
   - `button:has-text('Submit')`
   - `a:has-text('Login')`
   - `span:text('Error message')`

7. **XPath** (when CSS is not sufficient):
   - `//button[text()='Submit']`
   - `//input[@placeholder='Username']`
   - `//div[contains(@class,'error') and contains(text(),'Invalid')]`

**VERIFICATION CHECKLIST**:
Before finalizing a selector, verify:
1. It matches exactly one element
2. It's not too generic (avoid single class names like .btn)
3. It's not overly complex (keep it maintainable)
4. It's stable (won't break with minor UI changes)
5. It works with page.locator() method

**COMMON PITFALLS TO AVOID**:
- Don't use position-based selectors (e.g., :nth-child) unless absolutely necessary
- Don't rely on dynamic class names that include hashes or numbers
- Don't use selectors that match multiple elements
- Don't return getByRole(), getByText(), or other Playwright methods

**EXAMPLES OF GOOD LOCATORS**:
- `[data-testid='password-input']`
- `#login-button`
- `input[name='username'][type='text']`
- `button[aria-label='Submit login form']`
- `//button[text()='Login' and @type='submit']`

**IMPORTANT**: 
1. Return ONLY CSS selectors or XPath that work with page.locator()
2. Do NOT return getByRole(), getByText(), getByLabel() or similar methods
3. Make selectors as specific as needed to target exactly one element
4. Prefer CSS selectors over XPath when possible"""

        return f"""{system_prompt}

**HEALING CONTEXT**:
- Failed locator: '{original_locator}'
- Element description: '{description}'
- Error: {error_message}
- Page context: {page_context}
- DOM snapshot available for analysis

**TASK**: Analyze the failed locator and suggest a better, more robust CSS selector or XPath for the '{description}' element.

**OUTPUT**: Return ONLY a CSS selector or XPath string that works with page.locator(). 
Examples: 
- "#password" 
- "[data-testid='submit-btn']"
- "input[name='password'][type='password']"
- "//button[text()='Login']"

Do NOT return getByRole(), getByText(), or other Playwright methods. Return raw selectors only."""

    def _get_command_from_ai(self, prompt: str, request_type: str) -> Optional[str]:
        """
        Get locator suggestion from OpenAI.

        Args:
            prompt: The prompt to send to AI
            request_type: Type of request (alternative_locator, specific_locator, etc.)

        Returns:
            AI suggested locator string or None if failed
        """
        logger.info(f"Requesting {request_type} from OpenAI")

        try:
            client = get_client()
            # Check if OpenAI client is available
            if not client.api_key:
                logger.warning("OpenAI API key not available. Using fallback logic.")
                return self._fallback_locator_suggestion(prompt, request_type)

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Playwright automation expert. Provide only locator strings, no explanations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.1,
            )

            ai_response = response.choices[0].message.content.strip()
            logger.info(f"OpenAI suggested locator: {ai_response}")
            return ai_response

        except Exception as e:
            logger.error(f"Error querying OpenAI: {str(e)}")
            logger.info("Falling back to heuristic suggestions")
            return self._fallback_locator_suggestion(prompt, request_type)

    def _fallback_locator_suggestion(self, prompt: str, request_type: str) -> Optional[str]:
        """
        Fallback method to suggest alternative locators without AI.

        This method provides basic heuristic-based locator suggestions when AI is not available.

        Args:
            prompt: The original prompt (contains locator info)
            request_type: Type of request

        Returns:
            Suggested locator or None
        """
        logger.info("Using fallback locator suggestion logic")

        try:
            # Extract original locator from prompt
            lines = prompt.split("\n")
            original_locator = None

            for line in lines:
                if "locator '" in line and "' for element" in line:
                    start = line.find("locator '") + 9
                    end = line.find("' for element")
                    original_locator = line[start:end]
                    break

            if not original_locator:
                return None

            logger.info(f"Generating fallback suggestions for: {original_locator}")

            # Generate alternative locators based on common patterns
            alternatives = []

            # If it's a CSS selector, try variations
            if not original_locator.startswith("//") and not original_locator.startswith("xpath="):
                # Try with different attribute combinations
                if "#" in original_locator:
                    # ID-based selector, try by class or tag
                    element_id = original_locator.split("#")[1].split(".")[0].split("[")[0]
                    alternatives.extend(
                        [
                            f"[id='{element_id}']",
                            f"*[id*='{element_id}']",
                            f"input[id='{element_id}']",
                            f"button[id='{element_id}']",
                        ]
                    )

                elif "." in original_locator:
                    # Class-based selector
                    class_name = original_locator.split(".")[1].split("#")[0].split("[")[0]
                    alternatives.extend(
                        [
                            f"[class*='{class_name}']",
                            f"*[class*='{class_name}']",
                            f".{class_name}:first-child",
                            f".{class_name}:visible",
                        ]
                    )

                else:
                    # Tag-based selector, try with common attributes
                    alternatives.extend(
                        [
                            f"{original_locator}:visible",
                            f"{original_locator}:first-child",
                            f"{original_locator}[type]",
                            f"{original_locator}[name]",
                        ]
                    )

            # Return first alternative for now
            if alternatives:
                return alternatives[0]

        except Exception as e:
            logger.error(f"Error in fallback locator suggestion: {str(e)}")

        return None

    def _get_page_context(self) -> Dict[str, Any]:
        """
        Get current page context for AI analysis.

        Returns:
            Dictionary containing page context information
        """
        try:
            context = {
                "url": self.page.url,
                "title": self.page.title(),
                "viewport": self.page.viewport_size,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Add more context if needed
            try:
                context["visible_text"] = self.page.locator("body").inner_text()[:500]  # First 500 chars
            except:
                context["visible_text"] = "Unable to extract visible text"

            return context

        except Exception as e:
            logger.error(f"Error getting page context: {str(e)}")
            return {"error": str(e)}

    def _save_dom_snapshot(self, description: str) -> str:
        """
        Save current DOM snapshot for AI analysis.

        Args:
            description: Description for the snapshot filename

        Returns:
            Path to the saved snapshot file
        """
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            safe_description = "".join(c for c in description if c.isalnum() or c in (" ", "-", "_")).rstrip()
            safe_description = safe_description.replace(" ", "_")

            # Ensure reports directory exists
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            filename = f"{reports_dir}/dom_snapshot_{safe_description}_{timestamp}.html"

            # Get page content
            content = self.page.content()

            # Save to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"DOM snapshot saved: {filename}")
            self.last_dom_snapshot = filename

            return filename

        except Exception as e:
            logger.error(f"Failed to save DOM snapshot: {str(e)}")
            return ""

    def reset_healing_attempts(self):
        """Reset the healing attempts counter."""
        self.healing_attempts = 0
        logger.info("Healing attempts counter reset")


# End of AutoHealer class
