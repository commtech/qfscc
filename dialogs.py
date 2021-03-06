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

from PySide.QtGui import *


class FNoPortsFound(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FNoPortsFound, self).__init__(*args, **kwargs)

        self.setWindowTitle('No FSCC Ports Found')
        self.setText('There wasn\'t any FSCC ports found. Make sure you '
                     'have a card inserted and the driver loaded.')
        self.setIcon(QMessageBox.Information)


class FPortNotFound(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FPortNotFound, self).__init__(*args, **kwargs)

        self.setWindowTitle('Problem Opening Port')
        self.setText('There was a problem opening this port. Make sure the '
                     'port is enabled.')
        self.setIcon(QMessageBox.Information)


class FInvalidAccess(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FInvalidAccess, self).__init__(*args, **kwargs)

        self.setWindowTitle('Insufficient Permissions')
        self.setText('There was a problem opening this port. Make sure you '
                     'have sufficient permissions.')
        self.setIcon(QMessageBox.Warning)


class FInvalidClockFrequency(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FInvalidClockFrequency, self).__init__(*args, **kwargs)

        value_range = (15000, 270000000)

        self.setWindowTitle('Invalid Clock Frequency')
        self.setText('The clock frequency was not set. Make sure to set the '
                     'clock frequency to a value between '
                     '{:,.0f} and {:,.0f} Hz.'.format(*value_range))
        self.setIcon(QMessageBox.Warning)


class FInvalidMemoryCap(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FInvalidMemoryCap, self).__init__(*args, **kwargs)

        self.setWindowTitle('Invalid Memory Cap')
        self.setText('The memory cap was not set. Make sure to set valid '
                     'memory cap values.')
        self.setIcon(QMessageBox.Warning)


class FInvalidSettingsFile(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FInvalidSettingsFile, self).__init__(*args, **kwargs)

        self.setWindowTitle('Invalid Settings File')
        self.setText('There was a problem opening this settings file. Make sure '
                     'you select the correct file.')
