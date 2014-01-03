from PySide.QtCore import Signal
from PySide.QtGui import *

from fscc.tools import list_ports
from array import array

import fscc
import os
import struct
import re


class FBoxLayout(QWidget):

    def __init__(self, layout_type, *args, **kwargs):
        super(FBoxLayout, self).__init__(*args, **kwargs)

        self.layout = layout_type()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def addWidget(self, widget):
        self.layout.addWidget(widget)

    def addLayout(self, widget):
        self.layout.addLayout(widget)

    def addStretch(self):
        self.layout.addStretch()


class FHBoxLayout(FBoxLayout):

    def __init__(self, *args, **kwargs):
        super(FHBoxLayout, self).__init__(QHBoxLayout, *args, **kwargs)


class FVBoxLayout(FBoxLayout):

    def __init__(self, *args, **kwargs):
        super(FVBoxLayout, self).__init__(QVBoxLayout, *args, **kwargs)


def is_fscc_port(filename):
        if filename.find('fscc') != -1:
            return True
        else:
            return False


class FPortName(FHBoxLayout):
    port_changed = Signal(fscc.Port)
    apply_changes = Signal(fscc.Port)

    def __init__(self, apply_changes_signal):
        super(FPortName, self).__init__()

        self.port = None

        self.label = QLabel('Port')

        port_names = sorted([x[1] for x in list_ports.fsccports()])

        self.combo_box = QComboBox()
        self.combo_box.addItems(port_names)
        self.combo_box.currentIndexChanged.connect(self.currentIndexChanged)
        self.combo_box.setCurrentIndex(-1)

        apply_changes_signal.connect(self.apply_changes_clicked)

        self.addWidget(self.label)
        self.addWidget(self.combo_box)

    def set_port(self, port_name):
        index = self.combo_box.findText(port_name)

        if index >= 0:
            self.combo_box.setCurrentIndex(index)

    def currentIndexChanged(self):
        if self.port:
            self.port.close()
            self.port = None

        port_name = self.combo_box.currentText()

        if port_name:
            port_num = int(re.search('(\d+)$', port_name).group(0))

            msgBox = QMessageBox()
            msgBox.setWindowTitle('Problem Opening Port')
            msgBox.setText('There was a problem opening this port.')
            msgBox.setIcon(QMessageBox.Information)

            try:
                self.port = fscc.Port(port_num, None, None)
            except fscc.PortNotFoundError as e:
                msgBox.exec_()
            except IOError as e:
                msgBox.exec_()
                raise e

        # Will be None if port connection didn't complete
        self.port_changed.emit(self.port)

    def apply_changes_clicked(self):
        self.apply_changes.emit(self.port)


class PortChangedTracker:

    def __init__(self, port_widget):
        super(PortChangedTracker, self).__init__()

        port_widget.port_changed.connect(self._port_changed)
        port_widget.apply_changes.connect(self._apply_changes)

        self.setEnabled(False)

    def _port_changed(self, port):
        # There isn't a port opened so we disable the widget
        if port is None:
            self.setEnabled(False)
            return

        try:
            # Call port_changed on child class
            self.port_changed(port)
        except AttributeError:
            # This functionality isn't supported on this port
            self.unsupported()
        except:  # Raise any random unknown exceptions for debugging
            raise
        else:
            self.supported()

    def _apply_changes(self, port):
        if self.isEnabled():
            self.apply_changes(port)

    def port_changed(self, port):
        raise NotImplementedError

    def apply_changes(self, port):
        raise NotImplementedError

    def supported(self):
        self.setEnabled(True)
        self.setToolTip('')

    def unsupported(self):
        self.setEnabled(False)
        self.setToolTip('This feature is not supported on this port.')


