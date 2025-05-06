import csv

def split_routes(file_path: str):
    with open(file_path, "r") as rf:
        with open("routes_splitted.txt", "w") as wf:
            for line in rf:
                route = line.split()[-1]
                wf.write(route )

def read_routes(file_path: str):
    with open(file_path, "r") as rf:
        routes = rf.readlines()
    return routes

def write_routes(from_file_path: str, to_file_path: str, route_type = "bus"):
    with open(from_file_path, "r") as rf:
        routes = rf.readlines()
        with open(to_file_path, "a") as wf:
            writer = csv.writer(wf)

            for route in routes:
                route = route.strip("\n")
                writer.writerow([route, route_type])

write_routes("routes_bus.txt", "routes.csv")
write_routes("routes_micro_bus.txt", "routes.csv", "micro_bus")
