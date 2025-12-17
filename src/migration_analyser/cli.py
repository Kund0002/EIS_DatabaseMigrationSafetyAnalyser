"""Command-line interface for the migration analyser."""

import argparse
import sys
from pathlib import Path

from migration_analyser import engine


def main():
    """Run the migration analyser from the command line."""
    parser = argparse.ArgumentParser(
        description="Analyse PostgreSQL migration scripts for safety issues."
    )
    parser.add_argument(
        "sql_files",
        nargs="+",
        type=Path,
        help="SQL file(s) to analyse",
    )
    parser.add_argument(
        "--fail-on-danger",
        action="store_true",
        default=True,
        help="Exit with code 1 if dangerous statements are found (default: True)",
    )
    parser.add_argument(
        "--no-fail-on-danger",
        action="store_false",
        dest="fail_on_danger",
        help="Don't fail even if dangerous statements are found",
    )

    args = parser.parse_args()

    # Validate all files exist
    for sql_file in args.sql_files:
        if not sql_file.exists():
            print(f"❌ Error: File not found: {sql_file}", file=sys.stderr)
            sys.exit(2)
        if not sql_file.is_file():
            print(f"❌ Error: Not a file: {sql_file}", file=sys.stderr)
            sys.exit(2)

    # Run analysis on all files
    all_dangerous = []
    total_statements = 0

    for sql_file in args.sql_files:
        print(f"\n{'='*70}")
        print(f"Analysing: {sql_file}")
        print("=" * 70)

        dangerous_count, stmt_count = engine.analyse_file(sql_file)
        total_statements += stmt_count

        if dangerous_count > 0:
            all_dangerous.append((sql_file, dangerous_count))

    # Print overall summary
    print(f"\n{'='*70}")
    print("OVERALL SUMMARY")
    print("=" * 70)
    print(f"Total files analysed: {len(args.sql_files)}")
    print(f"Total statements analysed: {total_statements}")
    print(f"Files with dangerous statements: {len(all_dangerous)}")

    if all_dangerous:
        print("\n⚠️  WARNING: Dangerous statements found in:")
        for sql_file, count in all_dangerous:
            print(f"  - {sql_file}: {count} dangerous statement(s)")
        print("\n❌ ANALYSIS FAILED - Review these files before merging!")
        print("=" * 70)

        if args.fail_on_danger:
            sys.exit(1)
    else:
        print("\n✅ All statements are SAFE to execute")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
