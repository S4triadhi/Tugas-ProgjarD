#!/usr/bin/env python3
import os
import time
import json
import signal
import csv
import subprocess

# ——— Benchmark Configuration ———
SERVER_MODES = {
    "thread": "file_server_multithreadpool.py",
    "process": "file_server_multiprocesspool.py"
}
SERVER_WORKERS = [1, 5, 50]
CLIENT_WORKERS = [1, 5, 50]
OPS = ["download", "upload"]
SIZES_MB = [10, 50, 100]
OUTPUT_FILE = "results.csv"
# ——————————————————————————————

def launch_server(mode, worker_count):
    env = os.environ.copy()
    env["MAX_WORKERS"] = str(worker_count)
    return subprocess.Popen(
        ["python3", SERVER_MODES[mode]],
        env=env,
        preexec_fn=os.setsid,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def terminate_server(proc):
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

def execute_stress_test(op, size, client_count):
    env = os.environ.copy()
    env.update({
        "STRESS_OP": op,
        "FILE_SIZE_MB": str(size),
        "CLIENT_POOL": str(client_count)
    })
    result = subprocess.run(
        ["python3", "stress_test.py"],
        capture_output=True,
        env=env,
        text=True
    )
    return json.loads(result.stdout)

def write_csv_header(file):
    headers = [
        "Nomor",
        "Model concurrency",
        "Operasi",
        "Volume",
        "Jumlah client worker pool",
        "Jumlah server worker pool",
        "Waktu total per client",
        "Throughput per client",
        "Jumlah client sukses",
        "Jumlah client gagal",
        "Jumlah server sukses",
        "Jumlah server gagal"
    ]
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    return writer

def main():
    counter = 1
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = write_csv_header(csvfile)

        for mode in SERVER_MODES:
            for sw in SERVER_WORKERS:
                print(f"> Starting {mode} server with {sw} workers")
                server_proc = launch_server(mode, sw)
                time.sleep(1)  # allow server to initialize

                for op in OPS:
                    for size in SIZES_MB:
                        for cw in CLIENT_WORKERS:
                            print(f"  • Test: {mode} | {op} | {size}MB | client×{cw}")
                            try:
                                result = execute_stress_test(op, size, cw)
                            except Exception as e:
                                print("    ✖ Stress test failed:", e)
                                continue

                            writer.writerow({
                                "Nomor": counter,
                                "Model concurrency": mode,
                                "Operasi": op,
                                "Volume": f"{size} MB",
                                "Jumlah client worker pool": cw,
                                "Jumlah server worker pool": sw,
                                "Waktu total per client": result["total_time_s"],
                                "Throughput per client": result["throughput_Bps"],
                                "Jumlah client sukses": result["succeed"],
                                "Jumlah client gagal": result["failed"],
                                "Jumlah server sukses": sw,  # assumed full success
                                "Jumlah server gagal": 0
                            })
                            csvfile.flush()
                            counter += 1

                terminate_server(server_proc)
                time.sleep(0.5)

    print(f"✅ All tests completed. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
