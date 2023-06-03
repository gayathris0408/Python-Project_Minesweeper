#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pygame
import sys
from random import randrange
from tkinter import *
from PIL import Image, ImageTk

# Colors used
BLACK = (0, 0, 0)
WHITE = (239, 255, 255)
RED = (255, 0, 0)
TURQUOISE = (50, 127, 127)
# Set the WIDTH and HEIGHT of each grid location
WIDTH = 40
HEIGHT = 40
# Set the margin between each cell
MARGIN = 5
# Set size of menu
MENU_SIZE = 40
# Define LEFT_CLICK and RIGHT_CLICK
LEFT_CLICK = 1
RIGHT_CLICK = 3

# Assign initial values to variables
NSQUARES = 0
NBOMBS = 0
proceed = ""
game_over = False
click_count = 0

# Class that holds the game logic          
class Game:
    def __init__(self, NSQUARES, NBOMBS):
        # Create a grid of NSQUARES x NSQUARES
        self.grid = [[Cell(x, y) for x in range(NSQUARES)] for y in range(NSQUARES)]
        self.init = False
        self.game_lost = False
        self.game_won = False
        self.num_bombs = NBOMBS
        self.squares_x = NSQUARES
        self.squares_y = NSQUARES
        self.resize = False
        self.flag_count = 0

    def draw(self):
        # Set the screen background color
        screen.fill(BLACK)
        IMAGE_SIZE = (40, 40)
        # Load the mine icon
        bomb_image = pygame.image.load("mine.png")
        bomb_image = pygame.transform.scale(bomb_image, IMAGE_SIZE)
        # Load the flag icon
        flag_image = pygame.image.load("flag.png")
        flag_image = pygame.transform.scale(flag_image, IMAGE_SIZE)
        # Draw the grid
        for row in range(self.squares_y):
            for column in range(self.squares_x):
                color = WHITE
                self.grid[row][column].bomb_image = bomb_image
                self.grid[row][column].flag_image = flag_image
                if self.grid[row][column].is_visible:
                    if self.grid[row][column].has_bomb:
                        # Calculate the position based on row and column indices
                        x = ((column)*(MARGIN + WIDTH)) + MARGIN
                        y = ((row)*(MARGIN + HEIGHT)) + 45
                        # Draw the bomb image at the calculated position
                        screen.blit(self.grid[row][column].bomb_image, (x, y))
                    else:
                        color = TURQUOISE
                elif self.grid[row][column].has_flag:
                    # Calculate the position based on row and column indices
                    x = ((column)*(MARGIN + WIDTH)) + MARGIN
                    y = ((row)*(MARGIN + HEIGHT)) + 45
                    # Draw the flag image at the calculated position
                    screen.blit(self.grid[row][column].flag_image, (x, y))
                if self.grid[row][column].has_bomb and self.grid[row][column].is_visible:
                    pass
                elif self.grid[row][column].has_flag:
                    pass
                else:
                    pygame.draw.rect(screen, color,
                                [(MARGIN + WIDTH) * column + MARGIN,
                                (MARGIN + HEIGHT) * row + MARGIN + MENU_SIZE,
                                WIDTH, HEIGHT])
                self.grid[row][column].show_text()
                
    # Makes all cells visible when user loses
    def game_over(self):
        for row in range(self.squares_y):
            for column in range(self.squares_x):
                if self.grid[row][column].has_bomb:
                    self.grid[row][column].is_visible = True
                self.grid[row][column].has_flag = False

    # Changes the number of bombs placed and caps it
    def change_num_bombs(self, bombs):
        self.num_bombs += bombs
        if self.num_bombs < 1:
            self.num_bombs = 1
        elif self.num_bombs > (self.squares_x * self.squares_y) // 3:
            self.num_bombs = self.squares_x * self.squares_y // 3
    
   # Place bombs on random squares
    def place_bombs(self, row, column):
        bombplaced = 0
        while bombplaced < self.num_bombs:
            x = randrange(self.squares_y)
            y = randrange(self.squares_x)
            if not self.grid[x][y].has_bomb and not (row == x and column == y):
                self.grid[x][y].has_bomb = True
                bombplaced += 1
        self.count_all_bombs()
        if self.grid[row][column].bomb_count != 0:
            self.reset_game()
            self.place_bombs(row, column)
        
    # Count all bombs next to a cell (3x3) for the entire grid
    def count_all_bombs(self):
        for row in range(self.squares_y):
            for column in range(self.squares_x):
                self.grid[row][column].count_bombs(self.squares_y, self.squares_x)
    
    # Restarts the game
    def reset_game(self):
        for row in range(self.squares_y):
            for column in range(self.squares_x):
                self.init = False
                self.grid[row][column].is_visible = False
                self.grid[row][column].has_bomb = False
                self.grid[row][column].bomb_count = 0
                self.grid[row][column].test = False
                self.grid[row][column].has_flag = False
                self.game_lost = False
                self.game_won = False
                self.flag_count = 0

    # Checks if the game has been won
    def check_victory(self):   
        count = 0
        total = self.squares_x * self.squares_y
        for row in range(self.squares_y):
            for column in range(self.squares_x):
                if self.grid[row][column].is_visible:
                    count += 1
        if ((total - count) == self.num_bombs) and not self.game_lost:
            self.game_won = True
            for row in range(self.squares_y):
                for column in range(self.squares_x):
                    if self.grid[row][column].has_bomb:
                        self.grid[row][column].has_flag = True
        
    # Counts the total number of flags placed
    def count_flags(self):
        total_flags = 0
        for row in range(self.squares_y):
            for column in range(self.squares_x):
                if self.grid[row][column].has_flag:
                    total_flags += 1
        self.flag_count = total_flags

    # Handle for grid clicks
    def click_handle(self, row, column, button):
        if button == LEFT_CLICK and self.game_won:
            pass
        elif button == LEFT_CLICK and not self.grid[row][column].has_flag: 
            if not self.game_lost:
                # Place bombs after first click so you never click a bomb first
                if not self.init:
                    self.place_bombs(row, column)
                    self.init = True
                # Set the click square to visible
                self.grid[row][column].is_visible = True
                self.grid[row][column].has_flag = False
                if self.grid[row][column].has_bomb:
                    self.game_over()
                    self.game_lost = True
                if self.grid[row][column].bomb_count == 0 and not self.grid[row][column].has_bomb:
                    self.grid[row][column].open_neighbours(self.squares_y, self.squares_x)
                self.check_victory()
            else:
                self.game_lost = True
        elif button == RIGHT_CLICK and not self.game_won:
            if not self.grid[row][column].has_flag:
                if self.flag_count < self.num_bombs and not self.grid[row][column].is_visible:
                    self.grid[row][column].has_flag = True
            else:
                self.grid[row][column].has_flag = False
            self.count_flags()

