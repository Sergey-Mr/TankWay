# 840x840 for game window
# 1920x1080 for menu window 
# Serhii Tupikin 24.11.2023

from tkinter  import Tk, IntVar, Label, PhotoImage, Radiobutton, Button, Canvas, Entry, Frame, StringVar, Toplevel
from random import randint as rand, shuffle
from PIL import ImageTk, Image
from time import sleep
import random
import time

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.shape = item

    #def get_position(self):
    #    return self.canvas.coords(self.shape)

    def move(self, x, y):
        self.canvas.move(self.shape, x, y)

    def delete(self):
        self.canvas.delete(self.shape)

    def get_position(self):
        '''The top-left and bottom-right corners'''
        if self.canvas.find_withtag(self.shape):  # Check if the shape exists on the canvas
            x1, y1 = self.canvas.coords(self.shape)
            x2, y2 = x1 + self.width, y1 + self.height
            return [x1, y1, x2, y2]
        else:
            return None


class Tank(GameObject):
    def __init__(self, canvas, x, y):
        "Tank`s parameteres"
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80


class TankEnemy(Tank):
    def __init__(self, canvas, x, y, main_tank, is_moving, is_shooting):
        '''Enemy tank`s parameters'''
        global bullets_enemy
        super().__init__(canvas, x, y)
        self.height = y
        self.is_moving = is_moving
        self.is_shooting = is_shooting

        # Load the image
        # The image is take from the web-site https://opengameart.org/content/tank-pack-bleeds-game-art
        # License: CC BY 3.0 DEED
        # Creator: Bleed
        img = Image.open("img/main_character/KV-2_preview.png") 
        self.tank_image = ImageTk.PhotoImage(img)
        self.width, self.height = img.size

        self.shot_length = 550
        self.main_tank = main_tank
        self.speed = 5

        # Set the image as the tank
        self.shape = canvas.create_image(x, y, image=self.tank_image, anchor='nw')
    
        self.bullets_enemy = []

        self.shoot()  # Start shooting
        self.move_down()  # Start moving down


    def shoot(self):
        '''Shooting logic of the enemy tank'''
        global game_flag
        if game_flag == True:
            if self.get_position() is not None:
                if self.is_shooting:
                    self.x = self.get_position()[0] + (self.width)/2
                    self.y = self.get_position()[1] 
    
                    bullet = Bullet_enemy(self.canvas, self.x, self.y+self.height)
    
                    # allow the enemy tank to shoot only once the previous bullet disappears
                    if len(self.bullets_enemy) == 0:
                        self.bullets_enemy.append(bullet)
                        self.move_bullet(bullet)  # Start moving the bullet


    def move_bullet(self, bullet):
        '''Move the bullet and schedule the next move'''
        global game_flag
        if game_flag == True:
            position = bullet.get_position()
            if position is not None and bullet.get_position()[1] < (self.y + self.shot_length):
                bullet.movement_enemy(self.canvas)
                self.canvas.after(50, lambda: self.move_bullet(bullet))  # Call function again after 50 ms
            else:
                bullet.delete()
                if bullet in self.bullets_enemy:
                    self.bullets_enemy.remove(bullet)

                self.shoot()  # schedule the next shooting


    def move_down(self):
        '''Move the tank down'''
        global game_flag
        if game_flag == True:
            if self.y + self.speed < 840:
                self.y += self.speed
                self.movement(self.y, 840)


    def movement(self, cur_loc, fut_loc):
        '''Recursive movement function'''
        global game_flag, enemy_movement_id
        if game_flag == True:
            if self.is_moving and cur_loc <= fut_loc:
                self.canvas.move(self.shape, 0, self.speed)
                enemy_movement_id = self.canvas.after(55, lambda: self.movement(cur_loc+self.speed, fut_loc))

            # Remove not destroyed tanks after passing the window boarder
            if self.get_position() is not None:
                x1, y1, x2, y2 = self.get_position()
                if y2 > 1050:  # Check if the tank has crossed the border
                    if self in enemy_tanks:
                        self.canvas.delete(self.shape)  # Delete the tank
                        enemy_tanks.remove(self)  # Remove the tank from the list

 
    def get_position(self):
        '''The top-left and bottom-right corners'''
        coords = self.canvas.coords(self.shape)
        if coords:
            x1, y1 = self.canvas.coords(self.shape)
            x2, y2 = x1 + self.width, y1 + self.height
            return [x1, y1, x2, y2]
        else:
            return None
    

    def stop_movement(self):
        '''Stop the tank'''
        self.is_moving = False
        print ('Movement stopped')


    def stop_shooting(self):
        '''Stop shooting'''
        self.is_shooting = False
        enemy_tanks.remove(self)
        print ('Shooting stopped')


