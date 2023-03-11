from pySerialTransfer import pySerialTransfer as txfer
from pySerialTransfer.pySerialTransfer import InvalidSerialPort


class ArduinoHandler:
    """
    Handles connections and messaging to an Arduino.

    Attributes:
        conn:   PySerialTransfer connection; has None value when no successsful
                connection has been made
        port:   name of connection port currently being used; has None value when
                no successful port has been used
    """

    def __init__(self):
        self.conn = None
        self.port = None

    def connect(self, port: str) -> None:
        """
        Initializes a connection to an arduino at a specified port. If successful,
        the conn and port attributes are updated

        Args:
            cropped_frame:  cropped frame img containing the microbot, indicated by list of coords
            bot_blur_list:  list of previous blur values from each frame, originally contained=
                            in a Robot class
            debug_mode: Optional debugging boolean; if True, debugging information is printed
        Returns:
            List of contours
        """
        if self.conn is None:
            try:
                self.conn = txfer.SerialTransfer(port)
                self.port = port
                self.conn.open()
                print(f" -- Arduino Connection initialized using port {port} --")
            except InvalidSerialPort:
                print("Could not connect to arduino, disabling")
                self.conn = None
                self.port = None
        else:
            print(
                f"Connection already initialized at port {self.port}, new port {port} ignored"
            )

    def send(self, typ: float, input1: float, input2: float, input3: float) -> None:
        """
        Applies a pipeline of preprocessing to a cropped frame, then gets the contours from the
        cropped, preprocesed image.

        Args:
            cropped_frame:  cropped frame img containing the microbot, indicated by list of coords
            bot_blur_list:  list of previous blur values from each frame, originally contained=
                            in a Robot class
            debug_mode: Optional debugging boolean; if True, debugging information is printed
        Returns:
            List of contours
        """
        if self.conn is None:
            print("Connection not initialized, message not sent")
        else:
            data = [float(typ), float(input1), float(input2), float(input3)]
            message = self.conn.tx_obj(data)
            self.conn.send(message)
            print("Data sent:", [float(typ), float(input1), float(input2), float(input3) ])

    def close(self) -> None:
        """
        Closes the current connection, if applicable

        Args:
            None
        Returns:
            None
        """
        if self.conn is None:
            print("Connection not initialized, ignoring close() call")
        else:
            print(f"Closing connection at port {self.port}")
            self.conn.close()
