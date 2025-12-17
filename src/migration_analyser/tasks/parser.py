from pathlib import Path

import sqlglot


class SqlParser:
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return f"SqlParser(info='{self.info}')"


def parse_sql():
    sql_file = "examplesql.sql"
    sql_text = Path(sql_file).read_text()

    sql = sqlglot.parse(sql_text)

    """ print(f"\nParsed {len(sql)} statement(s) from {sql_file}")
    for i, stmt in enumerate(sql, start=1):
        print(f"\n--- Statement {i} ---")
        print(stmt)
        print("\n--- AST ---")
        print(repr(stmt)) """

    return sql  # Return all statements, not just the last one
