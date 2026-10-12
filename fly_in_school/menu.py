from parser import Parser
from graph import Graph

# def show_menu():
#     print("\n==== WELCOME TO FLY-IN ====\n")
#     print("Choose an option:")
#     print("1. Run simulation")
#     print("2. Create visualization")
#     print("0. Exit")

#     choice = int(input("Choose an option: "))
#     if choice == "1":
#         choose_map()

#     if choice == "2":
#         print("Visualization created")
#         create_visualization()

#     elif choice == "0":
#         print("Good bye!")

# def choose_map(choice):

#     if choice == "1":
#         print("Choose map to use:")
#         print("1. easy")
#         print("2. medium")
#         print("3. hard")
#         print("4. challenger")

#         map_to_run = input("Choose an option")
#         return map_to_run

# def create_visualization():
#     pass

def main() -> None:

    while True:

        print("\n==== WELCOME TO FLY-IN ====\n")
        print("Choose an option:")
        print("1. Run simulation")
        print("2. Create visualization")
        print("0. Exit")
        print()

        choice = input("Your choice: ")

        if choice is "1":
            print("Choose map level")
            print("1. easy")
            print("2. medium")
            print("3. hard")
            print("4. challenger")
            print()

            choice = input("Enter your choice: ")

            if choice is "1":
                print("Coose map")
                print("1. linear path")
                print("2. simple fork")
                print("3. basic capacity")

                choice = input("Enter your choice: ")

                if choice is "1":
                    file_name = "./maps/easy/01_linear_path.txt"
                elif choice is "2":
                    file_name = "./maps/easy/02_simple_fork.txt"
                elif choice is "3":
                    file_name = "./maps/easy/03_basic_capacity.txt"

            elif choice is "2":
                print("Coose map")
                print("1. dead end trap")
                print("2. circular loop")
                print("3. priority puzzle")

                choice = input("Enter your choice: ")

                if choice is "1":
                    file_name = "./maps/medium/01_dead_end_trap.txt"
                elif choice is "2":
                    file_name = "./maps/medium/02_circular_loop.txt"
                elif choice is "3":
                    file_name = "./maps/medium/03_priority_puzzle.txt"

            elif choice is "3":
                print("Coose map")
                print("1. maze nightmare")
                print("2. capacity_hell")
                print("3. ultimate challenge")

                choice = input("Enter your choice: ")

                if choice is "1":
                    file_name = "./maps/medium/01_maze_nightmare.txt"
                elif choice is "2":
                    file_name = "./maps/medium/02_capacity_hell.txt"
                elif choice is "3":
                    file_name = "./maps/medium/03_ultimate_challenge.txt"



            if choice is "1":
                file_name = "./maps/01_linear_path.txt"
    