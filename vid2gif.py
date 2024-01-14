import tkinter as tk
from tkinter import filedialog, messagebox, Scale
import subprocess
import threading
import os
from moviepy.editor import VideoFileClip

# Function to convert HH:MM:SS.mmm to seconds
def hhmmss_to_seconds(timestr):
    parts = timestr.split(':')
    hours, minutes = map(int, parts[:2])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

# Function to convert seconds to HH:MM:SS.mmm
def seconds_to_hhmmss(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds*1000):03}"

# Function to get the duration of the video
def get_video_duration(filepath):
    with VideoFileClip(filepath) as clip:
        return int(clip.duration)

# Define the function to convert video to gif using FFmpeg
def convert_video_to_gif(video_path, start_time, end_time, output_gif):
    try:
        ffmpeg_cmd = [
            'ffmpeg',
            '-ss', seconds_to_hhmmss(start_time),
            '-to', seconds_to_hhmmss(end_time),
            '-i', video_path,
            '-vf', 'fps=12,scale=640:-2:flags=lanczos',
            '-c:v', 'gif',
            output_gif
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        messagebox.showinfo("Success", "GIF created successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def convert_video_to_webm(video_path, start_time, end_time, output_webm):
    try:
        ffmpeg_webm_cmd = [
            'ffmpeg',
            '-ss', seconds_to_hhmmss(start_time),
            '-to', seconds_to_hhmmss(end_time),
            '-i', video_path,
            '-c:v', 'libvpx-vp9',
            '-b:v', '1M',
            '-c:a', 'libopus',
            output_webm
        ]
        subprocess.run(ffmpeg_webm_cmd, check=True)
        messagebox.showinfo("Success", "WebM created successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Define the function to convert video to webm using FFmpeg
def convert_video_to_gif_and_webm(video_path, start_time, end_time, output_gif, output_webm):
    create_gif_thread(video_path, start_time, end_time, output_gif)
    create_webm_thread(video_path, start_time, end_time, output_webm)


# Function to create a thread to run the FFmpeg command
def create_gif_thread(video_path, start_time, end_time, output_gif):
    # Run the FFmpeg command in a separate thread
    thread = threading.Thread(target=convert_video_to_gif, args=(video_path, start_time, end_time, output_gif))
    thread.start()

# Function to create a thread to run the FFmpeg command
def create_webm_thread(video_path, start_time, end_time, output_webm):
    # Run the FFmpeg command in a separate thread
    thread = threading.Thread(target=convert_video_to_webm, args=(video_path, start_time, end_time, output_webm))
    thread.start()

# Create the main application window
root = tk.Tk()
root.title("Video to GIF Converter")

# Variables to store user input
video_path_var = tk.StringVar()
video_duration = tk.IntVar(value=0)  # Variable to store video duration in seconds

# Function to update the video path variable and the sliders
def open_file_dialog():
    filepath = filedialog.askopenfilename()
    if filepath:
        video_path_var.set(filepath)
        duration = get_video_duration(filepath) * 1000  # Convert duration to milliseconds
        video_duration.set(duration)
        # Update the sliders' range to the video's duration
        start_slider.config(to=duration)
        end_slider.config(to=duration)
        start_slider.set(0)
        end_slider.set(duration)
        # Update the entry fields
        start_time_entry.delete(0, tk.END)
        start_time_entry.insert(0, seconds_to_hhmmss(start_slider.get() / 1000))  # Convert slider value to seconds
        end_time_entry.delete(0, tk.END)
        end_time_entry.insert(0, seconds_to_hhmmss(end_slider.get() / 1000))  # Convert slider value to seconds

# Function to sync the slider with the entry field
def update_time_entry_from_slider(slider, entry):
    time_in_milliseconds = slider.get()
    entry.delete(0, tk.END)
    entry.insert(0, seconds_to_hhmmss(time_in_milliseconds / 1000))

# Function to sync the entry field with the slider
def update_slider_from_time_entry(entry, slider):
    time_str = entry.get()
    try:
        # Validate and convert the time
        time_in_seconds = hhmmss_to_seconds(time_str)
        if 0 <= time_in_seconds <= video_duration.get():
            slider.set(time_in_seconds * 1000)
        else:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Warning", "Please enter a valid time in HH:MM:SS.mmm format.")

# Function to trigger the conversion process
def on_convert_button_click():
    video_path = video_path_var.get()
    start_time = start_slider.get() / 1000  # Convert from milliseconds to seconds
    end_time = end_slider.get() / 1000  # Convert from milliseconds to seconds
    if not video_path:
        messagebox.showwarning("Warning", "Please select a video file.")
        return
    # Base output path
    output_base = os.path.expanduser('~/Projects/vid2gif/outputs/') + os.path.splitext(os.path.basename(video_path))[0]
    output_gif = output_base + '.gif'
    output_webm = output_base + '.webm'
    # Check if file already exists
    i = 1
    while os.path.exists(output_gif):
        output_gif = f"{output_base}_{i}.gif"
        i += 1
    create_gif_thread(video_path, start_time, end_time, output_gif)

    # Check if file already exists
    while os.path.exists(output_webm):
        output_webm = f"{output_base}_{i}.webm"
        i += 1

def on_convert_to_webm_button_click():
    video_path = video_path_var.get()
    start_time = start_slider.get() / 1000  # Convert from milliseconds to seconds
    end_time = end_slider.get() / 1000  # Convert from milliseconds to seconds
    if not video_path:
        messagebox.showwarning("Warning", "Please select a video file.")
        return
    # Base output path
    output_base = os.path.expanduser('~/Projects/vid2gif/outputs/') + os.path.splitext(os.path.basename(video_path))[0]
    output_webm = output_base + '.webm'
    # Check if file already exists
    i = 1
    while os.path.exists(output_webm):
        output_webm = f"{output_base}_{i}.webm"
        i += 1
    create_webm_thread(video_path, start_time, end_time, output_webm)

def on_convert_to_gif_and_webm_button_click():
    video_path = video_path_var.get()
    start_time = start_slider.get() / 1000  # Convert from milliseconds to seconds
    end_time = end_slider.get() / 1000  # Convert from milliseconds to seconds
    if not video_path:
        messagebox.showwarning("Warning", "Please select a video file.")
        return
    # Base output path
    output_base = os.path.expanduser('~/Projects/vid2gif/outputs/') + os.path.splitext(os.path.basename(video_path))[0]
    output_gif = output_base + '.gif'
    output_webm = output_base + '.webm'
    # Check if file already exists
    i = 1
    while os.path.exists(output_gif) or os.path.exists(output_webm):
        output_gif = f"{output_base}_{i}.gif"
        output_webm = f"{output_base}_{i}.webm"
        i += 1
    convert_video_to_gif_and_webm(video_path, start_time, end_time, output_gif, output_webm)

# GUI Layout

tk.Label(root, text="Video Path:").grid(row=0, column=0, sticky="w")
video_path_entry = tk.Entry(root, textvariable=video_path_var, width=50, state='readonly')
video_path_entry.grid(row=0, column=1)
browse_button = tk.Button(root, text="Browse", command=open_file_dialog)
browse_button.grid(row=0, column=2)

# tk.Label(root, text="Start Time (HH:MM:SS):").grid(row=1, column=0, sticky="w")
# start_time_entry = tk.Entry(root, textvariable=start_slider)
# start_time_entry.grid(row=1, column=1)

# tk.Label(root, text="End Time (HH:MM:SS):").grid(row=2, column=0, sticky="w")
# end_time_entry = tk.Entry(root, textvariable=end_slider)
# end_time_entry.grid(row=2, column=1)


# Sliders and entry fields for start and end times
start_slider = tk.Scale(root, from_=0, to=video_duration.get() * 1000, orient='horizontal', label='Start Time', variable=tk.IntVar(), command=lambda value: update_time_entry_from_slider(start_slider, start_time_entry))

end_slider = tk.Scale(root, from_=0, to=video_duration.get() * 1000, orient='horizontal', label='End Time', variable=tk.IntVar(), command=lambda value: update_time_entry_from_slider(end_slider, end_time_entry))

start_time_entry = tk.Entry(root, width=8)
end_time_entry = tk.Entry(root, width=8)

start_time_entry.bind("<FocusOut>", lambda event: update_slider_from_time_entry(start_time_entry, start_slider))
end_time_entry.bind("<FocusOut>", lambda event: update_slider_from_time_entry(end_time_entry, end_slider))

# Position the widgets on the grid
start_slider.grid(row=1, column=1, sticky="we")
end_slider.grid(row=2, column=1, sticky="we")
start_time_entry.grid(row=1, column=2)
end_time_entry.grid(row=2, column=2)

# Set initial values for the entry fields
start_time_entry.insert(0, "00:00:00")
end_time_entry.insert(0, "00:00:10")

convert_button = tk.Button(root, text="Convert to GIF", command=on_convert_button_click)
convert_button.grid(row=3, column=1, pady=10)

tk.Button(root, text="Convert to WebM", command=on_convert_to_webm_button_click).grid(row=4, column=1, pady=10)
tk.Button(root, text="Convert to GIF and WebM", command=on_convert_to_gif_and_webm_button_click).grid(row=5, column=1, pady=10)

# Run the application
root.mainloop()
