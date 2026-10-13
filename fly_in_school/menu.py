from collections.abc import Callable


def run_menu(
    run_simulation: Callable[[str], object],
    run_visualization: Callable[[str], object],
) -> None:
    """Shows the main menu until the user chooses to exit."""

    while True:

        print("\n==== WELCOME TO FLY-IN ====\n")
        print("WHAT TO DO:")
        print("Run simulation - 1")
        print("Create visualization - 2")
        print("Exit - 0")
        print()

        choice = input("Enter your choice: ")

        if choice == "0":
            print("Good bye!")
            break

        elif choice == "1":
            file_name = choose_level()

            if file_name is not None:
                run_simulation(file_name)

        elif choice == "2":
            file_name = choose_level()

            if file_name is not None:
                run_visualization(file_name)

        else:
            print("Invalid input. Please choose option 0, 1 or 2")


def choose_level() -> str | None:
    """Asks for a level and a map, returns its path or None for back."""

    while True:

        print("CHOOSE MAP LEVEL")
        print("easy - 1")
        print("medium - 2")
        print("hard - 3")
        print("challenger - 4")
        print("Back to main menu - 5")

        choice = input("Enter your choice: ")
        print()

        if choice == "1":
            print("CHOOSE EASY LEVEL MAP")
            print("linear path - 1")
            print("simple fork - 2")
            print("basic capacity - 3")

            choice = input("Enter your choice: ")
            print()

            if choice == "1":
                return "./maps/easy/01_linear_path.txt"
            elif choice == "2":
                return "./maps/easy/02_simple_fork.txt"
            elif choice == "3":
                return "./maps/easy/03_basic_capacity.txt"
            else:
                print("Invalid input. Please try again")

        elif choice == "2":
            print("CHOOSE MEDIUM LEVEL MAP")
            print("dead end trap - 1")
            print("circular loop - 2")
            print("priority puzzle - 3")

            choice = input("Enter your choice: ")
            print()

            if choice == "1":
                return "./maps/medium/01_dead_end_trap.txt"
            elif choice == "2":
                return "./maps/medium/02_circular_loop.txt"
            elif choice == "3":
                return "./maps/medium/03_priority_puzzle.txt"
            else:
                print("Invalid input. Please try again")

        elif choice == "3":
            print("CHOOSE HARD LEVEL MAP")
            print("maze nightmare - 1")
            print("capacity_hell - 2")
            print("ultimate challenge - 3")

            choice = input("Enter your choice: ")
            print()

            if choice == "1":
                return "./maps/hard/01_maze_nightmare.txt"
            elif choice == "2":
                return "./maps/hard/02_capacity_hell.txt"
            elif choice == "3":
                return "./maps/hard/03_ultimate_challenge.txt"
            else:
                print("Invalid input. Please try again")

        elif choice == "4":
            return "./maps/challenger/01_the_impossible_dream.txt"

        elif choice == "5":
            return None

        else:
            print("Invalid input. Please try again")
