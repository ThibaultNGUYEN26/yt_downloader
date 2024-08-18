import yt_dlp
from tkinter import *
from PIL import Image, ImageTk

WIDTH = 800
HEIGHT = 600
DARK_COLOR = "#282828"
RED_COLOR = "#FF0000"
WHITE_COLOR = "#FFFFFF"
BASE_FONT_SIZE = 18
BASE_IMAGE_SIZE = 50  # Base size of the image (width and height)

def exit_win(event):
    root.destroy()

# Function to dynamically adjust layout and font size on window resize
def responsive_app(root, event):
    # Calculate the new font size proportionate to the window height
    max_font_size = int(root.winfo_width() / 30)  # Adjust the divisor for scaling
    min_font_size = 10

    # Calculate the new font size based on the window width and text length
    font_size = max(min_font_size, min(max_font_size, root.winfo_width() // len(title.cget("text"))))

    # Calculate the new image size proportionate to the window width
    new_image_size = max(20, int(BASE_IMAGE_SIZE * (root.winfo_width() / WIDTH)))

    # Resize the image
    resized_image = original_image.resize((new_image_size, new_image_size), Image.Resampling.LANCZOS)

    # Convert the resized image to a format Tkinter can use
    logo_image_resized = ImageTk.PhotoImage(resized_image)

    # Update the label's font size and image
    title.config(font=("Roboto", font_size, "bold"), image=logo_image_resized)
    title.image = logo_image_resized  # Keep a reference to prevent garbage collection
    title.place_configure(relx=0.5, rely=0.1, anchor=CENTER)

root = Tk()
root.title("YouTube Downloader")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.config(bg=DARK_COLOR)
root.minsize(int(WIDTH // 1.2), int(HEIGHT // 1.2))

# Load the image using Pillow
original_image = Image.open("src/logo.png")  # Replace with your image file

# Initial resizing of the image
resized_image = original_image.resize((BASE_IMAGE_SIZE, BASE_IMAGE_SIZE), Image.Resampling.LANCZOS)

# Convert the image to a format Tkinter can use
logo_image = ImageTk.PhotoImage(resized_image)

# Create the title label with the resized image and text
title = Label(root, text="YouTube Downloader", bg=DARK_COLOR, fg=WHITE_COLOR, font=("Roboto", BASE_FONT_SIZE), image=logo_image, compound="left", padx=10)
title.place(relx=0.5, rely=0.1, anchor=CENTER)

request = Entry(root, width=WIDTH // 20, font=("Roboto", BASE_FONT_SIZE))
request.place(relx=0.5, rely=0.5, anchor=CENTER)

# Bind the Escape key to close the window
root.bind("<Escape>", exit_win)

# Bind the Configure event to handle window resizing
root.bind("<Configure>", lambda event: responsive_app(root, event))

# Start the Tkinter main loop
root.mainloop()

def download():
	# URL of the YouTube video or playlist
	url = input("Enter the YouTube URL (video or playlist): ").strip()

	# Initialize yt-dlp without any options to start with
	ydl_opts = {}

	# Ask the user if they want to download audio or video
	media_type = input("Do you want to download audio or video? (Enter 'audio' or 'video'): ").strip().lower()

	# Validate the input
	if media_type not in ['audio', 'video']:
		print("Invalid input. Please enter 'audio' or 'video'.")
		exit()

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		# Extract information without downloading
		info_dict = ydl.extract_info(url, download=False)

		# Check if the URL is a playlist or a single video
		if 'entries' in info_dict:
			# It's a playlist, so get all video entries
			video_entries = info_dict['entries']
			print(f"Playlist detected with {len(video_entries)} videos.")
		else:
			# It's a single video
			video_entries = [info_dict]

		# Process the first video in the playlist to select the quality
		first_video_info = video_entries[0]

		if media_type == 'audio':
			formats = [f for f in first_video_info.get('formats', []) if f.get('vcodec') == 'none' and f['ext'] != 'webm' and f.get('format_note') and f['format_note'] != 'N/A']
		else:  # media_type == 'video'
			formats = [f for f in first_video_info.get('formats', []) if f.get('vcodec') != 'none' and f['ext'] != 'webm' and f.get('format_note') and f['format_note'] != 'N/A']

		# Keep only one entry per unique Note
		seen_notes = set()
		unique_formats = []
		for f in formats:
			format_note = f['format_note']
			if format_note not in seen_notes:
				unique_formats.append(f)
				seen_notes.add(format_note)

		# Display the available formats to the user
		print("Available formats:")
		for i, f in enumerate(unique_formats):
			format_note = f.get('format_note', 'N/A')
			resolution = f.get('resolution', 'audio only') if media_type == 'audio' else f.get('resolution', 'N/A')
			print(f"{i}: Format code: {f['format_id']}, Extension: {f['ext']}, Resolution: {resolution}, Note: {format_note}")

		# Check if the list is empty
		if not unique_formats:
			print("No available formats match your criteria.")
			exit()

		# Ask the user to select a format
		format_index = int(input("Enter the number of the format you want to download: "))
		selected_format = unique_formats[format_index]['format_id']

		# Set the format in ydl_opts based on the user selection
		ydl_opts['format'] = selected_format
		ydl_opts['outtmpl'] = '%(title)s.%(ext)s'  # Set the output filename template

		# Now download all videos in the playlist using the selected format
		for video_info in video_entries:
			print(f"Downloading {video_info['title']}...")
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				ydl.download([video_info['webpage_url']])
			print(f"Download completed for {video_info['title']}!")

	print("All downloads completed!")

