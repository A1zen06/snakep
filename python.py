"""Игра «Изгиб Питона» (Змейка на Pygame с использованием ООП)."""

from random import randint
import sys

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр игрового поля:
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения змейки:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цветовая палитра:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения игрового цикла:
SPEED = 20

# Настройка главного игрового окна Pygame:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: tuple[int, int] = SCREEN_CENTER,
        body_color: tuple[int, int, int] | None = None,
    ):
        """Инициализирует базовые параметры игрового объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """Абстрактный метод отрисовки объекта на игровой поверхности."""
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(self, occupied_positions: list[tuple[int, int]] | None = None):
        """Инициализирует цвет яблока и его начальное положение."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions or [])

    def randomize_position(
        self, occupied_positions: list[tuple[int, int]] | None = None
    ) -> None:
        """Устанавливает случайное положение яблока на свободных ячейках."""
        occupied = occupied_positions or []
        while True:
            random_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            random_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (random_x, random_y)
            if new_position not in occupied:
                self.position = new_position
                break

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её механику перемещения."""

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        super().__init__(position=SCREEN_CENTER, body_color=SNAKE_COLOR)
        self.reset()

    def update_direction(self) -> None:
        """Обновляет текущее направление движения на следующее заданное."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет координаты сегментов змейки с циклическим проходом границ."""
        current_x, current_y = self.get_head_position()
        delta_x, delta_y = self.direction

        # Вычисляем новую позицию головы с цикличным переносом через стены:
        new_x = (current_x + delta_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (current_y + delta_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Добавляем новую голову в начало списка сегментов:
        self.positions.insert(0, new_head)
        self.position = new_head

        # Если длина змейки не увеличилась, удаляем последний хвостовой сегмент:
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает все сегменты змейки и затирает предыдущий хвост."""
        # Отрисовка головы змейки:
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание следа последнего удаленного сегмента:
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в исходное начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш пользователя и меняет направление движения."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()


def main() -> None:
    """Главная функция с основным игровым циклом."""
    pygame.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    while True:
        clock.tick(SPEED)

        # 1. Обработка пользовательского ввода:
        handle_keys(snake)
        snake.update_direction()

        # 2. Перемещение змейки:
        snake.move()

        # 3. Проверка столкновения головы с собственным телом:
        if snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        # 4. Проверка поедания яблока:
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # 5. Отрисовка игровых объектов и обновление экрана:
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()