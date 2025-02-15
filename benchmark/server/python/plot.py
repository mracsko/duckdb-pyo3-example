import matplotlib.pyplot as plt
import numpy as np
import csv

def plot_compare(title, file_name, output_file):
    categories = []
    json_values = []
    flight_values = []

    with open(file_name, mode='r') as file:
        csvFile = csv.reader(file)
        header_processed = False
        for lines in csvFile:
            if not header_processed:
                header_processed = True
                continue
            categories.append(lines[0])
            json_values.append(float(lines[1]))
            flight_values.append(float(lines[2]))

    # Convert values to nanoseconds
    json_values_us = [val * 1e9 for val in json_values]
    flight_values_us = [val * 1e9 for val in flight_values]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width / 2, json_values_us, width, label='JSON', color='#96DCF8')
    rects2 = ax.bar(x + width / 2, flight_values_us, width, label='Flight', color='#F6C6AD')

    # Labels, title, and custom x-axis tick labels
    ax.set_xlabel(f'Measurement ({title})')
    ax.set_ylabel('Nanoseconds (ns)')
    ax.set_title(f'Comparison of JSON vs Flight ({title})')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=30, ha="right")
    ax.legend()

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:,}'.replace(",", " ").replace(".0", "")))

    def add_labels(rects, percentage_baselines=None):
        for i,rect in enumerate(rects):
            height = rect.get_height()
            label = f'{int(height):,}'.replace(",", " ") + f"\n({height/percentage_baselines[i].get_height()*100:.2f}%)"
            ax.text(
                rect.get_x() + rect.get_width() / 2, height,  # Adjusted position
                label,  # Format with spaces
                ha='center', va='bottom', fontsize=6
            )

    # Add value labels on bars
    add_labels(rects1,rects2)
    add_labels(rects2,rects1)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Plot saved to {output_file}")


def plot_measurement_compare(file_name, output_file):
    categories = []
    json_values = []
    flight_values = []

    with open(file_name, mode='r') as file:
        csvFile = csv.reader(file)
        header_processed = False
        for lines in csvFile:
            if not header_processed:
                header_processed = True
                continue
            categories.append(lines[0])
            json_values.append(float(lines[1]))
            flight_values.append(float(lines[2]))

    json_values_us = [val * 1e9 for val in json_values]
    flight_values_us = [val * 1e9 for val in flight_values]
    json_values_percentage = []
    flight_values_percentage = []

    for i, value in enumerate(json_values_us):
        json_values_percentage.append(value / flight_values_us[i] * 100)
        flight_values_percentage.append(flight_values_us[i] / value * 100)


    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot lines
    ax.plot(categories, json_values_percentage, marker='o', linestyle='-', label='JSON', color='#0F9ED5')
    ax.plot(categories, flight_values_percentage, marker='o', linestyle='-', label='Flight', color='#E97132')

    # Labels, title, and formatting
    ax.set_xlabel(f'Measurements')
    ax.set_ylabel('Difference (%)')
    ax.set_title(f'Comparison of JSON vs Flight Mean Duration')
    ax.legend()

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:,}'.replace(",", " ").replace(".0", "")))

    # Function to add labels to points
    def add_labels(x_values, y_values, percentages, baseline_values):
        for i, value in enumerate(y_values):
            label = f'{int(value):,}'.replace(","," ") + f"\n({value / baseline_values[i] * 100:.2f}%)"
            ax.text(
                x_values[i], percentages[i] + (percentages[i] * 0.01),  # Offset for visibility
                label,
                ha='center', fontsize=6
            )

    # Add labels to both lines
    add_labels(categories, json_values_us, json_values_percentage, flight_values_us)
    add_labels(categories, flight_values_us, flight_values_percentage, json_values_us)

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Plot saved to {output_file}")