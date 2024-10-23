import tkinter as tk
import random

class Road:
    def __init__(self, canvas):
        self.canvas = canvas
        self.create_road()
        
    def create_road(self):
        self.canvas.create_rectangle(100, 0, 200, 600, fill="#404040")
        for y in range(0, 600, 40):
            self.canvas.create_rectangle(145, y, 155, y + 20, fill="white")
        self.canvas.create_line(100, 0, 100, 600, fill="white", width=2)
        self.canvas.create_line(200, 0, 200, 600, fill="white", width=2)

class Car:
    def __init__(self, canvas):
        self.canvas = canvas
        self.explosion_elements = []
        self.green_light_count = 0  # Track number of green lights encountered
        self.create_new_car()
        
    def create_new_car(self):
        self.x = 150
        self.y = 550
        self.speed = random.randint(20, 30)
        self.target_speed = self.speed
        self.stopped = False
        self.exploded = False
        self.will_run_light = random.random() < 0.3  # 30% chance to run the light
        self.max_speed = 50  # Maximum speed for second green light
        self.last_light_state = None  # Track light state changes
        
        self.shape = self.canvas.create_polygon(
            self.x, self.y,
            self.x - 15, self.y + 20,
            self.x + 15, self.y + 20,
            fill="blue" if not self.will_run_light else "red",  # Visual indicator
            outline="black"
        )
        
        self.speed_display = self.canvas.create_text(
            self.x + 25, self.y + 10,
            text=f"Speed: {self.speed} km/h",
            fill="white",
            font=("Helvetica", 10)
        )

    def cleanup(self):
        self.canvas.delete(self.shape)
        self.canvas.delete(self.speed_display)
        for element in self.explosion_elements:
            self.canvas.delete(element)
        self.explosion_elements.clear()

    def adjust_speed(self, light_state, distance_to_light):
        # Track green light transitions
        if self.last_light_state != light_state:
            if light_state == 2:  # Green light
                self.green_light_count += 1
            self.last_light_state = light_state

        if distance_to_light < 300 and not self.exploded:
            if light_state == 0:  # Red light
                if self.will_run_light:
                    self.target_speed = random.randint(25, 30)
                    self.speed = min(self.speed + 2, self.target_speed)
                    self.stopped = False
                else:
                    if distance_to_light < 150:
                        self.target_speed = 0
                        self.speed = max(0, self.speed - 5)
                        self.stopped = True
                    else:
                        target = (distance_to_light - 150) / 150 * 30
                        self.target_speed = min(target, self.speed)
                        self.speed = max(0, self.speed - 2)
            elif light_state == 1:  # Yellow light
                self.target_speed = random.randint(20, 30)
                if self.speed > self.target_speed:
                    self.speed -= 1
                self.stopped = False
            else:  # Green light
                self.stopped = False
                if self.green_light_count >= 2:
                    # Second or later green light - accelerate to max speed
                    self.target_speed = self.max_speed
                    self.speed = min(self.speed + 3, self.max_speed)  # Faster acceleration
                else:
                    # First green light - normal behavior
                    self.target_speed = 30
                    if self.speed < self.target_speed:
                        self.speed += 1
        else:
            self.stopped = False
            if self.green_light_count >= 2:
                self.target_speed = self.max_speed
                self.speed = min(self.speed + 3, self.max_speed)
            else:
                self.target_speed = random.randint(25, 30)
                if abs(self.speed - self.target_speed) > 0.1:
                    if self.speed > self.target_speed:
                        self.speed -= 1
                    else:
                        self.speed += 1

        # Update speed display with color indication for second green light
        speed_color = "yellow" if self.green_light_count >= 2 and self.speed > 40 else "white"
        self.canvas.itemconfig(
            self.speed_display,
            text=f"Speed: {self.speed:.1f} km/h",
            fill=speed_color
        )

    def move(self):
        if not self.stopped and not self.exploded:
            speed_factor = self.speed / 50
            move_y = -2 * speed_factor
            self.y += move_y
            
            x = round(self.x)
            y = round(self.y)
            
            self.canvas.coords(
                self.shape,
                x, y,
                x - 15, y + 20,
                x + 15, y + 20
            )
            
            self.canvas.coords(
                self.speed_display,
                x + 25, y + 10
            )

    def explode(self):
        if not self.exploded:
            self.exploded = True
            boom_text = self.canvas.create_text(self.x, self.y - 30, text="BOOM!", fill="red", font=("Helvetica", 20))
            self.explosion_elements.append(boom_text)
            self.animate_explosion(1)

    def animate_explosion(self, step):
        if step < 10:
            radius = step * 10
            color = "red" if step < 5 else "orange"
            explosion_circle = self.canvas.create_oval(
                self.x - radius, self.y - radius,
                self.x + radius, self.y + radius,
                fill=color, outline=""
            )
            self.explosion_elements.append(explosion_circle)
            self.canvas.after(50, self.animate_explosion, step + 1)
            self.canvas.after(100, lambda: self.canvas.delete(explosion_circle))

