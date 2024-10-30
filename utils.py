import typing

def __write_line(file: typing.IO, line):
    if not line:
        file.write("\n")
        
    elif isinstance(line[0], str):
        file.write(";".join(line) + "\n")

    elif isinstance(line[0], list):
        for array in line:
            __write_line(file, array)


def write_to_file(filename: str, *lines: list):
    with open(filename, "w") as f:
        for line in lines:
            __write_line(f, line)