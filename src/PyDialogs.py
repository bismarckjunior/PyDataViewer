from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt

#TODO: Testar linha ls=''
class PyDialog_Lines(QtGui.QDialog):

    def __init__(self, parent=None, lines=[], texts=[], canvas=None):
        super(PyDialog_Lines, self).__init__(parent)

        self.lines_ = lines
        self.texts_ = texts
        self.canvas_ = canvas
        self.set_layout()
        self.setWindowTitle('Lines Properties')

    def set_layout(self):
        # Button box
        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | 
                                         QtGui.QDialogButtonBox.Cancel,
                                         QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.ok_button)
        buttons.rejected.connect(self.cancel_button)

        # Layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.create_table())
        # layout.addLayout(hDel)
        # layout.addStretch()
        layout.addWidget(buttons)

        self.setMinimumWidth(588)


    def create_table(self):
        self.table_ = QtGui.QTableWidget(2,8, self)
        self.bkp_row_ = []
        self.hHeader_ = self.table_.horizontalHeader()
        self.hHeader_.setVisible(False)
        # self.hHeader_.setResizeMode(QtGui.QHeaderView.Stretch)
        self.vHeader_ = self.table_.verticalHeader()
        self.vHeader_.setVisible(False)
        # self.table_.setHorizontalHeaderLabels(['Name', 'Color', 'Style', 'Width', 'Color', 'Style', 'Size'])
        self.table_.setSpan(0, 0, 2, 1)
        self.table_.setSpan(0, 1, 2, 1)
        self.table_.setSpan(0, 2, 1, 3)
        self.table_.setSpan(0, 5, 1, 7)
        self.table_.resizeRowsToContents()
        self.vHeader_.setDefaultSectionSize(self.table_.rowHeight(0))

        item = QtGui.QTableWidgetItem("Name")  
        item.setBackground(QtGui.QBrush(QtGui.QColor(230, 230, 230)))
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        item.setFlags( QtCore.Qt.ItemIsEnabled )
        font = QtGui.QFont()
        font.setWeight(56)
        # font.setBold(True)
        item.setFont(font)
        self.table_.setItem(0, 1, item)

        nitem = item.clone()
        nitem.setText("")
        self.table_.setItem(0, 0, nitem)

        nitem = item.clone()
        nitem.setText("Line")
        self.table_.setItem(0, 2, nitem)
        nitem = item.clone()
        nitem.setText("Color")
        self.table_.setItem(1, 2, nitem)
        nitem = item.clone()
        nitem.setText("Style")
        self.table_.setItem(1, 3, nitem)
        nitem = item.clone()
        nitem.setText("Width")
        self.table_.setItem(1, 4, nitem)

        nitem = item.clone()
        nitem.setText("Marker")
        self.table_.setItem(0, 5, nitem)
        nitem = item.clone()
        nitem.setText("Color")
        self.table_.setItem(1, 5, nitem)
        nitem = item.clone()
        nitem.setText("Style")
        self.table_.setItem(1, 6, nitem)
        nitem = item.clone()
        nitem.setText("Width")
        self.table_.setItem(1, 7, nitem)
        self.table_.resizeColumnsToContents()

        self.table_.setColumnWidth(0, 25)
        self.table_.setColumnWidth(1, 200)
        
        self.bkp_ = []
        self.bkp_row_ = range(self.table_.rowCount())
        for line, text in zip(self.lines_, self.texts_):
            self.add_row(line, text)
            self.bkp_.append(self.get_row(self.table_.rowCount()-1))
        
        self.add_last_row()

        # for i in range(self.table_.rowCount()):
        #     self.bkp_row_.append(i)
        #     

        return self.table_

    def add_row(self, lines, text, row=None):
        if (row is None):
            row = self.table_.rowCount()
        get = lambda x: plt.getp(lines[0], x)
        # get = lambda x: lines[0][x]

        self.table_.insertRow(row)
        self.bkp_row_.append(len(self.bkp_row_))

        # Move Up
        frm = QtGui.QFrame()
        frm.setContentsMargins(1,3,1,3)
        b = QtGui.QPushButton('-', frm) if row == 2 else QtGui.QPushButton('/\\', frm)
        b.clicked.connect(lambda: self.move_up(row))
        l = QtGui.QHBoxLayout(frm)
        l.addWidget(b)
        l.setContentsMargins(0,0,0,0)
        self.table_.setCellWidget(row, 0, frm)

        # Label
        item = QtGui.QTableWidgetItem(text)
        self.table_.setItem(row, 1, item)
        self.table_.cellChanged.connect(lambda r, c: self.update_row(row, lines) if (r==row) else None)

        # Line: Color
        color = QtGui.QColor(get('color'))
        frm = QtGui.QFrame()
        frm.setContentsMargins(16,3,16,3)
        b = QtGui.QPushButton(frm)
        b.setStyleSheet("background-color:" + color.name())
        b.clicked.connect(lambda: self.change_color(row, 2, lines))
        l = QtGui.QHBoxLayout(frm)
        l.addWidget(b)
        l.setContentsMargins(0,0,0,0)
        self.table_.setCellWidget(row, 2, frm)

        # Line: Style
        ls = [u'', u'-', u'--', u'-.', u':']
        cb = QtGui.QComboBox()
        cb.addItems(ls)
        cb.setCurrentIndex(ls.index(get('ls')))
        cb.currentIndexChanged.connect(lambda: self.update_row(row, lines))
        self.table_.setCellWidget(row, 3, cb)

        # Line: Width
        sp = QtGui.QSpinBox()
        sp.setMinimum(0.5)
        sp.setSingleStep(1.0)
        sp.setValue(get('lw'))
        sp.valueChanged.connect(lambda: self.update_row(row, lines))
        self.table_.setCellWidget(row, 4, sp)

        # Marker: Color
        color = QtGui.QColor(get('mfc'))
        frm = QtGui.QFrame()
        frm.setContentsMargins(16,3,16,3)
        b = QtGui.QPushButton(frm)
        b.setStyleSheet("background-color:" + color.name())
        b.clicked.connect(lambda: self.change_color(row, 5, lines))
        l = QtGui.QHBoxLayout(frm)
        l.addWidget(b)
        l.setContentsMargins(0,0,0,0)
        self.table_.setCellWidget(row, 5, frm)

        # Marker: Style
        m = ["",".",",","o","v","^","<",">","1","2","3","4","8","s","p","P","*","h","H","+","x","X","D","d","|","_"]
        cb = QtGui.QComboBox()
        cb.addItems(m)
        cb.setCurrentIndex(m.index(get('marker')))
        cb.currentIndexChanged.connect(lambda: self.update_row(row, lines))
        self.table_.setCellWidget(row, 6, cb)

        # Line: Width
        sp = QtGui.QSpinBox()
        sp.setMinimum(0.5)
        sp.setSingleStep(1.0)
        sp.setValue(get('ms'))
        sp.valueChanged.connect(lambda: self.update_row(row, lines))
        self.table_.setCellWidget(row, 7, sp)

    def add_last_row(self):
        row = self.table_.rowCount()
        self.table_.insertRow(row)
        for col in [0]+range(2, self.table_.columnCount()):
            item = QtGui.QTableWidgetItem('')
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table_.setItem(row, col, item)

        def new_line(row, col):
            if (row == self.table_.rowCount()-1 and col == 1):
                text = self.table_.item(row, col).text()
                parent = self.parent()
                if (parent.add_table_data(text)):
                    table = parent.stacked_.currentWidget()
                    self.table_.blockSignals(True)
                    self.add_row(table.lines.values(), text, row)
                    self.table_.item(row+1, col).setText('')
                    self.table_.blockSignals(False)
                else:
                    self.table_.blockSignals(True)
                    self.table_.item(row, col).setText('')
                    self.table_.blockSignals(False)

        self.table_.cellChanged.connect(new_line)

    def change_color(self, row, col, lines):
        frm = self.table_.cellWidget(row, col)
        button = frm.children()[0]
        color = QtGui.QColor(button.styleSheet().split(':')[-1])
        change = False
        if (col == 2):
            frm2 = self.table_.cellWidget(row, 5)
            button2 = frm2.children()[0]
            color2 = QtGui.QColor(button2.styleSheet().split(':')[-1])
            change = color == color2

        # New color
        color = QtGui.QColorDialog.getColor(color)

        if (color.isValid()):
            button.setStyleSheet("background-color:" + color.name())
            if (change):
                button2.setStyleSheet("background-color:" + color.name())

            self.update_row(row, lines)

    def move_up(self, row_orig):
        row_curr = self.bkp_row_[row_orig]
        if (row_curr == 2):
            self.table_.removeRow(2)
            self.bkp_row_ = map(lambda x: x-1, self.bkp_row_)

            if (self.table_.rowCount() > 3):
                # button = self.table_.cellWidget(row_orig, 0).children()[0]
                button = self.table_.cellWidget(2, 0).children()[0]
                button.setText('-')

        else:
            row_orig_up = self.bkp_row_.index(row_curr-1)
            self.bkp_row_[row_orig] = row_curr-1
            self.bkp_row_[row_orig_up] = row_curr
            self.vHeader_.moveSection(row_curr,row_curr-1)

        if (row_curr == 3):
            button = self.table_.cellWidget(row_orig, 0).children()[0]
            button.setText('-')
            button2 = self.table_.cellWidget(row_orig_up, 0).children()[0]
            button2.setText('/\\')

    def get_row(self, row):
        row_data = {}        

        # Label
        row_data['label'] = str(self.table_.item(row, 1).text())
        
        # Line: Color
        frm = self.table_.cellWidget(row, 2)
        button = frm.children()[0]
        row_data['color'] = str(button.styleSheet().split(':')[-1])

        # Line: Style
        ls = str(self.table_.cellWidget(row, 3).currentText())
        row_data['ls'] = ls

        # Line: Width
        row_data['lw'] = self.table_.cellWidget(row, 4).value()

        # Marker: Color
        frm = self.table_.cellWidget(row, 5)
        button = frm.children()[0]
        row_data['mfc'] = str(button.styleSheet().split(':')[-1])

        # Marker: Style
        row_data['marker'] = str(self.table_.cellWidget(row, 6).currentText())

        # Marker: Size
        row_data['ms'] = self.table_.cellWidget(row, 7).value()

        return row_data

    def update_row(self, row, lines):
        # print row
        parent = self.parent()
        # parent.combo_.setItemText(row-2, self.table_.item(row, 1).text())
        parent.change_table_name(row-2, self.table_.item(row, 1).text())

        if (row == self.table_.rowCount()-1):
            return
            
        for line in lines:
            # for k, v in self.get_row(row).items():
                plt.setp(line, **self.get_row(row))

        self.canvas_.draw()

    #TODO: ordenar o combobox
    def ok_button(self):
        # print 'ok'
        # print self.bkp_row_

        parent = self.parent()
        # tables = []
        # for i in range(parent.combo_.count()-1):
        #     table = parent.get_table(i) 
        #     parent.stacked_.removeWidget(table)
        #     tables.append(table)

        # for index in range(len(self.bkp_), len(self.bkp_row_)-2):

        print parent.sindex_
        print self.bkp_row_
        for i in range(len(self.bkp_row_))[::-1]:
            if (self.bkp_row_[i] < 0):
                parent.remove_table_data(i)
                del self.bkp_row_[i]
                del parent.sindex_[self.texts_[i]]

        print self.bkp_row_
        parent.combo_.blockSignals(True)
        parent.combo_.clear()
        # for i in np.argsort(self.bkp_row_[2:]):
        for i, row in enumerate(range(2, self.table_.rowCount()-1)):
            text = self.table_.item(self.bkp_row_.index(row), 1).text()
            parent.combo_.addItem(text)
            # parent.stacked_.insertWidget(i, tables[i])
            parent.sindex_[text] = self.bkp_row_[2+i]-2
    
        print parent.sindex_
        print 
        # print 
        parent.combo_.addItem('New data...')
        parent.combo_.blockSignals(False)

        self.accept()

    def cancel_button(self):
        parent = self.parent()

        # Remove news
        for index in range(len(self.bkp_), len(self.bkp_row_)-2):
            parent.remove_table_data(index)

        # Rename
        for index, text in enumerate(self.texts_):
            parent.change_table_name(index, text)

        # Backup lines
        for bkp, lines in zip(self.bkp_, self.lines_):
            for line in lines:
                plt.setp(line, **bkp)
            
        self.canvas_.draw()

        self.reject()
