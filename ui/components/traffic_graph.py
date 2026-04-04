import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
import random


class TrafficGraph(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.graph = pg.PlotWidget()
        self.graph.setTitle("📊 Live Traffic")
        self.graph.setYRange(0, 200)

        layout.addWidget(self.graph)

        self.data = [0]*50
        self.curve = self.graph.plot(self.data)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)

    def update_graph(self):
        self.data.pop(0)
        self.data.append(random.randint(0, 150))  # replace with real packets
        self.curve.setData(self.data)