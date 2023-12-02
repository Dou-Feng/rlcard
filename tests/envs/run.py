import subprocess
import time

def run_python_file(file_path):
    try:
        if not subprocess.run(['python', file_path], check=True):
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script execution aborted.")
    return True

def main():
    file_path = 'test_limitholdem_env.py'  # Replace with the path to your Python file
    run_interval_seconds = 1 # Replace with the desired interval in seconds

    try:
        while True:
            if not run_python_file(file_path):
                break
            # time.sleep(run_interval_seconds)
    except KeyboardInterrupt:
        print("Script execution stopped.")

if __name__ == "__main__":
    main()
