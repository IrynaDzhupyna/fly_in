from collections.abc import Callable


def run_menu(
    run_simulation: Callable[[str], object],
    run_visualization: Callable[[str], object],
) -> None:
    """Shows the main menu until the user chooses to exit."""

    while True:

        print("\n==== WELCOME TO FLY-IN ====\n")
        print("CHOOSE WHAT TO DO:")
        print("1 - run simulation")
        print("2 - create visualization")
        print("0 - exit")

        choice = input("Enter your choice: ")

        if choice == "0":
            print("Program was terminated. Good bye!")
            break

        elif choice == "1":
            file_name = choose_level()

            if file_name is not None:
                run_simulation(file_name)

                print("SHOW VISUALIZATION")
                print("1 - yes")
                print("2 - no")

                choice = input("Enter your choice: ")

                if choice == "1":
                    run_visualization(file_name)
                elif choice == "2":
                    continue
                else:
                    print("Invalid input. Please try again")


        elif choice == "2":
            file_name = choose_level()

            if file_name is not None:
                run_visualization(file_name)

        else:
            print("Invalid input. Please choose option 0, 1 or 2")


def choose_level() -> str | None:
    """Asks for a level and a map, returns its path or None for back."""

    while True:

        print("\nCHOOSE MAP LEVEL")
        print("1 - easy")
        print("2 - medium")
        print("3 - hard")
        print("4 - challenger")
        print("5 - back to main menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            print("\nCHOOSE EASY LEVEL MAP")
            print("1 - linear path")
            print("2 - simple fork")
            print("3 - basic capacity")

            choice = input("Enter your choice: ")

            if choice == "1":
                return "./maps/easy/01_linear_path.txt"
            elif choice == "2":
                return "./maps/easy/02_simple_fork.txt"
            elif choice == "3":
                return "./maps/easy/03_basic_capacity.txt"
            else:
                print("Invalid input. Please try again")

        elif choice == "2":
            print("\nCHOOSE MEDIUM LEVEL MAP")
            print("1 - dead end trap")
            print("2 - circular loop")
            print("3 - priority puzzle")

            choice = input("Enter your choice: ")

            if choice == "1":
                return "./maps/medium/01_dead_end_trap.txt"
            elif choice == "2":
                return "./maps/medium/02_circular_loop.txt"
            elif choice == "3":
                return "./maps/medium/03_priority_puzzle.txt"
            else:
                print("Invalid input. Please try again")

        elif choice == "3":
            print("\nCHOOSE HARD LEVEL MAP")
            print("1 - maze nightmare")
            print("2 - capacity_hell")
            print("3 - ultimate challenge")

            choice = input("Enter your choice: ")

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
