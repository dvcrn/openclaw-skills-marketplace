#!/usr/bin/env python3
import argparse, csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=int, default=60)
    ap.add_argument("--out", default="agenda.csv")
    args = ap.parse_args()
    segments = [
        ("00:00","Welcome","Align goals","Intro","Host",""),
        ("00:10","Context","Frame problem","Brief","Host",""),
        ("00:20","Working block","Generate input","Discussion","All",""),
        ("00:45","Decision","Choose next steps","Decision","Lead",""),
        ("00:55","Close","Confirm owners","Recap","Host","")
    ]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Time","Segment","Goal","Method","Owner","Notes"])
        w.writerows(segments)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
