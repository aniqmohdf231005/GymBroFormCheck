from pathlib import Path

import pandas as pd


def _window_for_series(series, requested_window, polyorder):
    valid_count = int(series.notna().sum())
    if valid_count <= polyorder:
        return None

    window = min(requested_window, valid_count)
    if window % 2 == 0:
        window -= 1

    if window <= polyorder:
        window = polyorder + 1
        if window % 2 == 0:
            window += 1

    return window if window <= valid_count else None


def smooth_coordinates(
    input_csv,
    output_csv=None,
    window_length=11,
    polyorder=2,
    progress_callback=None,
):
    """Smooth landmark coordinate columns using a Savitzky-Golay filter."""
    try:
        from scipy.signal import savgol_filter
    except ImportError as exc:
        raise RuntimeError(
            "Coordinate smoothing needs scipy. Run: pip install -r requirements.txt"
        ) from exc

    input_csv = Path(input_csv)
    output_csv = Path(output_csv or Path("data/outputs") / f"{input_csv.stem}_smoothed.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if progress_callback:
        progress_callback(62, "Smoothing landmark coordinates...")

    df = pd.read_csv(input_csv)
    coordinate_columns = [
        column
        for column in df.columns
        if column != "frame" and not column.startswith("visibility_")
    ]

    for column in coordinate_columns:
        numeric = pd.to_numeric(df[column], errors="coerce")
        filled = numeric.interpolate(limit_direction="both")
        window = _window_for_series(filled, window_length, polyorder)

        if window is None:
            df[column] = filled
        else:
            df[column] = savgol_filter(filled, window_length=window, polyorder=polyorder)

    df.to_csv(output_csv, index=False)
    if progress_callback:
        progress_callback(70, "Smoothed landmark CSV exported.")
    return str(output_csv)
