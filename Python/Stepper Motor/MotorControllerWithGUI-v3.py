import sys
import random
import serial
import serial.tools.list_ports
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit, QStyleFactory, QStyle
from PySide6 import QtWidgets, QtCore

class MoveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.numbers = ["2038", "5000", "0", "3000", "500", "1000", "1500"]
        self.counter = 0
        self.incrementStep = 100
        self.text = QtWidgets.QLabel("0", alignment=QtCore.Qt.AlignCenter)
        self.selectedPort = None 

        # Main layout
        self.mainLayout = QHBoxLayout(self)
        self.FindComPorts()

        # Left column for random buttons
        self.randomLayout = QVBoxLayout()
        button = QtWidgets.QPushButton("Random Next Position ")
        button.clicked.connect(self.sendRandomNumber)
        self.randomLayout.addWidget(button)

        # Middle column for de/incremental buttons
        self.fixedLayout = QVBoxLayout()
        incrementButton = QPushButton(f"Increment button")
        incrementButton.clicked.connect(self.sendIncrementedNumber)
        self.fixedLayout.addWidget(incrementButton)

        decrementButton = QPushButton(f"Decrement button")
        decrementButton.clicked.connect(self.sendDecrementedNumber)
        self.fixedLayout.addWidget(decrementButton)

        # Right column for entering text
        self.textLayout = QVBoxLayout()
        textField = QLineEdit(f"1000")
        self.textLayout.addWidget(textField)
        textButton = QPushButton(f"Send text")
        textButton.clicked.connect(lambda: self.sendTextField(textField))
        self.textLayout.addWidget(textButton)

        # Add widgets to main layout
        self.mainLayout.addLayout(self.randomLayout)
        self.mainLayout.addWidget(self.text)
        self.mainLayout.addLayout(self.fixedLayout)
        self.mainLayout.addLayout(self.textLayout)

    @QtCore.Slot()
    def sendRandomNumber(self):
        # Sends a random number to the selected COM port
        if self.selectedPort and self.selectedPort.is_open:
            randomValue = random.choice(self.numbers)
            self.text.setText(randomValue)
            self.selectedPort.write(randomValue.encode())

        else:
            print("No COM port selected or connected")

    @QtCore.Slot()
    def sendIncrementedNumber(self):
        if self.selectedPort and self.selectedPort.is_open:
            self.counter += self.incrementStep
            incrementValue = str(self.counter)
            self.text.setText(incrementValue)
            self.selectedPort.write(incrementValue.encode())
        else:
            print("No COM port selected or connected")

    @QtCore.Slot()
    def sendDecrementedNumber(self):
        if self.selectedPort and self.selectedPort.is_open:
            self.counter -= self.incrementStep
            decrementValue = str(self.counter)
            self.text.setText(decrementValue)
            self.selectedPort.write(decrementValue.encode())
        else:
            print("No COM port selected or connected")

    @QtCore.Slot()
    def sendTextField(self, textField):
        if self.selectedPort and self.selectedPort.is_open:
            valueToSend = textField.text()
            self.selectedPort.write(valueToSend.encode())

    def FindComPorts(self):
        #Scan for COM ports and add buttons for each port. This is for arduino connection
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            comButton = QPushButton(f"Connect to {port.device}")
            comButton.clicked.connect(lambda _, p=port.device: self.selectComPort(p))
            self.mainLayout.addWidget(comButton)

    def selectComPort(self, portName):
        #Select COM port for communication with COM. This is for arduino connection
        try:
            #close existing port if open
            if self.selectedPort and self.selectedPort.is_Open:
                self.selectedPort.close()

            #Open new selected port
            self.selectedPort = serial.Serial(portName, baudrate=9600, timeout=1)
            print(f"Connected to {portName}")
            self.text.setText(f"Connected to {portName}")
        
        except serial.SerialException as exception:
            print (f"Failed to connect to {portName}: {exception}")
            self.text.setText(f"Connection Failed")
            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoveWidget()

    window.show()
    sys.exit(app.exec())
