# Logic to open apps
import subprocess

# Example CMDs Functionality to give user an idea of what they can do with the program
def open_chrome():
    try:
        subprocess.Popen(["open", "-a", "Google Chrome"]) # using terminal cmd and implementing into our program:
        print("Opening Chrome...")
    except Exception as e:
        print(f"Error launching Google Chrome: {e}")

def open_vscode():
    try:
        subprocess.Popen(["open", "-a", "Visual Studio Code"])
        print("Opening VS Code...")
    except Exception as e:
        print(f"Error launching VS Code: {e}")

def open_safari(): # to be replaced by "quit" application example
    try:
        subprocess.Popen(["open", "-a", "Safari"])
        print("Opening Safari...")
    except Exception as e:
        print(f"Error launching Safari: {e}")

def open_notes(): # to be replaced by another example of what this application launcher can do...
    try:
        subprocess.Popen(["open", "-a", "Notes"])
        print("Opening Notes...")
    except Exception as e:
        print(f"Error launching Notes: {e}")
# another example of what this application launcher can do...
# def open_...():

# another example of what this application launcher can do...
# def open_...():