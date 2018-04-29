file = open("./levels/-2.level", "w+")
file.write("10 10\n500 500 100-600-1080-600-500-20 1.2\n")
print("File initialised")
for n in range(1280):
    for m in range(720):
        file.write("{nn} {mm} 1 1 False ".format(nn = n, mm = m))
file.close()
print("Done")
