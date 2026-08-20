import sys

NB_DRONES = 0

def open_the_file(file_name: str):
    try:
        with open(file_name, "r") as file:
            content = file.readlines()
    except OSError:
        print("Problem with opening the file")
        return
    return content

def read_to_dict(content):
    for line in content:
        if line is None or line.startswith("#"):
            continue
        elif line.startswith("nb_drones"):
            name, NB_DRONES = line.split("=")
            print(NB_DRONES)
            

def validate_file()
def main() -> None:
    if len(sys.argv) < 2:
        print("Not enough arguments")
        return

    file_name = sys.argv[1]
    content = open_the_file(file_name)
    read_to_dict(content)

if __name__ == "__main__":
    main()