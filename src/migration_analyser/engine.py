from pathlib import Path

import sqlglot

from migration_analyser.tasks import context_where, task_example


def analyse_file(sql_file_path):
    """
    Analyse a SQL file for safety issues.

    Args:
        sql_file_path: Path to the SQL file to analyse

    Returns:
        tuple: (number of dangerous statements, total number of statements)
    """
    sql_file = Path(sql_file_path)
    sql_text = sql_file.read_text()

    # Parse all SQL statements
    parsed_statements = sqlglot.parse(sql_text)

    if not parsed_statements:
        print("\nNo statements found to analyse.")
        return 0, 0

    print("\n" + "=" * 70)
    print("Running Safety Checks")
    print("=" * 70)

    # Track results for summary
    all_results = []
    dangerous_statements = []

    # Check each statement individually
    for i, stmt in enumerate(parsed_statements, start=1):
        print(f"\n{'='*70}")
        print(f"Checking Statement {i} of {len(parsed_statements)}")
        print("=" * 70)

        # Run example task
        print("\nTask: Example Detection")
        print("-" * 40)
        result_example = task_example.run_task(stmt)
        print(f"\n  Result: {result_example}")

        # Run WHERE clause safety check
        print("\nTask: WHERE Clause Safety Check")
        print("-" * 40)
        result_where = context_where.run_task(stmt, statement_num=i)
        print(f"\n  Result: {result_where}")

        all_results.append(result_where)
        if not result_where.is_safe:
            dangerous_statements.append(i)

    # Print summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"\nTotal statements analyzed: {len(parsed_statements)}")
    print(f"Safe statements: {len([r for r in all_results if r.is_safe])}")
    print(f"Dangerous statements: {len(dangerous_statements)}")

    if dangerous_statements:
        print(f"\n⚠️  WARNING: Dangerous statements found at positions: {dangerous_statements}")
        print("   Review these statements before executing the SQL script!")
        print("\nDangerous statement details:")
        for stmt_num in dangerous_statements:
            result = all_results[stmt_num - 1]
            print(f"  - Statement {stmt_num}: {result.statement_type} without WHERE clause")
    else:
        print("\n✓ All statements are SAFE to execute")

    print("=" * 70)

    return len(dangerous_statements), len(parsed_statements)


def main():
    """Run the analyser on the default example SQL file."""
    analyse_file("examplesql.sql")


if __name__ == "__main__":
    main()
