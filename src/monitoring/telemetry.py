"""
Telemetry Monitoring Module

Provides real-time performance metrics for video processing applications.
Displays live updating status line with FPS, CPU, and RAM usage.
"""
import time
import sys
from typing import Optional, Tuple, List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class TelemetryMonitor:
    """
    Non-invasive telemetry monitor for real-time performance tracking.

    Tracks FPS using exponential moving average, RAM usage in MB/GB,
    and per-core CPU percentages. Outputs to terminal using carriage
    return for live updating status line.

    Example:
        monitor = TelemetryMonitor(enabled=True)

        while True:
            monitor.start_frame()
            # ... process frame ...
            monitor.print_status()

        monitor.print_final_stats()
    """

    def __init__(self, enabled: bool = True, smoothing: float = 0.1):
        """
        Initialize the telemetry monitor.

        Args:
            enabled: If False, all methods become no-ops
            smoothing: EMA smoothing factor (0.0-1.0)
                      Lower = smoother, Higher = more responsive
                      Recommended: 0.1 (10-frame smoothing)
        """
        self.enabled = enabled and PSUTIL_AVAILABLE
        self.smoothing = smoothing

        # FPS tracking
        self.fps = 0.0
        self.last_frame_time: Optional[float] = None
        self.frame_count = 0

        # Process handle for metrics
        if self.enabled:
            self.process = psutil.Process()
            self.cpu_count = psutil.cpu_count()
            # Prime CPU measurement to get accurate readings immediately
            psutil.cpu_percent(interval=0.1, percpu=True)
        else:
            self.process = None
            self.cpu_count = 0

        # Display state
        self.last_status_length = 0

        # Warn if psutil not available
        if enabled and not PSUTIL_AVAILABLE:
            print("Warning: psutil not installed. Telemetry disabled.")
            print("Install with: pip install psutil")

    def start_frame(self) -> None:
        """
        Mark the start of a frame. Call at the beginning of each loop iteration.

        Calculates FPS using exponential moving average for smooth, stable readings.
        """
        if not self.enabled:
            return

        current_time = time.time()

        # Calculate FPS using exponential moving average
        if self.last_frame_time is not None:
            frame_time = current_time - self.last_frame_time
            if frame_time > 0:
                instant_fps = 1.0 / frame_time
                # EMA: smooth FPS to avoid jitter
                self.fps = (self.smoothing * instant_fps +
                           (1 - self.smoothing) * self.fps)

        self.last_frame_time = current_time
        self.frame_count += 1

    def get_ram_usage(self) -> Tuple[float, str]:
        """
        Get current RAM usage of this process.

        Returns:
            tuple: (value, unit) e.g., (245.3, "MB") or (1.2, "GB")
        """
        if not self.enabled:
            return 0.0, "MB"

        bytes_used = self.process.memory_info().rss
        mb_used = bytes_used / (1024 * 1024)

        if mb_used >= 1024:
            return mb_used / 1024, "GB"
        else:
            return mb_used, "MB"

    def get_cpu_usage(self) -> List[float]:
        """
        Get per-core CPU usage percentages.

        Returns:
            list: CPU percentage for each core (0.0-100.0)
                  Empty list if monitoring disabled
        """
        if not self.enabled:
            return []

        # Get per-core percentages
        # interval=0 uses cached values for performance
        return psutil.cpu_percent(interval=0, percpu=True)

    def format_status_line(self) -> str:
        """
        Format the complete telemetry status line.

        Returns:
            Formatted string: "FPS: 29.4 | RAM: 245.3 MB | CPU: [12.5, 8.3, 15.2, 10.1]%"
        """
        if not self.enabled:
            return ""

        # Get metrics
        ram_value, ram_unit = self.get_ram_usage()
        cpu_percentages = self.get_cpu_usage()

        # Format CPU as compact list
        cpu_str = "[" + ", ".join(f"{cpu:.1f}" for cpu in cpu_percentages) + "]"

        # Build status line
        status = (f"FPS: {self.fps:.1f} | "
                 f"RAM: {ram_value:.1f} {ram_unit} | "
                 f"CPU: {cpu_str}%")

        return status

    def print_status(self) -> None:
        """
        Print live updating status line using carriage return.

        Overwrites previous line in-place for smooth terminal updates.
        Works correctly with cv2.imshow() windows.
        """
        if not self.enabled:
            return

        status = self.format_status_line()

        # Clear previous line if it was longer
        if len(status) < self.last_status_length:
            # Pad with spaces to clear old text
            status = status.ljust(self.last_status_length)

        self.last_status_length = len(status)

        # Print with carriage return (no newline)
        sys.stdout.write(f'\r{status}')
        sys.stdout.flush()

    def print_final_stats(self) -> None:
        """
        Print final statistics summary on program exit.

        Adds newline to prevent terminal prompt from overwriting status.
        """
        if not self.enabled:
            return

        print()  # New line after live status
        print("\n" + "=" * 50)
        print("Telemetry Summary:")
        print(f"  Total Frames: {self.frame_count}")
        print(f"  Average FPS: {self.fps:.1f}")

        ram_value, ram_unit = self.get_ram_usage()
        print(f"  Final RAM: {ram_value:.1f} {ram_unit}")
        print("=" * 50)