class TankMain(Tank):
    def __init__(self, canvas, x, y):
        '''Main tank`s parameters'''
        super().__init__(canvas, x, y)
        # Upload the image
        # The image is taken from https://opengameart.org/content/tank-pack-bleeds-game-art
        # License: CC BY 3.0 DEED
        # Creator: Bleed
        img = Image.open("img/main_character/M-6_preview.png")
        img = img.rotate(180)
        self.tank_image = ImageTk.PhotoImage(img)
        self.shot_length = 400

        # Set the image as the tank
        self.shape = canvas.create_image(x, y, image=self.tank_image, anchor='nw')

        # Set the health paratemeters and icons
        self.health = [1, 1, 1]  # defines 3 hearts for player
        self.heart_images = []
        self.mainchar_hit = False
        self.kill_counter = 0
        self.create_health()


    def update_health(self):
        '''Reduce the health of the main tank when hit'''
        if self.mainchar_hit:
            if 0 in self.health:
                index = self.health.index(0)
                self.health.pop(index-1)
                self.health.append(0)
                print(self.health)
                self.create_health()
            else:
                self.health.pop()
                self.health.append(0)
                print(self.health)
                self.create_health()
        
        if 1 not in self.health:
            print('Done')
            game_over()  # stop the game if the no more health left


    def add_health(self):
        '''Add health to the main tank when 5 enemies are killed'''
        if 0 in self.health:
            self.health.reverse()
            index = self.health.index(0)
            self.health.pop(index)
            self.health.append(1)
            self.health.reverse()
            self.create_health()
        else:
            pass


    def create_health(self):
        # Delete the old heart images from the canvas
        for heart_object in self.heart_images:
            self.canvas.delete(heart_object)
        self.heart_images.clear()

        # Update the heart images
        for i in range (0, len(self.health)):
            if self.health[i] == 1:
                # Load the heart image
                # The image is taken from https://opengameart.org/content/health
                # License is CC BY 3.0 DEED
                # Creator: knik1985
                heart = PhotoImage(file="img/heart.png")
                heart = heart.subsample(10, 10)  # resize the heart
                self.heart_images.append(heart)
                canvas.create_image(650 + i*60, 50, image=heart, anchor='nw')

            elif self.health[i] == 0: # change the icon to empty heart if the health[i] is 0
                # Load the heart image
                # The image is taken from https://opengameart.org/content/health
                # License is CC BY 3.0 DEED
                # Creator: knik1985
                heart = PhotoImage(file="img/empty_health.png")
                heart = heart.subsample(10, 10)
                self.heart_images.append(heart)
                canvas.create_image(650 + i*60, 50, image=heart, anchor='nw')

    def shoot(self, event):
        '''Shooting logic of the main tank'''
        global main_shooting, main_shoot_allow
        if main_shoot_allow == True:
            main_shooting = False
            self.x = self.get_position()[0] + (self.width)/2
            self.y = self.get_position()[1] 
    
            bullet = Bullet(self.canvas, self.x+15, self.y)
    
            # allow the user to shoot only once
            if len(bullets) == 0:
                main_shooting = True
                bullets.append(bullet)
                if kill_counter > 0 and kill_counter % 5 == 0:
                    self.add_health()
    
                self.move_bullet(bullet)  # Start moving the bullet
    
            else:  # show the message if the user tries to shoot more than once
                text = self.canvas.create_text(440, 325, text="Reloading, capitan!", fill="red", font=('Helvetica 30 bold'))
                self.canvas.pack()
    
                self.canvas.after(2000, lambda: self.canvas.delete(text))  # delete the text after 2 seconds


    def move_bullet(self, bullet):
        '''Move the bullet and make a recursive call'''
        position = bullet.get_position()
        if position is not None and bullet.get_position()[1] > (self.y - self.shot_length):
            bullet.movement(self.canvas)

            self.canvas.after(50, lambda: self.move_bullet(bullet))  # Call this function again after 50 ms
        else:
            bullet.delete()
            bullets.remove(bullet)


    def move_left(self, event):
        """Movement of the tank to the left"""
        global game_flag
        if game_flag == True:
            left_limit = 0
            x = self.get_position()[0]
            y = self.get_position()[1]

            if x > left_limit+2*130:
                if x != x-130 and len(movements) == 0:
                    movements.append(1)
                    self.move_left_move(x, x-130, event)  # start moving the tank

            else:  # show a message if the user tries to leave the road
                text = self.canvas.create_text(440, 325, text="No retriet!", fill="red", font=('Helvetica 30 bold'))
                self.canvas.pack()

                self.canvas.after(1000, lambda: self.canvas.delete(text))  # dele the text

    
    def move_left_move(self, cur_loc, fut_loc, event):
        '''Move the tank and schedule the next move'''
        if cur_loc > fut_loc:
            self.canvas.move(self.shape, -10, 0)
            self.canvas.after(35, lambda: self.move_left_move(cur_loc-10, fut_loc, event))

        if cur_loc == fut_loc:
            movements.clear()


    def move_right(self, event):
        """Movement of the tank to the right"""
        global game_flag
        if game_flag == True:
            right_limit = self.canvas.winfo_width() - self.width
            x = self.get_position()[0]
            y = self.get_position()[1]

            if x < right_limit-2*130:
                if x != x+130 and len(movements) == 0:
                    movements.append(1)
                    self.move_right_move(x, x+130, event)  # start moving the tank

            else:  # show a message if the user tries to leave the road
                text = self.canvas.create_text(440, 325, text="No retriet!", fill="red", font=('Helvetica 30 bold'))
                self.canvas.pack()

                self.canvas.after(1000, lambda: self.canvas.delete(text))  # delete the text 

    
    def move_right_move(self, cur_loc, fut_loc, event):
        '''Move the tank and schedule the next move'''
        if cur_loc < fut_loc:
            self.canvas.move(self.shape, 10, 0)
            self.canvas.after(35, lambda: self.move_right_move(cur_loc+10, fut_loc, event))

        if cur_loc == fut_loc:
            movements.clear()


    def check_enemies(self):
        '''Check if there are any enemies on the road'''
        if not enemy_tanks:
            generate_enemy()

        print (enemy_tanks)
        delay = 5000
        canvas.after(delay, lambda:self.check_enemies())


