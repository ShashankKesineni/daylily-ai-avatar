import subprocess
import random
import time

# List of human-like commit messages
COMMIT_MESSAGES = [
    "Update project files",
    "Minor improvements and fixes",
    "Refactor code and update docs",
    "Routine commit",
    "Work in progress",
    "Update backend logic",
    "Polish endpoints",
    "Tweak server setup",
    "General updates",
    "Sync changes"
]

def auto_commit_loop():
    while True:
        # Stage all changes
        subprocess.run(["git", "add", "-A"])
        # Pick a random commit message
        message = random.choice(COMMIT_MESSAGES)
        # Commit changes
        subprocess.run(["git", "commit", "-m", message])
        # Push to remote
        subprocess.run(["git", "push"])
        # Wait 60–90 minutes (randomized)
        wait_minutes = random.randint(60, 90)
        print(f"Committed and pushed. Waiting {wait_minutes} minutes for next commit...")
        time.sleep(wait_minutes * 60)

if __name__ == "__main__":
    # Run indefinitely in the background if started
    auto_commit_loop() 