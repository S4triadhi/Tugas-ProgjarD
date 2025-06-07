#!/usr/bin/env python3

# Standard libraries
import json
import os
import time

# Concurrency libraries
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

# Import client worker functions
from client_worker import download_file
from client_worker import upload_file


def get_config():
    """
    Read configuration from environment variables and return as a dictionary.
    Defaults are used if variables are not set.
    """
    return {
        "operation": os.getenv("STRESS_OP", "download"),     # 'download' or 'upload'
        "file_size_mb": int(os.getenv("FILE_SIZE_MB", 10)),  # File size in MB
        "pool_type": os.getenv("CLIENT_POOL_TYPE", "thread"),# 'thread' or 'process'
        "num_clients": int(os.getenv("CLIENT_POOL", 1)),     # Number of concurrent clients
    }


def prepare_files(op, file_name, size_mb):
    """
    Prepare dummy files required for the stress test:
    - Creates server-side dummy file if missing.
    - Copies it to client-side if operation is 'upload'.
    """
    os.makedirs("server_files", exist_ok=True)
    server_path = os.path.join("server_files", file_name)

    # Create dummy file on server side if it doesn't exist
    if not os.path.exists(server_path):
        with open(server_path, "wb") as f:
            f.write(os.urandom(size_mb * 1024 * 1024))

    # If uploading, make sure the client has a copy to upload
    if op == "upload" and not os.path.exists(file_name):
        with open(server_path, "rb") as src, open(file_name, "wb") as dst:
            dst.write(src.read())


def run_worker(op, file_name, size_mb, client_id):
    """
    Function executed by each worker/client.
    Measures transfer time and success status.
    """
    start = time.time()

    if op == "download":
        # Use a unique filename per client to avoid collision
        local_name = f"client_{client_id}_{file_name}"
        success = download_file(file_name, save_as=local_name)

        # Get file size if download succeeded
        transferred = os.path.getsize(local_name) if success and os.path.exists(local_name) else 0
    else:
        # For upload, file size is known in advance
        success = upload_file(file_name)
        transferred = size_mb * 1024 * 1024 if success else 0

    duration = time.time() - start

    return {
        "ok": success,
        "time": duration,
        "bytes": transferred
    }


def execute_pool(pool_type, num_workers, task_func, *args):
    """
    Executes the `task_func` concurrently with the chosen executor type.
    Each worker gets a unique index `i` passed for identification.
    """
    Executor = ThreadPoolExecutor if pool_type == "thread" else ProcessPoolExecutor
    with Executor(max_workers=num_workers) as executor:
        return list(executor.map(lambda i: task_func(*args, i), range(num_workers)))


def summarize_results(results, num_clients, pool_type, op, file_size_mb):
    """
    Aggregates results and prints performance summary as JSON.
    Includes throughput and success/failure count.
    """
    total_time = sum(r["time"] for r in results)
    total_bytes = sum(r["bytes"] for r in results)
    successes = sum(1 for r in results if r["ok"])
    failures = num_clients - successes

    summary = {
        "clients": num_clients,
        "pool": pool_type,
        "op": op,
        "size_mb": file_size_mb,
        "total_time_s": round(total_time, 3),
        "throughput_Bps": int(total_bytes / total_time) if total_time > 0 else 0,
        "succeed": successes,
        "failed": failures
    }

    # Output final summary as JSON
    print(json.dumps(summary))


def main():
    """
    Main execution flow:
    - Reads config
    - Prepares files
    - Runs the stress test
    - Prints result summary
    """
    config = get_config()
    file_name = f"dummy_{config['file_size_mb']}MB.bin"

    # Ensure required files are present
    prepare_files(config["operation"], file_name, config["file_size_mb"])

    # Run concurrent worker pool
    results = execute_pool(
        config["pool_type"],
        config["num_clients"],
        run_worker,
        config["operation"],
        file_name,
        config["file_size_mb"]
    )

    # Summarize and print results
    summarize_results(
        results,
        config["num_clients"],
        config["pool_type"],
        config["operation"],
        config["file_size_mb"]
    )


# Entry point of the script
if __name__ == "__main__":
    main()