class Bullet(GameObject):
    def __init__(self, canvas, x, y):
        '''Main character`s bullets` parameters'''
        self.canvas = canvas
        self.x = x 
        self.y = y
        self.width = 10
        self.height = 10

        # Load the sprite images
        # Images were downloaded from https://craftpix.net/product/2d-top-down-tank-game-assets/
        # License: https://craftpix.net/file-licenses/
        self.sprites = [ImageTk.PhotoImage(Image.open(f"img/bullet/Sprite_Effects_Exhaust_01_00{i}.png")) for i in range(0, 18)] 
        self.current_sprite = 0

        # Set the initial image
        self.shape = canvas.create_image(x, y, image=self.sprites[self.current_sprite])

        self.is_exploding = False

    def movement(self, canvas):
        """Sprite changing logic"""
        global game_flag
        if game_flag == True:
            self.canvas.move(self.shape, 0, -20)

            for tank in enemy_tanks.copy():
                if main_shooting == True:
                    self.check_collision(tank)

            # Update the sprite image
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)  # use modulus to reset the index to 0 when maximum
            self.canvas.itemconfig(self.shape, image=self.sprites[self.current_sprite])


    def check_collision(self, tank):
        '''Check if a bullet has hit a tank'''
        global kill_counter

        # Get the coordinates of the bullet and the tank
        bullet_coords = self.get_position()
        tank_coords = tank.get_position()

        #Check if the coordinates overlap
        if bullet_coords is not None:
            if bullet_coords and tank_coords:
                if (bullet_coords[0] < tank_coords[2] and bullet_coords[2] > tank_coords[0] and
                    bullet_coords[1] < tank_coords[3] and bullet_coords[3] > tank_coords[1]):

                    # Calculate the center of the tank
                    center_x = (tank_coords[0] + tank_coords[2]) / 2
                    center_y = (tank_coords[1] + tank_coords[3]) / 2

                    # Create an explosion at the center of the tank
                    if not self.is_exploding:
                        kill_counter +=1  # add kill to the counter
            
                        update_kills()

                        self.create_explosion(center_x, center_y)

                    tank.stop_shooting()


    def get_position(self):
        '''The top-left and bottom-right corners'''
        if self.canvas.coords(self.shape):
            x1, y1 = self.canvas.coords(self.shape)
            x2, y2 = x1 + self.width, y1 + self.height
            return [x1, y1, x2, y2]
        else:
            return None

    
    def create_explosion(self, x, y):
        '''Create an explosion at the given coordinates'''
        # Load the explosion images
        # Images were downloaded from https://craftpix.net/product/2d-top-down-tank-game-assets/
        # License: https://craftpix.net/file-licenses/
        self.explosion_images = [ImageTk.PhotoImage(Image.open(f"img/explosion/Explosion_{i}.png")) for i in range(1, 6)]

        # Create the explosion image object
        self.explosion_id = self.canvas.create_image(x, y, image=self.explosion_images[0])

        # Start the animation
        self.is_exploding = True
        self.animate_explosion(0)


    def animate_explosion(self, i):
        '''Animate the explosion'''
        if i < len(self.explosion_images):
            # Update the image
            self.canvas.itemconfig(self.explosion_id, image=self.explosion_images[i])

            # Schedule the next frame
            self.canvas.after(65, lambda: self.animate_explosion(i + 1))

        else:
            # Delete the explosion image object after the animation is complete
            self.canvas.delete(self.explosion_id)
            self.delete()


