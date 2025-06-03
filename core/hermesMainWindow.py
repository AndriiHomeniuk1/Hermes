import sys
import multiprocessing
import json
import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QLineEdit
from ui.hermes_ui import Ui_MainWindow
from ui.customTitleBar import CustomTitleBar
from ui.ui_helpers import flash_input_error, toggle_secret_key_visibility
from core.client_binance import BinanceClient
from core.client_warmup import start_warmup
from core.websockets_listener import run_listener
from core.binance_utils import is_valid_symbol, get_quantity_precision, get_price_precision
from core.place_order import place_market_order, close_position_by_order_id
from config.config_paths import CONFIG_PATH, STYLE_PATH



class HermesMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize UI components
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Indicates whether the app is closing; set to False initially.
        self.closing = False

        # Load and apply custom styles
        self.load_styles()

        # Add a custom title bar
        self.title_bar = CustomTitleBar(self)

        # Set up the main layout with title bar and central widget
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.ui.centralwidget)

        # Wrap layout into a container widget and set it as the main window content
        container = QtWidgets.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply window customizations for a frameless, translucent look
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setObjectName("MainWindow")

        # Adjust window height dynamically based on screen size
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_height = screen_geometry.height()
        self.window_height = screen_height

        # Set initial window size
        self.resize(180, self.window_height)

        # Position the window on the right side of the screen
        self.move(screen_geometry.right() - self.width(), 0)

        # Connect tab switching event to window resizing logic
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Apply window shape updates after resizing
        self.update_window_mask()

        # Configure secret key field

        # setting an icon for 'secretKeyIconLabel'
        self.secretKeyIconLabel = self.ui.secretKeyIconLabel
        self.secretKeyIconLabel.setText("🔒")
        self.secretKeyIconLabel.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        # Mask API key input by default for security
        self.ui.secretKeyLineEdit.setEchoMode(QLineEdit.Password)

        # Enable click-to-toggle visibility functionality
        self.secretKeyIconLabel.mousePressEvent = lambda event: toggle_secret_key_visibility(
            self.ui.secretKeyLineEdit, self.secretKeyIconLabel
        )


        # Initialize Binance client for API communication
        self.binance_client = BinanceClient()

        # Populate API key fields if stored in .env file
        self.ui.apiKeyLineEdit.setText(
            self.binance_client.api_key if self.binance_client.api_key else ""
        )
        self.ui.secretKeyLineEdit.setText(
            self.binance_client.api_secret if self.binance_client.api_secret else ""
        )

        # Automatically check connection status upon startup
        self.refresh_connection_status()

        # Connect the "Connect" button to manual API authentication
        self.ui.connectButton.clicked.connect(self.manual_connect)

        #  Trigger warmup process if Binance client is already connected
        if self.binance_client.is_connected:
            start_warmup(self.binance_client.client)


        # Symbol
        # Load configuration settings from config/settings.json
        self.settings = self.load_settings()
        self.symbol = self.settings.get("symbol", "")

        # Define precision variables for trading calculations
        self.precision = None
        self.use_decimal = None
        self.price_precision = None

        # Insert the saved symbol into the input field
        self.ui.symbolLineEdit.setText(self.symbol)

        # Set initial connection status to "Disconnected"
        self.update_pair_status(False)

        # Create shared memory variables for price tracking
        self.price_value = multiprocessing.Value("d", 0.0)
        self.event = multiprocessing.Event()
        self.ws_process = None

        # Set up a timer to monitor `self.event` at a 100ms interval
        self.check_event_timer: QTimer = QTimer()
        self.check_event_timer.setInterval(100)
        self.check_event_timer.timeout.connect(self.check_event)

        # Automatically activate WebSocket listener if a symbol exists
        self.auto_activate_symbol()

        # Connect "Activate" button to symbol activation function
        self.ui.activateSymbolPairButton.clicked.connect(self.activate_symbol)


        # Load USD, Stop-Loss (St), and Take-Profit (Tp) settings from config
        self.usd = self.settings.get("usd", None)
        self.st_percentage = self.settings.get("st_percentage", None)
        self.tp_percentage = self.settings.get("tp_percentage", None)
        self.populate_saved_inputs()

        # Update values when input fields lose focus
        self.ui.usdLineEdit.editingFinished.connect(self.update_usd)
        self.ui.st_percentageLineEdit.editingFinished.connect(self.update_st_percentage)
        self.ui.tp_percentageLineEdit.editingFinished.connect(self.update_tp_percentage)

        # Store the last order ID for tracking purposes
        self.last_order_id = None

        # Connect trading buttons: Buy, Sell, and Close Position
        self.ui.buyButton.clicked.connect(lambda: self.place_order("BUY"))
        self.ui.sellButton.clicked.connect(lambda: self.place_order("SELL"))
        self.ui.closePositionButton.clicked.connect(self.close_position)



    def place_order(self, side: str) -> None:
        """Executes a market order (BUY or SELL) with predefined parameters."""

        # Ensure Binance client is connected before placing the order
        if not self.binance_client.is_connected:
            return
        # Validate the symbol before proceeding
        if not self.symbol:
            return

        # Retrieve the latest price value
        price = self.price_value.value

        # Execute the market order
        order_id = place_market_order(
            client=self.binance_client.client,
            symbol=self.symbol,
            side=side,
            amount_usd=self.usd,
            precision=self.precision,
            price_precision=self.price_precision,
            st_percentage=self.st_percentage,
            tp_percentage=self.tp_percentage,
            price=price,
            use_decimal=self.use_decimal
        )
        # Store the last order ID if the order was successful
        if order_id:
            self.last_order_id = order_id

    def close_position(self) -> None:
        """Closes the last open position if an order ID exists."""

        if not self.last_order_id:
            return

        #Execute position closure using the stored order ID
        close_position_by_order_id(
            client=self.binance_client.client,
            symbol=self.symbol,
            order_id=self.last_order_id
        )
        # Clear the last order ID after successful closure
        self.last_order_id = None

    def update_precision_flags(self, precision: int | None) -> None:
        #If precision is defined and greater than 3, enable decimal usage
        self.use_decimal = precision is not None and precision > 3

    def update_precision(self) -> None:
        """Updates quantity and price precision settings for the current symbol."""
        if not self.symbol:
            self.precision = None
            self.price_precision = None
            return

        # Retrieve precision values from Binance API
        self.precision = get_quantity_precision(
            self.binance_client.client,
            self.symbol
        )
        self.price_precision = get_price_precision(
            self.binance_client.client,
            self.symbol
        )

        # Update precision flags based on retrieved values
        self.update_precision_flags(self.precision)

        # Log precision details for debugging purposes
        print(f"Quantity precision for {self.symbol} = {self.precision}")
        print(f"Price precision for {self.symbol} = {self.price_precision}")
        print(f"Decimal mode: {'ON' if self.use_decimal else 'OFF'}")

    def populate_saved_inputs(self) -> None:
        """Populates input fields with saved values, if available."""
        # Set stored USD amount, if available
        if self.usd is not None:
            self.ui.usdLineEdit.setText(str(self.usd))

        # Set stored stop-loss percentage, if available
        if self.st_percentage is not None:
            self.ui.st_percentageLineEdit.setText(str(self.st_percentage))

        # Set stored take-profit percentage, if available
        if self.tp_percentage is not None:
            self.ui.tp_percentageLineEdit.setText(str(self.tp_percentage))

    def update_usd(self) -> None:
        """Validates and updates the USD input value."""
        text = self.ui.usdLineEdit.text()
        try:
            value = float(text)
            if value <= 0:
                raise ValueError("USD must be positive")
            self.usd = value # Store valid USD amount
            self.save_settings("usd", self.usd)  # Save to settings file
        except ValueError:
            flash_input_error(self.ui.usdLineEdit)

    def update_st_percentage(self) -> None:
        """Validates and updates the stop-loss percentage value."""
        text = self.ui.st_percentageLineEdit.text()
        try:
            value = float(text)
            if not (0 < value < 100):
                raise ValueError("ST% must be between 0 and 100")

            self.st_percentage = value  # Store valid stop-loss percentage
            self.save_settings("st_percentage", self.st_percentage)  # Save to settings file
        except ValueError:
            flash_input_error(self.ui.st_percentageLineEdit)

    def update_tp_percentage(self) -> None:
        """Validates and updates the take-profit percentage value."""
        text = self.ui.tp_percentageLineEdit.text()
        try:
            value = float(text)
            if not (0 < value <= 100):
                raise ValueError("TP% must be between 0 and 100")

            self.tp_percentage = value  # Store valid take-profit percentage
            self.save_settings("tp_percentage", self.tp_percentage)  # Save to settings file
        except ValueError:
            flash_input_error(self.ui.tp_percentageLineEdit)

    def load_settings(self) -> dict:
        """Loads configuration parameters from config/settings.json."""
        if not os.path.exists(CONFIG_PATH):
            return {}
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_settings(self, key, value) -> None:
        """Saves a parameter to config/settings.json."""
        settings = self.load_settings()
        settings[key] = value

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    def validate_symbol(self, symbol: str) -> bool:
        """Validates the symbol input, checks Binance client connection,
        and verifies symbol existence.
        """
        if not symbol:
            print("Symbol not provided! Listener will not start.")
            return False

        if not self.binance_client.client:
            print("Error! Binance client is not connected.")
            return False

        if not is_valid_symbol(self.binance_client.client, symbol):
            print(f"Error! Trading pair {symbol} does not exist.")
            flash_input_error(self.ui.symbolLineEdit)
            return False

        return True

    def start_waiting_for_price(self) -> None:
        """Clears the event flag and starts the price check timer."""
        self.event.clear()
        self.check_event_timer.start()
        print("Waiting for the first price update...")

    def check_event(self) -> None:
        """Checks if the price update event is triggered and handles activation."""
        if self.event.is_set():
            self.check_event_timer.stop()
            print("Price updated! Switching status to Activated")
            self.update_pair_status(True)  # Update the trading pair status

    def auto_activate_symbol(self) -> None:
        """Automatically starts the WebSocket and waits for the first price update."""
        # Validate the symbol before proceeding
        if not self.validate_symbol(self.symbol):
            return

        # Update quantity and price precision
        self.update_precision()
        # Clear the event flag to prevent false event.wait() triggers
        self.event.clear()
        print(f"Auto-starting WebSocket for {self.symbol}")
        # Start the WebSocket listener
        self.start_listener()
        # Initiate non-blocking price waiting using a timer
        self.start_waiting_for_price()

    def activate_symbol(self) -> None:
        """Starts WebSocket listener for a new symbol
        and waits for the first price update.
        """
        new_symbol = self.ui.symbolLineEdit.text().strip()

        # Validate the symbol before proceeding
        if not self.validate_symbol(new_symbol):
            print(
                "Invalid symbol! Stopping listener"
                "and setting status to 'Disconnected'."
            )
            self.stop_listener()
            self.event.clear()
            self.update_pair_status(False)
            return

        # If symbol has changed, restart the WebSocket connection
        if new_symbol != self.symbol:
            print(f"Restarting WebSocket for {new_symbol}")
            self.stop_listener()
            self.event.clear()
            print("Setting status to Disconnected")
            self.update_pair_status(False)

            # Allow GUI to refresh before proceeding
            QtWidgets.QApplication.processEvents()

            # Update symbol and precision settings
            self.symbol = new_symbol
            self.save_settings("symbol", self.symbol)
            self.update_precision()
            self.start_listener()

        # Begin non-blocking price monitoring
        self.start_waiting_for_price()

    def update_pair_status(self, is_active: bool) -> None:
        """Updates the connection status icon for the trading pair."""
        if is_active:
            self.ui.pairStatusIcon.setPixmap(
                QtGui.QPixmap(":/icons/activated_pair.png")
            )
        else:
            self.ui.pairStatusIcon.setPixmap(
                QtGui.QPixmap(":/icons/disconected_pair.png")
            )

    def start_listener(self) -> None:
        """Starts the WebSocket listener in a separate process
        and updates status upon receiving the first price update.
        """
        print(f"Starting WebSocket for {self.symbol}...")
        # Set status to "Disconnected" until WebSocket receives the first price update
        self.update_pair_status(False)

        # Launch WebSocket listener in a separate process
        self.ws_process = multiprocessing.Process(
            target=run_listener,
            args=(self.symbol, self.price_value, self.event)
        )
        self.ws_process.start()

        print("WebSocket started successfully!")

    def stop_listener(self) -> None:
        """Stops the WebSocket listener if it is running."""
        if self.ws_process:
            print("Stopping current WebSocket...")

            # Terminate and clean up the WebSocket process
            self.ws_process.terminate()
            self.ws_process.join()
            self.ws_process = None

            # Update status based on closing condition
            if not self.closing:
                print("Skipping update_pair_status(False)— "
                      "status will be updated externally")
            else:
                self.update_pair_status(False)

    def closeEvent(self, event) -> None:
        """Handles application shutdown by stopping
        all processes before exiting.
        """
        self.closing = True
        print("Shutting down...")

        # Stop WebSocket listener if it is running
        self.stop_listener()

        # Properly close the application
        event.accept()
        sys.exit(0)

    def refresh_connection_status(self) -> None:
        """Automatically checks and updates the connection status."""
        self.update_connection_status(self.binance_client.is_connected)

    def manual_connect(self) -> None:
        """Allows the user to enter API keys manually
        and initiate the connection."""

        # Retrieve API keys from input fields
        api_key = self.ui.apiKeyLineEdit.text()
        api_secret = self.ui.secretKeyLineEdit.text()
        if not api_key or not api_secret:
            print("API keys are missing")
            return

        self.binance_client.save_keys(api_key, api_secret)
        self.refresh_connection_status()

    def update_connection_status(self, is_connected: bool) -> None:
        """Updates the connection status label and applies appropriate styling."""
        if is_connected:
            self.ui.connectionStatusLabel.setText("Connected")
            self.ui.connectionStatusLabel.setStyleSheet(
                "background-color: green;"
                "color: white;"
                "padding: 5px;"
                "border-radius: 5px;"
            )
        else:
            self.ui.connectionStatusLabel.setText("Not Сonnected")
            self.ui.connectionStatusLabel.setStyleSheet(
                "background-color: red;"
                "color: white;"
                "padding: 5px;"
                "border-radius: 5px;"
            )

    def load_styles(self) -> None:
        """Loads styles from the `style.qss` file and applies them."""
        try:
            with open(STYLE_PATH, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"The style file was not found at the specified path: {STYLE_PATH}")

    def update_window_mask(self) -> None:
        """Applies a rounded corner mask to the window."""
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.rect())
        # Set the rounding radius
        radius = 9.0
        path.addRoundedRect(rect, radius, radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event) -> None:
        """window resizing by updating the mask and adjusting position."""
        super().resizeEvent(event)
        self.update_window_mask()

        # Adjust window position dynamically based on screen geometry
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.right() - self.width(), 0)

    def on_tab_changed(self, index: int) -> None:
        """Handles tab switching and adjusts window size accordingly."""
        if index == 0:
            self.resize(180, self.window_height)
        elif index == 1:
            self.resize(650, 300)
