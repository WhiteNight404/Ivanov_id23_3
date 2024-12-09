import pygame
import random
import json
import os

# Константы программы
WIDTH, HEIGHT = 1000, 800
FPS = 60
CONFIG_DIR = os.getcwd() 

# Параметры дождя по умолчанию
DEFAULT_RAIN_CONFIG = {
    "density": 5,
    "speed": (4, 10),  # (min_speed, max_speed)
    "drop_length": (6, 12),  # (min_drop_length, max_drop_length)
    "drop_width": (1, 2)  # (min_drop_width, max_drop_width)
}

# Капли дождя
class Raindrop:
    def __init__(self, x, y, length, width, speed):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.speed = speed

    def fall(self):
        self.y += self.speed

    def is_off_screen(self):
        return self.y > HEIGHT

# Тучка
class Cloud:
    _id_counter = 1

    @classmethod
    def get_next_id(cls):
        cls._id_counter += 1
        return cls._id_counter - 1

    def __init__(self, x, y, width, height, shape):
        self.rect = pygame.Rect(x, y, width, height)
        self.shape = shape 
        self.config_file = os.path.join(CONFIG_DIR, f"cloud_{Cloud.get_next_id()}.json")
        self.load_config()
        self.raindrops = []

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.rain_config = json.load(f)
        else:
            self.rain_config = {
                "density": DEFAULT_RAIN_CONFIG['density'],
                "speed": DEFAULT_RAIN_CONFIG['speed'],
                "drop_length": DEFAULT_RAIN_CONFIG['drop_length'],
                "drop_width": DEFAULT_RAIN_CONFIG['drop_width'],
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.rain_config, f)

    def delete_config(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def generate_raindrops(self):
        density = int(self.rain_config['density'])
        if density > 0:  
            for _ in range(random.randint(1, density)):
                x = random.randint(self.rect.left, self.rect.right)
                y = self.rect.bottom  # Капли начинают падать из нижней части тучки
                length = random.randint(int(self.rain_config['drop_length'][0]), int(self.rain_config['drop_length'][1]))
                width = random.randint(int(self.rain_config['drop_width'][0]), int(self.rain_config['drop_width'][1]))
                speed = random.uniform(self.rain_config['speed'][0], self.rain_config['speed'][1])
                self.raindrops.append(Raindrop(x, y, length, width, speed))

    def draw(self, surface):
        if self.shape == 'rectangle':
            pygame.draw.rect(surface, (255, 255, 255), self.rect)
        elif self.shape == 'oval':
            pygame.draw.ellipse(surface, (255, 255, 255), self.rect)
        elif self.shape == 'triangle':
            points = [(self.rect.centerx, self.rect.top), 
                      (self.rect.left, self.rect.bottom), 
                      (self.rect.right, self.rect.bottom)]
            pygame.draw.polygon(surface, (255, 255, 255), points)

        for drop in self.raindrops:
            pygame.draw.rect(surface, (0, 0, 255), (drop.x, drop.y, drop.width, drop.length))

    def update(self):
        for drop in self.raindrops:
            drop.fall()
        self.raindrops = [drop for drop in self.raindrops if not drop.is_off_screen()]

# Создание тучки
def create_random_cloud(x, y):
    width = random.randint(80, 120)
    height = random.randint(20, 50)
    shape = random.choice(['rectangle', 'oval', 'triangle']) 
    return Cloud(x, y, width, height, shape)

# Основная функция игры
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("И пускай капает, капает с неба...")
    clock = pygame.time.Clock()

    clouds = []
    selected_cloud = None
    mouse_offset = (0, 0)
    dragging = False
    slider_dragging = None

    # Параметры панели редактирования
    editor_rect = pygame.Rect(WIDTH - 250, 0, 250, 250)

    # Начальные позиции ползунков
    density_slider_pos = (WIDTH - 240, 50)
    speed_slider_pos = (WIDTH - 240, 100)
    drop_length_slider_pos = (WIDTH - 240, 150)
    drop_width_slider_pos = (WIDTH - 240, 200)

    # Значения ползунков по умолчанию
    speed_slider_value = 0
    drop_length_slider_value = 0
    drop_width_slider_value = 0
    density_slider_value = 0

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    if editor_rect.collidepoint(event.pos) and selected_cloud:
                        pass 
                    else:
                        for cloud in clouds:
                            if cloud.rect.collidepoint(event.pos):
                                selected_cloud = cloud
                                mouse_offset = (cloud.rect.x - event.pos[0], cloud.rect.y - event.pos[1])
                                dragging = True
                                # Обновляние значения ползунков для выбранного облака
                                density_slider_value = int((selected_cloud.rain_config['density'] / 10) * 200)  
                                speed_slider_value = int(((selected_cloud.rain_config['speed'][0] + selected_cloud.rain_config['speed'][1]) / 2 - 4) / 6 * 200)  
                                drop_length_slider_value = int(((selected_cloud.rain_config['drop_length'][0] + selected_cloud.rain_config['drop_length'][1]) / 2 - 6) / 6 * 200)  
                                drop_width_slider_value = int(((selected_cloud.rain_config['drop_width'][0] + selected_cloud.rain_config['drop_width'][1]) / 2 - 1) / 1 * 200)  
                                break
                        else:
                            new_cloud = create_random_cloud(event.pos[0], event.pos[1])
                            clouds.append(new_cloud)
                            selected_cloud = new_cloud
                            # Обновляние значения ползунков для нового облака
                            density_slider_value = int((new_cloud.rain_config['density'] / 10) * 200)  
                            speed_slider_value = int(((new_cloud.rain_config['speed'][0] + new_cloud.rain_config['speed'][1]) / 2 - 4) / 6 * 200)  
                            drop_length_slider_value = int(((new_cloud.rain_config['drop_length'][0] + new_cloud.rain_config['drop_length'][1]) / 2 - 6) / 6 * 200)  
                            drop_width_slider_value = int(((new_cloud.rain_config['drop_width'][0] + new_cloud.rain_config['drop_width'][1]) / 2 - 1) / 1 * 200)  
                elif event.button == 3:  # Правый клик
                    if selected_cloud:
                        selected_cloud.delete_config()
                        clouds.remove(selected_cloud)
                        selected_cloud = None
                        speed_slider_value = 0
                        drop_length_slider_value = 0
                        drop_width_slider_value = 0
                        density_slider_value = 0
                # Проверка нажатия на ползунки
                if speed_slider_pos[0] <= event.pos[0] <= speed_slider_pos[0] + 200 and speed_slider_pos[1] <= event.pos[1] <= speed_slider_pos[1] + 20:
                    slider_dragging = 'speed'
                elif drop_length_slider_pos[0] <= event.pos[0] <= drop_length_slider_pos[0] + 200 and drop_length_slider_pos[1] <= event.pos[1] <= drop_length_slider_pos[1] + 20:
                    slider_dragging = 'drop_length'
                elif drop_width_slider_pos[0] <= event.pos[0] <= drop_width_slider_pos[0] + 200 and drop_width_slider_pos[1] <= event.pos[1] <= drop_width_slider_pos[1] + 20:
                    slider_dragging = 'drop_width'
                elif density_slider_pos[0] <= event.pos[0] <= density_slider_pos[0] + 200 and density_slider_pos[1] <= event.pos[1] <= density_slider_pos[1] + 20:
                    slider_dragging = 'density'

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    slider_dragging = None
                else:
                    if not any(cloud.rect.collidepoint(event.pos) for cloud in clouds):
                        selected_cloud = None
            if event.type == pygame.MOUSEMOTION:
                if dragging and selected_cloud:
                    selected_cloud.rect.topleft = (event.pos[0] + mouse_offset[0], event.pos[1] + mouse_offset[1])

                if slider_dragging and selected_cloud:
                    if slider_dragging == 'speed':
                        new_value = max(0, min(200, event.pos[0] - speed_slider_pos[0]))
                        speed_slider_value = new_value
                    elif slider_dragging == 'drop_length':
                        new_value = max(0, min(200, event.pos[0] - drop_length_slider_pos[0]))
                        drop_length_slider_value = new_value
                    elif slider_dragging == 'drop_width':
                        new_value = max(0, min(200, event.pos[0] - drop_width_slider_pos[0]))
                        drop_width_slider_value = new_value
                    elif slider_dragging == 'density':
                        new_value = max(0, min(200, event.pos[0] - density_slider_pos[0]))
                        density_slider_value = new_value

        for cloud in clouds:
            cloud.generate_raindrops()
            cloud.update()

        if selected_cloud:
            # Измение параметров дождя и сохранение в JSON при изменении ползунков
            if slider_dragging == 'speed':
                speed_center = (DEFAULT_RAIN_CONFIG['speed'][0] + DEFAULT_RAIN_CONFIG['speed'][1]) / 2
                speed_range = (DEFAULT_RAIN_CONFIG['speed'][1] - DEFAULT_RAIN_CONFIG['speed'][0]) * 0.25
                selected_cloud.rain_config['speed'] = (
                    max(0, speed_center - speed_range + (speed_slider_value / 200) * (2 * speed_range)),
                    max(0, speed_center + speed_range + (speed_slider_value / 200) * (2 * speed_range))
                )
            elif slider_dragging == 'drop_length':
                drop_length_center = (DEFAULT_RAIN_CONFIG['drop_length'][0] + DEFAULT_RAIN_CONFIG['drop_length'][1]) / 2
                drop_length_range = (DEFAULT_RAIN_CONFIG['drop_length'][1] - DEFAULT_RAIN_CONFIG['drop_length'][0]) * 0.25
                selected_cloud.rain_config['drop_length'] = (
                    max(0, drop_length_center - drop_length_range + (drop_length_slider_value / 200) * (2 * drop_length_range)),
                    max(0, drop_length_center + drop_length_range + (drop_length_slider_value / 200) * (2 * drop_length_range))
                )
            elif slider_dragging == 'drop_width':
                drop_width_center = (DEFAULT_RAIN_CONFIG['drop_width'][0] + DEFAULT_RAIN_CONFIG['drop_width'][1]) / 2
                drop_width_range = (DEFAULT_RAIN_CONFIG['drop_width'][1] - DEFAULT_RAIN_CONFIG['drop_width'][0]) * 0.25
                selected_cloud.rain_config['drop_width'] = (
                    max(1, drop_width_center - drop_width_range + (drop_width_slider_value / 200) * (2 * drop_width_range)),
                    max(1, drop_width_center + drop_width_range + (drop_width_slider_value / 200) * (2 * drop_width_range))
                )
            elif slider_dragging == 'density':
                density_center = DEFAULT_RAIN_CONFIG['density']
                density_range = density_center * 0.25
                selected_cloud.rain_config['density'] = max(1, density_center - density_range + (density_slider_value / 200) * (2 * density_range))

            selected_cloud.save_config() 
        # Общий Фон
        screen.fill((192, 192, 192))  
        for cloud in clouds:
            cloud.draw(screen)
        # Панель редактирования
        pygame.draw.rect(screen, (0, 0, 0), editor_rect)
        if selected_cloud:
            font = pygame.font.Font(None, 24)

            density_text = font.render(f"Density: {selected_cloud.rain_config['density']:.2f}", True, (255, 255, 255))
            screen.blit(density_text, (WIDTH - 240, 25))
            pygame.draw.rect(screen, (255, 0, 0), (density_slider_pos[0], density_slider_pos[1], 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (density_slider_pos[0] + density_slider_value, density_slider_pos[1], 10, 20))

            speed_text = font.render(f"Speed: {selected_cloud.rain_config['speed'][0]:.2f} - {selected_cloud.rain_config['speed'][1]:.2f}", True, (255, 255, 255))
            screen.blit(speed_text, (WIDTH - 240, 80))
            pygame.draw.rect(screen, (255, 0, 0), (speed_slider_pos[0], speed_slider_pos[1], 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (speed_slider_pos[0] + speed_slider_value, speed_slider_pos[1], 10, 20))

            drop_length_text = font.render(f"Droplet Length: {selected_cloud.rain_config['drop_length'][0]:.2f} - {selected_cloud.rain_config['drop_length'][1]:.2f}", True, (255, 255, 255))
            screen.blit(drop_length_text, (WIDTH - 240, 130))
            pygame.draw.rect(screen, (255, 0, 0), (drop_length_slider_pos[0], drop_length_slider_pos[1], 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (drop_length_slider_pos[0] + drop_length_slider_value, drop_length_slider_pos[1], 10, 20))

            drop_width_text = font.render(f"Droplet Width: {selected_cloud.rain_config['drop_width'][0]:.2f} - {selected_cloud.rain_config['drop_width'][1]:.2f}", True, (255, 255, 255))
            screen.blit(drop_width_text, (WIDTH - 240, 180))
            pygame.draw.rect(screen, (255, 0, 0), (drop_width_slider_pos[0], drop_width_slider_pos[1], 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (drop_width_slider_pos[0] + drop_width_slider_value, drop_width_slider_pos[1], 10, 20))

        pygame.display.flip()

    for cloud in clouds:
        cloud.delete_config()  # Удаляем конфигурации при выходе

    pygame.quit()

if __name__ == "__main__":
    main()