class Bullet_enemy(Bullet):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y)
        '''Enemies` bullets parameters'''
        # Load the sprite images
        # Images were downloaded from https://craftpix.net/product/2d-top-down-tank-game-assets/
        # License: https://craftpix.net/file-licenses/
        self.sprites = [ImageTk.PhotoImage(Image.open(f"img/bullet/Sprite_Effects_Exhaust_01_00{i}.png").rotate(180)) for i in range(0, 18)] 
        self.current_sprite = 0

        # Set the initial image
        self.shape = canvas.create_image(x, y, image=self.sprites[self.current_sprite])

    def movement_enemy(self, canvas):
        """Sprite changing logic and movement of the enemy bullet"""
        global game_flag
        if game_flag == True:
            self.canvas.move(self.shape, 0, 20)

            self.check_collision(main_tank)

            # Update the sprite image
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)  # use modulus to reset the index to 0 when maximum
            self.canvas.itemconfig(self.shape, image=self.sprites[self.current_sprite])


    def check_collision(self, tank):
        '''Check if a bullet has hit a tank'''
        global kill_counter
        # Get the coordinates of the bullet and the tank
        bullet_coords = self.get_position()
        tank_coords = tank.get_position()
        #print(bullet_coords, tank_coords)
        
        #Check if the coordinates overlap
        if bullet_coords is not None:
            if bullet_coords and tank_coords:
                if (bullet_coords[0] < tank_coords[2] and bullet_coords[2] > tank_coords[0] and
                    bullet_coords[1] < tank_coords[3] and bullet_coords[3] > tank_coords[1]):

                    # Calculate the center of the tank
                    center_x = (tank_coords[0] + tank_coords[2]) / 2
                    center_y = (tank_coords[1] + tank_coords[3]) / 2

                    # Create an explosion at the center of the tank
                    if not self.is_exploding:
                        tank.mainchar_hit = True
                        tank.update_health()

                        self.create_explosion(center_x, center_y)

                    self.create_explosion(center_x, center_y)


    def get_position(self):
        '''The top-left and bottom-right corners'''
        if self.canvas.coords(self.shape):
            x1, y1 = self.canvas.coords(self.shape)
            x2, y2 = x1 + self.width, y1 + self.height
            return [x1, y1, x2, y2]
        else:
            return None

    
    def create_explosion(self, x, y):
        '''Create an explosion at the given coordinates'''
        global game_flag
        if game_flag == True:
            # Load the explosion images
            # Images were downloaded from https://craftpix.net/product/2d-top-down-tank-game-assets/
            # License: https://craftpix.net/file-licenses/
            self.explosion_images = [ImageTk.PhotoImage(Image.open(f"img/explosion/Explosion_{i}.png")) for i in range(1, 6)]

            # Create the explosion image object
            self.explosion_id = self.canvas.create_image(x, y, image=self.explosion_images[0])

            # Start the animation
            self.is_exploding = True
            self.animate_explosion(0)


    def animate_explosion(self, i):
        '''Animate the explosion'''
        if i < len(self.explosion_images):
            # Update the image
            self.canvas.itemconfig(self.explosion_id, image=self.explosion_images[i])

            # Schedule the next frame
            self.canvas.after(65, lambda: self.animate_explosion(i + 1))

        else:
            # Delete the explosion image object after the animation is complete
            mainchar_hit = False
            self.canvas.delete(self.explosion_id)
            self.delete()


