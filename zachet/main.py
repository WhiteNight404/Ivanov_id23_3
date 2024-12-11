# Вариант 7
# Симуляция работы поршневого двигателя
import sys
import numpy as np
import pygame
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QSlider, QPushButton, QSpinBox)
from PyQt5.QtCore import Qt, QTimer


class EngineSimulation(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.setupPygame()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.running = False
        self.time = 0

    def initUI(self):
        self.setWindowTitle('Симуляция работы поршневого двигателя')
        self.setGeometry(100, 100, 1200, 600)

        layout = QVBoxLayout()

        # Угловая скорость
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        layout.addWidget(QLabel('Угловая скорость (рад/с)'))
        layout.addWidget(self.speed_slider)

        # Количество цилиндров
        self.cylinder_spinbox = QSpinBox()
        self.cylinder_spinbox.setRange(1, 10)
        self.cylinder_spinbox.setValue(4)
        layout.addWidget(QLabel('Количество цилиндров'))
        layout.addWidget(self.cylinder_spinbox)

        # Размер поршня
        self.piston_size_slider = QSlider(Qt.Horizontal)
        self.piston_size_slider.setRange(20, 120)
        self.piston_size_slider.setValue(50)
        layout.addWidget(QLabel('Размер поршня'))
        layout.addWidget(self.piston_size_slider)

        # Радиус кривошипа
        self.crank_radius_slider = QSlider(Qt.Horizontal)
        self.crank_radius_slider.setRange(20, 75)
        self.crank_radius_slider.setValue(50)
        layout.addWidget(QLabel('Радиус кривошипа'))
        layout.addWidget(self.crank_radius_slider)

        # Кнопка запуска анимации
        self.start_button = QPushButton('Запуск анимации')
        self.start_button.clicked.connect(self.startAnimation)
        layout.addWidget(self.start_button)

        # Кнопка сброса
        self.reset_button = QPushButton('Сброс параметров и остановка')
        self.reset_button.clicked.connect(self.reset)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def setupPygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption('Двигатель')
        self.clock = pygame.time.Clock()

    def startAnimation(self):
        if not self.running:
            self.running = True
            self.timer.start(16)
            self.time = 0

    def reset(self):
        self.running = False
        self.timer.stop()
        self.time = 0

    def update(self):
        if self.running:
            self.time += 0.016
            self.draw()

    def draw(self):
        self.screen.fill((255, 255, 255))

        omega = self.speed_slider.value() / 10.0 
        n = self.cylinder_spinbox.value() 
        piston_size = self.piston_size_slider.value()  
        crank_radius = self.crank_radius_slider.value()  

        cylinder_height = 5 + piston_size * 1 + crank_radius * 1.5  

        for i in range(n):
            x_offset = (i + 1) * (1200 / (n + 1))  
            pygame.draw.rect(self.screen, (0, 0, 0), (x_offset - 20, 250, 40, cylinder_height))  

            # Положение поршня с учетом радиуса кривошипа
            piston_y = 250 + cylinder_height - (crank_radius * (1 + np.sin(omega * self.time + i)))  
            pygame.draw.rect(self.screen, (255, 0, 0), (x_offset - 20, piston_y, 40, piston_size))  

            # Кколенчатый вал
            if i > 0:  
                pygame.draw.line(self.screen, (169, 169, 169), (x_offset - 20, piston_y + piston_size), 
                                 (x_offset - 20, 300), 5)

            for j in range(5): 
                zigzag_x = x_offset - 20 + j * 8
                zigzag_y = 300 + (20 * (-1) ** j) 
                pygame.draw.line(self.screen, (169, 169, 169), 
                                 (zigzag_x, 300), (zigzag_x, zigzag_y), 5)

        pygame.display.flip() 
        self.clock.tick(60)  


if __name__ == '__main__':
    app = QApplication(sys.argv)
    engine_sim = EngineSimulation()
    engine_sim.show()
    sys.exit(app.exec_())