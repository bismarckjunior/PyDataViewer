import sys, os, csv
import numpy as np
from PyQt4 import QtGui, QtCore


class PyTableRow_Item(QtGui.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super(PyTableRow_Item, self).__init__(*args, **kwargs)

        self.tmp_ = True
        self.format_ = None
        self.value_ = ""
        
        self.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.setFont(QtGui.QFont("Courier New"))

    def __lt__(self, item):
        var = self.data(QtCore.Qt.DisplayRole)
        var2 = item.data(QtCore.Qt.DisplayRole)

        if (not var.toString()):
            return False

        if (not var2.toString()):
            return True

        real1 = var.toReal()
        real2 = var2.toReal()
        if (real1[1] and real2[1]):
            return real1[0] < real2[0]

        return QtGui.QTableWidgetItem.__lt__(self, item)

    def set_formatting(self, formatting):
        try:
            formatting % 1
        except:
            formatting = None

        self.format_ = formatting

    def get_formatting(self):
        return self.format_ if self.format_ else ''

    def check_formatting(self, formatting):
        var = self.data(QtCore.Qt.DisplayRole)
        if (not var.toString() or var.toReal()[1]):
            return True

        return False

    def check_value(self, value):
        if (self.format_):
            return QtCore.QVariant(value).toReal()[1]
        else:
            return True

    def set_data(self, role, var):
        QtGui.QTableWidgetItem.setData(self, role, var)

    def setData(self, role, var):
        if (self.tmp_ and not(role & QtCore.Qt.WhatsThisRole)):
            self.tmp_ = False
            real = var.toReal()
            if (self.format_):
                if (real[1]):
                    txt = self.format_ % real[0]
                    self.value_ = real[0]
                else:
                    txt = ""
                    self.value_ = txt
            else:
                txt = var.toString()
                self.value_ = txt

            self.setText(txt)
        else:
            QtGui.QTableWidgetItem.setData(self, role, var)

        self.tmp_ = True

    def get_value(self):
        return self.value_


class PyTableRow(QtGui.QTableWidget):
    last_dir_ = ''
    updated = QtCore.pyqtSignal(list)

    def __init__(self, rows, cols, headers=[], formatting=[], parent=None):
        if (type(cols)==list):
            cols, headers = len(cols), cols
        super(PyTableRow, self).__init__(0, cols, parent)
        self.setHorizontalHeaderLabels(headers)

        self.ini_rows_ = rows
        self.cur_dir_ = ''
        self.col_formatting_ = {}
        for col,fmt in enumerate(formatting+['']*(cols-len(formatting))):
            self.col_formatting_[col] = fmt

        for row in range(rows):
            self.insertRow(row)

        self.set_defaults()

    def set_defaults(self):
        # Set vertical header properties
        vHeader = self.verticalHeader()
        self.resizeRowsToContents()
        vHeader.setResizeMode(QtGui.QHeaderView.Fixed)
        vHeader.setDefaultSectionSize(self.rowHeight(0))
        vHeader.setDefaultAlignment(QtCore.Qt.AlignRight)
        vHeader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        vHeader.customContextMenuRequested.connect(self.context_menu_row)

        # Set horizontal header properties
        hHeader = self.horizontalHeader()
        hHeader.setResizeMode(QtGui.QHeaderView.Stretch)
        hHeader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        hHeader.customContextMenuRequested.connect(self.context_menu_col)

        # Set corner header properties
        self.corner_ = self.findChild(QtGui.QAbstractButton)
        self.corner_.clicked.connect(lambda:True)
        self.corner_.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.corner_.customContextMenuRequested.connect(self.context_menu_corner)
        
        # Connections
        self.itemSelectionChanged.connect(self.insert_last_row)

    def test_func(self):
        print 'corner'

    def insert_last_row(self):
        row = self.currentRow()
        if (row == self.rowCount()-1):
            self.insertRow(row+1)

    def get_selection(self):
        d = [ (s.row(), s.column()) for s in self.selectedIndexes()]
        sel = np.array(d, dtype=[('row', int), ('col', int)])
        sel = np.sort(sel, order=['row', 'col'])
        return sel

    def copy_selection(self):
        sel = self.get_selection()
        if (len(sel)==0):
            return
        min_col = min([s[1] for s in sel])
        lst_row, lst_col = sel[0]
        txt = ''
        for row, col in sel:
            if (lst_row != row):
                txt += '\n'
                lst_col = min_col
            txt += '\t'*(col-lst_col)
            if (self.item(row, col)):
                txt += str(self.item(row, col).get_value())
            lst_row = row
            lst_col = col
        QtGui.qApp.clipboard().setText(txt)

    def clear_selection(self):
        for row, col in self.get_selection():
            self.item(row, col).setText('')

    def cut_selection(self):
        self.copy_selection()
        self.clear_selection()

    def paste(self):
        sel = self.get_selection()
        if (len(sel) != 0):
            txt = str(QtGui.qApp.clipboard().text())
            self.set_txt_data(txt, *sel[0])

    def insertRow(self, row):
        super(PyTableRow, self).insertRow(row)

        for col in range(self.columnCount()):
            item = PyTableRow_Item('')
            if (col in self.col_formatting_):
                item.set_formatting(self.col_formatting_[col])
            self.setItem(row, col, item)


    def insert_rows(self, rows):
        lst_row = 0
        lis = []
        tmp = []
        for row in rows:
            if (row == lst_row+1):
                tmp.append(row)
            else:
                lis = tmp + lis
                tmp = [row]
            lst_row = row
        lis = tmp + lis

        self.blockSignals(True)
        for row in lis:
            self.insertRow(row)
        self.blockSignals(False)
        self.updated.emit(rows)
            
    def remove_rows(self, rows):
        self.blockSignals(True)
        for row in rows[::-1]:
            if (self.rowCount()>1):
                self.removeRow(row)
            else:
                self.clear_selection()

        self.blockSignals(False)
        self.updated.emit(rows)

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copy_selection()
            print 'Ctrl+C'

        elif event.matches(QtGui.QKeySequence.Paste):
            self.paste()
            print 'Ctrl+V'

        elif event.matches(QtGui.QKeySequence.Cut):
            self.cut_selection()
            print 'Ctrl+X'

        elif event.matches(QtGui.QKeySequence.Delete):
            self.clear_selection()
            print 'Del'

        elif event.matches(QtGui.QKeySequence.InsertParagraphSeparator):
            row = self.currentRow()
            # if (row == self.rowCount()-1):
            #     self.insertRow(row+1)
            self.setCurrentCell(row+1, self.currentColumn())
            print 'Enter'

        else:
            super(PyTableRow, self).keyPressEvent(event)

    def create_context_menu(self):
        # Action buttons
        act_cut_ = QtGui.QAction('Cut', self)
        act_copy_ = QtGui.QAction('Copy', self)
        act_paste_ = QtGui.QAction('Paste', self)
        act_clear_ = QtGui.QAction('Clear', self)

        act_cut_.triggered.connect(self.cut_selection)
        act_copy_.triggered.connect(self.copy_selection)
        act_paste_.triggered.connect(self.paste)
        act_clear_.triggered.connect(self.clear_selection)

        # Context menu
        menu = QtGui.QMenu(self)
        menu.addAction(act_cut_)
        menu.addAction(act_copy_)
        menu.addAction(act_paste_)
        menu.addAction(act_clear_)
        menu.addSeparator()

        return menu

    def context_menu_row(self, event):
        rows = [r.row() for r in self.selectionModel().selectedRows()]
        row = self.indexAt(event).row()
        if (row not in rows):
            rows = [row]
            r = QtGui.QTableWidgetSelectionRange(0, 0, self.rowCount()-1, 
                                                 self.columnCount()-1)
            self.setRangeSelected(r, False)

            # Set current cell
            self.setCurrentCell(row, 0)

        else:
            # Diselect other cells
            for sel in self.selectedIndexes():
                if (sel.row() not in rows):
                    r = QtGui.QTableWidgetSelectionRange(sel.row(), sel.column(), 
                                                         sel.row(), sel.column())
                    self.setRangeSelected(r, False)

        # Select current row
        r = QtGui.QTableWidgetSelectionRange(row, 0, row, self.columnCount()-1)
        self.setRangeSelected(r, True)

        # Action buttons
        Act_Insert = QtGui.QAction('Insert rows', self)
        Act_Remove = QtGui.QAction('Remove rows', self)
        Act_Insert.triggered.connect(lambda: self.insert_rows(rows))
        Act_Remove.triggered.connect(lambda: self.remove_rows(rows))

        # Context menu
        menu = self.create_context_menu()
        menu.addAction(Act_Insert)
        menu.addAction(Act_Remove)
        pos = QtGui.QCursor.pos()
        menu.popup(QtCore.QPoint(pos.x()+2, pos.y()+2))

    def context_menu_col(self, event):
        cols = [r.column() for r in self.selectionModel().selectedColumns()]
        col = self.indexAt(event).column()
        if (col not in cols):
            cols = [col]
            r = QtGui.QTableWidgetSelectionRange(0, 0, self.rowCount()-1, 
                                                 self.columnCount()-1)
            self.setRangeSelected(r, False)

            # Set current cell
            self.setCurrentCell(0, col)
            
        else:
            # Diselect other cells
            for sel in self.selectedIndexes():
                if (sel.column() not in cols):
                    r = QtGui.QTableWidgetSelectionRange(sel.row(), sel.column(), 
                                                         sel.row(), sel.column())
                    self.setRangeSelected(r, False)
        
        # Select current column
        r = QtGui.QTableWidgetSelectionRange(0, col, self.rowCount()-1, col)
        self.setRangeSelected(r, True)

        # Action button
        act_sort = QtGui.QAction('Sort', self)
        act_format = QtGui.QAction('Formatting...', self)
        act_sort.triggered.connect(lambda: self.sortItems(col))
        act_sort.triggered.connect(lambda: self.updated.emit([]))
        act_format.triggered.connect(lambda: self.formatting_cols(cols))

        # Context menu
        menu = self.create_context_menu()
        if (len(cols) == 1):
            menu.addAction(act_sort)
        menu.addAction(act_format)
        pos = QtGui.QCursor.pos()
        menu.popup(QtCore.QPoint(pos.x()+2, pos.y()+2))

    def context_menu_corner(self, event):
        # Action buttons
        act_test_ = QtGui.QAction('Test', self)
        act_import_ = QtGui.QAction('Import...', self)
        act_export_ = QtGui.QAction('Export...', self)
        act_test_.triggered.connect(self.test_func)
        act_import_.triggered.connect(self.import_data)
        act_export_.triggered.connect(self.export_data)

        # Context menu
        menu = QtGui.QMenu(self)
        menu.addAction(act_import_)
        menu.addAction(act_export_)
        menu.addSeparator()
        menu.addAction(act_test_)
        menu.addSeparator()
        pos = QtGui.QCursor.pos()
        menu.popup(QtCore.QPoint(pos.x()+2, pos.y()+2))

    def contextMenuEvent(self, event):
        menu = self.create_context_menu()
        pos = QtGui.QCursor.pos()
        menu.popup(QtCore.QPoint(pos.x()+2, pos.y()+2))

    def formatting_cols(self, cols):
        txt, ok = QtGui.QInputDialog.getText(self, "Formatting", 
            r"Formatting (eg: %.2f):", text=self.col_formatting_[cols[0]])

        try:
            txt = str(txt)
            if (txt):
                txt % 1
        except:
            return

        if ok:
            for col in cols:
                self.set_col_formatting(col, txt, check=True)

    def set_col_formatting(self, col, txt, check=False):
        ok = QtGui.QMessageBox.Yes
        if (check):
            try:
                txt = str(txt)
                if (txt):
                    txt % 1
            except:
                return
                
            for row in range(self.rowCount()):
                item = self.item(row, col)
                if (not item.check_formatting(txt)):
                    ok = QtGui.QMessageBox.question(self,'Warning', 
                        'Some data will be lost in column "%s"\nbecause numberic formatting. Continue?' 
                          % self.horizontalHeaderItem(col).text(), 
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    break

        if (ok == QtGui.QMessageBox.Yes):
            self.col_formatting_[col] = txt
            for row in range(self.rowCount()):
                item = self.item(row, col)
                item.set_formatting(txt)
                text = item.text()
                if (text):
                    item.setText(text)


    def get_data(self):
        data = []
        for row in range(self.rowCount()):
            line = []
            for col in range(self.columnCount()):
                line.append(str(self.item(row, col).get_value()))
                # line.append(str(self.item(row, col).text()))
            
            data.append(line)

        while (len(data)>0 and data[-1] == ['']*self.columnCount()):
            del data[-1]

        return data

    def get_col(self, col):
        column = []
        for row in range(self.rowCount()):
            try:
                val = self.item(row, col).get_value()
                    
                if (val == ''):
                    val = np.nan
            except:
                val = np.nan

            column.append(val)

        return np.array(column)

    def get_txt_data(self):
        data = self.get_data()
        return '\n'.join(['\t'.join(d) for d in data])

    def set_data(self, data, row=0, col=0, clear=False):
        row_ini = row
        bad_formatting = []
        for j in range(len(data[0])):
            col_ = col +j
            if (self.col_formatting_[col_]):
                for i in range(len(data)):
                    # print i,j, data[i]
                    # print data[i][j]
                    item = self.item(row+i, col_)
                    if( item and not item.check_value(data[i][j]) ):
                        bad_formatting.append(col_)
                        break

        if (bad_formatting):
            txt = 's ' if len(bad_formatting)>1 else ' '
            txt += ', '.join(['"%s"'% self.horizontalHeaderItem(c).text() for c in bad_formatting])
            ok = QtGui.QMessageBox.question(self, 'Warning', 
                'Some data will be lost in column%s\nbecause numberic formatting.\n\nContinue?' % txt, 
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

            if (ok == QtGui.QMessageBox.No):
                ok2 = QtGui.QMessageBox.question(self, 'Warning', 
                    'Remove numberic formatting for column%s and continue?' % txt, 
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

                if (ok2 == QtGui.QMessageBox.Yes):
                    ok = QtGui.QMessageBox.Yes
                    for c in bad_formatting:
                        self.set_col_formatting(c, "")
        else:
            ok = QtGui.QMessageBox.Yes

        if (ok == QtGui.QMessageBox.Yes):
            self.blockSignals(True)
            if (clear):
                while (self.rowCount() > 0):
                    self.removeRow(0)
                while (self.rowCount() < self.ini_rows_):
                    self.insertRow(0)

            for line in data:
                if (row == self.rowCount()):
                    self.insertRow(row)
                for i,val in enumerate(line):
                    self.item(row, col+i).setText(str(val))
                row += 1

            if (row == self.rowCount()):
                self.insertRow(row)

            self.blockSignals(False)
            self.updated.emit(range(row_ini, row))

    def set_txt_data(self, txt, row=0, col=0):
        data = [line.split('\t') for line in txt.split('\n')]
        self.set_data(data, row, col)
        
    def export_data(self):
        dir_ = self.cur_dir_ if self.cur_dir_ else PyTableRow.last_dir_
        fname = QtGui.QFileDialog.getSaveFileName(self, caption="Select File", 
            directory = dir_)#, filter="Text file (*.csv *.txt)")

        if (fname):
            fname = str(fname)
            self.cur_dir_ = os.path.dirname(fname)
            PyTableRow.last_dir_ = self.cur_dir_

            with open(fname, 'w') as f:
                if (fname.endswith(".csv")):
                    wr = csv.writer(f)
                    for row in self.get_data():
                        wr.writerow(row)
                else:
                    f.write(self.get_txt_data())

            print 'exporting', fname

    def import_data(self):
        dir_ = self.cur_dir_ if self.cur_dir_ else PyTableRow.last_dir_
        fname = QtGui.QFileDialog.getOpenFileName(self, caption="Select File", 
            directory = dir_, filter="Text file (*.csv *.txt)")

        if (fname):
            fname = str(fname)
            self.cur_dir_ = os.path.dirname(fname)
            PyTableRow.last_dir_ = self.cur_dir_

            with open(fname, 'r') as f:
                if (fname.endswith(".csv")):
                    lines = csv.reader(f)
                else:
                    lines = [line.split('\t') for line in f.readlines()]
                
                data = []
                for line in lines:
                    data.append(line)

                self.set_data(data, clear=True)

            print 'importing', fname


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = QtGui.QDialog()
    main.setSizeGripEnabled(True) 
    table = PyTableRow(12, ['x','y'], formatting=['%10.3E']*2)
    table2 = PyTableRow(10, ['x','y'])
    layout = QtGui.QHBoxLayout(main)
    layout.addWidget(table)
    layout.addWidget(table2)
    # layout.addWidget(QtGui.QLabel(QtGui.qApp.clipboard().text()))
    main.resize(main.frameGeometry().width(), 500)

    main.show()

    sys.exit(app.exec_())