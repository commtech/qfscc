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

import re
import json

from PySide.QtCore import Signal
from PySide.QtGui import *

from dialogs import *

import fscc
from fscc.tools import list_ports


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


class FPortName(FHBoxLayout):
    port_changed = Signal(fscc.Port)
    apply_changes = Signal(fscc.Port)

    def __init__(self, apply_changes_signal):
        super(FPortName, self).__init__()

        self.port = None

        self.label = QLabel('Port')

        port_names = [x[1] for x in sorted(list_ports.fsccports())]

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

            try:
                self.port = fscc.Port(port_num, None, None)
            except fscc.PortNotFoundError:
                FPortNotFound().exec_()
            except fscc.InvalidAccessError:
                FInvalidAccess().exec_()

        # Will be None if port connection didn't complete
        self.port_changed.emit(self.port)

    def apply_changes_clicked(self):
        self.apply_changes.emit(self.port)


class PortChangedTracker:

    def __init__(self):
        super(PortChangedTracker, self).__init__()

        self.setEnabled(False)

    def attach_port_changed(self, signal):
        signal.connect(self._port_changed)

    def attach_apply_changes(self, signal):
        signal.connect(self._apply_changes)

    def attach_import_settings(self, signal):
        signal.connect(self._import_settings)

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

    def _import_settings(self, settings):
        if self.isEnabled():
            self.import_settings(settings)

    def port_changed(self, port):
        raise NotImplementedError

    def apply_changes(self, port):
        raise NotImplementedError

    def import_settings(self, settings):
        raise NotImplementedError

    def supported(self):
        self.setEnabled(True)
        self.setToolTip('')

    def unsupported(self):
        self.setEnabled(False)
        self.setToolTip('This feature is not supported on this port.')


class FRegisters(FVBoxLayout, PortChangedTracker):

    def __init__(self):
        FVBoxLayout.__init__(self)
        PortChangedTracker.__init__(self)

        self.register_names = fscc.Port.Registers.editable_register_names
        self.register_names.remove(
            *fscc.Port.Registers.writeonly_register_names)

        table = QTableWidget(len(self.register_names), 1)

        for i, register_name in enumerate(self.register_names):
            widget = QTableWidgetItem('{:08x}'.format(0))
            setattr(self, register_name.lower(), widget)
            table.setItem(i, 0, getattr(self, register_name.lower()))

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.hide()

        table.setVerticalHeaderLabels(self.register_names)
        table.resizeColumnsToContents()

        self.addWidget(table)

    def port_changed(self, port):
        for reg_name in self.register_names:
            register_value = getattr(port.registers, reg_name)
            hex_display = '{:08x}'.format(register_value)
            getattr(self, reg_name.lower()).setText(hex_display)

    def apply_changes(self, port):
        for reg_name in self.register_names:
            register_value = int(getattr(self, reg_name.lower()).text(), 16)
            setattr(port.registers, reg_name, register_value)

    def import_settings(self, settings):
        for name, value in settings['registers'].items():
            try:
                hex_display = '{:08x}'.format(int(value, 0))
                getattr(self, name.lower()).setText(hex_display)
            except AttributeError:
                pass


class FClockFrequency(FHBoxLayout, PortChangedTracker):

    def __init__(self):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self)

        label = QLabel('Clock Frequency')
        self.line_edit = QLineEdit()

        self.addWidget(label)
        self.addWidget(self.line_edit)
        self.addStretch()

    def port_changed(self, port):
        self.line_edit.setText('')

    def apply_changes(self, port):
        if self.line_edit.text():
            try:
                port.clock_frequency = int(self.line_edit.text())
            except fscc.InvalidParameterError:
                FInvalidClockFrequency().exec_()
            except ValueError:
                FInvalidClockFrequency().exec_()

    def import_settings(self, settings):
        pass


class FBooleanAttribute(QCheckBox, PortChangedTracker):

    def __init__(self, label, attribute):
        QCheckBox.__init__(self, label)
        PortChangedTracker.__init__(self)

        self.attribute = attribute

    def port_changed(self, port):
        self.setChecked(getattr(port, self.attribute))

    def apply_changes(self, port):
        setattr(port, self.attribute, self.isChecked())

    def import_settings(self, settings):
        self.setChecked(settings[self.attribute])


class FAppendStatus(FBooleanAttribute):

    def __init__(self):
        super(FAppendStatus, self).__init__(
            'Append Status', 'append_status')


class FAppendTimestamp(FBooleanAttribute):

    def __init__(self):
        super(FAppendTimestamp, self).__init__(
            'Append Timestamp', 'append_timestamp')


class FRxMultiple(FBooleanAttribute):

    def __init__(self):
        super(FRxMultiple, self).__init__(
            'RX Multiple', 'rx_multiple')


class FIgnoreTimeout(FBooleanAttribute):

    def __init__(self):
        super(FIgnoreTimeout, self).__init__(
            'Ignore Timeout', 'ignore_timeout')


