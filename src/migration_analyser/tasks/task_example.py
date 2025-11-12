class StatementDetector:
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return f"statementDetectorResult(info='{self.info}')"


def run_task(parsed_stmt):
    # do the fuckass detection here
    print("heres the stmn")
    print(parsed_stmt)
    result = StatementDetector("script is fine")
    return result