# Class Cell representing each square of the grid
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_visible = False
        self.has_bomb = False
        self.bomb_count = 0
        self.text = ""
        self.test = False
        self.has_flag = False

    # Display the number of bombs adjacent to a Cell
    def show_text(self):
        if self.is_visible:
            if self.bomb_count == 0:
                self.text = font.render("", True, BLACK)
            else:
                self.text = font.render(str(self.bomb_count), True, BLACK)
            screen.blit(self.text, (self.x * (WIDTH + MARGIN) + 17, self.y * (HEIGHT + MARGIN) + 13 + MENU_SIZE))
        
    # Counts how many bombs are next to a particular cell (3x3)
    def count_bombs(self, squaresx, squaresy):
        if not self.test:
            self.test = True
            if not self.has_bomb:
                for column in range(self.x - 1, self.x + 2):
                    for row in range(self.y - 1, self.y + 2):
                        if (row >= 0 and row < squaresx and column >= 0 and column < squaresy
                            and not (column == self.x and row == self.y)
                            and game.grid[row][column].has_bomb):
                                self.bomb_count += 1
        
    # Open all cells with zero bombs next to the clicked cell
    def open_neighbours(self, squaresx, squaresy):
        column = self.x
        row = self.y
        for row_off in range(-1, 2):
            for column_off in range(-1, 2):
                if ((row_off == 0 or column_off == 0) and row_off != column_off
                    and row + row_off >= 0 and column + column_off >= 0 and row + row_off < squaresx and column+column_off < squaresy):
                        game.grid[row + row_off][column + column_off].count_bombs(game.squares_y, game.squares_x)
                        if not game.grid[row + row_off][column + column_off].is_visible and not game.grid[row + row_off][column + column_off].has_bomb:  
                            game.grid[row + row_off][column + column_off].is_visible = True
                            game.grid[row + row_off][column + column_off].has_flag = False
                            if game.grid[row + row_off][column + column_off].bomb_count == 0: 
                                game.grid[row + row_off][column + column_off].open_neighbours(game.squares_y, game.squares_x)

