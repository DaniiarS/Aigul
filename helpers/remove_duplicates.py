import json


#============================================================================================================
# DEFINITION:
#============================================================================================================

# NOTE: "rmd" stand for "remove duplicates" 
def rmd_bus_stop(file_path):
    modified = []
    with open(file_path+"/bus_stop-aigul.json", "r") as rf:
        data = json.load(rf)
        lat_lon = set()

        for obj in data:
            pair = (str(obj["lat"]), str(obj["lon"]))
            if pair not in lat_lon:
                modified.append(obj)
                lat_lon.add(pair)
    
    with open(file_path+"/bus_stop-rmd.json", "w") as wf:
        json.dump(modified, wf, ensure_ascii=False, indent=2)


#============================================================================================================
# EXECUTION:
#============================================================================================================

rmd_bus_stop("app/db/migrations/data")