import cv2  # load OpenCV library for reading and processing images
import numpy as np  # load NumPy library for array operations and math on arrays
import flet as ft  # load Flet framework for building graphical user interfaces
import os  # load OS module for checking and creating folders, working with file paths
import subprocess  # load subprocess module for running external system commands
from PIL import (
    Image,
)  # load Pillow Image class for additional image handling (not directly used here)
import time  # load time module for time-related functions (not actively used)
import math  # load math module for precise rounding functions like ceil


# Define the main function that sets up the app window and connects everything
def main(page: ft.Page):
    page.title = "Parivartan - 2D to 3D Converter"  # set window title
    page.padding = 20  # add space around the window content
    page.theme_mode = ft.ThemeMode.LIGHT  # start the app in light theme
    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )  # center content left to right
    page.vertical_alignment = (
        ft.MainAxisAlignment.CENTER
    )  # center content top to bottom

    # ---------------------- THEME HANDLING ----------------------
    # function to change colors when theme toggles
    def update_theme():
        if page.theme_mode == ft.ThemeMode.DARK:
            page.bgcolor = (
                ft.ColorFilter.color
            )  # set dark background color (placeholder)
            header_text.color = ft.Colors.YELLOW  # make header text yellow
            status_text.color = ft.Colors.DEEP_ORANGE  # make status text deep orange
            progress_text.color = (
                ft.Colors.DEEP_ORANGE
            )  # make progress text deep orange
            plus_icon.color = ft.Colors.WHITE  # make add-icon white
            plus_text.color = ft.Colors.WHITE  # make add-text white
        else:
            page.bgcolor = (
                ft.ColorFilter.color
            )  # set light background color (placeholder)
            header_text.color = ft.Colors.BLUE  # make header text blue
            status_text.color = ft.Colors.GREEN_900  # make status text dark green
            progress_text.color = ft.Colors.GREEN_900  # make progress text dark green
            plus_icon.color = ft.Colors.DEEP_PURPLE_900  # make add-icon deep purple
            plus_text.color = ft.Colors.DEEP_PURPLE_900  # make add-text deep purple
        page.update()  # redraw the page with new colors

    # function to flip the theme when switch is toggled
    def toggle_theme(e: ft.ControlEvent):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        update_theme()  # apply updated colors

    # ---------------------- HEADER & THEME SWITCH ----------------------
    theme_switch = ft.Switch(
        label="Dark Mode",  # label next to the on/off switch
        value=False,  # start off (light mode)
        on_change=toggle_theme,  # call toggle_theme when switch changes
        label_style=ft.TextStyle(font_family="Bahnschrift", size=14),  # set label font
    )
    header_text = ft.Text(
        "Parivartan",  # display app name
        size=32,  # large text size
        weight="bold",  # bold font style
        font_family="Bahnschrift",
        text_align=ft.TextAlign.CENTER,  # center text horizontally
    )
    header_row = ft.Row(
        controls=[header_text, theme_switch],  # add title and switch side by side
        alignment=ft.MainAxisAlignment.CENTER,  # center them
        spacing=20,  # space between them
    )

    # ---------------------- IMAGE AREA SETUP ----------------------
    selected_file_paths = []  # empty list to store paths of chosen images
    plus_icon = ft.Icon(ft.Icons.ADD, size=80)  # icon showing a plus sign
    plus_text = ft.Text(
        "Click to add image", size=16, font_family="Bahnschrift"
    )  # prompt text
    plus_container = ft.Container(
        width=400,  # box width
        height=300,  # box height
        alignment=ft.alignment.center,  # center its contents
        content=ft.Column(
            controls=[plus_icon, plus_text],  # stack icon and text vertically
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=True
        ),  # open file dialog
    )
    image_area = ft.Container(
        content=plus_container, alignment=ft.alignment.center
    )  # hold image or placeholder

    # function to refresh what shows in the image box
    def update_preview():
        if not selected_file_paths:
            image_area.content = plus_container  # if no files, show placeholder
        elif len(selected_file_paths) == 1:
            preview = ft.Image(
                src=selected_file_paths[0],  # show the single image
                fit="contain",
                width=400,
                height=300,
            )
            image_area.content = ft.Container(
                content=preview, alignment=ft.alignment.center
            )  # display centered image
        else:
            thumbnails = []  # list to hold many small previews
            for path in selected_file_paths:
                thumb = ft.Image(src=path, fit="contain", width=200, height=150)
                thumbnails.append(thumb)  # add each thumbnail
            image_area.content = ft.Container(
                content=ft.Row(
                    controls=thumbnails,  # row of all thumbnails
                    wrap=True,  # allow wrapping to next line
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,  # enable scroll if too many
                ),
                alignment=ft.alignment.center,
            )
        page.update()  # redraw page with new preview

    # ---------------------- STATUS & PROGRESS INDICATORS ----------------------
    status_text = ft.Text(
        value="Waiting for action...",  # initial status message
        size=14,
        text_align=ft.TextAlign.CENTER,
        font_family="Bahnschrift",
    )
    progress_ring = ft.ProgressRing(
        width=60, height=60, stroke_width=5, value=0
    )  # circular progress bar
    progress_text = ft.Text(
        value="",  # text inside progress ring (e.g., "50%")
        size=14,
        text_align=ft.TextAlign.CENTER,
        font_family="Bahnschrift",
    )
    progress_stack = ft.Stack(
        controls=[
            progress_ring,  # background ring
            ft.Container(
                content=progress_text, alignment=ft.alignment.center, expand=True
            ),
        ],
        visible=True,  # show it when processing
        width=60,
        height=60,
    )

    # ---------------------- FILE PICKER CALLBACK ----------------------
    def dialog_picker(e: ft.FilePickerResultEvent):
        nonlocal selected_file_paths  # allow modifying the outer variable
        if e.files:
            selected_file_paths = [
                file.path for file in e.files
            ]  # collect chosen file paths
            status_text.value = f"{len(selected_file_paths)} floorplan(s) loaded. Ready to convert."  # update status with count
        else:
            selected_file_paths = []  # reset if none chosen
        update_preview()  # refresh preview box

    file_picker = ft.FilePicker(on_result=dialog_picker)  # create hidden file dialog

    # ---------------------- 2D -> 3D CONVERSION PROCESS ----------------------
    def convert(e):
        nonlocal selected_file_paths  # use outer variable
        if not selected_file_paths:
            page.update()  # nothing to do if no files
            return  # exit function

        status_text.value = "Processing..."  # show processing status
        progress_stack.visible = True  # make progress ring visible
        progress_ring.value = 0  # start at 0%
        progress_text.value = "0%"  # show 0%
        page.update()  # redraw page

        # set parameters as float for precision
        kernel_size = 2.5  # width of the cleaning filter
        erosion_iter = 2.0  # how many times to shrink white areas
        dilation_iter = 2.0  # how many times to grow white areas

        # round up to nearest whole number for OpenCV
        kernel_dim = math.ceil(kernel_size)
        erosion_iterations = math.ceil(erosion_iter)
        dilation_iterations = math.ceil(dilation_iter)

        output_dir = "objects"  # folder to save 3D files
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # create folder if missing

        last_output_file = None  # track last saved file path

        for idx, file_path in enumerate(selected_file_paths, start=1):  # loop each file
            try:
                img = cv2.imread(file_path, 0)  # read image in grayscale
                if img is None:
                    status_text.value = f"Error: Could not load image: {file_path}"
                    continue  # skip bad file

                # convert to black-white image automatically
                _, thresh = cv2.threshold(
                    img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
                )
                kernel = np.ones(
                    (kernel_dim, kernel_dim), np.uint8
                )  # make square filter
                thresh = cv2.erode(
                    thresh, kernel, iterations=erosion_iterations
                )  # shrink noise
                thresh = cv2.dilate(
                    thresh, kernel, iterations=dilation_iterations
                )  # grow shape
                thresh = cv2.morphologyEx(
                    thresh, cv2.MORPH_CLOSE, kernel, iterations=1
                )  # close gaps

                edges = cv2.Canny(thresh, 50, 150)  # detect edges in cleaned image
                contours, hierarchy = cv2.findContours(
                    edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                )  # find outlines

                vertices = []  # list to store 3D points
                faces = []  # list to store faces made of points

                # helper function to build walls from each outline
                def create_wall(contour, height=100):
                    for i in range(len(contour)):
                        x1, y1 = contour[i][0]  # current point
                        x2, y2 = contour[(i + 1) % len(contour)][0]  # next point
                        v1 = [x1, 0, y1]  # bottom of wall at point1
                        v2 = [x2, 0, y2]  # bottom of wall at point2
                        v3 = [x2, height, y2]  # top of wall at point2
                        v4 = [x1, height, y1]  # top of wall at point1
                        vertices.extend([v1, v2, v3, v4])  # save four corners
                        base_idx = len(vertices) - 4  # index of first new corner
                        faces.append(
                            [base_idx + 1, base_idx + 2, base_idx + 3, base_idx + 4]
                        )  # define face by these corners

                for contour in contours:
                    create_wall(contour)  # build wall for each outline

                xs = [v[0] for v in vertices]  # extract all x values
                zs = [v[2] for v in vertices]  # extract all z values
                if xs and zs:
                    min_x, max_x = min(xs), max(xs)  # find leftmost and rightmost
                    min_z, max_z = min(zs), max(zs)  # find topmost and bottommost
                    floor_v1 = [min_x, 0, min_z]  # four corners of floor plane
                    floor_v2 = [max_x, 0, min_z]
                    floor_v3 = [max_x, 0, max_z]
                    floor_v4 = [min_x, 0, max_z]
                    floor_base_idx = len(vertices)  # starting index for floor vertices
                    vertices.extend(
                        [floor_v1, floor_v2, floor_v3, floor_v4]
                    )  # add to list
                    faces.append(
                        [
                            floor_base_idx + 1,
                            floor_base_idx + 2,
                            floor_base_idx + 3,
                            floor_base_idx + 4,
                        ]
                    )  # add floor face

                output_file = os.path.join(
                    output_dir, f"floor_plan_3d_{idx}.obj"
                )  # set output path
                with open(output_file, "w") as file:  # open file for writing text
                    for v in vertices:
                        file.write(f"v {v[0]} {v[1]} {v[2]}\n")  # write each point line
                    for f in faces:
                        file.write(
                            f"f {f[0]} {f[1]} {f[2]} {f[3]}\n"
                        )  # write each face line
                last_output_file = output_file  # remember last saved file

            except Exception as ex:
                status_text.value = (
                    f"Error processing {file_path}: {ex}"  # show error message
                )
                page.update()  # refresh page

        progress_ring.value = 1  # set progress to 100%
        progress_text.value = "100%"  # show 100%
        status_text.value = "Processing complete. OBJ files saved in the 'objects' folder."  # show done message
        progress_stack.visible = False  # hide progress ring
        page.update()  # redraw page

        if last_output_file:
            try:
                if os.name == "nt":
                    os.startfile(last_output_file)  # open file on Windows
                else:
                    if "darwin" in os.uname().sysname.lower():
                        subprocess.call(["open", last_output_file])  # open on macOS
                    else:
                        subprocess.call(["xdg-open", last_output_file])  # open on Linux
            except Exception as ex:
                print("Error opening file:", ex)  # print opening error

    # ---------------------- BUTTONS ----------------------
    select_button = ft.ElevatedButton(
        text="Select Image",  # label on button
        icon=ft.Icons.PHOTO,  # photo icon
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(font_family="Bahnschrift", size=16)
        ),
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),  # open picker
    )
    convert_button = ft.ElevatedButton(
        text="Convert to 3D",  # label on button
        icon=ft.Icons.TRANSFORM,  # transform icon
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(font_family="Bahnschrift", size=16)
        ),
        on_click=convert,  # start conversion when clicked
    )
    button_row = ft.Row(
        controls=[select_button, convert_button, progress_stack],  # row of buttons
        alignment=ft.MainAxisAlignment.CENTER,  # center row
        spacing=10,  # space between controls
    )

    # ---------------------- FINAL LAYOUT ----------------------
    page.add(
        file_picker,  # hidden file picker component
        header_row,  # header with title and switch
        ft.Divider(),  # a dividing line
        image_area,  # area for image preview
        button_row,  # row of action buttons
        status_text,  # area for status messages
    )

    update_theme()  # apply theme colors at start
    page.update()  # draw everything on screen


# Function to start the Flet application
def run_app():
    ft.app(target=main)  # launch app with main function


if __name__ == "__main__":
    run_app()  # run when script is executed directly
