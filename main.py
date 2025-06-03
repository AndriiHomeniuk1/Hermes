import sys
from PyQt5.QtWidgets import QApplication
from core.hermesMainWindow import HermesMainWindow

# Ensures Nuitka includes this module for python-binance WebSocket support
import websockets.legacy.client  # noqa: F401



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HermesMainWindow()
    window.show()
    sys.exit(app.exec_())
