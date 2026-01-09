"""
Example: How to use the error handling system in your services.

This shows a before/after comparison of adding error handling to LexiconResolver.
"""
from typing import List, Optional
import logging

from shared.services.lexicon.comprehensive_lexicon_service import (
    ComprehensiveLexiconService,
    LexiconEntry
)
from shared.errors import (
    AppError,
    ErrorCode,
    with_error_handling,
    error_boundary,
    ServiceError
)

logger = logging.getLogger(__name__)


# ============================================================================
# BEFORE: No Error Handling
# ============================================================================

class LexiconResolverOld:
    """Original version without error handling."""

    def __init__(self):
        self.comprehensive = ComprehensiveLexiconService()

    def lookup_hebrew(self, word: str) -> List[LexiconEntry]:
        """
        Problems with this approach:
        - No error handling
        - If file not found, user sees ugly exception
        - No logging
        - Can't recover from errors
        """
        return self.comprehensive.lookup(word, "hebrew")


# ============================================================================
# AFTER: With Error Handling
# ============================================================================

class LexiconResolverNew:
    """Enhanced version with error handling."""

    def __init__(self):
        try:
            self.comprehensive = ComprehensiveLexiconService()
        except Exception as e:
            raise ServiceError(
                code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
                message=f"Failed to initialize lexicon service: {e}",
                user_message="Failed to load lexicon files. Please reinstall Isopgem.",
                details=str(e),
                recoverable=False,
                cause=e
            )

    @with_error_handling(
        operation="lookup_hebrew",
        component="LexiconResolver",
        fallback_value=[],  # Return empty list on error
        retry_count=1  # Allow one retry if error is recoverable
    )
    def lookup_hebrew(self, word: str) -> List[LexiconEntry]:
        """
        Benefits of this approach:
        - Automatic error handling
        - User-friendly error messages
        - Automatic logging with context
        - Returns fallback value on error
        - Offers retry for recoverable errors
        """
        # Validate input
        if not word or not word.strip():
            raise ServiceError(
                code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
                message="Word parameter is required",
                user_message="Please enter a word to look up",
                recoverable=True  # User can fix this
            )

        # Perform lookup (errors are handled by decorator)
        results = self.comprehensive.lookup(word, "hebrew")

        # Check if no results
        if not results:
            logger.info(f"No Hebrew lexicon results for word: {word}")
            # Don't raise error - this is a valid result

        return results

    def lookup_greek_with_boundary(self, word: str) -> List[LexiconEntry]:
        """
        Alternative approach using error_boundary context manager.

        This is useful when you need more control over error handling
        in specific code blocks.
        """
        # Validate
        if not word:
            raise ServiceError(
                code=ErrorCode.ERR_VAL_REQUIRED_FIELD,
                message="Word is required",
                user_message="Please enter a word to look up",
                recoverable=True
            )

        # Use error boundary for risky operation
        with error_boundary(
            operation="lookup_greek",
            component="LexiconResolver",
            user_action=f"Looking up Greek word: {word}",
            fallback_value=[],  # Return empty list on error
            notify_user=True
        ):
            results = self.comprehensive.lookup(word, "greek")

            if not results:
                logger.info(f"No Greek lexicon results for word: {word}")

            return results

    def lookup_with_custom_error(self, word: str, language: str) -> List[LexiconEntry]:
        """
        Example of raising custom errors with rich context.
        """
        # Validate language
        supported_languages = ["hebrew", "greek", "latin", "english", "sanskrit"]
        if language not in supported_languages:
            raise ServiceError(
                code=ErrorCode.ERR_VAL_INVALID_TYPE,
                message=f"Unsupported language: {language}",
                user_message=f"Language '{language}' is not supported. Please choose from: {', '.join(supported_languages)}",
                recoverable=True,
                context={
                    "word": word,
                    "requested_language": language,
                    "supported_languages": supported_languages
                }
            )

        # Try to load lexicon
        try:
            results = self.comprehensive.lookup(word, language)
        except FileNotFoundError as e:
            raise ServiceError(
                code=ErrorCode.ERR_LEX_FILE_NOT_FOUND,
                message=f"Lexicon file not found for language: {language}",
                user_message=f"The {language} lexicon is not installed. Please reinstall Isopgem.",
                details=f"Missing file: {e}",
                recoverable=False,
                cause=e,
                context={
                    "word": word,
                    "language": language,
                    "error_type": "FileNotFoundError"
                }
            )
        except Exception as e:
            # Catch-all for unexpected errors
            raise ServiceError(
                code=ErrorCode.ERR_LEX_LOOKUP_FAILED,
                message=f"Unexpected error during lookup: {e}",
                user_message="An unexpected error occurred. Please try again.",
                details=str(e),
                recoverable=True,
                cause=e,
                context={
                    "word": word,
                    "language": language
                }
            )

        return results


# ============================================================================
# Usage Examples
# ============================================================================

def example_basic_usage():
    """Example 1: Basic usage with automatic error handling."""
    service = LexiconResolverNew()

    # Errors are handled automatically
    results = service.lookup_hebrew("שלום")

    # If error occurs:
    # 1. Error is logged with context
    # 2. User sees friendly error dialog
    # 3. Empty list is returned (fallback value)
    # 4. No exception propagates to caller

    for entry in results:
        print(f"{entry.word}: {entry.definition}")


def example_with_validation():
    """Example 2: Input validation with recoverable errors."""
    service = LexiconResolverNew()

    # This will show error dialog: "Please enter a word to look up"
    # User can fix the issue (recoverable)
    results = service.lookup_hebrew("")  # Empty input

    print(f"Found {len(results)} results")


def example_unsupported_language():
    """Example 3: Validation error with helpful message."""
    service = LexiconResolverNew()

    # This will show error with list of supported languages
    try:
        results = service.lookup_with_custom_error("hello", "french")
    except ServiceError as e:
        # Error is already logged and user notified
        # Can handle programmatically if needed
        print(f"Error code: {e.code}")
        print(f"Context: {e.context}")


def example_file_not_found():
    """Example 4: Non-recoverable error (missing file)."""
    service = LexiconResolverNew()

    # If lexicon file missing:
    # 1. Shows error: "The hebrew lexicon is not installed"
    # 2. marked as non-recoverable (no retry button)
    # 3. Logs detailed error with file path
    results = service.lookup_hebrew("אלהים")


if __name__ == "__main__":
    # Run examples
    print("Example 1: Basic usage")
    example_basic_usage()

    print("\nExample 2: Validation error")
    example_with_validation()

    print("\nExample 3: Unsupported language")
    example_unsupported_language()

    print("\nExample 4: File not found")
    example_file_not_found()
