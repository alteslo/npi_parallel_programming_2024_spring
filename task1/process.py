import csv
import multiprocessing
import os
import time

import matplotlib.pyplot as plt
import psutil


def infinite_loop():
    while True:
        # Спим 1 секунду в каждой итерации, чтобы избежать полного захвата процессора
        a = 1000 * 10000 // 10 / 10 * 1000
        # time.sleep(1)


def set_affinity(cpu):
    p = psutil.Process(os.getpid())
    p.cpu_affinity([cpu])


def monitor_cpu_usage(duration, interval, output_file):
    end_time = time.time() + duration
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'cpu_percent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while time.time() < end_time:
            cpu_percent = psutil.cpu_percent(interval=interval, percpu=True)
            writer.writerow({'timestamp': time.time(),
                            'cpu_percent': cpu_percent})


def plot_cpu_usage(file):
    timestamps = []
    cpu_usage = []

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamps.append(float(row['timestamp']))
            cpu_usage.append([float(x)
                             for x in row['cpu_percent'][1:-1].split(', ')])

    # Транспонируем список, чтобы получить загрузку по каждому процессору
    cpu_usage = list(map(list, zip(*cpu_usage)))

    for i, usage in enumerate(cpu_usage):
        plt.plot(timestamps, usage, label=f'CPU {i}')

    plt.xlabel('Time')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage Over Time')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    # Создаем процесс с бесконечным циклом
    p = multiprocessing.Process(target=infinite_loop)
    p.start()

    # Запускаем мониторинг загрузки процессоров в отдельном процессе
    monitor_process = multiprocessing.Process(
        target=monitor_cpu_usage, args=(60, 1, 'cpu_usage.csv'))
    monitor_process.start()

    # Последовательное переключение выполнения задачи на различные процессоры
    cpu_count = psutil.cpu_count()

    for cpu in range(cpu_count):
        print(f"Переключился на логический процессор: {cpu}")
        set_affinity(cpu)
        time.sleep(15)  # Ждем 15 секунд на каждом процессоре

    # Завершаем процессы
    p.terminate()
    monitor_process.terminate()

    # Построение графика загрузки процессоров
    plot_cpu_usage('cpu_usage.csv')
