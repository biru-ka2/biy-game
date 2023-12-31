import math
from enum import Enum
from typing import List, Tuple

from src.configurations import *
from src.utility.player_state import PlayerState


class Player:
    """Implement a player component that will be used in the pygame window.
    Parameters:
        game (Game): An object of the game type.
        image_file_name (str): The name of the image file.
        pos_x (float): The x coordinate of the player.
        pos_y (float): The y coordinate of the player.
    Attributes:
        state (PlayerState): The state of the player.
        game (Game): An object of the game type.
        pos_x (float): The x coordinate of the player.
        pos_y (float): The y coordinate of the player.
        direction (int): The direction of the player.
        biy (pygame.Rect): The bounding rectangle of the player.
        image (pygame.Surface): The image of the player.
        speed_x (int): The speed of the player in the x direction.
        speed_y (int): The speed of the player in the y direction.
        gures (set): A set of gures.
    Methods:
        center(): Return the center of the player.
        handle_event(event): Handle events for the player.
        update(): Update the player.
        draw(screen): Draw the player.
    """
    width = player_width
    height = player_height

    def __init__(self, game, image_file_name: str, pos_x: float, pos_y: float) -> None:
        self.state = PlayerState.IDLE
        self.game = game

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.direction = 0
        self.speed_x = 0
        self.speed_y = 0

        self.biy = pygame.Rect(self.pos_x, self.pos_y, self.width, self.height)
        self.image = pygame.transform.scale(pygame.image.load(image_file_name), (self.width, self.height))

        self.gures = set()

        self.shooting_start_position = self.center()

    def center(self) -> List[int]:
        """Return the center of the player.
        Parameters:
            None.
        Return:
            list: A list of the x and y coordinates of the center of the player.
        """
        return [self.pos_x + self.width // 2, self.pos_y + self.height // 2]

    def handle_event(self, event: pygame.event.Event) -> int:
        """Handle events for the player.
        Parameter:
            event (pygame.event.Event): An event object.
        Return:
            int: The status of the plaeyer, 1 if they are done, 0 if they are not.
        """
        # Allow for long press key presses
        if event.type != pygame.KEYDOWN:
            return 0

        key = event.key
        if key == pygame.K_SPACE:
            self.state = PlayerState.SHOOTING
            self.shooting_start_position = self.center()

            self.speed_x = 0.01 * self.game.power_size * math.cos(math.radians(self.direction))
            self.speed_y = 0.01 * self.game.power_size * math.sin(math.radians(self.direction))

            return 1

        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.state = PlayerState.AIMING

            pygame.key.set_repeat(500, 100)
            pygame.time.set_timer(pygame.USEREVENT, 100)

            if key == pygame.K_RIGHT:
                self.direction += 5

            elif key == pygame.K_LEFT:
                self.direction -= 5

        elif key in (pygame.K_UP, pygame.K_DOWN):
            self.state = PlayerState.POWER
            if key == pygame.K_UP and self.game.power_size < max_power_size:
                self.game.set_power_size(self.game.power_size + 100)
            elif key == pygame.K_DOWN and self.game.power_size > 0:
                self.game.set_power_size(self.game.power_size - 100)

        return 0

    def update(self):
        """Update the player's position and speed.
        Parameter:
            None.
        Return:
            None.
        """
        # Check if the custom event for long press has been triggered
        if pygame.event.peek(pygame.USEREVENT):
            # Handle long press here for aiming
            for event in pygame.event.get(pygame.USEREVENT):
                if event.type == pygame.USEREVENT:
                    if pygame.key.get_pressed()[pygame.K_LEFT]:
                        self.direction -= 5
                    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                        self.direction += 5

        self.pos_x, self.pos_y = self.pos_x + self.speed_x, self.pos_y + self.speed_y
        self.biy.x, self.biy.y = self.pos_x, self.pos_y

        if self.speed_x == 0 and self.speed_y == 0:
            self.game.shooting = False

        if self.pos_x <= self.width or self.pos_x >= self.game.screen.get_width():
            self.speed_x = -1 * self.speed_x

        if self.pos_y <= self.height or self.pos_y >= self.game.screen.get_height():
            self.speed_y = -1 * self.speed_y

        self.speed_x = self.update_speed(self.speed_x)
        self.speed_y = self.update_speed(self.speed_y)
        # self.start = [(self.pos_x + self.width) // 2, (self.pos_y + self.height) // 2]

        if self.state == PlayerState.SHOOTING and self.speed_x == self.speed_y == 0:
            self.state = PlayerState.IDLE

    def stop(self):
        """Stop the player.
        Parameter:
            None.
        Return:
            None.
        """
        self.speed_x = 0
        self.speed_y = 0

    @staticmethod
    def update_speed(speed: int) -> int:
        """Update the speed of the player.
        Parameter:
            speed (int): The speed of the player.
        Return:
            int: The updated speed of the player.
        """
        speedDx = {True: -0.05, False: 0.05}
        x = speed > 0
        speed += speedDx[speed > 0]
        y = speed > 0
        if x != y:
            return 0
        return speed

    def draw(self, screen: pygame.Surface, scale_factor: float, translation_vector: Tuple[float]) -> None:
        """Draw the player.
        Parameter:
            screen (pygame.Surface): The screen to draw the player on.
            scale_factor (float): The scale factor to scale the player by.
            translation_vector (Tuple[float]): The translation vector to translate the player by.
        Return:
            None.
        """
        if self.state in [PlayerState.AIMING, PlayerState.POWER]:
            start = self.center()
            end = [start[0] + 100 * math.cos(math.radians(self.direction)) * scale_factor,
                   start[1] + 100 * math.sin(math.radians(self.direction)) * scale_factor]
            pygame.draw.line(screen, white, start, end, 2)

        if self.state == PlayerState.POWER:
            self.game.power_bar.draw(scale_factor)

        # use the scaling factor and translation vector to calculate the players current position
        self.pos_x = self.pos_x * scale_factor + translation_vector[0]
        self.pos_y = self.pos_y * scale_factor + translation_vector[1]

        # scale self.image to the new size
        self.image = pygame.transform.scale(self.image,
                                            (int(self.width * scale_factor), int(self.height * scale_factor)))
        screen.blit(self.image, (self.pos_x, self.pos_y))
