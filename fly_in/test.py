my_list = [1, 2, 3, 4, 2]
i = 0

while my_list:
    i = i + 1
    print(f"Element {i}: {my_list.pop(0)}")
    # i += 1