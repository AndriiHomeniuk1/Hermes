from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QLineEdit, QPushButton



def toggle_secret_key_visibility(
        line_edit: QLineEdit,
        toggle_button: QPushButton
) -> None:
    """
    Toggles the visibility of the password/secret
    key in a QLineEdit widget.
    Args:
        line_edit (QLineEdit): The input field containing the secret key/password.
        toggle_button (QPushButton): The button used to toggle visibility.
    """
    if line_edit.echoMode() == QLineEdit.Password:
        line_edit.setEchoMode(QLineEdit.Normal)
        toggle_button.setText("👀")
    else:
        line_edit.setEchoMode(QLineEdit.Password)
        toggle_button.setText("🔒")


def flash_input_error(
        widget: QtWidgets.QWidget,
        duration: int = 1000
) -> None:
    """
    Temporarily highlights a widget (e.g., QLineEdit) with a red border and background
    to indicate an input error. The highlight fades after the specified duration.

    Args:
        widget (QWidget): The widget to highlight.
        duration (int): Duration in milliseconds for which the error highlight stays visible.
    """
    # Red border and light red background for QLineEdit
    error_style = (
        "QLineEdit {"
        "border: 2px solid rgb(220, 60, 60);"
        "background-color: rgb(255, 235, 235);"
        "border-radius: 6px;"
        "}"
    )

    # Default style (empty string resets to whatever is defined by the current QSS/theme)
    normal_style = ""

    # Apply the temporary error style to the widget
    widget.setStyleSheet(error_style)

    # Force immediate GUI update so the user sees the error effect
    QtWidgets.QApplication.processEvents()

    # Set a timer to reset the style after the specified duration
    QTimer.singleShot(duration, lambda: widget.setStyleSheet(normal_style))
