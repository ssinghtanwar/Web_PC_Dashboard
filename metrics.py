import psutil, datetime, platform, time
try:
    import pynvml
    pynvml.nvmlInit()
except ImportError:
    pynvml = None


def uptime():
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    return datetime.datetime.now() - boot

def cpu_usage():
    return psutil.cpu_percent(percpu=False)

def per_proc_cpu():
    # returns (name, pid, percent) sorted descending
    procs = [(p.name(), p.pid, p.cpu_percent())
             for p in psutil.process_iter(['name'])]
    return sorted(procs, key=lambda x: x[2], reverse=True)

def ram_usage():
    vm = psutil.virtual_memory()
    return vm.used / vm.total * 100  # percent

def gpu_usage():
    if not pynvml:
        return None
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    util   = pynvml.nvmlDeviceGetUtilizationRates(handle)
    return util.gpu  # percent

def net_usage():
    io = psutil.net_io_counters()
    return {'bytes_sent': io.bytes_sent, 'bytes_recv': io.bytes_recv,
            'time': time.time()}

def top_cpu_proc():
    """(name, pid, pct) for biggest CPU consumer in the last instant."""
    procs = [(p.name(), p.pid, p.cpu_percent())
             for p in psutil.process_iter(['name'])]
    return max(procs, key=lambda x: x[2], default=("–", 0, 0.0))

def top_ram_proc():
    """Return (name, pid, MB_used) of process with most resident RAM."""
    procs = [(p.name(), p.pid, p.memory_info().rss / 2**20)  # MiB
             for p in psutil.process_iter(['name'])]
    return max(procs, key=lambda x: x[2], default=("–", 0, 0.0))

def top_gpu_proc():
    """
    Return (name, pid, MiB) of process with most GPU memory.
    Falls back to (None, 0, 0) if NVML missing or no processes found.
    """
    if not pynvml:
        return ("–", 0, 0.0)

    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    try:
        procs = pynvml.nvmlDeviceGetGraphicsRunningProcesses_v3(handle)
    except AttributeError:        # older driver
        procs = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)

    if not procs:
        return ("–", 0, 0.0)

    # Build (name, pid, used_mb) tuples
    table = []
    for p in procs:
        pid = p.pid
        used = p.usedGpuMemory / 2**20          # bytes → MiB
        try:
            name = psutil.Process(pid).name()
        except psutil.NoSuchProcess:
            name = "pid_" + str(pid)
        table.append((name, pid, used))

    return max(table, key=lambda x: x[2])

def top_net_proc():
    """
    Return (name, pid, MB_total_io) of the process with the most cumulative
    network traffic (bytes_sent + bytes_recv).

    Works on Linux with psutil ≥ 5.10 where Process.net_io_counters()
    is implemented.  On other OSes (or kernels that don’t expose it),
    it falls back gracefully.
    """
    totals = []
    for p in psutil.process_iter(['name']):
        try:
            io = p.net_io_counters()           # may raise AttributeError
            if io is None:
                continue
            mb = (io.bytes_sent + io.bytes_recv) / 2**20
            totals.append((p.name(), p.pid, mb))
        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                AttributeError):
            continue

    return max(totals, key=lambda x: x[2],
               default=("–", 0, 0.0))

