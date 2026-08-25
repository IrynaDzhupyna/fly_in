ZONE_PREFIXES = ["start_hub", "hub", "end_hub"]

with open("01_linear_path.txt", "r") as file:
    content = file.readlines()
    for line in content:
        if line.startswith("#") or not line.strip():
            continue

        try:
            key, value = line.split(": ", 1)
        except ValueError:
            print("Not working")
        else:
            if key == "nb_drones":
                print(f"Key: {key}")
                print(f"Value: {value}")

            elif key in ZONE_PREFIXES:
                name, x, y, metadata = value.split(" ", 3)
                print(f"Name: {name}")
                print(f"Coordinates: {x}, {y}")
                print(f"Metadata: {metadata}")