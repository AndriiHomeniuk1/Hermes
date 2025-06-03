from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5 import QtWidgets, QtCore, QtGui



class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(34)
        self.setObjectName("CustomTitleBar")

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self.close_button = QtWidgets.QPushButton("×")
        self.close_button.setFixedSize(12, 12)
        self.close_button.setObjectName("closeButton")

        self.minimize_button = QtWidgets.QPushButton("_")
        self.minimize_button.setFixedSize(12, 12)
        self.minimize_button.setObjectName("minimizeButton")

        self.title_label = QtWidgets.QLabel("Hermes")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.close_button)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.title_label, stretch=1)

        self.setLayout(layout)

        # Connect buttons to window actions
        self.close_button.clicked.connect(self.parent_window.close)
        self.minimize_button.clicked.connect(self.parent_window.showMinimized)

        # Create a dark shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)  # More blur for a smooth shadow
        shadow.setOffset(0, 6)  # Strong vertical offset for depth
        shadow.setColor(QtGui.QColor(15, 15, 15, 230))  # Deep dark shadow

        # Create a highlight effect for a metallic sheen
        highlight = QGraphicsDropShadowEffect(self)
        highlight.setBlurRadius(14)  # Softer blur for a broader highlight
        highlight.setOffset(0, -4)  # Slight upward offset for reflection effect
        highlight.setColor(QtGui.QColor(255, 255, 255, 120))  # Semi-transparent white
        self.setGraphicsEffect(highlight)

        # Create a soft glow effect to enhance the metallic look
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(10)  # Less blur for more focus
        glow.setOffset(0, -2)  # Subtle top glow
        glow.setColor(QtGui.QColor(200, 200, 200, 80))  # Light gray
        self.setGraphicsEffect(glow)

    def mousePressEvent(self, event):
        """
        Store the initial mouse position to enable window dragging.

        Parameters:
            event (QMouseEvent): The mouse press event.
        """
        if event.button() == QtCore.Qt.LeftButton:
            # Calculate the offset between mouse position and top-left corner of the window
            self.drag_position = event.globalPos() - self.parent_window.pos()

    def mouseMoveEvent(self, event):
        """
        Move the entire window while dragging with the left mouse button.

        Parameters:
            event (QMouseEvent): The mouse move event.
        """
        if event.buttons() == QtCore.Qt.LeftButton:
            # Move the parent window to follow the cursor
            self.parent_window.move(event.globalPos() - self.drag_position)

    def paintEvent(self, event):
        """
        Custom paint event to draw the title bar with rounded top corners.

        Parameters:
            event (QPaintEvent): The paint event.
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing) # Enable smooth edges

        rect = self.rect()
        radius = 10  # Corner radius

        path = QtGui.QPainterPath()
        # Start drawing from top-right corner and apply top-corner rounding
        path.moveTo(rect.width(), 0)
        path.arcTo(rect.width() - 2 * radius, 0, 2 * radius, 2 * radius, 0, 90)
        path.lineTo(radius, 0)
        path.arcTo(0, 0, 2 * radius, 2 * radius, 90, 90)
        # Complete the path with straight lines on sides and bottom
        path.lineTo(0, rect.height())
        path.lineTo(rect.width(), rect.height())
        path.closeSubpath()