# Class that represents menu
class Menu():
    def __init__(self,NSQUARES):
        self.width = pygame.display.get_surface().get_width() - 2*MARGIN
        self.btn_minus = self.Button(10, 10, 20, 20, "-", 6, -3)
        self.btn_plus = self.Button(60, 10, 20, 20, "+", 3, -4)
        if NSQUARES == 8:
            self.btn_flags = self.Button(290, 16, 10, 10, "")
        if NSQUARES == 10:
            self.btn_flags = self.Button(380, 16, 10, 10, "")
        if NSQUARES == 12:
            self.btn_flags = self.Button(470, 16, 10, 10, "")
        self.btn_flags.background = RED
        if NSQUARES == 8:
            self.label_bombs = self.Label(37, 10)
        if NSQUARES == 10 or NSQUARES == 12:
            self.label_bombs = self.Label(30, 10)
        if NSQUARES == 8:
            self.label_game_end = self.Label(120, 10)
        if NSQUARES == 10:
            self.label_game_end = self.Label(150, 10)
        if NSQUARES == 12:
            self.label_game_end = self.Label(200, 10)
        self.label_flags = self.Label(self.width - 50, 10)

    def click_handle(self, obj):
        if self.btn_minus.click_handle() and obj.init == False:
            obj.change_num_bombs(-1)
        if self.btn_plus.click_handle() and obj.init == False:
            obj.change_num_bombs(1)
        
    def draw(self, obj):
        self.width = pygame.display.get_surface().get_width() - 2*MARGIN 
        pygame.draw.rect(screen, TURQUOISE, [MARGIN, 0, self.width, MENU_SIZE])
        self.btn_minus.draw(screen)
        self.btn_plus.draw(screen)
        self.btn_flags.draw(screen)
        self.label_bombs.show(screen, game.num_bombs)
        self.label_flags.show(screen, game.flag_count)
        if obj.game_lost:
            self.label_game_end.show(screen, "Game Over")
        elif obj.game_won:
            self.label_game_end.show(screen, "You Won!")
   
    # Menu sub-class
    class Label:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.text = ""
        
        def show(self, surface, value): 
            text = str(value)
            self.text = font.render(text, True, BLACK)     
            surface.blit(self.text, (self.x, self.y))
    
    # Menu sub-class
    class Button:
        def __init__(self, x, y, width, height, text, xoff=0, yoff=0):
            self.x = x
            self.y = y
            self.height = height
            self.width = width
            self.background = WHITE
            self.text = text
            self.x_offset = xoff
            self.y_offset = yoff

        def draw(self, surface):
            pygame.draw.ellipse(surface, self.background, [self.x, self.y, self.width, self.height], 0)
            text = font.render(self.text, True, BLACK)     
            surface.blit(text, (self.x + self.x_offset, self.y + self.y_offset))
        
        def click_handle(self):
            pos = pygame.mouse.get_pos()
            if pos[0] > self.x and pos[1] > self.y and pos[0] < (self.x + self.width) and pos[1] < (self.y + self.height):
                return True
            else:
                return False

