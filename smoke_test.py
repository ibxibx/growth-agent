r"""
smoke_test.py — proves the keystone mechanic of the pitch:
Claude generates a scoring script, and that UNTRUSTED generated code
runs inside an ISOLATED Daytona sandbox, not on our machine.

Run:  .\.venv\Scripts\python.exe smoke_test.py
"""
import os
from dotenv import load_dotenv
from daytona import Daytona, DaytonaConfig

load_dotenv()


def main():
    daytona = Daytona(DaytonaConfig(api_key=os.environ["DAYTONA_API_KEY"]))

    print("Spinning up an isolated sandbox...")
    sandbox = daytona.create()
    try:
        # This stands in for code that Claude will GENERATE at runtime.
        # The point: we never run it locally; it executes inside the sandbox.
        generated_code = (
            "candidate = {'skills': ['python', 'fastapi'], 'years': 4}\n"
            "target = {'required': ['python', 'kubernetes', 'aws']}\n"
            "have = set(candidate['skills'])\n"
            "need = set(target['required'])\n"
            "gap = sorted(need - have)\n"
            "coverage = round(len(have & need) / len(need) * 100)\n"
            "print(f'GAP={gap} COVERAGE={coverage}%')\n"
        )

        print("Running GENERATED code inside the sandbox...")
        resp = sandbox.process.code_run(generated_code)

        if resp.exit_code != 0:
            print(f"Sandbox error: {resp.exit_code}\n{resp.result}")
        else:
            print("Sandbox output:", resp.result.strip())
            print("\nKEYSTONE PROVEN: generated code executed in isolation.")
    finally:
        print("Destroying sandbox (data lives and dies here)...")
        sandbox.delete()


if __name__ == "__main__":
    main()
