sel=C.object

def translade(x,y,z):
    sel.location.x+=x
    sel.location.y+=y
    sel.location.z+=z   
     
def move_duplicate(x,y,z):
    bpy.ops.object.duplicate_move()
    translade(x,y,z)    

def custom(name):
    for obj in D.objects:
        if obj.name.startswith(name):
            #do what you want
            pass


