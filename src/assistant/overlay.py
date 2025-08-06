import tkinter as tk



def overlay_gui(root: tk.Tk, position: str) -> None:
    """Overlay helps find items on the screen"""

    if position != "null":
        overlay_window = tk.Toplevel(root)
        overlay_window.overrideredirect(True)
        overlay_window.attributes("-topmost", True)
        overlay_window.attributes("-alpha", 0.25)

        screen_width = overlay_window.winfo_screenwidth()
        screen_height = overlay_window.winfo_screenheight()

        x, y = 0, 0
        width, height = screen_width, screen_height

        match position:
            case "left":
                width, height = screen_width // 2, screen_height

            case "right":
                width, height = screen_width // 2, screen_height
                x = screen_width // 2

            case "top":
                width, height = screen_width, screen_height // 2

            case "bottom":
                width, height = screen_width, screen_height // 2
                y = screen_height // 2

            case "topleft":
                width, height = screen_width // 2, screen_height // 2

            case "topright":
                width, height = screen_width // 2, screen_height // 2
                x = screen_width // 2

            case "bottomleft":
                width, height = screen_width // 2, screen_height // 2
                y = screen_height // 2

            case "bottomright":
                width, height = screen_width // 2, screen_height // 2
                x = screen_width // 2
                y = screen_height // 2
        

        overlay_window.geometry(f"{width}x{height}+{x}+{y}")

        canvas = tk.Canvas(
            master=overlay_window,
            width=width,
            height=height,
            bg="white",
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True)

        overlay_window.after(3000, overlay_window.destroy)