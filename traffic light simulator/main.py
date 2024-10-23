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
        for x in range(105, 195, 15):
            self.canvas.create_rectangle(x, 80, x + 10, 100, fill="white")

class Car:
    def __init__(self, canvas):
        self.canvas = canvas
        self.explosion_elements = []  
        self.create_new_car()
        
    def create_new_car(self):
        self.x = 150
        self.y = 550
        self.speed = random.randint(40, 60)
        self.target_speed = self.speed
        self.stopped = False
        self.exploded = False
        self.will_run_light = random.random() < 0.4
        self.decision_made = False
        
        # Create car shape
        self.shape = self.canvas.create_polygon(
            self.x, self.y,
            self.x - 15, self.y + 20,
            self.x + 15, self.y + 20,
            fill="blue" if not self.will_run_light else "red",
            outline="black"
        )
        
        self.speed_display = self.canvas.create_text(
            self.x + 25, self.y + 10,
            text=f"Speed: {self.speed} km/h",
            fill="white",
            font=("Helvetica", 10)
        )

    def cleanup(self):
        """Remove all car-related elements from canvas"""
        self.canvas.delete(self.shape)
        self.canvas.delete(self.speed_display)
        # Remove any explosion elements
        for element in self.explosion_elements:
            self.canvas.delete(element)
        self.explosion_elements.clear()

    def decide_to_run_light(self, distance_to_light):
        if not self.decision_made and distance_to_light < 200:
            self.decision_made = True
            return self.will_run_light
        return self.will_run_light

    def adjust_speed(self, light_state, distance_to_light):
        if distance_to_light < 300 and not self.exploded:
            if light_state == 0:  # Red light
                if self.decide_to_run_light(distance_to_light):
                    # Accelerate through red light
                    self.target_speed = random.randint(60, 80)
                    self.speed = min(self.speed + 2, self.target_speed)
                    self.stopped = False
                else:
                    # Normal stopping behavior
                    if distance_to_light < 150:
                        self.target_speed = 0
                        self.speed = max(0, self.speed - 5)
                        self.stopped = True
                    else:
                        target = (distance_to_light - 150) / 150 * 40
                        self.target_speed = min(target, self.speed)
                        self.speed = max(0, self.speed - 2)
            else:  # Yellow or Green light
                self.stopped = False
                self.target_speed = random.randint(40, 60)
                if self.speed < self.target_speed:
                    self.speed += 1
        else:
            self.stopped = False
            self.target_speed = random.randint(40, 60)
            if abs(self.speed - self.target_speed) > 0.1:
                if self.speed > self.target_speed:
                    self.speed -= 1
                else:
                    self.speed += 1

    def move(self):
        if not self.stopped and not self.exploded:
            speed_factor = self.speed / 50
            move_y = -3 * speed_factor
            self.y += move_y
            
            self.canvas.coords(
                self.shape,
                self.x, self.y,
                self.x - 15, self.y + 20,
                self.x + 15, self.y + 20
            )
            
            self.canvas.coords(
                self.speed_display,
                self.x + 25, self.y + 10
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
        self.setup_game()
        
    def setup_game(self):
        self.road = Road(self.canvas)
        self.create_lights()
        self.create_ui_elements()
        self.initialize_game_state()
        self.car = Car(self.canvas)
        self.start_game_loop()
        
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
        
    def initialize_game_state(self):
        self.state_matrix = {
            1: (0, 5000),  # Yellow -> Red
            0: (2, 5000),  # Red -> Green
            2: (1, 5000),  # Green -> Yellow
        }
        
        self.car_state_matrix = {
            1: ("SLOW_DOWN", 5000),  # Yellow light: Car should slow down
            0: ("STOP", 5000),  # Red light: Car should stop
            2: ("GO", 5000),  # Green light: Car can go
        }
        
        self.color_map = {0: "Red", 1: "Yellow", 2: "Green"}
        self.state = 1  # Start with the Yellow light
        self.remaining_time = 5
        self.timer_running = True
        self.waiting_for_next_state = False
        self.game_active = True

        self.color_map = {0: "Red", 1: "Yellow", 2: "Green"}
        self.state = 1
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
                    # If car has stopped, reset any warning
                    warning_text = ""

            elif self.state == 1:  
                if self.car.speed > 40:
                    warning_text = "CAUTION: Slow down"

        self.canvas.itemconfig(self.speed_warning, text=warning_text)

        if not self.car.exploded:
            self.car.adjust_speed(self.state, distance_to_light)
            self.car.move()
            self.canvas.itemconfig(self.car.speed_display, text=f"Speed: {int(self.car.speed)} km/h")

        if self.car.y < -50:  
            self.show_game_over("Car passed successfully!")

        if self.game_active:
            self.canvas.after(50, self.check_speed)


    def show_game_over(self, message="Game Over"):
        self.game_over_text = self.canvas.create_text(300, 250, text=message, fill="white", font=("Helvetica", 24))
        self.create_restart_button()
        self.timer_running = False
        self.game_active = False

    def create_restart_button(self):
        restart_button = tk.Button(self.canvas, text="New Car", command=self.new_car)
        self.restart_button_window = self.canvas.create_window(300, 300, window=restart_button)

    def new_car(self):
        self.canvas.delete(self.game_over_text)
        self.canvas.delete(self.restart_button_window)
        
        self.car.cleanup()
        
        self.car = Car(self.canvas)
        self.game_active = True
        self.timer_running = True
        self.remaining_time = 5
        
        self.state = 1
        self.update_light()
        
        # Start the speed check and timer
        self.check_speed()
        self.update_timer()


    def switch_state(self):
        if self.state in self.state_matrix:
            next_state, _ = self.state_matrix[self.state]
            self.state = next_state
            self.remaining_time = 5
            self.timer_running = True
            self.waiting_for_next_state = False
            self.update_light()
            return True
        return False

    def update_light(self):
        for light in self.lights.values():
            self.canvas.itemconfig(light, fill="gray")

        if self.state in self.color_map:
            color = self.color_map[self.state].lower()
            self.canvas.itemconfig(self.lights[self.state], fill=color)

    def run(self):
        if self.game_active:
            self.canvas.after(1000, self.run)

    def update_timer(self):
        if not self.game_active:
            return
            
        if self.timer_running:
            if self.remaining_time >= 0:
                self.canvas.itemconfig(self.timer_text, text=f"Time: {self.remaining_time} s")
                self.remaining_time -= 1
                self.canvas.after(1000, self.update_timer)
            elif not self.waiting_for_next_state:
                self.waiting_for_next_state = True
                if self.switch_state():
                    self.canvas.itemconfig(self.timer_text, text=f"Time: {self.remaining_time} s")
                    self.canvas.after(1000, self.update_timer)
        else:
            self.canvas.itemconfig(self.timer_text, text="")

def main():
    root = tk.Tk()
    root.title("Traffic Light Simulation")

    canvas = tk.Canvas(root, width=600, height=600, bg="#202020")
    canvas.pack(expand=True, fill="both")

    traffic_light = TrafficLightFSM(canvas)

    root.mainloop()

if __name__ == "__main__":
    main()

