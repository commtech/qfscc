import sys

from PySide.QtCore import Signal
from PySide.QtGui import *

from widgets import *

from fscc.tools import list_ports


class PortForm(QDialog):
    apply_changes = Signal()

    def __init__(self):
        super(PortForm, self).__init__()

        self.port_name = FPortName(self.apply_changes)
        firmware = FFirmware(self.port_name)
        clock_frequency = FClockFrequency(self.port_name)
        registers = FRegisters(self.port_name)
        append_status = FAppendStatus(self.port_name)
        append_timestamp = FAppendTimestamp(self.port_name)
        rx_multiple = FRxMultiple(self.port_name)
        ignore_timeout = FIgnoreTimeout(self.port_name)
        tx_modifiers = FTxModifiers(self.port_name)
        commands = FCommands(self.port_name)
        memory_cap = FMemoryCap(self.port_name)

        buttons = QDialogButtonBox(QDialogButtonBox.Apply |
                                        QDialogButtonBox.Ok |
                                        QDialogButtonBox.Close)

        settings = QVBoxLayout()
        settings.addWidget(self.port_name)
        settings.addWidget(firmware)
        settings.addWidget(clock_frequency)
        settings.addWidget(append_status)
        settings.addWidget(append_timestamp)
        settings.addWidget(rx_multiple)
        settings.addWidget(ignore_timeout)
        settings.addWidget(tx_modifiers)
        settings.addWidget(commands)
        settings.addWidget(memory_cap)

        layout_options = QHBoxLayout()
        layout_options.addLayout(settings, 1)
        layout_options.addWidget(registers)
        layout_options.addStretch()

        # Create layout and add widgets
        layout = QVBoxLayout()

        layout.addLayout(layout_options)
        layout.addWidget(buttons)

        # Set dialog layout
        self.setLayout(layout)

        apply_button = buttons.button(QDialogButtonBox.Apply)
        apply_button.clicked.connect(self.apply_clicked)

        buttons.accepted.connect(self.ok_clicked)
        buttons.rejected.connect(self.close_clicked)

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

    try:
        # Try and set the default port after the form is already showing
        default_port = sorted(list_ports.fsccports())[0][1]
        form.port_name.set_port(default_port)
    except IndexError:
        pass

    # Run the main Qt loop
    sys.exit(app.exec_())
