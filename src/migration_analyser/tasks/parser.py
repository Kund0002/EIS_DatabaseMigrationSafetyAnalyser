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

    for _i, stmt in enumerate(sql, start=1):
        print("\nStatement")
        print(stmt)
        print("\nAST")
        print(repr(stmt))
    return repr(stmt)
