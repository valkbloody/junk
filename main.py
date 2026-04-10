import numpy as np
import matplotlib.pyplot as plt

# Форматирование времени в вид HH:MM
def format_time(total_minutes, start_hour=8, start_minute=0):
    total = start_hour * 60 + start_minute + int(total_minutes)
    hours = (total // 60) % 24
    minutes = total % 60
    return f"{hours:02d}:{minutes:02d}"

# Генерация количества вагонов в одном поезде
def gen_wag_amount(avr_wagons, avr_div):
    wagons = round(np.random.normal(avr_wagons, avr_div))
    return max(1, wagons)

# Один эксперимент моделирования
def simulate_one_experiment(T_minutes, lam, avr_wagons=10, avr_div=4):
    arrival_times = []
    wagon_counts = []

    current_time = 0.0

    while True:

        delta_t = np.random.exponential(scale=1 / lam)
        current_time += delta_t

        if current_time > T_minutes:
            break

        wagons = gen_wag_amount(avr_wagons, avr_div)

        arrival_times.append(current_time)
        wagon_counts.append(wagons)

    return arrival_times, wagon_counts

# Расчеты для одного эксперимента
def calculate_statistics(arrival_times, wagon_counts, T_minutes, lam, avr_wagons):
    train_count = len(arrival_times)
    total_wagons = sum(wagon_counts)
    avg_wagons = total_wagons / train_count if train_count > 0 else 0.0
    est_train_int = train_count / T_minutes
    est_wagon_int = total_wagons / T_minutes
    theory_train_int = lam
    theory_wagon_int = lam * avr_wagons

    return {
        "Количество поездов": train_count,
        "Количество вагонов": total_wagons,
        "Среднее число вагонов на поезд": avg_wagons,
        "Оценка интенсивности потока поездов": est_train_int,
        "Теоретическая интенсивность потока поездов": theory_train_int,
        "Оценка интенсивности потока вагонов": est_wagon_int,
        "Теоретическая интенсивность потока вагонов": theory_wagon_int,
    }


#Рассчет для всех эксперементов
def run_multiple_experiments(T_minutes, lam, experiments,  start_hour, start_minute, avr_wagons, avr_div):
    train_counts = []
    wagon_totals = []
    avg_wagons_list = []
    train_intensities = []
    wagon_intensities = []
    first_arrivals = None
    first_wagons = None

    for i in range(experiments):
        arrival_times, wagon_counts = simulate_one_experiment(T_minutes, lam, avr_wagons, avr_div)
        if i == 0:
            first_arrivals = arrival_times
            first_wagons = wagon_counts
        stats = calculate_statistics(arrival_times, wagon_counts, T_minutes, lam, avr_wagons)
        train_counts.append(stats["Количество поездов"])
        wagon_totals.append(stats["Количество вагонов"])
        avg_wagons_list.append(stats["Среднее число вагонов на поезд"])
        train_intensities.append(stats["Оценка интенсивности потока поездов"])
        wagon_intensities.append(stats["Оценка интенсивности потока вагонов"])
        print_event_table(first_arrivals, first_wagons, start_hour, start_minute, i+1)

    summary_stats = {
        "Среднее количество поездов": np.mean(train_counts),
        "Среднее количество вагонов": np.mean(wagon_totals),
        "Среднее число вагонов на поезд": np.mean(avg_wagons_list),
        "Средняя оценка интенсивности потока поездов": np.mean(train_intensities),
        "Средняя оценка интенсивности потока вагонов": np.mean(wagon_intensities),
        "Стандартное отклонение числа поездов": np.std(train_counts, ddof=1) if experiments > 1 else 0.0,
        "Стандартное отклонение числа вагонов": np.std(wagon_totals, ddof=1) if experiments > 1 else 0.0,
    }
    return first_arrivals, first_wagons, summary_stats

# Печать таблицы поездов
def print_event_table(arrival_times, wagon_counts, start_hour=10, start_minute=0, num = 1):
    print("\nТаблица прибытия поездов "+str(num))
    print("-" * 30)
    print(f"{'№':<6}{'Время':<12}{'Количество вагонов':<10}")
    print("-" * 30)

    for i, (t, w) in enumerate(zip(arrival_times, wagon_counts), start=1):
        print(f"{i:<6}{format_time(t, start_hour, start_minute):<12}{w:<10}")

    print("-" * 30)


# Печать статистики
def print_statistics(single_stats, summary_stats):
    print("\nРезультаты одного эксперимента")
    print("-" * 30)
    for key, value in single_stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")

    print("\nУсредненные результаты по серии экспериментов")
    print("-" * 30)
    for key, value in summary_stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")


# Подписи оси X в формате HH:MM
def build_time_ticks(T_minutes, start_hour=8, start_minute=0, step=60):
    step = T_minutes / 6
    ticks = np.arange(0, T_minutes + 1, step)
    labels = [format_time(t, start_hour, start_minute) for t in ticks]
    return ticks, labels


# Построение графиков
def plot_results(arrival_times, wagon_counts, T_minutes, lam, mean_wagons, start_hour=8, start_minute=0):
    if len(arrival_times) == 0:
        print("За время моделирования не произошло ни одного прибытия.")
        return

    arrival_times = np.array(arrival_times)
    wagon_counts = np.array(wagon_counts)
    cumulative_trains = np.arange(1, len(arrival_times) + 1)
    cumulative_wagons = np.cumsum(wagon_counts)
    theory_train_x = np.array([0, T_minutes])
    theoty_train_y = lam * theory_train_x
    theory_wagon_x = np.array([0, T_minutes])
    theory_wagon_y = lam * mean_wagons * theory_wagon_x
    ticks, labels = build_time_ticks(T_minutes, start_hour, start_minute)
    plt.figure(figsize=(14, 8))
    # График накопления поездов
    plt.subplot(2, 2, 1)
    plt.step(arrival_times, cumulative_trains, where="post", label="Смоделированный поток",color="black")
    plt.plot(theory_train_x, theoty_train_y, "--", label="Теоретическое ожидание", color="red")
    plt.title("Количество поездов, побывавшее на станции в момент времени")
    plt.xlabel("Время")
    plt.ylabel("Количество поездов")
    plt.xticks(ticks, labels, rotation=45)
    plt.grid(True)
    plt.legend()

    # График накопления вагонов
    plt.subplot(2, 2, 2)
    plt.step(arrival_times, cumulative_wagons, where="post", label="Смоделированный поток",color="black")
    plt.plot(theory_wagon_x, theory_wagon_y, "--", label="Теоретическое ожидание",color="red")
    plt.title("Количество вагонов, побывавшее на станции в момент времени")
    plt.xlabel("Время")
    plt.ylabel("Количество вагонов")
    plt.xticks(ticks, labels, rotation=45)
    plt.grid(True)
    plt.legend()
    # Гистограмма количества вагонов
    plt.subplot(2, 1, 2)
    bins = range(int(min(wagon_counts)), int(max(wagon_counts)) + 2)
    plt.hist(wagon_counts, bins=bins, edgecolor="black", align="left",color="green")
    plt.title("Количество вагонов в одном поезде")
    plt.xlabel("Количество вагонов")
    plt.ylabel("Частота")
    plt.grid(True)
    plt.tight_layout()
    plt.get_current_fig_manager().full_screen_toggle()
    plt.show()

# Проверка ввода
def validate_input(T_minutes, lam, experiments, mean_wagons, std_wagons):
    if lam <= 0:
        raise ValueError("Интенсивность потока поездов должна быть положительной.")
    if T_minutes <= 0:
        raise ValueError("Время моделирования должно быть положительным.")
    if experiments <= 0:
        raise ValueError("Количество экспериментов должно положительным.")
    if mean_wagons <= 0:
        raise ValueError("Среднее число вагонов должно быть больше 0.")
    if std_wagons < 0:
        raise ValueError("Стандартное отклонение не может быть отрицательным.")


def main():
    print("Вариант 4: процесс появления вагонов на железнодорожной станции\n")
    avr_vagons = 10 # среднее
    avr_dev = 4 # среднеквадратическое отклонение
    start_hour = 10
    start_minute = 0
    try:
        while(True):
            print(("-"*20)+"\nМеню\n"+("-"*20)+"\n1 - Начать моделирование\n0 - выход")
            choice = int(input("Ваш выбор: "))
            if(choice == 1):
                T_minutes = float(input("Введите время моделирования в минутах: "))
                lam = float(input("Введите интенсивность потока поездов(количество поездов в минуту): "))
                experiments = int(input("Введите количество экспериментов: "))
                validate_input(T_minutes, lam, experiments, avr_vagons, avr_dev)
                first_arrivals, first_wagons, summary_stats = run_multiple_experiments(T_minutes=T_minutes, lam=lam, experiments=experiments, start_hour=start_hour,start_minute=start_minute,avr_wagons=avr_vagons, avr_div=avr_dev)
                single_stats = calculate_statistics(first_arrivals,first_wagons,T_minutes,lam,avr_vagons)
                print_statistics(single_stats, summary_stats)
                plot_results(first_arrivals,first_wagons,T_minutes,lam,avr_vagons,start_hour,start_minute)
            elif(choice == 0):
                break
            else:
                print("Неверный выбор")
    except ValueError as error:
        print(f"Ошибка ввода: {error}")


if __name__ == "__main__":
    main()