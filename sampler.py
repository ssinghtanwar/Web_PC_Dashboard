from collections import deque
import threading, time
import metrics

HORIZON_SEC = 300        # 5-minute rolling window
SAMPLE_EVERY = 1.0       # seconds

buffers = {
    'cpu': deque(maxlen=HORIZON_SEC),
    'ram': deque(maxlen=HORIZON_SEC),
    'gpu': deque(maxlen=HORIZON_SEC),
    'net': deque(maxlen=HORIZON_SEC),
}

def _sample():
    now = time.time()
    buffers['cpu'].append((now, metrics.cpu_usage()))
    buffers['ram'].append((now, metrics.ram_usage()))
    gpu_val = metrics.gpu_usage()
    buffers['gpu'].append((now, gpu_val if gpu_val is not None else 0))
    net = metrics.net_usage()
    buffers['net'].append((now, net['bytes_sent'], net['bytes_recv']))
    threading.Timer(SAMPLE_EVERY, _sample).start()

def start():
    _sample()