# Function that opens a window at the centre of the screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Function that allows player to choose level of difficulty
def start():
    def level_nsquares1():
        global NSQUARES
        global NBOMBS
        NSQUARES = 8
        NBOMBS = 8
        level.destroy()

    def level_nsquares2():
        global NSQUARES
        global NBOMBS
        NSQUARES = 10
        NBOMBS = 10
        level.destroy()

    def level_nsquares3():
        global NSQUARES
        global NBOMBS
        NSQUARES = 12
        NBOMBS = 12
        level.destroy()

    def on_closing():
        level.destroy()
        pygame.quit()
        sys.exit()
    
    # Create a tkinter window
    level = Tk()
    level.resizable(False, False)
    level.title("Minesweeper")
    center_window(level, 500, 500)
    # Create a canvas widget
    canvas = Canvas(level, width=500, height=500)
    canvas.pack()
    # Load the image
    image = Image.open("background1.png")
    # Resize the image to fit the canvas
    resized_image = image.resize((500, 500), Image.LANCZOS)
    # Convert the image to PhotoImage
    background_image = ImageTk.PhotoImage(resized_image)
    # Create a Label widget with the image as its background
    canvas.create_image(0, 0, anchor='nw', image=background_image)
    # Add the buttons and other widgets on top of the background image
    Label(level, text="CHOOSE YOUR LEVEL OF DIFFICULTY:", font=('Times 15 bold')).place(x=65, y=50)
    Button(level, text="EASY", command=level_nsquares1, width=15, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=170, y=120)
    Button(level, text="INTERMEDIATE", command=level_nsquares2, width=15, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=170, y=200)
    Button(level, text="DIFFICULT", command=level_nsquares3, width=15, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=170, y=280)
    level.protocol("WM_DELETE_WINDOW", on_closing)
    level.mainloop()

# Function that opens window after game is lost or won
def over(game):
    def Restart():
        global proceed
        proceed = "restart"
        over.destroy()

    def Try_Again():
        global proceed
        proceed = "try again"
        over.destroy()

    def Next_Level():
        global proceed 
        proceed = "next level"
        over.destroy()

    def Quit():
        over.destroy()
        sys.exit()
        
    def On_Closing():
        over.destroy()
        pygame.quit()
        sys.exit()
        
    if game.game_won and NSQUARES == 12:
        # Create a tkinter window
        over = Tk()
        over.resizable(False, False)
        over.title("Minesweeper")
        center_window(over, 500, 500)
        # Create a canvas widget
        canvas = Canvas(over, width=500, height=500)
        canvas.pack()
        # Load the image
        image = Image.open("background2.png")
        # Resize the image to fit the canvas
        resized_image = image.resize((500, 500), Image.LANCZOS)
        # Convert the image to PhotoImage
        background_image = ImageTk.PhotoImage(resized_image)
        # Create a Label widget with the image as its background
        canvas.create_image(0, 0, anchor='nw', image=background_image)
        Label(over, text="YOU HAVE WON THE MOST DIFFICULT LEVEL!", font=('Times 14 bold')).place(x=30, y=50)
        Label(over, text="HOW DO YOU WANT TO PROCEED?", font=('Times 14 bold')).place(x=85, y=100)
        Button(over, text="RESTART", command=Restart, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=170)
        Button(over, text="QUIT", command=Quit, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=230)
        over.protocol("WM_DELETE_WINDOW", On_Closing)
        over.mainloop()
    elif game.game_won and (NSQUARES == 8 or NSQUARES == 10):
        # Create a tkinter window
        over = Tk()
        over.resizable(False, False)
        over.geometry("500x500")
        over.title("Minesweeper")
        center_window(over, 500, 500)
        # Create a canvas widget
        canvas = Canvas(over, width=500, height=500)
        canvas.pack()
        # Load the image
        image = Image.open("background2.png")
        # Resize the image to fit the canvas
        resized_image = image.resize((500, 500), Image.LANCZOS)
        # Convert the image to PhotoImage
        background_image = ImageTk.PhotoImage(resized_image)
        # Create a Label widget with the image as its background
        canvas.create_image(0, 0, anchor='nw', image=background_image)
        Label(over, text="HOW DO YOU WANT TO PROCEED?", font=('Times 14 bold')).place(x=85, y=50)
        Button(over, text="NEXT LEVEL", command=Next_Level, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=100)
        Button(over, text="RESTART", command=Restart, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=150)
        Button(over, text="QUIT", command=Quit, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=200)
        over.protocol("WM_DELETE_WINDOW", On_Closing)
        over.mainloop()
    elif game.game_lost:
        # Create a tkinter window
        over = Tk()
        over.resizable(False, False)
        over.geometry("500x500")
        over.title("Minesweeper")
        center_window(over, 500, 500)
        # Create a canvas widget
        canvas = Canvas(over, width=500, height=500)
        canvas.pack()
        # Load the image
        image = Image.open("background2.png")
        # Resize the image to fit the canvas
        resized_image = image.resize((500, 500), Image.LANCZOS)
        # Convert the image to PhotoImage
        background_image = ImageTk.PhotoImage(resized_image)
        # Create a Label widget with the image as its background
        canvas.create_image(0, 0, anchor='nw', image=background_image)
        Label(over, text="HOW DO YOU WANT TO PROCEED?", font=('Times 14 bold')).place(x = 85, y = 30)
        Button(over, text="TRY AGAIN", command=Try_Again, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=100)
        Button(over, text="RESTART", command=Restart, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=180)
        Button(over, text="QUIT", command=Quit, width=20, fg="dark blue", font="Times 14", bd=2, bg="light blue", relief="groove").place(x=150, y=260)
        over.protocol("WM_DELETE_WINDOW", On_Closing)
        over.mainloop()
    
    

