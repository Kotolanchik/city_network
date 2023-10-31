import heapq
import random
import numpy as np
import matplotlib.pyplot as plt


class CityGrid:
    def __init__(self, rows, cols, obstacle_density=0.3):
        self.cols = cols
        self.obstacle_density = obstacle_density
        self.rows = rows
        self.city_grid = self.generate_city_grid()
        self.optimal_towers = []
        self.obstacle = [row[:] for row in self.city_grid]

    def generate_city_grid(self):
        grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if random.random() < self.obstacle_density:
                    row.append(1)
                else:
                    row.append(0)
            grid.append(row)
        return grid

    def place_tower(self, row, col, radius):
        if self.city_grid[row][col] == 0:
            for r in range(row - radius, row + radius + 1):
                for c in range(col - radius, col + radius + 1):
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        self.city_grid[r][c] = 2

    def place_optimal_towers(self, radius):
        # блоки без препятствий
        available_blocks = [(i, j) for i in range(self.rows) for j in range(self.cols) if self.city_grid[i][j] == 0]

        while available_blocks:
            best_tower_location = None
            max_coverage = 0

            for block in available_blocks:
                row, col = block
                coverage = 0

                # считаем количество непокрытых блоков в радиусе башни
                for r in range(row - radius, row + radius + 1):
                    for c in range(col - radius, col + radius + 1):
                        if 0 <= r < self.rows and 0 <= c < self.cols and self.city_grid[r][c] == 0:
                            coverage += 1

                if coverage > max_coverage:
                    max_coverage = coverage
                    best_tower_location = (row, col)

            if best_tower_location:
                self.optimal_towers.append(best_tower_location)
                self.place_tower(best_tower_location[0], best_tower_location[1], radius)

                # убираем блоки, которые уже покрыты этой башней
                available_blocks = [block for block in available_blocks if
                                    abs(block[0] - best_tower_location[0]) > radius or
                                    abs(block[1] - best_tower_location[1]) > radius]

        return self.optimal_towers

    def find_most_reliable_path(self, start, end):
        visited = set()  # множество для отслеживания посещенных башен
        reliability = {tower: 0 for tower in self.optimal_towers}  # надежности для каждой башни
        reliability[start] = 1  # надежность для начальной башни
        queue = [(1, start)]  # (надежность, башня)
        parent = {start: None}  # словарь для отслеживания родительских башен

        while queue:
            current_reliability, current_tower = heapq.heappop(queue)  # извлекаем путь с наивысшей надежностью
            if current_tower == end:  # если достигнута конечная башня
                path = []  # создаем список для хранения пути
                while current_tower is not None:
                    path.insert(0, current_tower)  # добавляем текущую башню в путь
                    current_tower = parent[current_tower]  # переходим к родительской башне
                return current_reliability, path  # возвращаем надежность и путь

            if current_tower in visited:  # если текущую башню уже посетили, переходим к следующей
                continue

            visited.add(current_tower)  # добавляем текущую башню в посещенные

            for neighbor in self.optimal_towers:  # исследуем соседние башни
                if neighbor != current_tower:  # исключаем самопересечения
                    distance = abs(neighbor[0] - current_tower[0]) + abs(
                        neighbor[1] - current_tower[1])  # расстояние между башнями
                    new_reliability = current_reliability / distance  # новая надежность пути

                    if new_reliability > reliability[neighbor]:  # если путь более надежен
                        reliability[neighbor] = new_reliability  # обновляем надежность соседней башни
                        heapq.heappush(queue, (new_reliability, neighbor))  # добавляем в очередь
                        parent[neighbor] = current_tower  # отмечаем родительскую башню

        return 0, []  # надежного пути не найдено

    def visualize_tower_coverage(self, row, col, radius):
        tower_coverage = [[0] * self.cols for _ in range(self.rows)]

        for r in range(row - radius, row + radius + 1):
            for c in range(col - radius, col + radius + 1):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    tower_coverage[r][c] = 1

        plt.imshow(tower_coverage, cmap='Blues', interpolation='none')
        plt.colorbar()
        plt.show()

    def visualize_grid(self):
        plt.imshow(self.city_grid, cmap='viridis', interpolation='none')
        plt.colorbar()
        plt.show()

    def visualize_towers_without_coverage(self):
        city_copy = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        for tower_location in self.optimal_towers:
            i, j = tower_location[0], tower_location[1]
            city_copy[i][j] = 1

        plt.imshow(city_copy, cmap='viridis', interpolation='none')
        plt.colorbar()
        plt.show()

    def visualize_towers_with_obstacle(self):
        city_copy = [row[:] for row in self.obstacle]

        for tower_location in self.optimal_towers:
            i, j = tower_location[0], tower_location[1]
            city_copy[i][j] = 0.5

        plt.imshow(city_copy, cmap='viridis', interpolation='none')
        plt.colorbar()
        plt.show()

    def visualize_path(self, path):
        city_copy = [row[:] for row in self.city_grid]

        for tower in path:
            row, col = tower
            city_copy[row][col] = 3

        plt.imshow(city_copy, cmap='viridis', interpolation='none')
        plt.colorbar()
        plt.show()


if __name__ == '__main__':
    city = CityGrid(10, 10)
    city.visualize_grid()

    radius = 2
    optimal_towers = city.place_optimal_towers(radius)
    print("Оптимальное расположение башен (координаты):", city.optimal_towers)

    for tower_location in city.optimal_towers:
        city.visualize_tower_coverage(tower_location[0], tower_location[1], radius)

    city.visualize_towers_without_coverage()
    city.visualize_towers_with_obstacle()

    # башни для поиска пути
    start_tower = optimal_towers[0]
    end_tower = optimal_towers[-1]

    reliability, path = city.find_most_reliable_path(start_tower, end_tower)
    if reliability > 0:
        print("Надежность:", reliability)
        print("Путь:", path)
        city.visualize_path(path)
    else:
        print("Не удалось найти путь")