class TrafficLightFSM:
    def __init__(self, canvas):
        self.canvas = canvas
        self.spawn_button = None
        self.timer_id = None  
        self.setup_game()
        
    def setup_game(self):
        self.road = Road(self.canvas)
        self.create_lights()
        self.create_ui_elements()
        self.game_active = False
        self.create_spawn_button()

    def create_spawn_button(self):
        self.spawn_button = tk.Button(self.canvas, text="Start Game", command=self.start_game)
        self.spawn_button_window = self.canvas.create_window(200, 300, window=self.spawn_button)

    def create_lights(self):
        self.lights = {
            0: self.canvas.create_oval(20, 20, 60, 60, fill="gray"),
            1: self.canvas.create_oval(20, 70, 60, 110, fill="gray"),
            2: self.canvas.create_oval(20, 120, 60, 160, fill="gray"),
        }
        self.canvas.create_rectangle(35, 20, 45, 180, fill="#333333")
        self.canvas.create_rectangle(45, 90, 95, 100, fill="#333333")
        
    def create_ui_elements(self):
        self.speed_warning = self.canvas.create_text(
            250, 40,
            text="",
            fill="white",
            font=("Helvetica", 12)
        )
        self.timer_text = self.canvas.create_text(
            50, 200,
            text="",
            fill="white",
            font=("Helvetica", 24)
        )

    def start_game(self):
        self.canvas.delete(self.spawn_button_window)
        self.car = Car(self.canvas)
        self.initialize_game_state()
        self.start_game_loop()

    def initialize_game_state(self):
        self.state_matrix = {
            2: (1, 5000),  # Green -> Yellow
            1: (0, 5000),  # Yellow -> Red
            0: (2, 5000),  # Red -> Green
        }
        
        self.color_map = {0: "Red", 1: "Yellow", 2: "Green"}
        self.state = 2  # Start with Green light
        self.remaining_time = 5
        self.timer_running = True
        self.waiting_for_next_state = False
        self.game_active = True

    def start_game_loop(self):
        self.update_light()
        self.run()
        self.update_timer()
        self.check_speed()

    def check_speed(self):
        if not self.game_active:
            return

        dy = 90 - self.car.y
        distance_to_light = abs(dy)

        warning_text = ""
        if distance_to_light < 200:
            if self.state == 0:  
                if self.car.speed > 10:
                    warning_text = "WARNING: Red light ahead!"
                    if distance_to_light < 120:
                        if self.car.will_run_light or self.car.speed > 0:
                            warning_text = "VIOLATION: Running red light!"
                            self.car.explode()
                            self.show_game_over("Car ran the red light and exploded!")
                else:
                    warning_text = ""

            elif self.state == 1:  
                if self.car.speed > 40:
                    warning_text = "CAUTION: Slow down"

        self.canvas.itemconfig(self.speed_warning, text=warning_text)

        if not self.car.exploded:
            self.car.adjust_speed(self.state, distance_to_light)
            self.car.move()

        if self.car.y < -50:  
            self.show_game_over("Car reached the end of the road!")

        if self.game_active:
            self.canvas.after(30, self.check_speed)

    def show_game_over(self, message):
        self.game_active = False
        # Cancel any pending timer updates
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)
            self.timer_id = None
            
        self.canvas.create_text(
            150, 250,
            text=message,
            fill="white",
            font=("Helvetica", 24)
        )
        self.car.cleanup()
        self.create_spawn_button_after_game_over()

    def create_spawn_button_after_game_over(self):
        self.spawn_button = tk.Button(self.canvas, text="Spawn New Car", command=self.spawn_new_car)
        self.spawn_button_window = self.canvas.create_window(200, 300, window=self.spawn_button)

    def spawn_new_car(self):
        # Cancel any existing timers
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)
            self.timer_id = None
            
        # Clear canvas and recreate everything
        self.canvas.delete("all")
        
        # Recreate road, lights, and UI elements
        self.road = Road(self.canvas)
        self.create_lights()
        self.create_ui_elements()
        
        # Create new car
        self.car = Car(self.canvas)
        self.game_active = True
        
        # Reset game state
        self.initialize_game_state()
        
        # Start game loops
        self.start_game_loop()

    def update_light(self):
        for i, light_id in self.lights.items():
            color = "green" if i == 2 else "yellow" if i == 1 else "red"
            if i == self.state:
                self.canvas.itemconfig(light_id, fill=color)
            else:
                self.canvas.itemconfig(light_id, fill="gray")

    def run(self):
        if not self.game_active:
            return

        if self.waiting_for_next_state:
            self.remaining_time -= 1
            if self.remaining_time <= 0:
                self.state, next_time = self.state_matrix[self.state]
                self.remaining_time = next_time // 1000
                self.update_light()
            if self.game_active:
                self.canvas.after(1000, self.run)
        else:
            self.waiting_for_next_state = True
            self.run()

    def update_timer(self):
        if not self.game_active:
            return
        self.canvas.itemconfig(self.timer_text, text=f"{self.remaining_time}")
        # Store the timer ID so we can cancel it later
        self.timer_id = self.canvas.after(1000, self.update_timer)

def main():
    root = tk.Tk()
    root.title("Traffic Light Car Game")
    
    canvas = tk.Canvas(root, width=400, height=600, bg="black")
    canvas.pack()
    
    traffic_game = TrafficLightFSM(canvas)
    
    root.mainloop()

if __name__ == "__main__":
    main()