def start_game(window, kills=0, timer=0):
    global keys, pause_button, save_button, exit_button, new_window, game_flag, canvas, bg_image, bg, enemy_tanks, clock, timer_seconds, main_tank, enemy_ids, is_moving, is_shooting, mainchar_hit, kill_counter, kill_label, timer_flag, enemy_movement, enemy_shooting, main_shoot_allow, road_movement, generation_falg
    window.destroy()

    # Create a new window
    new_window = Tk() 
    new_window.title("Tank Game")
    new_window.geometry("840x900")
    new_window.configure(bg='black')
    new_window.update()
    game_flag = True
    
    canvas = Canvas(new_window, width=840, height=840)
    
    # Load the background image
    # Image is download from https://opengameart.org/content/road-for-2d-games
    # Licese: CC-BY 4.0
    # Creator: the_black_box
    img = Image.open("img/background-road.png")    
    bg_image = ImageTk.PhotoImage(img)

    # Get the height of the canvas and the image
    canvas_height = canvas.winfo_height()
    image_height = bg_image.height()

    # Set the image as the background
    bg = canvas.create_image(0, canvas_height, image=bg_image, anchor='w')

    # Create a label for the timer and enemy counter
    clock = canvas.create_text(80, 30, text="Time:", fill="white", font=('Helvetica 20 bold'))
    kill_label = canvas.create_text(80, 80, text="Kills:", fill="red", font=('Helvetica 20 bold'))

    canvas.pack() 

    road_movement = True 
    move_background() 

    timer_seconds = timer
    timer_flag = True

    # Create a Tank object
    main_shoot_allow = True
    main_tank = TankMain(canvas, 430, 530)

    enemy_tanks = []
    enemy_ids = []
    kill_counter = kills

    # Create enemy tanks
    enemy_movement = True
    enemy_shooting = True
    generation_falg = True
    generate_enemy()
    
    # Bind keys for movement
    canvas.bind(keys[0], lambda event: main_tank.move_left(event))
    canvas.bind(keys[1], lambda event: main_tank.move_right(event))

    # Define shooting logic 
    canvas.bind(keys[2], lambda event: main_tank.shoot(event))

    # Bind boss key
    canvas.bind('<Escape>', lambda event: boss_key())

    # Bind the 't' key to open the terminal and enter the cheat_code function
    canvas.bind('t', lambda event: cheat_code())

    # Create a pause button
    pause_button = Button(new_window, text="Pause", command= lambda: pause_game(new_window), font=("Arial Bold", 25), bg="#32a852")
    pause_button.place(relx=0.5, y=870, anchor='center')

    save_button = Button(new_window, text="Save", command=save_game, font=("Arial Bold", 25), bg="#32a852")
    exit_button = Button(new_window, text="Exit", command= lambda: exit(new_window), font=("Arial Bold", 25), bg="red")

    canvas.focus_set()  # Set keyboard focus to the canvas
    
    update_timer()
    update_kills()


def cheat_code():
    '''Define cheat code'''
    global game_flag
    if game_flag == True:
        game_flag = False

    print('Terminal opened')
    cheat_window = Toplevel()
    cheat_window.title("Terminal")
    cheat_window.geometry("500x200")

    entry = Entry(cheat_window, font=("Arial Bold", 25))
    entry.insert(0, "Enter the cheat code")
    entry.bind('<FocusIn>', lambda event: clear_entry(event, entry))

    enter = Button(cheat_window, text='Run', font=("Arial Bold", 25), bg='red', command=lambda: run_cheat(cheat_window, entry.get()))

    entry.place(relx=0.5, rely=0.4, anchor='center')
    enter.place(relx=0.5, rely=0.6, anchor='center')

    enter.pack()
    entry.pack()


def run_cheat(cheat_window, code):
    '''Define cheet codes'''
    if code == 'shoot_long':
        main_tank.shot_length = 1000
        print('Shoot long')
        label = Label(cheat_window, text='Shot lenght increased', font=("Arial Bold", 15), bg='green')
        label.place(relx=0.5, y=170, anchor='center')

    if code == 'health-5':
        main_tank.health = [1 for x in range(5)]
        main_tank.create_health()
        print('Health 5')

        label = Label(cheat_window, text='Health=5', font=("Arial Bold", 15), bg='green')
        label.place(relx=0.5, y = 170, anchor='center')


def pause_game(new_window):
    global game_flag, timer_flag, main_shoot_allow, enemy_tanks, bullets, save_button, exit_button

    game_flag = not game_flag
    
    save_button.place(relx=0.2, y=870, anchor= 'center')
    
    exit_button.place(relx=0.8, y=870, anchor= 'center')

    if game_flag == False:
        timer_flag = False
        main_shoot_allow = False

    else:
        timer_flag = True
        update_timer()
        main_shoot_allow = True

        # Hide the buttons
        save_button.place_forget()
        exit_button.place_forget()

        move_background()
        for enemy in enemy_tanks:
            enemy.shoot()  # Start shooting again
            enemy.move_down()  # Start moving again

    print('Paused')


def exit(window):
    configure_window(window)


def save_game():
    '''Save the game configurations'''
    global canvas, user

    # Update the saving database
    with open('savings.txt', 'r') as f:
        index = None
        lines = f.readlines()
        print('Saving')
        for i, line in enumerate(lines):
            if user[0] in line:
                index = i
                print('True, user has saved', index)

        user[1] = kill_counter
        user[2] = timer_seconds

        if index is not None:
            lines[index] = user[0] + '-' + str(user[1]) + '-' + str(user[2]) + '\n'
            print(lines)

        else:
            lines.append(user[0] + '-' + str(user[1]) + '-' + str(user[2]) + '\n')
        
        with open('savings.txt', 'w') as f:
            lines = ''.join(lines)
            f.write(lines)


    # Update the login database
    with open('database.txt', 'r') as f:
        index = 0
        lines = f.readlines()
        for line in lines:
            if user[0] in line:
                user[1] = kill_counter
                user[2] = timer_seconds
                index = lines.index(line)
                print(index)
                #print(lines)
    
        lines[index] = user[0] + '-' + str(user[1]) + '-' + str(user[2]) + '\n'
        print(lines)
        f.close()
                
        # Write the updated data to the file  
        with open('database.txt', 'w') as f:
            lines = ''.join(lines)
            f.write(lines)
            f.close()

        # Show the game over message
        text = canvas.create_text(440, 325, text="Game saved successfully", fill="green", font=('Helvetica 30 bold'))
        canvas.pack()

        # Schedule the text to be deleted after 1 second (1000 milliseconds)
        canvas.after(1000, lambda: canvas.delete(text))
    

