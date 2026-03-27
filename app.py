import cv2
import pytesseract
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk

# Ha nem találja:
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

REGION = (680, 600, 220, 160)

history = []
running = True

bankroll = 10000
stop_loss = 7000

# -------------------------

def get_signal():
    if len(history) < 5:
        return "WAIT", "white"

    last = history[-5:]
    low = sum(1 for x in last if x < 1.5)
    high = sum(1 for x in last if x > 2.5)

    if low >= 3:
        return "🔴", "red"
    elif high >= 3:
        return "🟢", "green"
    else:
        return "🟡", "yellow"

# -------------------------

def extract_number(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray,255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,11,2
    )

    text = pytesseract.image_to_string(
        thresh,
        config='--psm 7 -c tessedit_char_whitelist=0123456789.x'
    )

    try:
        return float(text.replace("x","").strip())
    except:
        return None

# -------------------------

def capture():
    screenshot = pyautogui.screenshot(region=REGION)
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

# -------------------------

def loop():
    global bankroll

    while running:
        img = capture()
        value = extract_number(img)

        if value:
            history.append(value)

            signal, color = get_signal()

            crash_var.set(f"{value:.2f}")
            signal_var.set(signal)
            signal_label.config(fg=color)

            if signal == "🟢":
                bankroll += 200
            elif signal == "🔴":
                bankroll -= 200

            bank_var.set(f"{bankroll} Ft")

            if bankroll <= stop_loss:
                signal_var.set("STOP")
                signal_label.config(fg="red")

        time.sleep(2)

# -------------------------

def start_move(event):
    root.x = event.x
    root.y = event.y

def on_motion(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

# -------------------------

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg="black")

crash_var = tk.StringVar(value="--")
signal_var = tk.StringVar(value="WAIT")
bank_var = tk.StringVar(value=f"{bankroll} Ft")

frame = tk.Frame(root, bg="black")
frame.pack(padx=10, pady=10)

tk.Label(frame, textvariable=crash_var, fg="cyan", bg="black", font=("Arial", 20)).pack()

signal_label = tk.Label(frame, textvariable=signal_var, fg="white", bg="black", font=("Arial", 18))
signal_label.pack()

tk.Label(frame, textvariable=bank_var, fg="white", bg="black", font=("Arial", 12)).pack()

frame.bind("<Button-1>", start_move)
frame.bind("<B1-Motion>", on_motion)

threading.Thread(target=loop, daemon=True).start()

root.mainloop()


    
