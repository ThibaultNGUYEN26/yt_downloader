import yt_dlp

# URL of the YouTube video
url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs'

# Initialize yt-dlp without any options to start with
ydl_opts = {}

# Ask the user if they want to download audio or video
media_type = input("Do you want to download audio or video? (Enter 'audio' or 'video'): ").strip().lower()

# Validate the input
if media_type not in ['audio', 'video']:
    print("Invalid input. Please enter 'audio' or 'video'.")
    exit()

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    # Extract video information without downloading
    info_dict = ydl.extract_info(url, download=False)
    
    # Filter formats based on the user's choice, exclude webm, exclude formats with Note: N/A
    if media_type == 'audio':
        formats = [f for f in info_dict.get('formats', []) if f.get('vcodec') == 'none' and f['ext'] != 'webm' and f.get('format_note') and f['format_note'] != 'N/A']
    else:  # media_type == 'video'
        formats = [f for f in info_dict.get('formats', []) if f.get('vcodec') != 'none' and f['ext'] != 'webm' and f.get('format_note') and f['format_note'] != 'N/A']

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

    # Set the format in ydl_opts
    ydl_opts['format'] = selected_format

    # Set the output filename template
    ydl_opts['outtmpl'] = '%(title)s.%(ext)s'

    # Download the selected format
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("Download completed!")
