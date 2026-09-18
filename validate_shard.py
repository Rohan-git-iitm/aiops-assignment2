# Entry point for each pod of the Job.
import csv, json, os, re, socket, time

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
REQUIRED = ["user_id", "name", "email", "signup_date"]


def main():
    shard = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
    data_dir = os.environ.get("DATA_DIR", "/app/shards")
    pod_name = os.environ.get("POD_NAME", socket.gethostname())
    node_name = os.environ.get("NODE_NAME", "unknown")
    path = f"{data_dir}/shard_{shard}.csv"

    print(f"[shard {shard}] pod={pod_name} node={node_name} file={path}", flush=True)

    t0 = time.time()
    total = missing = bad_email = 0
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            if any(not row[col].strip() for col in REQUIRED):
                missing += 1
            elif not EMAIL_RE.match(row["email"]):
                bad_email += 1

    result = {
        "shard": shard, "rows": total, "missing_field": missing, "bad_email": bad_email,
        "invalid": missing + bad_email, "seconds": round(time.time() - t0, 2),
        "pod_name": pod_name, "node_name": node_name,
    }
    print("RESULT_JSON:" + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
