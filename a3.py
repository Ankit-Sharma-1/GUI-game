import tkinter as tk
import math
from tkinter import messagebox

from core import Unit, Point2D, UnitManager
from model import TowerGame
from tower import SimpleTower, MissileTower,PulseTower, AbstractTower
from range_ import CircularRange,AbstractRange,PlusRange,DonutRange
from enemy import SimpleEnemy, AbstractEnemy
from utilities import Stepper, rectangles_intersect, get_delta_through_centre,angle_between,euclidean_distance, rotate_toward,Countdown
from view import GameView
from level import AbstractLevel
from advanced_view import  TowerView
from high_score_manager import HighScoreManager

#Works on Windows
import pygame
from pygame import mixer

BACKGROUND_COLOUR = "#4a2f48"

__author__ = "s4515529 Ankit Sharma"
__copyright__ = ""


# Could be moved to a separate file, perhaps levels/simple.py, and imported
class MyLevel(AbstractLevel):
    """A simple game level generating 10 waves"""
    waves = 10

    def get_wave(self, wave):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order 
        """
        enemies = []

        if wave == 1:
            # A hardcoded singleton list of (step, enemy) pairs
            enemies = [(10, SimpleEnemy())]
        elif wave == 2:
            # A hardcoded list of multiple (step, enemy) pairs
            enemies = [(10, SimpleEnemy()), (20, SimpleEnemy()),(30, SimpleEnemy()),
                       (40, SimpleEnemy())]

        elif 3 <= wave < 6:
            # List of (step, enemy) pairs spread across an interval of time (steps)

            steps = int(40 * (wave ** .5))  # The number of steps to spread the enemies across
            count = wave * 2  # The number of enemies to spread across the (time) steps
            for step in self.generate_intervals(steps, count):
                enemies.append((step, SimpleEnemy()))
        elif wave == 6:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (20, None, None, None, None),  # then nothing for 100 steps
                (50, 2, ResistantEnemy, (), {}),  # then another 2 enemies over 50 steps
                (20, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {})  # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)

        elif wave == 7:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 2, AdvancedEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {})  # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)

        elif wave == 8:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 3, ResistantEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 3, AdvancedEnemy, (), {}),  # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)

        elif wave == 9:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 4, ResistantEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 4, AdvancedEnemy, (), {}),  # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)


        elif wave == 10:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 5, ResistantEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {}),  # then another 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 5, AdvancedEnemy, (), {}),  # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)
        """

        else:  # 11 <= wave <= 20
            # Now it's going to get hectic

            sub_waves = [
                (
                    int(13 * wave),  # total steps
                    int(25 * wave ** (wave / 50)),  # number of enemies
                    SimpleEnemy,  # enemy constructor
                    (),  # positional arguments to provide to enemy constructor
                    {},  # keyword arguments to provide to enemy constructor
                ),
                # ...
            ]
            enemies = self.generate_sub_waves(sub_waves)"""

        return enemies

    
# Task 1.3 Create Status Bar class
class StatusBar(tk.Frame):
    """Define the status bar class which displays information to the user
        about their status.
        
        Parameters:
            master (TK): Parent Window for this game
    """

    def __init__(self, master):
        """Sets up the Status Bar

        Parameters:
            master (Tk): Window in which this widget is to be placed.

        """
        super().__init__(master)
        #self.pack(fill = tk.BOTH, expand=True)
        #Placing labels for Wave number
        self._wave_label = tk.Label(master, text="Wave: ",bg="white")
        self._wave_label.pack(side=tk.TOP, fill = tk.X)
        #Placing labels for Score value
        self._score_label = tk.Label(master, text="",bg='white')
        self._score_label.pack(side=tk.TOP, fill = tk.X)
        #Placing Coin image. Image is imported from specified location
        self._coin_image = tk.PhotoImage(file="images/coins.gif")
        self._coins_image_label = tk.Label(master, image=self._coin_image, bg='white')
        self._coins_image_label.pack(side=tk.LEFT)
        #Placing labels for Score value
        self._coins_label = tk.Label(master, text="50 coins",bg='white')
        self._coins_label.pack(side=tk.LEFT, fill = tk.X)
        #Placing Heart image. Image is imported from specified location
        self._heart_image = tk.PhotoImage(file="images/heart.gif")
        self._heart_image_label = tk.Label(master, image=self._heart_image, bg='white')
        self._heart_image_label.pack(side=tk.LEFT)
        #Placing labels for lives value
        self._lives_label = tk.Label(master, text="20 lives",bg='white')
        self._lives_label.pack(side=tk.LEFT, fill = tk.X)

    def set_wave(self, wave):
        """Updates the wave number in the wave_label

        Parameters:
            wave_n (int): The nth wave
        """
        #Wave label is configured based on wave value
        self._wave_label.config(text="Wave: {}/10".format(wave)) #Wave label is configured 

    def set_lives(self, lives):
        """Updates the lives value in the lives_label

        Parameters:
            lives (int): The number of lives left
        """
        #Lives label is configured based on life value
        self._lives_label.config(text="{} Lives".format(lives))

    def set_score(self, score):
        """Updates the score number in the score_label

        Parameters:
            score (int): The player score
        """
        #Score label is configured based on score value
        self._score_label.config(text="Score: {}".format(score))

    def set_coins(self, coins):
        """Updates the coin in the coins_label

        Parameters:
            coins (int): The player coins
        """
        #Coins label is configured based on coins value
        self._coins_label.config(text="{} Coins".format(coins))
        
# Task 2.2 Create Custom Tower
class EnergyTower(SimpleTower):
    """An energy tower with short range that rotates towards
        enemies and shoots energy at them.

        Attacks custom enemy immune to projectile and missile
    """
    #Set name and colour,range,cooldown and cost value
    name = 'Energy Tower'
    colour = '#FFFF00' #Yellow
    
    range = CircularRange(2)
    cool_down_steps = 5
    base_cost = 40
    level_cost = 50

    rotation_threshold = (1 / 6) * math.pi

    def __init__(self, cell_size: int, grid_size=(.9, .9), rotation=math.pi * .25,
                 base_damage=2, level: int = 1):
        super().__init__(cell_size, grid_size, rotation, base_damage, level)
        """Initialise the tower"""

        self._target: EnergyEnemy = None 

    def step(self, data):
        """Rotates toward 'target' and attacks if possible"""
        self.cool_down.step()

        #If no enemy in range does nothing    
        if self.get_unit_in_range(data.enemies) is None:
            return

        #If energy enemy is in range it faces and damages it      
        target = self.get_unit_in_range(data.enemies)
        angle = angle_between(self.position, target.position)
        partial_angle = rotate_toward(self.rotation, angle, self.rotation_threshold)
        self.rotation = partial_angle
        if partial_angle == angle:
            if target.name == "Energy Enemy":
                target.damage(self.get_damage(), 'energy')
        else:
            return

# Task 2.2 Create Custom Enemy
class ResistantEnemy(SimpleEnemy):
    """An enemy resistant to projectile and missile.
      Takes damage by Energy Tower only
      It can be slowed by SlowTower(Advanced tower)"""

    #Set name and colour and points
    
    name = "Energy Enemy"
    colour = '#4000FF'  #Ultramarine

    points = 5

    def __init__(self, grid_size=(.2, .2), grid_speed=5/60, health=100):
        super().__init__(grid_size, grid_speed, health)
        """Initialise the Enemy"""

    def damage(self, damage, type_):
        """Inflict damage on the enemy

        Parameters:
            damage (int): The amount of damage to inflict
            type_ (str): The type of damage to do i.e. projectile, explosive
        """
        if type_ == "energy":
            self.health -= damage
        if type_ == "slow":
            self.grid_speed = 2.5/60
        if self.health < 0:
            self.health = 0

    def step(self, data):
        """Move the enemy forward a single time-step

        Parameters:
            grid (GridCoordinateTranslator): Grid the enemy is currently on
            path (Path): The path the enemy is following

        Returns:
            bool: True iff the new location of the enemy is within the grid
        """
        grid = data.grid
        path = data.path

        # Repeatedly move toward next cell centre as much as possible
        movement = self.grid_speed
        while movement > 0:
            cell_offset = grid.pixel_to_cell_offset(self.position)

            # Assuming cell_offset is along an axis!
            offset_length = abs(cell_offset[0] + cell_offset[1])

            if offset_length == 0:
                partial_movement = movement
            else:
                partial_movement = min(offset_length, movement)

            cell_position = grid.pixel_to_cell(self.position)
            delta = path.get_best_delta(cell_position)

            # Ensures enemy will move to the centre before moving toward delta
            dx, dy = get_delta_through_centre(cell_offset, delta)

            speed = partial_movement * self.cell_size
            self.move_by((speed * dx, speed * dy))
            self.position = tuple(int(i) for i in self.position)

            movement -= partial_movement

        intersects = rectangles_intersect(*self.get_bounding_box(), (0, 0), grid.pixels)
        return intersects or grid.pixel_to_cell(self.position) in path.deltas

# Task 2.3 Create ShopTowerView class
class ShopTowerView(tk.Frame):
    """Define the shop tower view class which displays information to the user
        about towers they can buy.
        
        Parameters:
            master (TK): Parent Window for this game
    """

    def __init__(self, master,tower,*args,click_command, **kwargs):
        super().__init__(master, *args, **kwargs)

        """Inflict damage on the enemy

        Parameters:
            master (Tk): The window in which it appears
            tower: The tower for which information is displayed
            click_command: Allows selection from tower class
        """

        # Variables for setting dimension canvas inside Status Bar
        self._canvasHeight = 50
        self._canvasWidth = 100

        # Initilaise variables
        self._available_flag = None
        self._click_command = click_command

        #Create canvas
        self._canvas = tk.Canvas(master,bg = BACKGROUND_COLOUR,
                                 highlightbackground = BACKGROUND_COLOUR,
                                 width=self._canvasWidth,height=self._canvasHeight)
        self._canvas.pack(side=tk.TOP,fill=tk.BOTH, padx = 20)

        #Draw tower in canvas
        tower.position = (tower.cell_size // 2, tower.cell_size // 2)  # Position in centre
        tower.rotation = 3 * math.pi / 2  # Point up
        TowerView.draw(self._canvas, tower)

        #Create label fre tower name and value
        self._tower_label1 = tk.Label(self._canvas, text = "{}".format(tower.name),
                                      bg = BACKGROUND_COLOUR,font = ("Comic Sans",8),
                                      fg = "white")
        self._tower_label1.pack()
        self._tower_label2 = tk.Label(self._canvas,
                                      text = "{} coins".format(tower.get_value()),
                                      bg = BACKGROUND_COLOUR,font = ("Comic Sans",8),
                                      fg = "white")
        self._tower_label2.pack()

        
        #Bind mouse events to canvas.
        self._canvas.bind('<Button-1>', self._left_click)
        self._tower_label1.bind('<Button-1>',self._left_click)
        self._tower_label2.bind('<Button-1>',self._left_click)
        


##    def change_text_colour():
##        self._tower_label2.config(fg = "red")
        
    def set_available(self, available):
        """Changes the colour of coin cost based on availability

        Parameters:
            available (bool): True if tower is available
        """
        if available == True:
            self._tower_label1.config(fg = "white")
            self._tower_label2.config(fg = "white")
        else:
            self._tower_label1.config(fg = "red")
            self._tower_label2.config(fg = "red")

    def _left_click(self,event):
        """Select a tower from Status bar for building on canvas

        Parameters:
            click_command: Allows interaction with tower class
        """
        self._click_command()

# Task 3.1 Create Advanced Tower (Slow Tower)
class SlowTower(SimpleTower):
    """A simple tower with short range that rotates towards enemies and slows them down"""
    
    name = 'Slow Tower'
    colour = '#8B8D7A' #Stone Gray
    
    range = CircularRange(2)
    cool_down_steps = 5
    base_cost = 200
    level_cost = 50

    rotation_threshold = (1 / 6) * math.pi

    def __init__(self, cell_size: int, grid_size=(.9, .9), rotation=math.pi * .25,
                 base_damage=0, level: int = 1):
        super().__init__(cell_size, grid_size, rotation, base_damage, level)
        """Initialises the tower"""

        self._target: EnergyEnemy = None 

    def step(self, data):
        """Rotates toward 'target' and attacks if possible"""
        self.cool_down.step()
        
        if self.get_unit_in_range(data.enemies) is None:
            return

        target = self.get_unit_in_range(data.enemies)
        angle = angle_between(self.position, target.position)
        partial_angle = rotate_toward(self.rotation, angle, self.rotation_threshold)
        self.rotation = partial_angle
        if partial_angle == angle:
            target.damage(self.get_damage(), 'slow')
        else:
            return



class SimpleEnemy(SimpleEnemy):
    """Update SimpleEnemy to slow down when hit by slow tower"""
    def damage(self, damage, type_):
        """Inflict damage on the enemy

        Parameters:
            damage (int): The amount of damage to inflict
            type_ (str): The type of damage to do i.e. projectile, explosive
        """
        self.health -= damage
        if type_ == "slow":
            self.grid_speed = 2.5/60
        if self.health < 0:
            self.health = 0

# Task 3.2 Create Advanced Enemy
class AdvancedEnemy(AbstractEnemy):
    """An advanced enemy which is more resistant to projectile and missile
       It also cannot be slowed down
       On its health reducing to half it speeds up"""
    name = "Advanced Enemy"
    colour = '#CC7722'  #Ochre

    points = 5

    def __init__(self, grid_size=(.4, .4), grid_speed=5/60, health=100):
        super().__init__(grid_size, grid_speed, health)
        """Initialises the enemy"""

    def damage(self, damage, type_):
        """Inflict damage on the enemy

        Parameters:
            damage (int): The amount of damage to inflict
            type_ (str): The type of damage to do i.e. projectile, explosive
        """
        
        if type_ == "projectile" or type_ == "pulse" or type_ == "explosive":
            self.health -= (damage/20)
        if self.health < 0:
            self.health = 0

    def move_by(self, delta):
        """Moves normally only if health status is higher than 50%, otherwise gains a
        boost when moving forward and down."""
        x, y = self.position
        dx, dy = delta
        if self.health <= 50:
            self.grid_speed = 10/60
            self.position = x + dx, y + dy
        else:
            self.position = x + dx, y + dy
            

    def step(self, data):
        """Move the enemy forward a single time-step

        Parameters:
            grid (GridCoordinateTranslator): Grid the enemy is currently on
            path (Path): The path the enemy is following

        Returns:
            bool: True iff the new location of the enemy is within the grid
        """
        grid = data.grid
        path = data.path

        # Repeatedly move toward next cell centre as much as possible
        movement = self.grid_speed
        while movement > 0:
            cell_offset = grid.pixel_to_cell_offset(self.position)

            # Assuming cell_offset is along an axis!
            offset_length = abs(cell_offset[0] + cell_offset[1])

            if offset_length == 0:
                partial_movement = movement
            else:
                partial_movement = min(offset_length, movement)

            cell_position = grid.pixel_to_cell(self.position)
            delta = path.get_best_delta(cell_position)

            # Ensures enemy will move to the centre before moving toward delta
            dx, dy = get_delta_through_centre(cell_offset, delta)
            speed = partial_movement * self.cell_size
            self.move_by((speed * dx, speed * dy))
            self.position = tuple(int(i) for i in self.position)

            movement -= partial_movement

        intersects = rectangles_intersect(*self.get_bounding_box(), (0, 0), grid.pixels)
        return intersects or grid.pixel_to_cell(self.position) in path.deltas


class TowerGameApp(Stepper):
    """Top-level GUI application for a simple tower defence game"""

    # All private attributes for ease of reading
    _current_tower = None
    _paused = False
    _won = None

    _level = None
    _wave = None
    _score = None
    _coins = None
    _lives = None

    _master = None
    _game = None
    _view = None

    def __init__(self, master: tk.Tk, delay: int = 20):
        """Construct a tower defence game in a root window

        Parameters:
            master (tk.Tk): Window to place the game into
        """
        #Setting title of the Window
        master.title("Towers")

        self._master = master
        super().__init__(master, delay=delay)

        self._game = game = TowerGame()

        self.setup_menu()

        # create a game view and draw grid borders
        self._view = view = GameView(master, size=game.grid.cells,
                                     cell_size=game.grid.cell_size,
                                     bg='antique white')
        view.pack(side=tk.LEFT, expand=True)

        # Task 4.1 Postgraduate advanced feature. Initialise pygame and sounds
        pygame.init()
        mixer.init()
        self.build_sound = pygame.mixer.Sound("sound/build.wav")
        self.increase_coin = pygame.mixer.Sound("sound/coin.wav")
        self.decrease_life = pygame.mixer.Sound("sound/heart.wav")
        self.wave_m = pygame.mixer.Sound("sound/next_wave.wav")
        self.pause_play = pygame.mixer.Sound("sound/pause_play.wav")
        self.quit_m = pygame.mixer.Sound("sound/quit.wav")

        # Task 4.1 Postgraduate advanced feature. Play music
        pygame.mixer.music.load("sound/game_music.mp3")
        pygame.mixer.music.play(-1)

       
        # Task 1.3 (Status Bar): instantiate status bar

        # Put the status bar in a frame
        self._right_frame = tk.Frame(master, bg="white")
        self._right_frame.pack(fill=tk.BOTH, expand=True)

        self._status_bar = StatusBar(self._right_frame)
        self._status_bar.pack(side=tk.TOP)

        # Task 2.4 (High Score): instantiate highscore
        self._high_score = HighScoreManager()
        

        # Task 1.5 (Play Controls): instantiate widgets here
        # Create a frame for widgets
        self._bottom_frame = tk.Frame(master, bg=BACKGROUND_COLOUR)
        self._bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        #Create button for next wave
        self._next_wave_btn = tk.Button(self._bottom_frame,text = "Next Wave",
                                        state = tk.NORMAL, command=self.next_wave)
        self._next_wave_btn.pack(side=tk.LEFT,ipadx = 10, padx = 10, ipady = 10,
                                 pady = 10)
        #Create button for play/pause 
        self._play_btn = tk.Button(self._bottom_frame, text = "Pause",
                                   state =tk.NORMAL, command=self._toggle_paused)
        self._play_btn.pack(side=tk.LEFT,ipadx=10, padx=10, ipady=10)
        
        # bind game events
        game.on("enemy_death", self._handle_death)
        game.on("enemy_escape", self._handle_escape)
        game.on("cleared", self._handle_wave_clear)

        # Task 1.2 (Tower Placement): bind mouse events to canvas here
        # On leaving canvas hide mouse
        # On left click place tower
        # On right click sell tower
        self._view.bind('<Motion>', self._move)
        self._view.bind('<Leave>', self._mouse_leave)
        self._view.bind('<Button-1>', self._left_click)
        self._view.bind('<Button-3>', self._right_click)

        # Level
        self._level = MyLevel()
        
        #Choose tower on initialisation
        self.select_tower(SimpleTower)

        #Draw borders
        view.draw_borders(game.grid.get_border_coordinates())

        # Get ready for the game
        self._setup_game()

        # Task 2.3 (Shop) Creating Shop

        #Store towers present in the game for Shop
        towers = [SimpleTower,EnergyTower,PulseTower,MissileTower,SlowTower]

        #Create frmae for Shop window
        self._right_middle_frame = tk.Frame(master, bg=BACKGROUND_COLOUR)
        self._right_middle_frame.pack(fill=tk.BOTH, expand=True)

        #Put shop in the frame created
        shop = tk.Frame(self._right_middle_frame, bg=BACKGROUND_COLOUR)
        shop.pack(side=tk.BOTTOM, fill=tk.X)

        # Create views for each tower & store to update if availability changes
        self._tower_views = []
        for tower_class in towers:
            tower = tower_class(self._game.grid.cell_size // 2)
            view = ShopTowerView(shop, tower,bg=BACKGROUND_COLOUR,
                         click_command = lambda class_=tower_class: self.select_tower(class_))
            view.pack(fill=tk.X)
            self._tower_views.append((tower, view))  # Can use to check if tower is affordable when refreshing view
        
        # Task 1.4 On pressing delete(X) button in window prompt user before exit

        def callback():
            """Prompt user on pressing delete(X)"""
            if messagebox.askokcancel("Quit","Do you really wish to quit?"):
                self._high_score.save()
                pygame.mixer.Sound.play(self.quit_m)
                master.destroy()

        master.protocol("WM_DELETE_WINDOW", callback)

    def setup_menu(self):
        """Sets up the application menu"""
        # Task 1.4: construct file menu here
        # ...
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)

        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New Game", command=self._new_game)
        filemenu.add_command(label="High Scores", command=self._high_scores)
        filemenu.add_command(label="Exit", command=self._exit)

        


    def _toggle_paused(self, paused=None):
        """Toggles or sets the paused state

        Parameters:
            paused (bool): Toggles/pauses/unpauses if None/True/False, respectively
        """
        if paused is None:
            paused = not self._paused

        # Task 1.5 (Play Controls): Reconfigure the pause button here
        
        # On pause stop music and change label text
        if paused:
            self.pause()
            pygame.mixer.Sound.play(self.pause_play)
            self._play_btn.config(text="Play")
            pygame.mixer.music.pause()
        else:
        # On start/unpause start music and change label text
            self.start()
            pygame.mixer.Sound.play(self.pause_play)
            self._play_btn.config(text="Pause")
            pygame.mixer.music.unpause()
            
        self._paused = paused

    def _setup_game(self):
        """Sets up the game"""
        self._wave = 0
        self._score = 0
        self._coins = 100
        self._lives = 20

        self._won = False

        # Task 1.3 (Status Bar): Update status here
        #Set values displayed in status bar
        self._status_bar.set_coins(self._coins)
        self._status_bar.set_wave(self._wave)
        self._status_bar.set_lives(self._lives)
        self._status_bar.set_score(self._score)        
        
        # Task 1.5 (Play Controls): Re-enable the play controls here (if they were ever disabled)
        self._next_wave_btn.config(state=tk.NORMAL)
        self._play_btn.config(state=tk.NORMAL)
        self._game.reset()

        # Auto-start the first wave
        self.next_wave()
        self._toggle_paused(paused=True)

    # Task 1.4 (File Menu): Complete menu item handlers here (including docstrings!)
    #
    def _new_game(self):
        """Create a new message box file to check if player is sure and starts a new game"""
        reply = messagebox.askquestion(type=messagebox.YESNO,
                        title="Exit Towers",
                        message="Are you sure you want to start a new game?")
        if reply == messagebox.YES:
            self._game.reset()
            self._setup_game()
            self.refresh_view()
            self._view.draw_enemies(self._game.enemies)

    def _high_scores(self):
        """Enables user interaction when clicking on HighScores in File Menu"""

        #Creates a frame for highscore
        high_score_window = tk.Toplevel()
        high_score_window.title("High Scores")

        
        #Gets values stored in the file
        data_input=self._high_score.get_entries()
        Output = "Rank | Name | Score | Comment\n-----------------------------------\n"
        i = 1

        
        #Load values and shows on screen
        for dictionary in data_input:
            dictionary_values = str(dictionary.values())
            name,score,comment = dictionary_values.split(sep = ",")
            Output = Output + str(i) +"       |"+ name[14:-1] +"     |"+ score +"   |"+ comment[:-2]+"\n"
            i += 1

        #Button to returen to game 
        msg = tk.Message(high_score_window, text=Output)
        msg.pack()
        
        button = tk.Button(high_score_window, text="Return to Game", command=high_score_window.destroy)
        button.pack()
        
    def _exit(self):
        """ Opens message box on player trying to exit""" 
        reply = messagebox.askquestion(type=messagebox.YESNO,
                        title="Quit Towers",
                        message="Do you really wish to quit?")
        if reply == messagebox.YES:
            self._high_score.save()
            pygame.mixer.Sound.play(self.quit_m)
            self._master.destroy()
            
    

    def refresh_view(self):
        """Refreshes the game view"""


        #Draws towers and obstacles
        if self._step_number % 2 == 0:
            self._view.draw_enemies(self._game.enemies)
        self._view.draw_towers(self._game.towers)
        self._view.draw_obstacles(self._game.obstacles)

        #Sets available flag
        for tower_view in self._tower_views:
            if tower_view[0].get_value() > self._coins:
                tower_view[1].set_available(False)
            else:
                tower_view[1].set_available(True)

    def _step(self):
        """
        Perform a step every interval

        Triggers a game step and updates the view

        Returns:
            (bool) True if the game is still running
        """
        self._game.step()
        self.refresh_view()
        return not self._won

    # Task 1.2 (Tower Placement): Complete event handlers here (including docstrings!)
    # Event handlers: _move, _mouse_leave, _left_click
    def _move(self, event):
        """
        Handles the mouse moving over the game view canvas

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        if self._current_tower.get_value() > self._coins:
            return

        # move the shadow tower to mouse position
        position = event.x, event.y
        self._current_tower.position = position

        legal, grid_path = self._game.attempt_placement(position)

        # find the best path and covert positions to pixel positions
        path = [self._game.grid.cell_to_pixel_centre(position)
                for position in grid_path.get_shortest()]

        # Task 1.2 (Tower placement): Draw the tower preview here
        # Draw tower path and preview
        self._view.draw_preview(self._current_tower, legal)
        self._view.draw_path(path)
        
    def _mouse_leave(self, event):
        """
        Handles the mouse leaving the game view canvas

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        # Task 1.2 (Tower placement): Delete the preview
        # Hint: Relevant canvas items are tagged with: 'path', 'range', 'shadow'
        #       See tk.Canvas.delete (delete all with tag)
        #Deletes mouse preview
        self._view.delete("path")
        self._view.delete("range")
        self._view.delete("shadow")
        
    def _left_click(self, event):
        """
        Handles the mouse left clicking on the game view canvas

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        # retrieve position to place tower
        if self._current_tower is None:
            return
        #If tower value is greater than current coins doesn't do anything 
        if self._current_tower.get_value() > self._coins:
            return

        #Takes current position
        position = event.x, event.y
        cell_position = self._game.grid.pixel_to_cell(position)

        if self._game.place(cell_position, tower_type=self._current_tower.__class__):
        #Task 2.1 (Buy and sell Towers) : On placing a tower deduct the value of tower from players wallet
            self._coins -= self._current_tower.get_value()

        #On placing tower plays sound    
            pygame.mixer.Sound.play(self.build_sound)

    def _right_click(self, event):
        """
        Handles the mouse right clicking on the game view canvas

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        # retrieve position to sell tower
        position = event.x, event.y
        cell_position = self._game.grid.pixel_to_cell(position)

        self._game.remove(cell_position)

        """Task 2.1 (Buy and sell Towers) : player can sell a tower by right
            clicking on it. The tower should be removed from the grid and 80%
            of its value should be put back into the player's wallet."""
        self._coins += (self._current_tower.get_value()* 0.8)

    def next_wave(self):
        """Sends the next wave of enemies against the player"""
        # If is the last wave do nothing
        if self._wave == self._level.get_max_wave():
            return

        #else increase wave value
        self._wave += 1

        #Play sound on next wave
        pygame.mixer.Sound.play(self.wave_m)
        

        # Task 1.3 (Status Bar): Update the current wave display here
        # Update wave vlaue in Status Bar
        self._status_bar.set_wave(self._wave)

        # Task 1.5 (Play Controls): Disable the add wave button here (if this is the last wave)
        # Disable add wave button
        if self._wave == self._level.get_max_wave():
            self._next_wave_btn.config(state=tk.DISABLED)
            self._play_btn.config(state=tk.DISABLED)

        # Generate wave and enemy
        wave = self._level.get_wave(self._wave)
        for step, enemy in wave:
            enemy.set_cell_size(self._game.grid.cell_size)

        # Queue wave
        self._game.queue_wave(wave)

    def select_tower(self, tower):
        """
        Set 'tower' as the current tower

        Parameters:
            tower (AbstractTower): The new tower type
        """
        self._current_tower = tower(self._game.grid.cell_size)

    def _handle_death(self, enemies):
        """
        Handles enemies dying

        Parameters:
            enemies (list<AbstractEnemy>): The enemies which died in a step
        """
        bonus = len(enemies) ** .5
        for enemy in enemies:
            self._coins += enemy.points
            pygame.mixer.Sound.play(self.increase_coin)
            self._score += int(enemy.points * bonus)

        # Task 1.3 (Status Bar): Update coins & score displays here
        # Update coins and score in Status bar
        self._status_bar.set_coins(self._coins)
        self._status_bar.set_score(self._score)

        
    def _handle_escape(self, enemies):
        """
        Handles enemies escaping (not being killed before moving through the grid

        Parameters:
            enemies (list<AbstractEnemy>): The enemies which escaped in a step
        """
        self._lives -= len(enemies)

        #Play sound on losing life
        pygame.mixer.Sound.play(self.decrease_life)
        
        if self._lives < 0:
            self._lives = 0

        # Task 1.3 (Status Bar): Update lives display here
        # Update lives value in Status BAr
        self._status_bar.set_lives(self._lives)
        

        # Handle game over
        if self._lives == 0:
            self._handle_game_over(won=False)
            
            

    def _handle_wave_clear(self):
        """Handles an entire wave being cleared (all enemies killed)"""
        if self._wave == self._level.get_max_wave():
            self._handle_game_over(won=True)



    def _handle_game_over(self, won=False):
        """Handles game over
        
        Parameter:
            won (bool): If True, signals the game was won (otherwise lost)
        """
        self._won = won
        self.stop()
        self._next_wave_btn.config(state=tk.DISABLED)
        self._play_btn.config(state=tk.DISABLED)

        pygame.mixer.music.pause()

        # Task 1.4 (Dialogs): Show game over dialog here
        # Task 2.4 (High Scores) On users running out of lives, check and store score

        #Display message on winning or losing
        if self._won:
            messagebox.showinfo("Game Over","Congratulations!!! You Won")            
        else:
            messagebox.showinfo("Game Over","Better luck next time. You Lost" )

        #Store high score
        if self._high_score.does_score_qualify(self._score):

        #Create window to take input
            high_score_entry_window = tk.Toplevel()
            high_score_entry_window.title("High Score Entry")

            label = tk.Label(high_score_entry_window, text='Enter Name: ')
            label.pack(side=tk.LEFT)

            entry = tk.Entry(high_score_entry_window, width=20)
            entry.pack(side=tk.LEFT)

            #Function to add score & close window
            def add():
                name = entry.get()
                self._high_score.add_entry(name, self._score)
                pygame.mixer.Sound.play(self.quit_m)
                high_score_entry_window.destroy()

            calc = tk.Button(high_score_entry_window, text="Enter", command=add)
            calc.pack(side=tk.LEFT)
        

        
# Task 1.1 (App Class): Instantiate the GUI here
# ...
"Launch tower app GUI"
if __name__ == '__main__' :
    root = tk.Tk()
    app = TowerGameApp(root)
    root.mainloop()