def update_timer():
    '''Update the timer`s value'''
    global timer_seconds, timer_flag
    if timer_flag == True:
        # Convert the time to minutes and seconds
        minutes = timer_seconds // 60
        seconds = timer_seconds % 60

        # Update the timer label
        canvas.itemconfig(clock, text=f"Time: {minutes}:{seconds:02}")

        # Increment the timer
        timer_seconds += 1

        # Schedule the next update after 1000 ms (1 second)
        canvas.after(1000, lambda: update_timer())


def update_kills():
    '''Update the timer`s value'''
    global kill_counter, kill_label

    # Update the timer label
    canvas.itemconfig(kill_label, text=f"Kills: {kill_counter}")



def generate_enemy():
    '''Generate enemy tanks as time goes'''
    global game_flag
    if game_flag == True:
        if len(enemy_tanks) == 0:
            limit = 3  # maximum amount of tanks on the road
            possible_x = [157, 287, 417, 546]

            if timer_seconds < 60: # enemy generation rules for the 1st minute of the game
                amount = random.randint(1, limit-2)
                random.shuffle(possible_x)  # dont let enemies spaw on the same road line

                for i in range(0, amount):
                    index = list(x for x in range(0,3))  # create the list of avaliable indexes

                    tank_enemy = TankEnemy(canvas, possible_x[index[i]], -250, main_tank, True, True)
                    index.remove(i)
                    enemy_tanks.append(tank_enemy)

            elif 60 < timer_seconds < 120: # 2nd minute
                amount = random.randint(1, limit-1)
                random.shuffle(possible_x)

                for i in range(0, amount):
                    index = list(x for x in range(0,3))  # create the list of avaliable indexes

                    tank_enemy = TankEnemy(canvas, possible_x[index[i]], -250, main_tank, True, True)
                    index.remove(i)
                    enemy_tanks.append(tank_enemy)

            else: # 3d minute
                amount = random.randint(2, limit)
                random.shuffle(possible_x)

                for i in range(0, amount):
                    index = list(x for x in range(0,3))  # create the list of avaliable indexes

                    tank_enemy = TankEnemy(canvas, possible_x[index[i]], -250, main_tank, True, True)
                    index.remove(i)
                    enemy_tanks.append(tank_enemy)


            main_tank.check_enemies()


def game_over():
    '''Game over settings'''
    global pause_button, saved, timer_seconds, game_flag, kill_counter, user, timer_flag, main_shoot_allow,  enemy_movement, enemy_shooting, road_movement

    pause_button.place_forget()
    # Update the database
    with open('database.txt', 'r') as f:
        index = 0
        lines = f.readlines()
        for line in lines:
            if user[0] in line:
                user[1] = kill_counter
                user[2] = timer_seconds
                index = lines.index(line)
                print(index)
    
        lines[index] = user[0] + '-' + str(user[1]) + '-' + str(user[2]) + '\n'
        print(lines)
                

        with open('database.txt', 'w') as f:
            lines = ''.join(lines)
            f.write(lines)

            f.close()

        f.close()

    # Remove the user from the saving database
    with open('savings.txt', 'r') as f:
        index = 0
        lines = f.readlines()
        print('Saving')
        for line in lines:
            if user[0] in line:
                index = lines.index(line)
                lines.remove(line)
                with open('savings.txt', 'w') as f:
                    lines = ''.join(lines)
                    f.write(lines)
                
        f.close()

    saved = False
    # Show the game over message
    canvas.create_text(440, 325, text="Game Over!", fill="red", font=('Helvetica 30 bold'))
    
    game_flag = False  # stop the game
    timer_flag = False  # stop the timer


    # Create button in the middle of the screen to go back
    go_back = Button(new_window, text='Go back', font=("Arial Bold", 30), bg="#32a852", command=lambda: configure_window_after())
    go_back.place(relx=0.5, rely=0.5, anchor='center')


def move_background():
    '''Define the movement of background'''
    global game_flag
    if game_flag == True:

        x, y = canvas.coords(bg)  # Get the current position of the background
  
        canvas.move(bg, 0, 3)  # Move the background

        if y > canvas.winfo_height()/2:  # If the background has moved off the screen, move it back
            canvas.move(bg, 0, ((-canvas.winfo_height()/2)+210.5))
  
        canvas.after(50, lambda: move_background())  # Schedule the next move