class FRegisters(FVBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FVBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.register_names = fscc.Port.Registers.editable_register_names
        self.register_names.remove(*fscc.Port.Registers.writeonly_register_names)

        table = QTableWidget(len(self.register_names), 1)

        for i, register_name in enumerate(self.register_names):
            setattr(self, register_name.lower(), QTableWidgetItem('{:08x}'.format(0)))
            table.setItem(i, 0, getattr(self, register_name.lower()))

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.hide()

        table.setVerticalHeaderLabels(self.register_names)
        table.resizeColumnsToContents()

        self.addWidget(table)

    def port_changed(self, port):
        for register_name in self.register_names:
            register_value = getattr(port.registers, register_name)
            getattr(self, register_name.lower()).setText('{:08x}'.format(register_value))

    def apply_changes(self, port):
        for register_name in self.register_names:
            register_value = int(getattr(self, register_name.lower()).text(), 16)
            setattr(port.registers, register_name, register_value)


class FClockFrequency(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        label = QLabel('Clock Frequency')
        self.line_edit = QLineEdit()

        self.addWidget(label)
        self.addWidget(self.line_edit)
        self.addStretch()

    def port_changed(self, port):
        self.line_edit.setText('')

    def apply_changes(self, port):
        value_range = (15000, 270000000) #TODO: Move to pyfscc?

        if self.line_edit.text():
            error_title = 'Invalid Clock Frequency'
            error_text = 'Make sure to set the clock frequency to a value ' \
                'between {:,.0f} and {:,.0f} Hz.'.format(*value_range)

            try:
                port.clock_frequency = int(self.line_edit.text())
            except:
                msgBox = QMessageBox()
                msgBox.setWindowTitle(error_title)
                msgBox.setText(error_text)
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.exec_()


class FBooleanAttribute(QCheckBox, PortChangedTracker):

    def __init__(self, label, attribute, port_widget=None):
        QCheckBox.__init__(self, label)
        PortChangedTracker.__init__(self, port_widget)

        self.attribute = attribute

    def port_changed(self, port):
        self.setChecked(getattr(port, self.attribute))

    def apply_changes(self, port):
        setattr(port, self.attribute, self.isChecked())


class FAppendStatus(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(FAppendStatus, self).__init__(
            'Append Status', 'append_status', port_widget)


class FAppendTimestamp(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(FAppendTimestamp, self).__init__(
            'Append Timestamp', 'append_timestamp', port_widget)


class FRxMultiple(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(FRxMultiple, self).__init__(
            'RX Multiple', 'rx_multiple', port_widget)


class FIgnoreTimeout(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(FIgnoreTimeout, self).__init__(
            'Ignore Timeout', 'ignore_timeout', port_widget)


class FTxModifiers(FVBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FVBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.xrep_check_box = QCheckBox('Repeat Frames')

        self.label = QLabel('Transmit On')
        self.options = QComboBox()

        self.options.addItem('Write (Default)')
        self.options.addItem('Timer')
        self.options.addItem('External Signal')

        box = QHBoxLayout()

        self.txt_radio_button = QRadioButton('Transmit on Timer')
        self.txext_radio_button = QRadioButton('Transmit on External Signal')

        box.addWidget(self.label)
        box.addWidget(self.options)

        self.addWidget(self.xrep_check_box)
        self.addLayout(box)

        self.xrep_check_box.toggled.connect(self.check_box_toggled)

    def check_box_toggled(self):
        if self.xrep_check_box.isChecked():
            if self.options.currentIndex() == 2:
                self.options.setCurrentIndex(0)
            self.options.removeItem(2)
        else:
            self.options.addItem('External Signal')

    def port_changed(self, port):
        tx_modifiers = port.tx_modifiers

        self.options.setCurrentIndex(0)

        self.xrep_check_box.setChecked(tx_modifiers & fscc.XREP)

        if tx_modifiers & fscc.TXT:
            self.options.setCurrentIndex(1)

        if tx_modifiers & fscc.TXEXT:
            self.options.setCurrentIndex(2)

    def apply_changes(self, port):
        tx_modifiers = 0

        if self.xrep_check_box.isChecked():
            tx_modifiers |= fscc.XREP

        if self.options.currentIndex() == 1:
            tx_modifiers |= fscc.TXT

        if self.options.currentIndex() == 2:
            tx_modifiers |= fscc.TXEXT

        port.tx_modifiers = tx_modifiers


class FMemoryCap(QGroupBox, PortChangedTracker):

    def __init__(self, port_widget=None):
        QGroupBox.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.setTitle('Memory Cap (Bytes)')
        self.setFlat(True)

        box = QVBoxLayout()
        self.setLayout(box)

        input_label = QLabel('Input')
        output_label = QLabel('Output')

        self.input_line_edit = QLineEdit()
        self.output_line_edit = QLineEdit()

        input_box = QHBoxLayout()
        input_box.addWidget(input_label)
        input_box.addStretch()
        input_box.addWidget(self.input_line_edit)

        output_box = QHBoxLayout()
        output_box.addWidget(output_label)
        output_box.addStretch()
        output_box.addWidget(self.output_line_edit)

        box.addLayout(input_box)
        box.addLayout(output_box)

    def port_changed(self, port):
        self.input_line_edit.setText(str(port.memory_cap.input))
        self.output_line_edit.setText(str(port.memory_cap.output))

    # todo: add checks
    def apply_changes(self, port):
        port.memory_cap.input = int(self.input_line_edit.text())
        port.memory_cap.output = int(self.output_line_edit.text())


class FCommands(QGroupBox, PortChangedTracker):

    def __init__(self, port_widget=None):
        QGroupBox.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.setTitle('Commands')
        self.setFlat(True)

        box = QHBoxLayout()
        self.setLayout(box)

        purge_button = QPushButton('Purge')
        timr_button = QPushButton('Start Timer')
        stimr_button = QPushButton('Stop Timer')

        purge_button.clicked.connect(self.purge_clicked)
        timr_button.clicked.connect(self.timr_clicked)
        stimr_button.clicked.connect(self.stimr_clicked)

        box.addWidget(purge_button)
        box.addWidget(timr_button)
        box.addWidget(stimr_button)

    def port_changed(self, port):
        self._port = port

    def apply_changes(self, port):
        pass

    def purge_clicked(self):
        self._port.purge()

    def timr_clicked(self):
        self._port.registers.CMDR = 0x00000001

    def stimr_clicked(self):
        self._port.registers.CMDR = 0x00000001


class FFirmware(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        label = QLabel('Firmware Version')
        self.version = QLabel('')

        self.addWidget(label)
        self.addWidget(self.version)

    def port_changed(self, port):
        prev = (port.registers.VSTR & 0x0000ff00) >> 8
        frev = port.registers.VSTR & 0x000000ff
        self.version.setText('{:2x}.{:02x}'.format(prev, frev))

    def apply_changes(self, port):
        pass