class FTxModifiers(FVBoxLayout, PortChangedTracker):

    def __init__(self):
        FVBoxLayout.__init__(self)
        PortChangedTracker.__init__(self)

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

    def import_settings(self, settings):
        tx_modifiers = settings['tx_modifiers']

        self.options.setCurrentIndex(0)

        self.xrep_check_box.setChecked(tx_modifiers & fscc.XREP)

        if tx_modifiers & fscc.TXT:
            self.options.setCurrentIndex(1)

        if tx_modifiers & fscc.TXEXT:
            self.options.setCurrentIndex(2)


class FMemoryCap(QGroupBox, PortChangedTracker):

    def __init__(self):
        QGroupBox.__init__(self)
        PortChangedTracker.__init__(self)

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

    def apply_changes(self, port):
        try:
            input_memcap = int(self.input_line_edit.text())
            output_memcap = int(self.output_line_edit.text())

            if input_memcap < 0 or output_memcap < 0:
                FInvalidMemoryCap().exec_()
        except ValueError:
            FInvalidMemoryCap().exec_()
        else:
            port.memory_cap.input = input_memcap
            port.memory_cap.output = output_memcap

    def import_settings(self, settings):
        self.input_line_edit.setText(str(settings['memory_cap']['input']))
        self.output_line_edit.setText(str(settings['memory_cap']['output']))


class FCommands(QGroupBox, PortChangedTracker):

    def __init__(self):
        QGroupBox.__init__(self)
        PortChangedTracker.__init__(self)

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

    def import_settings(self, settings):
        pass

    def purge_clicked(self):
        self._port.purge()

    def timr_clicked(self):
        self._port.registers.CMDR = 0x00000001

    def stimr_clicked(self):
        self._port.registers.CMDR = 0x00000001


class FFileOptions(QGroupBox, PortChangedTracker):
    import_selected = Signal(dict)

    def __init__(self):
        QGroupBox.__init__(self)
        PortChangedTracker.__init__(self)

        self.setTitle('Settings')
        self.setFlat(True)

        box = QHBoxLayout()
        self.setLayout(box)

        import_button = QPushButton('Import')
        export_button = QPushButton('Export')
        defaults_button = QPushButton('Defaults')

        import_button.clicked.connect(self.import_clicked)
        export_button.clicked.connect(self.export_clicked)
        defaults_button.clicked.connect(self.defaults_clicked)

        box.addWidget(import_button)
        box.addWidget(export_button)
        box.addWidget(defaults_button)

    def import_clicked(self):
        filename, filter = QFileDialog.getOpenFileName(self, 'Open Settings', None, 'Settings Files (*.fscc)')
        try:
            with open(filename, 'r') as infile:
                try:
                    settings = json.load(infile)
                except ValueError:
                    FInvalidSettingsFile().exec_()
                else:
                    self.import_selected.emit(settings)
        except FileNotFoundError: # Handle 'Cancel' situation
            pass

    def export_clicked(self):
        filename, filter = QFileDialog.getSaveFileName(self, 'Save Settings', None, 'Settings Files (*.fscc)')
        try:
            with open(filename, 'w') as outfile:
                outfile.write(self._port.to_json(sort_keys=True, indent=4))
        except FileNotFoundError: # Handle 'Cancel' situation
            pass

    def defaults_clicked(self):
        try:
            with open('defaults.fscc', 'r') as infile:
                settings = json.load(infile)
                self.import_selected.emit(settings)
        except FileNotFoundError: # TODO: Handle missing defaults.fscc
            pass

    def port_changed(self, port):
        self._port = port

    def apply_changes(self, port):
        pass

    def import_settings(self, port):
        pass


class FFirmware(FHBoxLayout, PortChangedTracker):

    def __init__(self):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self)

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

    def import_settings(self, settings):
        pass


class FDialogButtonBox(QDialogButtonBox, PortChangedTracker):
    apply = Signal()

    def __init__(self):
        QDialogButtonBox.__init__(
            self,
            QDialogButtonBox.Apply |
            QDialogButtonBox.Ok |
            QDialogButtonBox.Close)

        PortChangedTracker.__init__(self)

        self.apply_button = self.button(QDialogButtonBox.Apply)
        self.apply_button.clicked.connect(self.apply_clicked)
        self.apply_button.setEnabled(False)

        self.ok_button = self.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)

        self.close_button = self.button(QDialogButtonBox.Close)
        self.close_button.setEnabled(True)

        self.setEnabled(True)

    def apply_clicked(self):
        self.apply.emit()

    def _port_changed(self, port):
        self.apply_button.setEnabled(bool(port))
        self.ok_button.setEnabled(bool(port))
        self.close_button.setEnabled(True)

    def apply_changes(self, port):
        pass

    def import_settings(self, settings):
        pass