def settings_func(window):
    '''Settings window configuration'''
    global bg_image, sprites, left_key, right_key, shooting_key, left_key_label, right_key_label, shooting_key_label, keys
    update_window(window)
    
    window.configure(bg='black')
    # Create a canvas with a black background
    canvas = Canvas(window, width=800, height=1080, bg='black')
    welcome = Label(window, text="Bind your keys", font=("Arial Bold", 30), fg="red", bg = 'black')
    welcome.place(relx=0.5, rely=0.1, anchor='center')

    # Create labels to display the keys
    left_key_label = Label(window, text="Move left: " + keys[0], font=("Arial Bold", 30), bg="green", fg="white", borderwidth=2, relief="solid")
    left_key_label.place(relx=0.5, rely=0.3, anchor='center')

    right_key_label = Label(window, text="Move right: " + keys[1], font=("Arial Bold", 30), bg="green", fg="white", borderwidth=2, relief="solid")
    right_key_label.place(relx=0.5, rely=0.5, anchor='center')

    shooting_key_label = Label(window, text="Shoot: " + keys[2], font=("Arial Bold", 30), bg="green", fg="white", borderwidth=2, relief="solid")
    shooting_key_label.place(relx=0.5, rely=0.7, anchor='center')

    # Variable to keep track of the currently selected button
    selected_button = StringVar()

    # Update selected_button when a button is clicked
    left_key_label.bind("<Button-1>", lambda event: selected_button.set('left'))
    right_key_label.bind("<Button-1>", lambda event: selected_button.set('right'))
    shooting_key_label.bind("<Button-1>", lambda event: selected_button.set('shoot'))

    def key_press(event):
        '''Update the selected key when a key is pressed'''
        key = event.char
        if selected_button.get() == 'left':
            left_key = key
            if left_key == ' ':
                left_key = '<space>'

            left_key_label.config(text="Move left: " + left_key)
            keys[0] = left_key
        elif selected_button.get() == 'right':
            right_key = key
            if right_key == ' ':
                right_key = '<space>'

            right_key_label.config(text="Move right: " + right_key)
            keys[1] = right_key
        elif selected_button.get() == 'shoot':
            shooting_key = key
            if shooting_key == ' ':
                shooting_key = '<space>'

            shooting_key_label.config(text="Shoot: " + shooting_key)
            keys[2] = shooting_key

    # Bind the key press event to the key_press function
    window.bind("<Key>", key_press)

    go_back = Button(window, text='Go back', font=("Arial Bold", 30), bg="#32a852", command=lambda: configure_window(window))
    #canvas.pack()
    go_back.place(relx=0.1, rely=0.1, anchor='center')

    canvas.pack()


def leader_board(window):
    '''Leader board window settings'''
    global bg_image, sprites
    update_window(window)
    # Create new widgets
    
    window.configure(bg='black')

    # Create a canvas with a black background
    canvas = Canvas(window, width=800, height=1080, bg='black')
    go_back = Button(window, text='Go back', font=("Arial Bold", 30), bg="#32a852", command=lambda: configure_window(window))
    canvas.pack()
    go_back.place(relx=0.1, rely=0.1, anchor='center')

    with open('database.txt', 'r') as f:
        # sort the elements in the database
        data = f.readlines()
        data = [line for line in data if '-' in line]
        data.remove(data[0])
        data.sort(key=lambda x: int(x.split('-')[1]), reverse=True)
        print(data)

    index = canvas.create_text(150, 50, text="Place", fill="White", font=('Helvetica 30 bold'))
    name = canvas.create_text(350, 50, text="Name", fill="White", font=('Helvetica 30 bold'))
    kills = canvas.create_text(550, 50, text="Kills", fill="White", font=('Helvetica 30 bold'))
    time = canvas.create_text(700, 50, text="Time", fill="White", font=('Helvetica 30 bold'))
        
    # Display the data
    for i, line in enumerate(data[:10]):  # Top 10 users
        name, kills, time = line.split('-')
        y = 150 + i * 90  # Vertical position of the labels

        # Create labels
        i +=1 
        time = time.replace('\n', '')
        if i == 1:
            canvas.create_rectangle(0, y-60, 800, y+50, fill='red')

        # Convert the time to minutes and seconds
        minutes = int(time) // 60
        seconds = int(time) % 60

        index = canvas.create_text(150, y, text=f"{i}.", fill="White", font=('Helvetica 30 bold'))
        name = canvas.create_text(350, y, text=f"{name}", fill="White", font=('Helvetica 30 bold'))
        kills = canvas.create_text(550, y, text=f"{kills}", fill="White", font=('Helvetica 30 bold'))
        time = canvas.create_text(700, y, text=f"{minutes}:{seconds:02}", fill="White", font=('Helvetica 30 bold'))


    canvas.create_line(0, 90, 800, 90, fill='white')
    

