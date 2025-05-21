import csv

with open("mapping.csv", "r") as rf:
    reader = csv.reader(rf)
    with open("addresses.csv", "a") as wf:
        writer = csv.writer(wf)
        for i, line in enumerate(reader):
            line.append(i)
            writer.writerow(line)