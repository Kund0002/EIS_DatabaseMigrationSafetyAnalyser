from tasks import parser, task_example


def main():
    print("lol lmao")
    parsed_stmt = parser.parse_sql()

    result_a = task_example.run_task(parsed_stmt)

    print(result_a)


if __name__ == "__main__":
    main()
