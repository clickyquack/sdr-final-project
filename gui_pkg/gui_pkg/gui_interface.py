import tkinter as tk
import subprocess
import os 
import signal
import time

# Config

WS = '~/pkd_ws'
DOMAIN_ID = 11
TB3_IP = 'atr@10.32.11.97'
MODEL="burger"
terminals = {}


# For Computer
# Open a new terminal, 
# source the ROS_DISTRO
# Define the turtlebot model ,  ROS Middleware implementation, Domain ID
#then run the command
def run_cmd(command,title):
    #  Prevent duplicate launches
    if title in terminals:
        # remove dead processes
        terminals[title] = [p for p in terminals[title] if p.poll() is None]

        if len(terminals[title]) > 0:
            print(f"{title} is already running")
            return

    #  Only runs if NOT already running
    full_cmd = [
        "gnome-terminal",
        "--wait",
        f"--title={title}",
        "--",
        "bash",
        "--noprofile",
        "--norc", 
        "-c",
        f"""
        source /opt/ros/jazzy/setup.bash &&
        export TURTLEBOT3_MODEL={MODEL} &&
        export RMW_IMPLEMENTATION=rmw_fastrtps_cpp  &&
        export ROS_DOMAIN_ID={DOMAIN_ID} &&
        {command};
        exec bash
        """
    ]
    proc = subprocess.Popen(full_cmd, preexec_fn=os.setsid)
    
    if title not in terminals:
        terminals[title] = []
    
    terminals[title].append(proc)
#For turtleBot
def run_ssh_init(title):
    #  Prevent duplicate launches
    if title in terminals:
        # remove dead processes
        terminals[title] = [p for p in terminals[title] if p.poll() is None]

        if len(terminals[title]) > 0:
            print(f"{title} is already running")
            return

    #  Only runs if NOT already running
    full_cmd = [
        "gnome-terminal",
        "--wait",
        f"--title={title}",
        "--",
        "bash",
        "-c",
        "exec bash"
    ]
    proc = subprocess.Popen(full_cmd, preexec_fn=os.setsid)

    if title not in terminals:
        terminals[title] = []
        
    terminals[title].append(proc)

#Open Rviz2
def open_riv2():
    run_cmd("rviz2","Rviz2")

#Launch Cartograher
def open_cartographer():
    run_cmd("ros2 launch turtlebot3_cartographer cartographer.launch.py","Cartographer")

#Copies Text from Button Click to a clipboard to paste later
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

#Run a Bringup and lidar command for the turtlebot
# Open a New terminal
#Click the buttons in order then paste into new terminal
def launch_bl():
    run_ssh_init("Launch Bringup/LiDar")

    cmd_window = tk.Toplevel(root)
    cmd_window.title("Launch Bringup/LiDar")
    cmd_window.geometry("500x500")

    tk.Label(cmd_window, 
             text="Click a command to copy then paste to new terminal:", 
             font=("Arial", 12)
             ).pack(pady=10)
    
    commands = [
        "cd ~",
        f"ssh {TB3_IP}",
        "cd ~/turtlebot3_ws",
        "source /opt/ros/jazzy/setup.bash",
        "source install/setup.bash",
        f"export TURTLEBOT3_MODEL={MODEL}",
        f"export ROS_DOMAIN_ID={DOMAIN_ID}",
        "ros2 launch my_package my_launch.py"
    ]

    for cmd in commands:
        tk.Button(
            cmd_window,
            text=cmd,
            width=75,
            anchor="w",
            command=lambda c=cmd: copy_to_clipboard(c)
        ).pack(pady=3)

# View the list of all topics being subscribed to within the DOMAIN ID
def check_topic():
    run_cmd("ros2 topic list","ROS Topic")

#Open Gazebo Simulator
def open_gz_sim():
    run_cmd("ros2 launch sdr-final-project rect_world_gz.launch.py","Gazebo Simulator")

#Use a controller
def use_contr():
    run_cmd("ros2 launch sdr-final-project joy_teleop.launch.py", "Connect to Controller")

#Open camera
def open_cam():
    run_cmd("ros2 run sdr-final-project camera_viewer","Turtlebot Camera")

#Open Navigation (Physical): 
def nav_phys():
    run_cmd("ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/turtlebot3_ws/src/sdr-final-project/map.yaml", "Navigation(Physical)")

#Open Navigation (Simulation): 
def nav_sim():
    run_cmd("ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/turtlebot3_ws/src/sdr-final-project/mapsim.yaml", "Navigation(Simulation)")

#Stop A terminal
def stop_terminal(title):
    """
    Stops all terminals associated with a given title.
    """

    try:
        # Try graceful shutdown first
        for proc in terminals.get(title, []):
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

        # Then force close terminal window
        subprocess.run(["pkill", "-f", title])

        print(f"[STOPPED] {title}")

    except Exception as e:
        print(f"[ERROR] Failed to stop {title}: {e}")

    terminals[title] = []

# GUI
def main():

    global root

    root = tk.Tk()
    root.title("ROS2 Control Panel")

    tk.Label(root, text='--Tools---').pack(pady=5)

    # Helper to create a row
    def add_row(label, start_cmd, title):
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text=label,
                  command=start_cmd,
                  width=25).pack(side="left")

        tk.Button(frame, text='Stop',
                  command=lambda: stop_terminal(title),
                  bg='red', fg='white',
                  width=10).pack(side="left")

    # Rows
    add_row('All topics', check_topic, "atr-lab@localhost:~/gui_control")
    add_row('Rviz2', open_riv2, "Rviz2")
    add_row('Gazebo Simulator', open_gz_sim, "Gazebo Simulator")
    add_row('Cartographer', open_cartographer, "Cartographer")
    add_row('Launch bringup/lidar', launch_bl, "Launch Bringup/LiDar")
    add_row('Launch Controller', use_contr, "Connect to Controller")
    add_row('Launch Turtlebot Camera', open_cam, "Launch Turtlebot Camera")
    add_row('Navigation (Physical)', nav_phys, "Navigation(Physical)")
    add_row('Navigation (Simulation)', nav_sim, "Navigation(Simulation)")

    root.mainloop()

if __name__ == "__main__":
    main()
