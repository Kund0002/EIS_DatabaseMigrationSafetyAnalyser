class StatementDetector:
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return f"statementDetectorResult(info='{self.info}')"


def run_task(parsed_stmt):
    # do the fuckass detection here
    print(parsed_stmt)
    result = StatementDetector("yes this is a script")
    return result
