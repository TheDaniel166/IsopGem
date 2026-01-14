"""
UI notification system for user-facing error messages.

Provides toast notifications and error dialogs for the user.
Integrates with PyQt6 for visual feedback.
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Internal shared/ modules only (2 references)
- CRITERION: 2 (Essential for app to function)
"""

from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QTimer
import logging

from .base import AppError, ErrorSeverity

logger = logging.getLogger(__name__)


# Global reference to main window (for showing notifications)
_main_window: Optional[QWidget] = None


def set_main_window(window: QWidget):
    """
    Set the main window for showing notifications.

    Call this from your main application:
        from shared.errors import set_main_window
        set_main_window(main_window)
    """
    global _main_window
    _main_window = window


def notify_error(
    message: str,
    details: Optional[str] = None,
    title: str = "Error",
    parent: Optional[QWidget] = None
):
    """
    Show an error notification to the user.

    Args:
        message: Main error message
        details: Optional detailed information
        title: Dialog title
        parent: Parent widget (uses main window if None)
    """
    parent = parent or _main_window

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    if details:
        msg_box.setDetailedText(details)

    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def notify_warning(
    message: str,
    details: Optional[str] = None,
    title: str = "Warning",
    parent: Optional[QWidget] = None
):
    """
    Show a warning notification to the user.

    Args:
        message: Warning message
        details: Optional detailed information
        title: Dialog title
        parent: Parent widget (uses main window if None)
    """
    parent = parent or _main_window

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    if details:
        msg_box.setDetailedText(details)

    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def notify_info(
    message: str,
    details: Optional[str] = None,
    title: str = "Information",
    parent: Optional[QWidget] = None,
    timeout_ms: Optional[int] = None
):
    """
    Show an information notification to the user.

    Args:
        message: Information message
        details: Optional detailed information
        title: Dialog title
        parent: Parent widget (uses main window if None)
        timeout_ms: Auto-close after this many milliseconds (None = manual close)
    """
    parent = parent or _main_window

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    if details:
        msg_box.setDetailedText(details)

    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    # Auto-close if timeout specified
    if timeout_ms:
        QTimer.singleShot(timeout_ms, msg_box.close)

    msg_box.exec()


def notify_success(
    message: str,
    details: Optional[str] = None,
    title: str = "Success",
    parent: Optional[QWidget] = None,
    timeout_ms: int = 2000
):
    """
    Show a success notification to the user.

    Args:
        message: Success message
        details: Optional detailed information
        title: Dialog title
        parent: Parent widget (uses main window if None)
        timeout_ms: Auto-close after this many milliseconds
    """
    parent = parent or _main_window

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    if details:
        msg_box.setDetailedText(details)

    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    # Auto-close after timeout
    QTimer.singleShot(timeout_ms, msg_box.close)

    msg_box.exec()


def notify_app_error(
    error: AppError,
    parent: Optional[QWidget] = None,
    show_details: bool = True
):
    """
    Show an AppError to the user with appropriate styling.

    Args:
        error: AppError instance
        parent: Parent widget (uses main window if None)
        show_details: Show technical details (for debugging)
    """
    # Choose notification type based on severity
    if error.severity == ErrorSeverity.CRITICAL:
        icon = QMessageBox.Icon.Critical
        title = "Critical Error"
    elif error.severity == ErrorSeverity.ERROR:
        icon = QMessageBox.Icon.Critical
        title = "Error"
    elif error.severity == ErrorSeverity.WARNING:
        icon = QMessageBox.Icon.Warning
        title = "Warning"
    else:
        icon = QMessageBox.Icon.Information
        title = "Notice"

    parent = parent or _main_window

    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(error.user_message or error.message)

    # Build details text
    if show_details:
        details_parts = []

        if error.details:
            details_parts.append(f"Details: {error.details}")

        if error.code:
            details_parts.append(f"Error Code: {error.code}")

        if error.context:
            details_parts.append(f"Context: {error.context}")

        if details_parts:
            msg_box.setDetailedText("\n\n".join(details_parts))

    # Add recovery hint if recoverable
    if error.recoverable:
        msg_box.setInformativeText("This error may be temporary. Please try again.")

    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

    # Log the error
    logger.error(str(error), extra=error.to_dict())


def ask_retry(
    message: str,
    details: Optional[str] = None,
    title: str = "Retry?",
    parent: Optional[QWidget] = None
) -> bool:
    """
    Ask user if they want to retry an operation.

    Args:
        message: Question message
        details: Optional detailed information
        title: Dialog title
        parent: Parent widget (uses main window if None)

    Returns:
        True if user wants to retry, False otherwise
    """
    parent = parent or _main_window

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    if details:
        msg_box.setDetailedText(details)

    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.Retry)

    result = msg_box.exec()
    return result == QMessageBox.StandardButton.Retry


# TODO: Implement toast notifications for non-blocking feedback
# These would appear in a corner of the window and auto-dismiss
# For now, using QMessageBox with timeout for simple cases