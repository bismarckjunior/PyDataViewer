import sys
from PyQt4 import QtGui, QtCore
import numpy as np
from PyTable import PyTableRow
from PyDialogs import PyDialog_Lines
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random

#TODO: erro ao abrir configuracoes no start up
#TODO: salvar ordem quando fechar configuracoes
#FIXME: trocar ordem e deletar (referencia a linha antiga)
class Window (QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # Canvas
        self.canvas_tabs_ = QtGui.QTabWidget()

        # Create splitter
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.create_frame_data())
        splitter.addWidget(self.canvas_tabs_)
        splitter.setSizes([250,1000])
        splitter.setContentsMargins(5, 5, 5, 5)

        # Variables
        self.curr_x_ = []
        self.curr_y_ = []
        self.sindex_ = {}

        # Set layout
        self.new_tab()
        self.add_table_data('Line 1')
        self.setCentralWidget(splitter)
        self.setGeometry(100,100,1000,607)
        self.setWindowTitle("PyDataView 2D")

        # Menu bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&B.')
        fileMenu.addAction(QtGui.QAction("&Bismarck eh 10", self))

    def new_tab(self, name="Bismarck"):
        self.canvas_tabs_.addTab(self.create_canvas_widget(), name)

    def create_frame_data(self):
        frame = QtGui.QFrame()
        # frame.setStyleSheet("border: 1px solid red")
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setMinimumWidth(250)

        self.combo_ = QtGui.QComboBox()
        self.combo_.addItem('New data...')
        self.combo_.currentIndexChanged.connect(self.change_table_data)
        b = QtGui.QPushButton('*')
        b.setFixedWidth(30)
        b.clicked.connect(self.open_line_properties)

        self.stacked_ = QtGui.QStackedWidget()
        # self.stacked_.addWidget(PyTableRow(20, ['x','y'], formatting=['%10.3E']*2))

        layout = QtGui.QVBoxLayout()
        frame.setLayout(layout)
        layout1 = QtGui.QHBoxLayout()
        label1 = QtGui.QLabel("Data:")
        # label1.setAlignment(QtCore.Qt.AlignCenter)
        label1.setFixedWidth(40)
        layout1.addWidget(label1)
        layout1.addWidget(self.combo_)
        layout1.addWidget(b)
        layout.addLayout(layout1)
        layout.addWidget(self.stacked_)
        # layout.addWidget(PyTableRow(20, ['x','y'], formatting=['%10.3E']*2))

        layout.setContentsMargins(5,5,5,5)

        return frame

    def create_canvas_widget(self):
        widget = QtGui.QWidget()
        canvas = FigureCanvas(Figure())
        toolbar = NavigationToolbar(canvas, self)
        b = QtGui.QPushButton('*')
        # b.setIcon(QtGui.QIcon.fromTheme("document-open"))
        b.setFixedWidth(30)
        toolbar.addWidget(b)
        # toolbar.setFrameShape(QtGui.QFrame.StyledPanel)

        self.canvas_ = canvas

        # Just some button connected to `plot` method
        button = QtGui.QPushButton('Plot')
        button.clicked.connect(self.plot)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(canvas)
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setMaximumHeight(40)
        frame.setMinimumHeight(40)
        v = QtGui.QHBoxLayout(frame)
        v.addWidget(toolbar)
        v.setContentsMargins(0,0,0,0)
        # frame.setContentsMargins(1,1,1,1)
        # frame.addWidget(toolbar)
        # layout.addWidget(toolbar)
        layout.addWidget(frame)
        layout.setContentsMargins(5,5,5,5)
        # layout.setMinimumWidth(300)

        widget.setLayout(layout)

        return widget

    def get_canvas(self, index=None):
        if (index is None):
            return self.canvas_tabs_.currentWidget().children()[2]
        else:
            return self.canvas_tabs_.widget(index).children()[2]

    def get_list_canvas(self):
        lcanvas = [] 
        for i in range(self.canvas_tabs_.count()):
            lcanvas.append(self.canvas_tabs_.widget(i).children()[2])

        return lcanvas

    def open_line_properties(self):
        N = self.combo_.count()-1

        lines, texts = [], []
        for i in range(N):
            text = self.combo_.itemText(i)
            lines.append(self.get_table(i).lines.values())
            texts.append(text)
                        
        diag = PyDialog_Lines(self, lines, texts, self.canvas_)
        diag.show()

    def get_table(self, text):
        if (type(text) == int):
            text = self.combo_.itemText(text)

        return self.stacked_.widget(self.sindex_[text])

    def change_table_data(self, index):

        if (index == self.combo_.count()-1):
            self.add_table_data()
        else:
            self.stacked_.setCurrentIndex(self.sindex_[self.combo_.itemText(index)])
            table = self.stacked_.currentWidget()
            self.curr_x_ = table.get_col(0)
            self.curr_y_ = table.get_col(1)

    def remove_table_data(self, index):
        table = self.get_table(index)
        for ax, line in table.lines.items():
            line.remove()
            del table.lines[ax]

        for canvas in self.get_list_canvas():
            # refresh canvas
            canvas.draw()

        self.stacked_.removeWidget(table)
        self.combo_.blockSignals(True)
        self.combo_.removeItem(index)
        self.combo_.blockSignals(False)
        if (self.combo_.count() == 1):
            self.add_table_data('Line 1')
        else:
            self.combo_.setCurrentIndex(0)

    def add_table_data(self, new_text=None):
        texts = [self.combo_.itemText(i) for i in range(self.combo_.count()-1)]

        if (new_text in texts):
            return False

        i = self.combo_.count()
        if (new_text is None):
            new_text = 'Line 1'
            while (new_text in texts):
                new_text = QtCore.QString('Line %d' % (i))
                i +=1

            new_text, ok = QtGui.QInputDialog.getText(self, "New Data", 
                r"Name:", text=new_text)

        new_text = QtCore.QString(new_text)
        # texts.append(new_text)
        # # texts.sort()
        # texts.append(QtCore.QString('New data...'))
        # index = texts.index(new_text)
        index = self.combo_.count()-1
            
        table = self.create_table()
        self.stacked_.insertWidget(index, table)

        self.combo_.blockSignals(True)
        # self.combo_.clear()
        # self.combo_.addItems(texts)
        self.combo_.insertItem(index, new_text)
        self.combo_.setCurrentIndex(index)
        self.combo_.blockSignals(False)

        self.plot_table(new_text, table, self.get_canvas())

        self.stacked_.setCurrentIndex(index)
        table = self.stacked_.currentWidget()
        self.curr_x_ = table.get_col(0)
        self.curr_y_ = table.get_col(1)

        self.sindex_[new_text] = index

        return True

    def create_table(self):
        table = PyTableRow(20, ['x','y'], formatting=['%10.3E']*2)
        # table.itemSelectionChanged.connect(func)
        table.updated.connect(self.update_plot)
        table.cellChanged.connect(lambda r, c: self.update_plot([r]))
        table.lines = {}  

        return table

    #TODO: reduzir
    def plot_table(self, text, table, canvas):
        # canvas = self.get_canvas()
        
        ax = canvas.figure.gca()

        # table =  self.stacked_.currentWidget()
        x = table.get_col(0)
        y = table.get_col(1)

        # plot data
        if (ax not in table.lines):
            table.lines[ax], = ax.plot(x, y, 'o-', lw=2, label=text)
        else:
            table.lines[ax].set_data(x, y)

        ax.relim()
        ax.autoscale_view(True,True,True)

        # refresh canvas
        canvas.draw()

    def update_plot(self, rows):
        table =  self.stacked_.currentWidget()
        if (rows == []):
            rows = range(table.rowCount())

        m = max(rows)+1
        while (len(self.curr_x_) < m):
            self.curr_x_.append(np.nan)
            self.curr_y_.append(np.nan)

        for row in rows:
            valx = table.item(row, 0).get_value()
            valy = table.item(row, 1).get_value()
            if (valx == ''):
                valx = np.nan
            if (valy == ''):
                valy = np.nan
            self.curr_x_[row] = valx
            self.curr_y_[row] = valy

        for canvas in self.get_list_canvas():
            # create an axis
            ax = canvas.figure.gca()

            # plot data
            if (ax in table.lines):

                table.lines[ax].set_data(self.curr_x_, self.curr_y_)

            # else:
            #     table.lines[ax], = ax.plot(x, y, '*-')

                ax.relim()
                ax.autoscale_view(True,True,True)

                # refresh canvas
                canvas.draw()

    def plot(self):
        ''' plot some random stuff '''
        # random data
        x = range(10)
        data = [random.random() for i in x]

        d = [[x[i], data[i]] for i in range(len(x))]
        # self.stacked_.currentWidget().itemChanged.disconnect()
        self.stacked_.currentWidget().set_data(d)
        # self.stacked_.currentWidget().itemChanged.connect(self.test)
        


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())