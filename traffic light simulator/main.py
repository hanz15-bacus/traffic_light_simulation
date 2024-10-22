import tkinter as tk

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
        self.x = 150
        self.y = 550
        self.speed = 50
        self.target_speed = self.speed
        self.stopped = False
        
       
        self.shape = self.canvas.create_polygon(
            self.x, self.y,                 
            self.x - 15, self.y + 20,      
            self.x + 15, self.y + 20,       
            fill="blue", outline="black"
        )
        
        self.speed_display = self.canvas.create_text(
            self.x + 25, self.y + 10,
            text=f"Speed: {self.speed} km/h",
            fill="white",
            font=("Helvetica", 10)
        )

    def adjust_speed(self, light_state, distance_to_light):
        if distance_to_light < 200:
            if light_state == 0:
                self.target_speed = 0
                self.stopped = True
            elif light_state == 1:
                self.target_speed = max(10, self.speed * 0.5)
                self.stopped = False
            elif light_state == 2:
                self.stopped = False
                self.target_speed = 50
        else:
            self.stopped = False
            self.target_speed = 50

        if abs(self.speed - self.target_speed) > 0.1:
            if self.speed > self.target_speed:
                self.speed -= 2
            else:
                self.speed += 1

    def move(self):
        if not self.stopped:
            speed_factor = self.speed / 50
            move_y = -3 * speed_factor
            self.y += move_y
            
            # Update the triangle's coordinates
            self.canvas.coords(
                self.shape,
                self.x, self.y,                  # Tip of the triangle
                self.x - 15, self.y + 20,        # Bottom left corner
                self.x + 15, self.y + 20         # Bottom right corner
            )
            
            self.canvas.coords(
                self.speed_display,
                self.x + 25, self.y + 10
            )

    def reset(self):
        self.x = 150
        self.y = 550
        self.speed = 50
        self.target_speed = self.speed
        self.stopped = False
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


class TrafficLightFSM:
    def __init__(self, canvas):
        self.canvas = canvas
        self.road = Road(canvas)
        
        self.lights = {
            0: self.canvas.create_oval(20, 20, 60, 60, fill="gray"),
            1: self.canvas.create_oval(20, 70, 60, 110, fill="gray"),
            2: self.canvas.create_oval(20, 120, 60, 160, fill="gray"),
        }
        self.canvas.create_rectangle(35, 20, 45, 180, fill="#333333")
        self.canvas.create_rectangle(45, 90, 95, 100, fill="#333333")
        
        self.speed_warning = self.canvas.create_text(
            250, 40,
            text="",
            fill="white",
            font=("Helvetica", 12)
        )
        
        self.state_matrix = {
            1: (0, 5000),
            0: (2, 5000),
            2: ("Off", 5000),
        }
        self.color_map = {0: "Red", 1: "Yellow", 2: "Green"}
        self.state = 1
        self.remaining_time = 5
        self.timer_text = self.canvas.create_text(50, 200, text="", fill="white", font=("Helvetica", 24))
        self.timer_running = True
        self.waiting_for_next_state = False
        
        self.car = Car(canvas)
        self.update_light()
        self.check_speed()

    def check_speed(self):
        dy = 90 - self.car.y
        distance_to_light = abs(dy)

        warning_text = ""
        if distance_to_light < 200:
            if self.state == 0:
                if self.car.speed > 5:
                    warning_text = "WARNING: Stop!\nRed light ahead"
            elif self.state == 1:
                if self.car.speed > 40:
                    warning_text = "CAUTION: Slow down"

        self.canvas.itemconfig(self.speed_warning, text=warning_text)
        
        self.car.adjust_speed(self.state, distance_to_light)
        
        self.car.move()
        
        self.canvas.itemconfig(self.car.speed_display, text=f"Speed: {int(self.car.speed)} km/h")
        
        if self.car.y < 0:  # Stop the car instead of resetting
            self.car.speed = 0
            self.car.stopped = True

        if not self.state == "Off":
            self.canvas.after(50, self.check_speed)

    def switch_state(self):
        if self.state in self.state_matrix:
            next_state, _ = self.state_matrix[self.state]
            self.state = next_state
            self.remaining_time = 5
            self.timer_running = self.state != "Off"
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
        if self.state == "Off":
            self.show_turn_off_message()
            self.timer_running = False
            self.canvas.itemconfig(self.timer_text, text="")
            self.canvas.after(2000, exit)
            return

        self.canvas.after(1000, self.run)

    def update_timer(self):
        if self.timer_running:
            if self.remaining_time >= 0:
                self.canvas.itemconfig(self.timer_text, text=f"Time: {self.remaining_time} s")
                self.remaining_time -= 1
                self.canvas.after(1000, self.update_timer)
            elif not self.waiting_for_next_state:
                self.waiting_for_next_state = True
                if self.switch_state():
                    if self.state != "Off":
                        self.canvas.itemconfig(self.timer_text, text=f"Time: {self.remaining_time} s")
                        self.canvas.after(1000, self.update_timer)
        else:
            self.canvas.itemconfig(self.timer_text, "")

    def show_turn_off_message(self):
        self.canvas.create_text(300, 250, text="Traffic light turned off", fill="white", font=("Helvetica", 16))

def main():
    root = tk.Tk()
    root.title("Traffic Light with Car Behavior and Speed Display")

    canvas = tk.Canvas(root, width=600, height=600, bg="#202020")
    canvas.pack(expand=True, fill="both")

    traffic_light = TrafficLightFSM(canvas)
    traffic_light.run()
    traffic_light.update_timer()

    root.mainloop()

if __name__ == "__main__":
    main()
