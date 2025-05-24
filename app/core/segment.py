import csv
#===============================================================
# DEFINITIONS: read_segments(), write_segments()
#===============================================================


        

def read_segments(ROUTE: str) -> list[str]:
    with open(f"{ROUTE}/addresses.csv", "r") as rf:
        reader = list(csv.reader(rf))
    return reader

def write_segments(ROUTE: str):
    with open(f"{ROUTE}/distances.csv", "r") as rf1:
        reader1 = csv.reader(rf1)
        distances = [line[0] for line in reader1 if line]

        with open(f"{ROUTE}/addresses.csv", "r") as rf2:
            reader2 = csv.reader(rf2)
            addresses = list(reader2)
            size = len(addresses)

            with open(f"{ROUTE}/segments.csv", "w") as wf:
                writer = csv.writer(wf)
                for i in range(size - 1):
                    writer.writerow([addresses[i][1], f"{addresses[i][2]} -- {addresses[i+1][2]}", f"({addresses[i][3]},{addresses[i][4]})", f"({addresses[i+1][3]},{addresses[i+1][4]})", distances[i], addresses[i][-1]])

SEGMENT_ROUTE = "7"

# segment_distances = read_segments(SEGMENT_ROUTE)
# write_segments(SEGMENT_ROUTE)