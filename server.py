# server.py
# This script acts as the server for real-time screen sharing.
# It receives screen data from the client and displays it in a Tkinter window.

import socket
import struct
import io
from PIL import Image, ImageTk
import tkinter as tk
import sys

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5555      # Port to listen on

# --- Global Variables ---
root = None
label = None
conn = None
addr = None
server_socket = None
is_running = True

def receive_all(sock, n):
    """Helper function to receive exactly n bytes from the socket."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None  # Connection closed or error
        data += packet
    return data

def update_screen():
    """
    Receives screen data from the client, processes it, and updates the Tkinter display.
    This function is called repeatedly using Tkinter's after method for real-time updates.
    """
    global is_running

    if not is_running:
        return

    try:
        # 1. Receive the size of the image data (4 bytes, unsigned long)
        size_data = receive_all(conn, 4)
        if not size_data:
            print("Client disconnected or error receiving size.")
            close_server()
            return

        image_size = struct.unpack('<L', size_data)[0]

        # 2. Receive the actual image data
        image_data = receive_all(conn, image_size)
        if not image_data:
            print("Client disconnected or error receiving image data.")
            close_server()
            return

        # 3. Open the image from bytes using Pillow
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)

        # 4. Resize the image to fit the Tkinter window (optional, but good for responsiveness)
        # Get current window size
        window_width = root.winfo_width()
        window_height = root.winfo_height()

        if window_width == 1 or window_height == 1: # Initial size might be 1x1 before actual geometry is set
            window_width = 1920 # Default size
            window_height = 1080 # Default size

        # Maintain aspect ratio
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height

        if window_width / window_height > aspect_ratio:
            # Window is wider than image, scale by height
            new_height = window_height
            new_width = int(new_height * aspect_ratio)
        else:
            # Window is taller than image, scale by width
            new_width = window_width
            new_height = int(new_width / aspect_ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS) # Use LANCZOS for high quality downsampling

        # 5. Convert Pillow image to Tkinter PhotoImage
        photo = ImageTk.PhotoImage(img)

        # 6. Update the label with the new image
        label.config(image=photo)
        label.image = photo  # Keep a reference to prevent garbage collection

    except (socket.error, struct.error, OSError) as e:
        print(f"Socket error or image processing error: {e}")
        close_server()
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        close_server()
        return

    # Schedule the next screen update after a short delay (e.g., 10ms for smooth animation)
    if is_running:
        root.after(10, update_screen)

def close_server():
    """Closes all active connections and shuts down the server."""
    global is_running, conn, server_socket
    is_running = False
    print("Shutting down server...")
    if conn:
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            print("Client connection closed.")
        except OSError as e:
            print(f"Error closing client connection: {e}")
    if server_socket:
        try:
            server_socket.close()
            print("Server socket closed.")
        except OSError as e:
            print(f"Error closing server socket: {e}")
    if root:
        root.quit()
        root.destroy()
    sys.exit(0) # Exit the script cleanly

def start_server():
    """Initializes the server socket and waits for a client connection."""
    global conn, addr, server_socket, root, label

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1) # Listen for one incoming connection
        print(f"Server listening on {HOST}:{PORT}...")

        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        # --- Tkinter Setup ---
        root = tk.Tk()
        root.title("Real-time Screen Share (Server)")
        root.geometry("800x600") # Initial window size
        root.protocol("WM_DELETE_WINDOW", close_server) # Handle window close event

        # Create a label to display the image
        label = tk.Label(root)
        label.pack(expand=True, fill=tk.BOTH)

        # Start the screen update loop
        root.after(10, update_screen)
        root.mainloop()

    except socket.error as e:
        print(f"Socket error: {e}")
        close_server()
    except Exception as e:
        print(f"An error occurred during server startup: {e}")
        close_server()

if __name__ == "__main__":
    start_server()
