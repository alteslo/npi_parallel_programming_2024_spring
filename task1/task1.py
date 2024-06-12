import csv
import math
import multiprocessing
import os
import time
from queue import Queue

import matplotlib.pyplot as plt
import psutil

task_queue = Queue()


def compute_task():
    """Вычислительно затратная задача."""
    primes = []
    for num in range(100000, 100500):
        if all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1)):
            primes.append(num)


def set_affinity(cpu):
    """Устанавливаем привязку процесса к конкретному CPU."""
    p = psutil.Process(os.getpid())
    p.cpu_affinity([cpu])


def monitor_cpu_usage(duration, interval, output_file):
    """Мониторим загрузку CPU и записываем данные в CSV файл."""
    end_time = time.time() + duration
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'cpu_percent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while time.time() < end_time:
            cpu_percent = psutil.cpu_percent(interval=interval, percpu=True)
            writer.writerow({'timestamp': time.time(),
                             'cpu_percent': cpu_percent})


def plot_cpu_usage(file, switch_times):
    """Построение графиков загрузки процессоров по данным из CSV файла."""
    timestamps = []
    cpu_usage = []

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamps.append(float(row['timestamp']))
            cpu_usage.append([float(x)
                              for x in row['cpu_percent'][1:-1].split(', ')])

    if not timestamps:
        print("Нет данных для построения графика.")
        return

    # Транспонируем список, чтобы получить загрузку по каждому процессору
    cpu_usage = list(map(list, zip(*cpu_usage)))

    # Создаем подграфики для каждого процессора
    num_cpus = len(cpu_usage)
    fig, axes = plt.subplots(
        num_cpus, 1, figsize=(10, 2 * num_cpus), sharex=True)

    if num_cpus == 1:
        axes = [axes]

    for i, usage in enumerate(cpu_usage):
        axes[i].plot(timestamps, usage, label=f'CPU {i}')
        for switch_time in switch_times:
            axes[i].axvline(x=switch_time, color='r', linestyle='--')
        axes[i].set_ylabel('Usage (%)')
        axes[i].legend(loc='upper right')

    plt.xlabel('Time (s)')
    plt.suptitle('CPU Usage Over Time with Switch Points')
    plt.show()


def process_task(cpu, duration):
    set_affinity(cpu)
    print(f"Переключился на логический процессор: {cpu}")
    end_time = time.time() + duration
    while time.time() < end_time:
        compute_task()
    print(
        f"Задача на процессоре {cpu} завершена за {end_time}.")


if __name__ == '__main__':
    # Запускаем мониторинг загрузки процессоров в отдельном процессе
    monitor_process = multiprocessing.Process(
        target=monitor_cpu_usage, args=(175, 1, 'cpu_usage.csv'))  # Увеличиваем время мониторинга до 175 секунд
    monitor_process.start()

    # Последовательное переключение выполнения задачи на различные процессоры
    cpu_count = psutil.cpu_count()
    switch_times = []

    for cpu in range(cpu_count):
        task_queue.put(cpu)

    while not task_queue.empty():
        cpu = task_queue.get()
        switch_times.append(time.time())
        # Выполняем задачу на каждом процессоре в течение 15 секунд
        process_task(cpu, 15)

    # Завершаем процессы мониторинга
    monitor_process.terminate()

    # Ждем, пока данные не будут записаны в файл
    time.sleep(2)

    # Построение графика загрузки процессоров
    plot_cpu_usage('cpu_usage.csv', switch_times)
