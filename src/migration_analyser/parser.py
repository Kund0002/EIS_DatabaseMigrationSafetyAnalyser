from pathlib import Path

import sqlglot

sql_file = "examplesql.sql"
sql_text = Path(sql_file).read_text()

sql = sqlglot.parse(sql_text)

for _i, stmt in enumerate(sql, start=1):
    print("\nStatement")
    print(stmt)
    print("\nAST")
    print(repr(stmt))
