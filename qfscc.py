"""
    Copyright (C) 2014 Commtech, Inc.

    This file is part of qfscc.

    qfscc is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    qfscc is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with qfscc.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys

from PySide.QtCore import Signal
from PySide.QtGui import *

from widgets import *
from dialogs import *

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

        buttons = FDialogButtonBox(self.port_name)
        buttons.apply.connect(self.apply_clicked)
        buttons.accepted.connect(self.ok_clicked)
        buttons.rejected.connect(self.close_clicked)

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

        layout_top = QHBoxLayout()
        layout_top.addLayout(settings, 1)
        layout_top.addWidget(registers)
        layout_top.addStretch()

        layout = QVBoxLayout()

        layout.addLayout(layout_top)
        layout.addWidget(buttons)

        # Set dialog layout
        self.setLayout(layout)

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
    app = QApplication(sys.argv)

    form = PortForm()
    form.show()

    ports = sorted(list_ports.fsccports())

    if ports:
        form.port_name.set_port(ports[0][1])
    else:
        form.port_name.set_port(None)
        FNoPortsFound().exec_()

    # Run the main Qt loop
    sys.exit(app.exec_())
