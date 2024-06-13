import statistics
import time

import numpy as np


def MultMat(A, B):
    """Перемножение матриц по стандартной формуле."""
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C


def TestMultTime(N, NT):
    """Тестирование времени выполнения перемножения матриц."""
    times = []
    for _ in range(NT):
        A = np.random.rand(N, N)
        B = np.random.rand(N, N)

        start = time.perf_counter()
        MultMat(A, B)
        end = time.perf_counter()

        times.append(end - start)

    min_time = min(times)
    max_time = max(times)
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    print(f"Размер матриц: {N}x{N}, Количество запусков: {NT}")
    print(f"Минимальное время: {min_time:.6f} секунд")
    print(f"Максимальное время: {max_time:.6f} секунд")
    print(f"Среднее время: {mean_time:.6f} секунд")
    print(f"Среднее квадратическое отклонение: {std_dev:.6f} секунд")

    return mean_time


def compute_mflops(mean_time, N):
    """Вычисление производительности в MFlops."""
    operations = 2 * (N ** 3)
    mflops = (operations / mean_time) / 1e6
    print(f"Производительность: {mflops:.2f} MFlops")
    return mflops


def optimized_mult_mat(A, B):
    """Оптимизированное перемножение матриц с использованием NumPy."""
    return np.dot(A, B)


def TestMultTimeOptimized(N, NT):
    """Тестирование времени выполнения оптимизированного перемножения матриц."""
    times = []
    for _ in range(NT):
        A = np.random.rand(N, N)
        B = np.random.rand(N, N)

        start = time.perf_counter()
        optimized_mult_mat(A, B)
        end = time.perf_counter()

        times.append(end - start)

    min_time = min(times)
    max_time = max(times)
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)

    print(
        f"Размер матриц: {N}x{N}, Количество запусков: {NT} (Оптимизировано)")
    print(f"Минимальное время: {min_time:.6f} секунд")
    print(f"Максимальное время: {max_time:.6f} секунд")
    print(f"Среднее время: {mean_time:.6f} секунд")
    print(f"Среднее квадратическое отклонение: {std_dev:.6f} секунд")

    return mean_time


def main():
    Ns = [100, 200, 300]  # Примеры различных размеров матриц
    NTs = [10, 20, 30]  # Примеры различных количества запусков

    for N in Ns:
        for NT in NTs:
            mean_time = TestMultTime(N, NT)
            compute_mflops(mean_time, N)

            mean_time_optimized = TestMultTimeOptimized(N, NT)
            compute_mflops(mean_time_optimized, N)


if __name__ == '__main__':
    main()
