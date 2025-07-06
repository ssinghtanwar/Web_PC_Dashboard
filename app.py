import dash
from dash import dcc, html, Output, Input
import plotly.graph_objs as go
import sampler, metrics

sampler.start()                  # Begin sampling

app = dash.Dash(__name__)
app.layout = html.Div(
    style={'fontFamily': 'sans-serif', 'margin': '2rem'},
    children=[
        html.H2("My PC Dashboard"),
        html.Div(id='uptime'),

        # ⇣ replace old single Div with this grid ⇣
        html.Div(
            id='resource-cards',
            style={'display': 'grid',
                   'gridTemplateColumns': 'repeat(auto-fit, minmax(220px,1fr))',
                   'gap': '0.5rem',
                   'margin':'1rem 0'}
        ),

        dcc.Graph(id='cpu-graph', animate=True),
        dcc.Graph(id='ram-graph', animate=True),
        dcc.Graph(id='gpu-graph', animate=True),
        dcc.Graph(id='net-graph', animate=True),
        dcc.Interval(id='interval', interval=1_000, n_intervals=0)
    ]
)


# Text widgets
@app.callback(Output('uptime', 'children'), Input('interval', 'n_intervals'))
def update_uptime(_):
    up = metrics.uptime()
    return f"Uptime: {str(up).split('.')[0]}"


# Graph helpers
def _time_series(trace_name, data):
    """Take deque([(t, val), ...]) -> Scatter trace."""
    if not data:                       # handle empty deque gracefully
        return go.Scatter(x=[], y=[], mode='lines', name=trace_name)
    xs, ys = zip(*data)                # now <-- no out-of-bounds risk
    return go.Scatter(x=xs, y=ys, mode='lines', name=trace_name)

# ------- callbacks -------
@app.callback(Output('cpu-graph', 'figure'), Input('interval', 'n_intervals'))
def cpu_fig(_):
    return {
        'data': [_time_series("CPU %", sampler.buffers['cpu'])],
        'layout': go.Layout(title="CPU usage (%)", yaxis=dict(range=[0, 100]))
    }

@app.callback(Output('ram-graph', 'figure'), Input('interval', 'n_intervals'))
def ram_fig(_):
    return {
        'data': [_time_series("RAM %", sampler.buffers['ram'])],
        'layout': go.Layout(title="RAM usage (%)", yaxis=dict(range=[0, 100]))
    }

@app.callback(Output('gpu-graph', 'figure'), Input('interval', 'n_intervals'))
def gpu_fig(_):
    return {
        'data': [_time_series("GPU %", sampler.buffers['gpu'])],
        'layout': go.Layout(title="GPU usage (%)", yaxis=dict(range=[0, 100]))
    }


@app.callback(Output('net-graph', 'figure'), Input('interval', 'n_intervals'))
def net_fig(_):
    xs, sent, recv = zip(*sampler.buffers['net'])
    data = [go.Scatter(x=xs, y=sent, mode='lines', name="Bytes sent"),
            go.Scatter(x=xs, y=recv, mode='lines', name="Bytes recv")]
    return {'data':data, 'layout': go.Layout(title="Network I/O (cumulative)")}

@app.callback(
    Output("resource-cards", "children"),
    Input("interval", "n_intervals"),
)
def update_top_consumers(_):
    cpu_name, cpu_pid, cpu_pct = metrics.top_cpu_proc()
    ram_name, ram_pid, ram_mb  = metrics.top_ram_proc()
    gpu_name, gpu_pid, gpu_mb  = metrics.top_gpu_proc()
    net_name, net_pid, net_mb  = metrics.top_net_proc()

    def card(title, body):
        return html.Div(
            style={
                "border": "1px solid #ccc",
                "borderRadius": "0.5rem",
                "padding": "0.8rem",
            },
            children=[html.Strong(title), html.Br(), body],
        )

    return [
        card("CPU-hungry",
             f"{cpu_name} (PID {cpu_pid}) – {cpu_pct:5.1f}%"),
        card("RAM-hungry",
             f"{ram_name} (PID {ram_pid}) – {ram_mb:,.0f} MiB"),
        card("GPU-hungry",
             f"{gpu_name} (PID {gpu_pid}) – {gpu_mb:,.0f} MiB"),
        card("Network-hungry",
             f"{net_name} (PID {net_pid}) – {net_mb:,.0f} MiB"),
    ]


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)    # http://127.0.0.1:8050

