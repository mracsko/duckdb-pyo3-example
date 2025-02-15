import plot

output_dir = "../stats"

plot.plot_compare("xxs", f"{output_dir}/python_json_vs_flight_comparison_xxs.csv", f"{output_dir}/python_json_vs_flight_comparison_xxs.png")
plot.plot_compare("xs", f"{output_dir}/python_json_vs_flight_comparison_xs.csv", f"{output_dir}/python_json_vs_flight_comparison_xs.png")
plot.plot_compare("s", f"{output_dir}/python_json_vs_flight_comparison_s.csv", f"{output_dir}/python_json_vs_flight_comparison_s.png")
plot.plot_compare("m", f"{output_dir}/python_json_vs_flight_comparison_m.csv", f"{output_dir}/python_json_vs_flight_comparison_m.png")
plot.plot_compare("l", f"{output_dir}/python_json_vs_flight_comparison_l.csv", f"{output_dir}/python_json_vs_flight_comparison_l.png")
plot.plot_compare("xl", f"{output_dir}/python_json_vs_flight_comparison_xl.csv", f"{output_dir}/python_json_vs_flight_comparison_xl.png")
plot.plot_compare("xxl", f"{output_dir}/python_json_vs_flight_comparison_xxl.csv", f"{output_dir}/python_json_vs_flight_comparison_xxl.png")

plot.plot_measurement_compare(f"{output_dir}/python_json_vs_flight_mean_comparison.csv", f"{output_dir}/python_json_vs_flight_mean_comparison.png")

plot.plot_compare("xxs", f"{output_dir}/rust_json_vs_flight_comparison_xxs.csv", f"{output_dir}/rust_json_vs_flight_comparison_xxs.png")
plot.plot_compare("xs", f"{output_dir}/rust_json_vs_flight_comparison_xs.csv", f"{output_dir}/rust_json_vs_flight_comparison_xs.png")
plot.plot_compare("s", f"{output_dir}/rust_json_vs_flight_comparison_s.csv", f"{output_dir}/rust_json_vs_flight_comparison_s.png")
plot.plot_compare("m", f"{output_dir}/rust_json_vs_flight_comparison_m.csv", f"{output_dir}/rust_json_vs_flight_comparison_m.png")
plot.plot_compare("l", f"{output_dir}/rust_json_vs_flight_comparison_l.csv", f"{output_dir}/rust_json_vs_flight_comparison_l.png")
plot.plot_compare("xl", f"{output_dir}/rust_json_vs_flight_comparison_xl.csv", f"{output_dir}/rust_json_vs_flight_comparison_xl.png")
plot.plot_compare("xxl", f"{output_dir}/rust_json_vs_flight_comparison_xxl.csv", f"{output_dir}/rust_json_vs_flight_comparison_xxl.png")

plot.plot_measurement_compare(f"{output_dir}/rust_json_vs_flight_mean_comparison.csv", f"{output_dir}/rust_json_vs_flight_mean_comparison.png")