# start() function is called to start the game
start()

# Main loop
while True:
    # Pygame is initialized
    pygame.init()
    # Set the caption of the pygame window
    pygame.display.set_caption("Minesweeper")
    # Font to use in the entire game
    font = pygame.font.Font('freesansbold.ttf', 24)
    size = (NSQUARES*(WIDTH + MARGIN) + MARGIN, (NSQUARES*(HEIGHT + MARGIN) + MARGIN) + MENU_SIZE)
    screen = pygame.display.set_mode(size)
    # Create instances for Game and Menu
    game = Game(NSQUARES, NBOMBS)
    menu = Menu(NSQUARES)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            # Closes the game if user clicked the X
            if event.type == pygame.QUIT:  
                pygame.quit()
                sys.exit()
            # Mouse clicks event
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get mouse position
                position = pygame.mouse.get_pos()
                # Change the screen coordinates to grid coordinates and caps max values
                column = position[0] // (WIDTH + MARGIN)
                row = (position[1] - MENU_SIZE) // (HEIGHT + MARGIN)
                if row >= game.squares_y:
                    row=game.squares_y - 1
                if column >= game.squares_x:
                    column = game.squares_x - 1
                if row >= 0:
                    game.click_handle(row, column, event.button)
                else:
                    menu.click_handle(game)
                # Deal with game loss or win
                if game.game_lost or game.game_won:
                    click_count += 1
                    game_over = True
            
        game.draw()
        menu.draw(game)
        clock.tick(60)
        # Update the screen
        pygame.display.flip()
        # Break from loop if game is over and user clicks on screen
        if game_over and click_count == 2:
            pygame.quit()
            break        
    # Function that opens window after game is done
    over(game)
    if proceed == "next level":
        game_over = False
        click_count = 0
        NSQUARES += 2
        NBOMBS += 2
    if proceed == "restart":
        game_over = False
        click_count = 0
        start()
    if proceed == "try again":
        game_over = False
        click_count = 0
