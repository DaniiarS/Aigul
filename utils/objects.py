class BusStop:
    def __init__(self, id: str, point: str, name: str = None):
        self.id = int(id)
        self.lat = self.get_coord(point)["lat"]
        self.lon = self.get_coord(point)["lon"]
        self.name = name
    
    def get_coord(self, point: str):
        coordinates = ""
        flag = False
        for ch in point:
            if ch == "(":
                flag = True
                continue
            elif ch == ")":
                flag = False
                break
            
            if flag:
                coordinates += ch
            
        coord_split = coordinates.split()
        return {"lon": coord_split[0], "lat": coord_split[1]}
    
    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, lat: {self.lat}, lon: {self.lon}"


