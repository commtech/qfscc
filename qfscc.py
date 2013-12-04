import sys

from PySide.QtCore import Signal
from PySide.QtGui import *

from widgets import *


class PortForm(QDialog):
    apply_changes = Signal()

    def __init__(self):
        super(PortForm, self).__init__()

        self.port_name = FPortName(self.apply_changes)
        self.firmware = FFirmware(self.port_name)
        self.clock_frequency = FClockFrequency(self.port_name)
        self.registers = FRegisters(self.port_name)
        self.append_status = FAppendStatus(self.port_name)
        self.append_timestamp = FAppendTimestamp(self.port_name)
        self.rx_multiple = FRxMultiple(self.port_name)
        self.ignore_timeout = FIgnoreTimeout(self.port_name)
        self.tx_modifiers = FTxModifiers(self.port_name)
        self.commands = FCommands(self.port_name)
        self.memory_cap = FMemoryCap(self.port_name)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Apply |
                                        QDialogButtonBox.Ok |
                                        QDialogButtonBox.Close)

        self.firmware.setEnabled(False)
        self.clock_frequency.setEnabled(False)
        self.append_status.setEnabled(False)
        self.append_timestamp.setEnabled(False)
        self.rx_multiple.setEnabled(False)
        self.ignore_timeout.setEnabled(False)
        self.tx_modifiers.setEnabled(False)
        self.commands.setEnabled(False)
        self.memory_cap.setEnabled(False)
        self.registers.setEnabled(False)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout_options = QHBoxLayout()
        layout_left = QVBoxLayout()

        layout.addLayout(layout_options)
        layout_options.addLayout(layout_left, 1)
        layout_options.addWidget(self.registers)
        layout_options.addStretch()
        layout.addWidget(self.buttons)

        layout_left.addWidget(self.port_name)
        layout_left.addWidget(self.firmware)
        layout_left.addWidget(self.clock_frequency)
        layout_left.addWidget(self.append_status)
        layout_left.addWidget(self.append_timestamp)
        layout_left.addWidget(self.rx_multiple)
        layout_left.addWidget(self.ignore_timeout)
        layout_left.addWidget(self.tx_modifiers)
        layout_left.addWidget(self.commands)
        layout_left.addWidget(self.memory_cap)

        # Set dialog layout
        self.setLayout(layout)

        apply_button = self.buttons.button(QDialogButtonBox.Apply)
        apply_button.clicked.connect(self.apply_clicked)
        self.buttons.accepted.connect(self.ok_clicked)
        self.buttons.rejected.connect(self.close_clicked)

        #TODO
        self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Fastcom FSCC Settings')

    def apply_clicked(self):
        self.apply_changes.emit()

    def ok_clicked(self):
        self.apply_changes.emit()
        self.close()

    def close_clicked(self):
        self.close()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the form
    form = PortForm()
    form.show()

    # Try and set the default port after the form is already showing
    default_port = 'FSCC0' if os.name == 'nt' else 'fscc0'
    form.port_name.set_port(default_port)

    # Run the main Qt loop
    sys.exit(app.exec_())