def clear_entry(event, entry):
    '''Deletes the default text in the entry box'''
    entry.delete(0, 'end')


def boss_key():
    '''Define boss key'''
    global game_flag
    if game_flag == True:
        game_flag = False

    print('Boss key pressed')
    image_window = Tk()
    image_window.title("Excel")
    image_window.geometry("1920x1080")
    
    # Load the image
    # This is own image and was screenshoted from the LibreOffice Calc
    img_pictre = Image.open("img/boss_key.png")
    global bg_picture
    bg_picture = ImageTk.PhotoImage(img_pictre)

    image_window.mainloop()


def configure_window(window):
    '''Menu window settings'''
    window.title("Tank Game")
    window.geometry("1920x1080")
    
    # Load the image
    # The image is downloaded from https://www.vecteezy.com/vector-art/10850377-soldier-in-war-scene
    # License: Free License
    # Creator: Andres Ramos
    img = Image.open("img/background-menu.jpg")
    global bg_image
    bg_image = ImageTk.PhotoImage(img)

    # Create a label with the image
    bg_label = Label(window, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    if user == []:
        login()
    
    else:
        menu(window)
 

def configure_window_after():
    '''Change the windows'''
    global window_later
    new_window.destroy()
    window_later = Tk()
    '''Menu window settings'''
    window_later.title("Tank Game")
    window_later.geometry("1920x1080")
    
    # Load the image
    # The image is downloaded from https://www.vecteezy.com/vector-art/10850377-soldier-in-war-scene
    # License: Free License
    # Creator: Andres Ramos
    img = Image.open("img/background-menu.jpg")
    global bg_image
    bg_image = ImageTk.PhotoImage(img)

    # Create a label with the image
    bg_label = Label(window_later, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    menu(window_later)


def login():
    '''Login function''' 
    global btn

    entry1 = Entry(window, font=("Arial Bold", 25))
    entry1.insert(0, "Enter your name")
    entry1.bind('<FocusIn>', lambda event: clear_entry(event, entry1))

    #x1 = entry1.get()
    login_b = Button(text='Login', font=("Arial Bold", 30), bg='green', command=lambda: verify(entry1.get()))

    entry1.place(relx=0.5, rely=0.5, anchor='center')
    login_b.place(relx=0.5, rely=0.6, anchor='center')


def verify(name):
    '''Verification of the user name'''
    global user
    found = False
    with open ('database.txt', 'r') as f:
        lines = []
        for line in f.readlines():
            #print(line)
            lines.append(line)

        for line in lines:
            if name in line:
                found = True
                user = line.split('-')


        if found == False:
            #append the user
            with open('database.txt', 'a') as f:  
                f.write('\n')
                line = name + '-0-0'
                f.write(line)
                user = line.split('-')

                f.close()
        f.close()
                
    user[2] = user[2].replace('\n', '')
    menu(window)


def menu(window):
    '''Menu window settings'''
    global kill_counter, timer_seconds, saved, user
    # if verification is passed: open menu
    print('Entrace', user)

    with open ('savings.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if user[0] in line:
                line = line.replace('\n', '')
                line = line.split('-')
                saved = True
                user = line

    print(user, saved)

    if saved == True:
        continue_game = Button(window, text="Continue", font=("Arial Bold", 50), bg="#32a852", command=lambda: start_game(window, kills=int(user[1]), timer=int(user[2])))
        continue_game.place(relx=0.5, rely=0.3, anchor='center')
    

    start = Button(window, text="Start New", font=("Arial Bold", 50), bg="#32a852", command=lambda: start_game(window))
    leaders = Button(window, text="Leader board", font=("Arial Bold", 50), bg="#32a852", command=lambda: leader_board(window))
    settings = Button(window, text="Settings", font=("Arial Bold", 50), bg="#32a852", command=lambda: settings_func(window))
    quit = Button(window, text="Quit", font=("Arial Bold", 50), bg="#c20619", command=lambda: window.destroy())

    start.place(relx=0.5, rely=0.4, anchor='center')  
    leaders.place(relx=0.5, rely=0.5, anchor='center')
    settings.place(relx=0.5, rely=0.6, anchor='center')
    quit.place(relx=0.5, rely=0.7, anchor='center') 


def update_window(window):
    '''Delete old widgets'''
    for widget in window.winfo_children():
        widget.destroy()


window = Tk()
bullets = []
movements = []  # containts 1 if the movement is in the process
user = []  # stores the player`s name, kills and time
saved = False


keys = ['<Left>', '<Right>', '<Button-1>']

configure_window(window)
window.mainloop()
