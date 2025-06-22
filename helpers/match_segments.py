import json

#============================================================================================================
# DEFINITION:
#============================================================================================================

def match_segments(file_path: str):
    with open(file_path+"/segment-aigul-1.json", "r") as rf1:
        data = json.load(rf1)
    
    with open(file_path+"/bus_stop-psql.json", "r") as rf2:
        bus_stops = json.load(rf2)
    

    for obj in data:
        bus_stop_a = obj["segment_bus_stop_a"][1:-1].split(", ")
        bus_stop_b = obj["segment_bus_stop_b"][1:-1].split(", ")

        bs_a_id = None
        bs_b_id = None

        for bs in bus_stops:
            if bs["lat"] == bus_stop_a[1] and bs["lon"] == bus_stop_a[0]:
                bs_a_id = bs["id"]
            
            if bs["lat"] == bus_stop_b[1] and bs["lon"] == bus_stop_b[0]:
                bs_b_id = bs["id"]
        
        obj["segment_bus_stop_a"] = bs_a_id
        obj["segment_bus_stop_b"] = bs_b_id
    
    with open(file_path+"/segment-upd.json", "w") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)

        
#============================================================================================================
# EXECUTION:
#============================================================================================================

match_segments("app/db/migrations/data")