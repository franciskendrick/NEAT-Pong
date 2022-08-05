import pygame
import time
import json
import os

pygame.init()
resources_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        "..", "..", 
        "resources", "windows"
        )
    )


class Window:
    # Window
    rect = pygame.Rect(0, 0, 640, 360)
    enlarge = 2
    # enlarge = max(
    #     pygame.display.Info().current_w / rect.width,
    #     pygame.display.Info().current_h / rect.height)

    # Court
    playable_rect = pygame.Rect(
        0, 10, rect.width, rect.height-20)
    center_line = pygame.Rect(
        rect.centerx - 10 // 2, 0,
        10, rect.height)

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Framerate
    framerate = 60

    # Initialize -------------------------------------------------- #
    def __init__(self):
        # Framerate
        self.last_time = time.perf_counter()
        self.update_deltatime()

    # Draw -------------------------------------------------------- #
    def draw_playablesurface(self, display):
        pygame.draw.rect(display, self.black, self.playable_rect)

    def draw_centerline(self, display):
        pygame.draw.rect(display, self.white, self.center_line)

    # Update ------------------------------------------------------ #
    def update_optionssettings(self, options_settings):
        # Get handle options settings
        handle_optionssettings = self.options_settings.copy()

        # Edit options' game settings
        for json_key, options_value in zip(
                handle_optionssettings.keys(), options_settings.values()):
            for (name, button) in options_value.buttons.items():
                if button[1]:  # buttons' toggle status is True
                    handle_optionssettings[json_key] = name
                    break

        # Edit options' sound settings
        sound_status = not options_settings["miscellaneous"].buttons["sound"][1]
        handle_optionssettings["sound"] = sound_status

        # Dump handle options settings to the JSON file
        with open(f"{resources_path}/options_settings.json", "w") as json_file:
            json.dump(handle_optionssettings, json_file)

    def update_deltatime(self, multiplier=1, using=True):
        if using:
            self.delta_time = time.perf_counter() - self.last_time
            self.delta_time *= (60 * multiplier)
            self.last_time = time.perf_counter()
        else:
            self.delta_time = 1


window = Window()
