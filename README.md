```markdown
# 🖥️ PC-Dashboard

_A live, browser-based system monitor written entirely in Python._

![demo gif](docs/demo.gif) <!-- Replace with an actual screenshot or GIF -->

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Project Layout](#project-layout)
- [Configuration](#configuration)
- [FAQ](#faq)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Category               | Detail                                                                                         | Status                            |
|------------------------|------------------------------------------------------------------------------------------------|-----------------------------------|
| **Uptime**             | Human-friendly uptime badge                                                                    | ✅                                |
| **CPU**                | • Current utilisation  <br>• 5-minute rolling chart  <br>• “CPU-hungry” process card           | ✅                                |
| **RAM**                | • Current utilisation  <br>• 5-minute rolling chart  <br>• “RAM-hungry” process card           | ✅                                |
| **GPU (NVIDIA)**       | • Current utilisation & memory  <br>• 5-minute rolling chart  <br>• “GPU-hungry” process card   | ✅                                |
| **Network (system-wide)** | • Bytes sent / received chart                                                              | ✅                                |
| **Network (per-process)** | “Network-hungry” process card via `pynethogs`                                               | 🚧 *Experimental – Linux-only*    |

> **Heads-up:** Per-process network stats rely on the Linux kernel’s traffic accounting and  
> the [`pynethogs`](https://github.com/raboof/pynethogs) binding.  
> On Windows/macOS (or if `pynethogs` isn’t installed) the card shows **“– (PID 0) – 0 MiB”** or is hidden.

---

## Quick Start

```bash
git clone https://github.com/<your-user>/pc-dashboard.git
cd pc-dashboard

# Core dependencies
pip install -r requirements.txt

# Optional extras
pip install gputil nvidia-ml-py3   # NVIDIA GPU stats
pip install pynethogs              # per-process network card (Linux only)

python app.py                      # then open http://localhost:8050
```

---

## Project Layout

```text
pc-dashboard
├── app.py          ← Dash UI & callbacks
├── metrics.py      ← Hardware / process-stat helpers
├── sampler.py      ← 1 Hz background sampler
├── requirements.txt
└── docs/
    └── demo.gif
```

---

## Configuration

| Option                | File         | Default | Notes                                                     |
|-----------------------|--------------|---------|-----------------------------------------------------------|
| Sampling interval     | `sampler.py` | 1 s     | Lower → smoother graphs (higher CPU)                      |
| History window        | `sampler.py` | 300 s   | `deque` automatically drops points older than window      |
| Per-process network   | `metrics.top_net_proc()` | off | Requires `pynethogs`; experimental / Linux-only           |

---

## FAQ

<details>
<summary>Why does the Network-hungry card show “– (PID 0) – 0 MiB”?</summary>

`psutil` cannot expose per-process traffic counters on most OSes.  
Install **pynethogs** on Linux (see *Quick Start*) or comment out the card in `app.py`.

</details>

<details>
<summary>GPU stats are blank on my AMD / Intel iGPU machine.</summary>

The current backend uses NVIDIA’s NVML.  
Multi-vendor support is on the roadmap — PRs welcome!

</details>

---

## Roadmap

- [ ] Dark-mode toggle  
- [ ] AMD / Intel GPU backend (`rocm-smi`, `intel-gpu-top`)  
- [ ] **Finish cross-platform per-process network monitoring**  
- [ ] Prometheus / InfluxDB exporter  
- [ ] Electron wrapper for tray-icon autostart  

---

## Contributing

1. **Fork** → create a feature branch → `pip install -r dev-requirements.txt`  
2. Run `pre-commit install` (black + isort + flake8)  
3. Submit a PR — small, self-contained commits appreciated 🙏  

---

## License

**MIT** © 2025 Your Name  
See [`LICENSE`](LICENSE) for details.
```

