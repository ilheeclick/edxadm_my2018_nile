rows = [
 ('1', '2', '3', "0,0,100,100/100,100,200,201"),
 ('4', '5', '6', "0,0,100,100/100,100,200,202"),
 ('7', '8', '9', "0,0,100,100/100,100,200,203"),

]

pop_list = []
for p in rows:
    map_positions = p[3]
    map_arr = map_positions.split('/')
    print 'check:', p + (map_arr,)
    pop_list.append(list(p + (map_arr,)))

