# Generates 8 shards of seeded synthetic user signup records with known number of invalid rows.
import argparse, csv, json, os, random

REQUIRED = ["user_id", "name", "email", "signup_date"]
FIELDS = REQUIRED + ["country"]
NAMES = ["Priya", "Arjun", "Meera", "Rahul", "Ananya", "Vikram", "Sneha", "Karthik"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "iitm.ac.in"]
COUNTRIES = ["IN", "US", "AU", "SG", "UK"]
BAD_EMAILS = ["{u}.gmail.com", "{u}@", "@gmail.com", "{u}@@gmail.com", "{u} @gmail.com", "{u}@gmail"]


def generate_shard(shard, rows, out_dir):
    rng = random.Random(42 + shard)
    n_bad_email = rng.randint(50, 150)
    n_missing = rng.randint(50, 150)
    picked = rng.sample(range(rows), n_bad_email + n_missing)
    bad_email_rows = set(picked[:n_bad_email])
    missing_rows = set(picked[n_bad_email:])

    with open(f"{out_dir}/shard_{shard}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for i in range(rows):
            user_id = shard * rows + i
            name = rng.choice(NAMES)
            row = {
                "user_id": str(user_id),
                "name": name,
                "email": f"{name.lower()}{user_id}@{rng.choice(DOMAINS)}",
                "signup_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "country": rng.choice(COUNTRIES),
            }
            if i in bad_email_rows:
                row["email"] = rng.choice(BAD_EMAILS).format(u=f"{name.lower()}{user_id}")
            elif i in missing_rows:
                row[rng.choice(REQUIRED)] = ""
            writer.writerow(row)

    return {"shard": shard, "rows": rows, "bad_email": n_bad_email,
            "missing_field": n_missing, "invalid": n_bad_email + n_missing}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="shards")
    parser.add_argument("--n-shards", type=int, default=8)
    parser.add_argument("--rows", type=int, default=200_000)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    expected = [generate_shard(s, args.rows, args.out_dir) for s in range(args.n_shards)]
    with open(f"{args.out_dir}/expected_counts.json", "w") as f:
        json.dump(expected, f, indent=2)
    for e in expected:
        print(e)
