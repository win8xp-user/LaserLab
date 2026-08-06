
# ==============================================================
# PART C
#
# Plot generation
# Final summary
# ==============================================================

from analysis.plots import (
    plot_time_trace,
    plot_histogram,
    plot_cdf,
    plot_boxplot,
    plot_probability,
    plot_autocorrelation,
    plot_fft,
    plot_psd,
    plot_allan,
)


def generate_plots(
    samples,
    statistics,
    metadata,
    results_dir,
):
    """
    Generate all analysis plots.

    Returns
    -------
    list[pathlib.Path]
        List of generated figure filenames.
    """

    print()
    print("Generating figures...")
    print("---------------------")

    sample_rate = 1.0 / SAMPLE_INTERVAL
    ts = metadata["timestamp"]

    generated = []

    generated.append(
        plot_time_trace(
            samples,
            sample_interval=SAMPLE_INTERVAL,
            statistics=statistics,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_histogram(
            samples,
            statistics=statistics,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_cdf(
            samples,
            statistics=statistics,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_boxplot(
            samples,
            statistics=statistics,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_probability(
            samples,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_autocorrelation(
            samples,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_fft(
            samples,
            sample_rate=sample_rate,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_psd(
            samples,
            sample_rate=sample_rate,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    generated.append(
        plot_allan(
            samples,
            sample_rate=sample_rate,
            results_dir=results_dir,
            experiment=EXPERIMENT,
            timestamp=ts,
            show=True,
        )
    )

    metadata["generated_plots"] = [p.name for p in generated]

    print()

    for p in generated:
        print(f"✓ {p.name}")

    return generated


# ----------------------------------------------------------------------
# Add the following immediately after:
#
# statistics = process_measurement(...)
# ----------------------------------------------------------------------
#
# figures = generate_plots(
#     samples,
#     statistics,
#     metadata,
#     results,
# )
#
# elapsed = time.perf_counter() - t_start
#
# print()
# print("=" * 62)
# print("Characterization complete")
# print("=" * 62)
# print()
# print("Result")
# print("------")
# print("PASS")
# print()
# print(f"Elapsed time : {elapsed:.2f} s")
# print(f"Results      : {results}")
# print(f"Figures      : {len(figures)}")
# print("=" * 62)
#
