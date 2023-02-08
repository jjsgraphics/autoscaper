"""Landscaper

This is a maya python script

"""
import maya.cmds as cmds
import random
import math as m
import pymel.core as pm

#Global Variables
globalSeperatedSea=False
wallsExist=False
buildingType=0
globalSeaLevel = -10
globalBottomOfCube = -10
filePath="C:\Users\jamal\OneDrive - Bournemouth University\Year 1\Semester 2\Python Project\Final Submission"

def errorMessage(error):
    ''' Error Message in a confirm dialog is thrown, giving the input error message '''
    cmds.confirmDialog( title='Error', message=error, button=['ok'], defaultButton='ok', cancelButton='ok', dismissString='ok' )

def cancelProc():
    ''' Deletes the UI '''
    cmds.deleteUI("Landscaper") 

delOBJList = 'tallTreeOBJ', 'smallTreeOBJ', 'houseOBJ', 'cityOBJ'
delTreeList = 'tree', 'pCylinder1', 'Trees'
delTerrainList = 'tree', 'pCylinder1', 'Trees', 'terrain', 'Buildings', 'water'

def deleteObjects(objectsToDelete):
    ''' deletes the existing objects in the objectstToDelete list
        
    objs:    List containing the existing object  
    '''
    global wallsExist
    objs = cmds.ls(objectsToDelete) 
    if objs: #if any of the objects in the list exist they are deleted
        cmds.delete(objs)
    if objectsToDelete == delTerrainList: #if the terrain list is passed deleted wallsExist is set to false so the next terrain can be turned into a cube
        wallsExist=False 
        globalSeperatedSea=False
    if objectsToDelete == 'water':
        globalSeperatedSea=False

def bumpTerrain(heightOffset):
    ''' if heightOffset is passed add some texture to the terrain by randomly increasing the vertex height by the heightOffset amount
        or 
        if heightOffset == 0, the terrain is slightly flattened
        
    heightOffset:              Stores the bump height or 0 to flatten the terrain

    totalVerts:             Total integer n.o. vertices on the terrain plane
    progressCancelled:      Boolean storing True if the function is cancelled (ESC is pressed)
    '''
    deleteObjects(delTreeList) #As the terrain is modified, delete the trees as they will look strange
    cmds.softSelect(sse=False) #disable softselect 
    cmds.select('terrain')
    totalVerts = cmds.polyEvaluate('terrain', v=True) #finds the n.o. vertices on the terrain
    cmds.progressWindow(t='Progress Bar', progress=0, status='', ii=True) #create the progress window
    progressCancelled=False
    for vtx in range(0, totalVerts): #loops through each vertex in the terrain
        if(cmds.progressWindow(q=True, ic=True)): #if the escape key is pressed, stop the function
            progressCancelled=True
            break
        if (cmds.pointPosition('terrain.vtx[' + str(vtx) + ']')[1] == globalBottomOfCube): #if the current vertex y coordinate is -10, it isn't move as it will modify the cubes walls
                continue
        if heightOffset == 0: #if 0 is passed, the terrain is flattened instead
            vtxPos1 = cmds.pointPosition('terrain.vtx[' + str(vtx) + ']') #store the coordinates of the current vertex
            cmds.select('terrain.vtx[' + str(vtx) + ']') #select the vertex
            cmds.move(vtxPos1[1]*0.8, y=True ) #move the vertex's y coordinate to 80% of it's original height (works with positive and negative values) 
            progressStatus = 'Flattening'
        else: #if any other number is passed the terrain is made more
            randomHeight = random.uniform(-1.0*heightOffset, heightOffset) #the vertex's location will be offset by a random value between the positive and negative heightOffset magnitude
            cmds.select('terrain.vtx[' + str(vtx) + ']') #select the vertex
            cmds.move(randomHeight, y=True, r=True) #move the vertex relatively by the random height
            progressStatus = 'Adding bumps'
        progress = float((float(vtx)/float(totalVerts)) * 100) #calculate the progress of the function
        cmds.progressWindow(edit=True, progress=progress, status=progressStatus) #update the progress bar
    cmds.progressWindow(endProgress=1) 

def smoothTerrain():
    ''' Performs a subdivision on the terrain plane if the n.o. vertices is < 100k (prevents lag issues '''
    
    if(cmds.polyEvaluate('terrain', v=True) > 100000): #if the n.o. verts on the terriain is > 10000
        errorMessage('Over 100,000 vertices, smoothing not executed')
        return #return before smoothing
    cmds.select('terrain')
    cmds.polySmooth(dv=1) 
    cmds.delete(ch=True)

def getVTXPosition(vtx):
    ''' Returns a string saying wether the vertex input is or isn't on the outer edge of the plane
    
    vtx:         Integer identifier of the vertex used
    
    polyInfo:    List of one string element containing the edge identifies connected to the vertex
    Split:       List of the polyinfo string split up into words
    list:        List holding only the edge integer identifiers connected to the vertex
    '''
    cmds.select('terrain.vtx[' + str(vtx) + ']') #select the vertex being passed in
    polyInfo = cmds.polyInfo(ve=True) #find the edges connected to the vertex
    
    ''' manipulate the polyInfo list to extract the data'''
    split = polyInfo[0].split(' ')
    split.remove('')
    list = []
    for i in split:
        if i == '' or i == 'VERTEX' or i == '\n':
            continue
        else:
            list.append(i)
    if len(list) > 4: #if there are four edges connected to the vertex, return 'inside' indicating the vertex is on the inside of the plane 
        return('Inside')
    elif len(list) > 3:
        return('Edge')
    else:
        return('Corner')

def areFacesSelected(multiple):
    ''' This function is run to detects what's selected and returns an error if not one or multiple faces
    multiple:     boolean holds True if multiple faces are selected

    selection:    variable stores the selected object's identifier
    '''
    selection = cmds.ls(sl=True) #stores the selection in a list
    if((len(selection) == 1 and multiple==False) or (len(selection) > 0 and multiple==True)): #if multiple=True and multiple items are selected OR if multiple=False and only one item is selected
        for face in selection:
            if 'terrain.f[' in face: #if the thing(s) are faces, return 1
                return 1

    errorString = 'a single face'
    if multiple == True: #if multiple is true change the error message
        errorString = 'one or more faces'
    
    errorMessage('Select '+ errorString +' on the terrain') 
    return 0

def createMountain(r, h):
    ''' Creates a mountain on the selected face
    
    r:            integer of the mountain's radius input by the user
    h:            integer of the mountain's height input by the user
    
    selection:    variable stores the selected object's identifier
    '''
    if areFacesSelected(False) == 0: #if faces aren't selected, exit function
        return()
    cmds.softSelect(sse=True, ssd=0.5*r) #Enable soft select with a distance of half the input radius to create a better mountain
    cmds.move(0, 1, 0, r=True) #create the top steepest part of the mountain
    cmds.softSelect(ssd=r) #change SS distance to be the raidus
    cmds.move(0, (1)*h, 0, r=True) #move the mountain up higher#dond
    cmds.softSelect(sse=False) #disable SS

def getFaceVTXValues(face):
    ''' Returns a list of a passed faces' vertices
    
    face:               Passes in the face

    faceObjectName:     Stores the face's object's name as a string
    polyInfo:           Stores a list which holds a string of the face's vertices in one element
    split:              A list which seperates the polyInfo string into multiple elements
    list:               A list containing each of the face's vertices in seperate elements
    '''
    faceObjectName = face[0].split('.')[0]
    polyInfo = cmds.polyInfo(fv=True)
    split = polyInfo[0].split(' ')
    if(split[0] != 'FACE' or faceObjectName != 'terrain'): #if the face var doesn't store a face or is not on the terrain object, exit function
        cmds.confirmDialog( title='Error', message="Select a face/faces to flatten on the terrain", button=['ok'], defaultButton='ok', cancelButton='ok', dismissString='ok' )
        return
    ''' modifying the list to extract the data '''
    split.remove('')
    list = []
    for i in split:
        if i == '' or i == 'FACE' or i == '\n':
            continue
        else:
            list.append(str(i))
    list.remove(list[0])
    return(list) #returns a list containing the verts which make up the selected face

def listSelectedFaces():
    ''' Lists selected faces
    '''
    selection = cmds.ls(sl=True) #stores the maya selection as a var 
    faces = []
    for face in selection: #loops through each selected face
        seperatedFaces = cmds.filterExpand(face, sm=34) #sm flag is a selection mask where passing 34 only selects faces
        faces.append(str(seperatedFaces[0]).split(',')) #appends the face list with the current selected face
    return faces

def flattenFaces(): 
    ''' Flattens the face selected by the user to its average y level
    
    vtxYValues:     integer holding the sum of the vertices' y values
    faceVerts:           List containing each of the face's vertices in seperate elements
    vtx:            Integer storing integer number of the current vertex being accessed
    vtxXYZ:         List storing the X Y and Z integer values of the current vertex
    '''
    if areFacesSelected(True) == 0: #if faces aren't selected, exit function
        return
    selectedFaces = listSelectedFaces() #store the selected faces in the variable
    for face in selectedFaces: #loop through each face
        vtxYValues=0 #intialise vtxYValues variable
        face = cmds.ls(sl=True) #store the selected face in the face var
        faceVerts = getFaceVTXValues(face) #store the 
        for i in range(len(faceVerts)): #loop the n.o. times that there are faces
            vtx=faceVerts[int(i)] #set the current vtx
            vtxXYZ = cmds.pointPosition('terrain.vtx['+vtx+']') #extract the vtx's XYZ coords
            vtxYValues = vtxYValues + vtxXYZ[1] #add the y values of the verts together
        for i in faceVerts:
            cmds.softSelect(sse=True, ssd=2)  
            cmds.move(vtxYValues/len(faceVerts),y=True) #move each of the face's vertices to the average Y value of all of them
            cmds.softSelect(sse=False)              

def createTrenches(softSelectDist, depth):
    '''  Creates trenches (holes in the ground) used to make rivers or valleys

    softSelectDist:    Int determines the smoothness of the trench walls
    depth:             Int stores the depth of the trench
    '''
    if areFacesSelected(True) == 0: #if faces aren't selected exit function
        return()
    cmds.softSelect(sse=False) #disable soft select
    selection = cmds.ls(sl=True) #store the selected faces in the selection var
    if (softSelectDist > 0): #if the softSelectDist is greater than 0, enable soft select with the 
        cmds.softSelect(sse=True, ssd=softSelectDist) 
    cmds.move((-1)*depth, y=True, r=True) #move the faces relatively downwards by the depth
    cmds.softSelect(sse=False) #disable soft select
         
def createWaterCube(seaLevel):
    ''' Creates a water level
    
    seaLevel = integer input by user to determine height of the water
    '''
    
    global globalSeaLevel #use the global variable
    globalSeaLevel = seaLevel #sets the global sea level var to the input sea level

    deleteObjects('water') #if an existing water block exists, delete it
    cmds.polyCube(n='water',w=19.9,h=20,d=19.9,sx=9,sz=9) #creates the water block #OLD W AND d = 20
    cmds.xform(t=(0,globalBottomOfCube,0)) #sets the pivot point to 0,-10,0
    cmds.move(0,seaLevel,0, r=True) #moves the top of the cube to be at the input sea level
    totalVerts = cmds.polyEvaluate('water', v=True) #stores n.o. verts on the water
    ''' Add water texture on top of the cube '''
    for vtx in range(0, totalVerts): #loops through each vert 
        if vtx<10 or vtx>108: #if the vertices are not on the top, skip vert ()
            continue
        heightOffset = 0.2
        randomHeight = random.uniform(-1.0*heightOffset, heightOffset) #randomHeight = a random int between the negative and positive height offset 
        cmds.select('water.vtx[' + str(vtx) + ']') #select the current vtx
        cmds.move(randomHeight, y=True, r=True) #offset the vtx by the random height
    cmds.select('water.vtx[0:9]', 'water.vtx[110:199]') #select all of the verts on the bottom of the cube and translate their Y coords to -10.1 #NOTE: Fix constant values
    cmds.move(globalBottomOfCube, y=True) #10.1

    #boolean differentiation isolates the water from the terrain
    #cmds.duplicate('terrain')
    #cmds.polyBoolOp('water', 'terrain1', op=2, n='water')
    #cmds.delete(ch=True)
    #cmds.rename('water')
    #seperateWater()
    
def undoFunc():
    ''' Allows a UI button to call the undo function '''
    cmds.undo() 

def redoFunc():
    ''' Allows a UI button to call the undo function '''
    cmds.redo() 

def importOBJ(fileName, importedName, newName, scaleValue, error1, error2):
    ''' Imports a specified OBJ file from the asset folder
    
    fileName:        String name(including .obj) of the file
    importedName:    String of the imported objects name
    newName:         String to rename the object 
    scaleValue:      Integer scale factor (to make the OBJs consistent style)
    error1:          String to aid the error message
    error2:          String to aid the error message
    
    filePath:        String path of the asset folder
    errorCheck:      Boolean which is set to True when an error occurs to trigger the error message
    '''
    global filePath #accesses the global filePath var
    if(cmds.objExists(newName) == True): #if the file
        return() 
    errorCheck=0 #initialises the errorcheck var to 0 [no error detected]
    try: #attempt to open the file specified
        cmds.file(filePath+fileName, i=True)
        cmds.select(importedName)
        cmds.rename(newName) #rename the object for easier access
        if(newName == 'tallTreeOBJ' or newName == 'houseOBJ'):
            cmds.xform(ztp=True) #resets the pivot points for the talltree and house objects [their pivot is in a bad place originally]
        if(newName == 'houseOBJ'):
            cmds.xform(sp=[0, -0.5, 0], rp=[0, -0.5, 0], r=True)
        cmds.move(1000,1000,1000) #moves the original objects far away so the user cannot accidently edit them, and they won't have to be imported ever
        cmds.scale(scaleValue,scaleValue,scaleValue) #scale the object to the imported value
    except: #if the file isn't found
        if(error1 == 'building'): #if the object type is a building replace it with a cube
            cmds.polyCube(n=newName, w=1, h=1, d=1.25)
        else: #otherwise replace the object with a sphere
            cmds.polySphere(n=newName, r=1)
        cmds.move(1000,1000,1000)
        print(error1 + " model not loaded in")
        errorCheck=1
    if(errorCheck==1):
        errorMessage('One or more ' + error1 +' models not found, replacing with ' + error2 + "'s\nGo into the guide tab, delete OBJ's & fix the path")

def generateTrees(spawnRate, treeHeight, minTreeSize, maxTreeSize, maxSteepness):        
    ''' Generates trees on the plane

    Note: Vertices on the outer edge of the plane are discarded so
          trees don't spawn off of the edge

    spawnRate:             Integer % chance that a tree will spawn on each vertex
    treeHeight:          Integer y level where small trees spawn < tree height and tall trees spawn on y levels > treeHeight
    minTreeSize:         Integer minimum tree size (scale factor) input by the user
    maxTreeSize:         Integer maximum tree size (scale factor) input by the user
    maxSteepness:        The steepest gradient (integer %) of the slope that trees can spawn on
    '''
    '''
    Other Variables:    
    insidePlaneVerts:    List of vertices on the edge of the plane
    outsidePlaneVerts:   List of vertices not on the edge of the plane
    errorCheck:          Boolean which is set to True when an error occurs to trigger the error message
    
    vtxCount:            Integer of the current vertex being accessed used for the progress bar
    noPlaneVerts:        Integer total of vertices on the plane
    noInsideVerts:       Integer total of vertices not on the edge of the plane
    progress2:           Integer % progress
    mesh:                String stores the name of the current selected mesh
    normal:              List storing the normal's vector (X,Y,Z integers) of the currently accessed vertex
    tree:                Identifier for the current tree being created
    vtxPos:              List of the integer X Y Z corrdinates of the currently accessed vertex
    treeSpread:          The max/min limits of the random tree X/Z translation
    randomScale:         The scale factor of the current tree in the user-set range
    treeObjs:            List of object string names which begin with tree
    '''

    global globalSeaLevel

    '''if the terrain doesn't exist, exit'''
    if (cmds.objExists('terrain') == False):
        errorMessage('Create a terrain first')
        return

    '''delete existing trees, initialise values, make sure the tree files are located'''
    errorCheck=0
    vtxCount=0
    cmds.select('terrain')
    noPlaneVerts = cmds.polyEvaluate(v=True)
    deleteObjects(delTreeList)
    importOBJ('tree.obj', 'Tree', 'smallTreeOBJ', 0.3, 'tree', 'sphere')
    importOBJ('tree2.obj', 'pCylinder1', 'tallTreeOBJ', 0.3, 'tree', 'sphere')
    cmds.progressWindow(t='Progress Bar', progress=0, status='Waiting...', ii=True)
    
    '''loop through every vertex on the inside of the plane'''
    cmds.select('terrain')
    print (range(0, noPlaneVerts))
    for i in range(0, noPlaneVerts):
        if(getVTXPosition(i) != 'Inside'):
            continue
        if(cmds.progressWindow(q=True, ic=True)):
            break
        vtxCount=vtxCount+1
        cmds.select('terrain')
        mesh = pm.selected()[0]
        normal = mesh.vtx[i].getNormal()
        
        if cmds.objExists('water') == False:
            globalSeaLevel = -99


        '''only create a tree if the random number is greater than
         the spawn rate and the terrain is flat enough'''
        vtxYlevel=cmds.pointPosition('terrain.vtx[' + str(i) + ']')[1]
        if(random.randint(0,100) < spawnRate and normal[1] > 1-maxSteepness and vtxYlevel > globalSeaLevel + 0.3 ):            
            '''spawn a tall tree above the input height and a small tree below'''    
            if(vtxYlevel < treeHeight ):
                tree = cmds.instance('smallTreeOBJ', n='Tree1')
                cmds.select(tree)
            else:
                tree = cmds.instance('tallTreeOBJ', n='Tree1')
                cmds.select(tree)
            
            '''adjust the position of the tree'''
            vtxPos = cmds.pointPosition('terrain.vtx[' + str(i) + ']')
            treeSpread = 0.3
            cmds.move(vtxPos[0] + random.uniform(-treeSpread,treeSpread), vtxPos[1], vtxPos[2] + random.uniform(-treeSpread,treeSpread), tree) #move the tree to the vert's position, with a slightly random x and z nudge to decrease uniformity 
            cmds.rotate(random.randint(0,360), y=True)
            randomScale=float(random.uniform(minTreeSize,maxTreeSize)/100.0)
            cmds.scale(randomScale, randomScale, randomScale)

            '''increase the visual progress on the progress bar'''
            progress2 = float((float(vtxCount)/float(noPlaneVerts+1)) * 100)
            cmds.progressWindow(edit=True, progress=progress2, status='generating trees')
    cmds.progressWindow(endProgress=1)
    treeObjs = cmds.ls('Tree*') #Selects all objects with the prefix 'Tree' then groups them
    
    '''group the trees'''
    if treeObjs:
        cmds.select(treeObjs)
    cmds.group(n="Trees")

def calculateSquareCentre(startXIndex, startYIndex, blockSize, width, terrainData, levelScale):
    ''' Calculates the height of the square step's centre 
    Function written by Xiaosong Yang
    
    startXIndex: index of the current block being calulated in the x direction   
    startYIndex: start y value
    blockSize: size of the current block being calulated (starts off at the max, gradually decreases)
    width: width of the plane
    terrainData: list of coordinates of each point 
    levelScale: scale of the terrain
    
    '''
    levelScale=1.0
    terrainData[startXIndex+blockSize/2+(startYIndex+blockSize/2)*width] = 0.25*( \
        terrainData[startXIndex           + startYIndex*width] + \
        terrainData[startXIndex+blockSize + startYIndex*width] + \
        terrainData[startXIndex           + (startYIndex+blockSize)*width] + \
        terrainData[startXIndex+blockSize + (startYIndex+blockSize)*width])+ m.sqrt(levelScale)*random.random()
    
def calculateDiamondCentre(startXIndex, startYIndex, blockSize, width, height, terrainData, levelScale):
    ''' Calculates the height of the diamonds steps centre 
    Function written by Xiaosong Yang
      
    startYIndex: start y value
    blockSize: size of the current block being calulated (starts off at the max, gradually decreases)
    width: width of the plane
    terrainData: list of coordinates of each point 
    levelScale: scale of the terrain
    '''
    levelScale=1.0
    tmp = 0
    count = 0;
    if startXIndex>0:
        tmp = tmp + terrainData[startXIndex-blockSize+startYIndex*width]
        count=count+1
    if startYIndex>0:
        tmp = tmp + terrainData[startXIndex+(startYIndex-blockSize)*width]
        count=count+1
    if startXIndex<width-1:
        tmp = tmp + terrainData[startXIndex+blockSize+startYIndex*width]
        count=count+1
    if startYIndex<height-1:
        tmp = tmp + terrainData[startXIndex+(startYIndex+blockSize)*width]
        count=count+1
    terrainData[startXIndex+startYIndex*width] = tmp/count + m.sqrt(levelScale)*random.random()
               
def createTerrain(n, c1Height, c2Height, c3Height, c4Height, smooth):
    ''' Performs the diamond square algorithm
        Function adapted from Xiaosong Yang
    
    n
    c[n]height:    Integer input value of a corner of the plane
    smooth:        Integer input value holding the amount of subdivisions to perform
    '''
    global wallsExist
    wallsExist = False
    
    deleteObjects(delTerrainList)
    subdx = subdy = 2 ** n
    width = height = subdx + 1 
    terrain = cmds.polyPlane(n='terrain', axis=[0,1,0], w=20, h=20, sx=subdx, sy=subdy, ch=False)[0]
    
    # initialise the terrain height data
    terrainData = [0.0]*width*height
    # the four corner
    terrainData[0] = c1Height
    terrainData[width-1] = c2Height
    terrainData[(height-1)*width] = c4Height
    terrainData[height*width-1] = c3Height
    
    for i in range(n, 0, -1): # different resolution
        blockSize = 2**i
        # for each resolution level, we need to calculate the height level for many blocks
        # calculate the square centre
        num = 2**(n-i)
        for j in range(num):
            startXIndex = j * blockSize
            for k in range(num):
                startYIndex = k * blockSize
                calculateSquareCentre(startXIndex, startYIndex, blockSize, width, terrainData, 1.0*i/n)
        num = 2**(n-i+1)+1
        for j in range(num):
            startXIndex = j * blockSize/2
            for k in range(num):
                startYIndex = k * blockSize/2
                if (j+k)%2==1:
                    calculateDiamondCentre(startXIndex, startYIndex, blockSize/2, width, height, terrainData, 1.0*i/n)
    
    # change the vertex position of the plan according tot he terrainData
    for i in range(height):
        for j in range(width):
            cmds.move(0, terrainData[i*width+j], 0, terrain+".vtx["+str(i*width+j)+"]", r=True)
    cmds.polySmooth(kb=False, dv=smooth)
    cmds.delete(ch=True)

def createBuildings(buildingsPerFace, maxSize, minSize, rotation):    
    ''' Generates the buildings on the selected face(s)
    
    buildingsPerFace:    Integer number of how many buildings are generated per face
    maxSize:             int The maximum size of each building
    minSize:             int The minimum size of each building
    rotation:            int angle of rotation for the building
    '''

    if areFacesSelected(False) == False: #exit function is faces arent selected
        return  
    flattenFaces()            
    if buildingType==0: #import the .OBJ files
        importOBJ('city.obj', 'pCube1', 'cityOBJ', 1, 'building', 'cube')
    elif buildingType==1:
        importOBJ('house.obj', 'pCube1', 'houseOBJ', 1, 'building', 'cube')
    
    ''' initialise variables '''
    selection=cmds.ls(sl=True)
    vtxXValues = 0
    vtxYValues = 0
    vtxZValues = 0
    faceVerts = []
    face = cmds.ls(sl=True)
    faceVerts = getFaceVTXValues(face)
    print(faceVerts)
    
    ''' store all of the face values so that the centre of the face can be located to place to building on'''
    for i in range(len(faceVerts)):
            vtx=faceVerts[int(i)]
            vtxXYZ = cmds.pointPosition('terrain.vtx['+vtx+']')
            vtxXValues = vtxXValues + vtxXYZ[0]
            vtxYValues = vtxYValues + vtxXYZ[1]
            vtxZValues = vtxZValues + vtxXYZ[2]
    
    grp = cmds.ls('Buildings') #ungroups buildings so new group can be made
    if grp:
        cmds.ungroup(grp)
    
    ''' duplicate the stored obj, puts it in the correct position and resizes it'''
    if(buildingType==0):
        building = cmds.duplicate('cityOBJ', n='building1')
        cmds.select(building)
        cmds.move(vtxXValues/4,vtxYValues/4,vtxZValues/4)
        cmds.select(building[0]+'.f[1]')
        cmds.move(0,random.uniform(-1,4),0, r=True)
    else:
        building = cmds.duplicate('houseOBJ', n='building1')
        cmds.select(building)
        cmds.move(vtxXValues/4,vtxYValues/4 +0.5,vtxZValues/4)
    cmds.select(building)
    randomScaleFactor = random.uniform(minSize, maxSize)/100
    cmds.scale(randomScaleFactor, randomScaleFactor, randomScaleFactor, r=True)  
    cmds.rotate(0, rotation, 0) 

    buildingObjs = cmds.ls('building*') #Selects all objects with the prefix 'building' then groups them
    if buildingObjs:
        cmds.select(buildingObjs)
    cmds.group(n="Buildings")
    cmds.select(selection)

def changeFilePath():
    ''' Changes the global filepath string if a non empty string is entered '''
    global filePath
    path = cmds.textField("newFilePath",query=True,text=True) #path store contents of the text field "newFilePath" as a string
    if(path != ''): #if the text box has words in it
        path = path.replace('"' ,'')
        path = path+"/"
        filePath = path #store the path contents in the global filepath var 
    print(filePath)
    cancelProc()
    createUI() 

def initialiseRadioButtons(r, *args):
    ''' Sets variables' values based on which radiobuttons are pressed
    
    r:                  Integer the radiobutton will pass when clicked
    
    Other Variables:
    buildingType:       Integer stores whether the building is a skyscraper (=0) or house (=1)
    '''
    global buildingType
    if(r==1):
        buildingType=0 #city
    elif(r==2):
        buildingType=1 #house

def createWalls():
    ''' Returns a string saying wether the vertex input is or isn't on the outer edge of the plane
    
    vtx:         Integer identifier of the vertex used
    
    polyInfo:    List of one string element containing the edge identifies connected to the vertex
    Split:       List of the polyinfo string split up into words
    list:        List holding only the edge integer identifiers connected to the vertex
    '''
    global wallsExist
    cmds.select('terrain')
    noVerts = cmds.polyEvaluate(v=True)
    progressCancelled = True
    
    '''checking if the terrain has already been extruded'''
    for vtx in range(noVerts):
        if(cmds.pointPosition('terrain.vtx['+str(vtx)+']')[1] == globalBottomOfCube):
            wallsExist = True
            break
    
    if (cmds.objExists('terrain') == False or wallsExist==True):
        errorMessage('No terrain to create a cube or cube already exists')
        print(wallsExist)
        return
    
    '''initialise progress window'''
    progressStatus = 'Turning terrain into a cube, please wait'
    progress = 0
    cmds.progressWindow(t='Progress Bar', progress=0, status=progressStatus, ii=True)

    '''find n.o. edges'''
    cmds.select('terrain')
    noEdges = cmds.polyEvaluate(e=True)
    noTopFaces = cmds.polyEvaluate(f=True) #saved
    outsideEdges = []
    for edge in range(noEdges): #loop through every edge  
        if(cmds.progressWindow(q=True, ic=True)):
            cmds.progressWindow(endProgress=1)
            return
        cmds.select('terrain.e[' + str(edge) + ']')
        polyInfo = cmds.polyInfo(ev=True)
        split = polyInfo[0].split(' ')
        for i in split:
            split.remove('')
        for i in split:
            if i == 'Hard\n':
                edgeNum = str(split[1])
                outsideEdges.append(edgeNum[:-1])

        progress = 100*(edge/noEdges)

    cmds.select(d=True)

    progressStatus='Extruding other plane vertices'
    progressCounter = 0
    for edge in outsideEdges:
        if(cmds.progressWindow(q=True, ic=True)):
            cmds.progressWindow(endProgress=1)
            return

        cmds.select('terrain.e[' + str(edge) + ']', add=True)

        progressCounter=progressCounter+1
        progress = 100*(progressCounter/len(outsideEdges))
        #progress = float(int(edge)/len(outsideEdges))
        cmds.progressWindow(edit=True, progress=progress, status=progressStatus)

    cmds.polyExtrudeEdge(t=(0,globalBottomOfCube,0), kft=True)
    
    '''Flatten the extruded vertices'''
    cmds.select('terrain')
    noNewVerts = cmds.polyEvaluate(v=True)
    cmds.select(d=True)
    progressStatus='Extruding outer plane vertices'
    progressCounter = 0
    for vtx in range(noVerts,noNewVerts):
        if(cmds.progressWindow(q=True, ic=True)):
            cmds.progressWindow(endProgress=1)
            return

        cmds.select('terrain.vtx[' + str(vtx) + ']', add=True)

        progressCounter=progressCounter+1
        progress = 100*(progressCounter/len(range(noVerts,noNewVerts)))
        cmds.progressWindow(edit=True, progress=progress, status=progressStatus)
    cmds.move(globalBottomOfCube, y=True)

    '''Create the bottom too''' #NOTE fix all the costant values (e.g. h=w=20, move to -10 etc.)
    bottomPlaneSubdivs = m.sqrt(noTopFaces)
    cmds.polyPlane(n='bottom', sx=bottomPlaneSubdivs, sy=bottomPlaneSubdivs, h=20, w=20)
    cmds.move(globalBottomOfCube, y=True)
    cmds.scale(1,-1,1)
    cmds.polyUnite('terrain', 'bottom')
    cmds.delete(ch=True)
    cmds.rename('terrain')
    cmds.polyMergeVertex(d=0.001)

    wallsExist=True

    ''' Delete History '''
    cmds.select('terrain')
    cmds.delete(ch=True)

    '''End progress'''
    cmds.progressWindow(endProgress=1) #d

def seperateWater():
    global globalSeperatedSea
    #if globalSeperatedSea == True:
        #return()
    cmds.duplicate('terrain')
    cmds.polyBoolOp('water', 'terrain1', op=1, n='water')
    cmds.delete(ch=True)
    cmds.select('terrain')
    cmds.delete()
    cmds.select('water')
    cmds.rename('terrain')
    globalSeperatedSea = True

def createCaves(sphereRadiusMax, sphereRadiusMin, noSpheres):
    '''if the terrain doesn't exist, exit'''
    if (cmds.objExists('terrain') == False or wallsExist == False):
        errorMessage('Create a cube terrain first')
        return


    ''' NOTE: IF WATER EXISTS THEN GIVE ERROR MSG HERE SAYING IF U CONTINUE THE WATER AND LAND IS COMBINED'''
    seperateWater() #merge sea and water ew

    #set values
    xPos=0
    yPos=0
    zPos=0
    xPosDiff=0
    yPosDiff=0
    zPosDiff=0
    up=True
    left=True

    #generate cave
    for i in range(noSpheres):
        #calculate their positions
        xPosDiff = random.uniform(2,3)
        
        yPosDiff = random.uniform(-1,1)
        if up==True:
            yPos += 1.5
        else:
            yPos -= 1.5
        
        zPosDiff = random.uniform(-1,1)
        if left==True:
            zPos -= 1.5
        else:
            zPos += 1.5
        
        if yPosDiff > 0:
            up=True
        else:
            up=False         
        if zPosDiff > 0:
            left=False
        else:
            left=True
          
        xPos += xPosDiff
        yPos += yPosDiff    
        zPos += zPosDiff
        
        #create the spheres
        cmds.polySphere(n='cave0', r=random.uniform(sphereRadiusMin,sphereRadiusMax), sx=random.randint(4,6), sy=random.randint(4,6))    
        cmds.move(xPos,yPos,zPos,r=True)
    
    #boolean union the shapes 
    for i in range(noSpheres):    
        if i==1:
            s1='cave0'
            s2='cave1'
            cmds.polyCBoolOp(s1, s2, op=1, n='mergedCave')
            cmds.delete(ch=True)
        if i>1:
            s2='cave'+str(i)
            cmds.polyCBoolOp('mergedCave', s2, op=1, n='mergedCave')
            cmds.delete(ch=True)
            cmds.rename('mergedCave')

    #make it more of a cave shape
    cmds.polyReduce(p=50)
    cmds.polySmooth(dv=2)
    
    #move the cave to be more in the terrains ground
    cmds.move(-20,random.uniform(-5,-12),0,r=True)
    cmds.rotate(0,random.randint(0,360),0)

    #difference the cave with the terrain to merge them 
    cmds.polyCBoolOp('terrain', 'mergedCave', op=2, n='terrain')
    cmds.delete(ch=True)
    cmds.rename('terrain')
    
def createRandomTerrain(checkboxesUsed):
    ''' Generates a random terrain by calling a combination of all of the functions

    checkboxesUsed: if the checkboxes are used, import True
    '''
    global wallsExist

    ''' initialis '''
    wallsExist=False
    waterExists=False
    globalSeperatedSea=False   
    trees=True
    sea=True
    mountains=True
    lowSubdivs=False
    cube=True
    caves=True

    if checkboxesUsed == True: #if the checkboxes are used, initialise their values
        trees = cmds.checkBoxGrp('randomTerrainCBG', q=True, v1=True)
        sea = cmds.checkBoxGrp('randomTerrainCBG', q=True, v2=True)
        mountains = cmds.checkBoxGrp('randomTerrainCBG', q=True, v3=True)
        lowSubdivs = cmds.checkBoxGrp('randomTerrainCBG2', q=True, v1=True)
        cube = cmds.checkBoxGrp('randomTerrainCBG2', q=True, v2=True)
        caves = cmds.checkBoxGrp('randomTerrainCBG2', q=True, v3=True)
        print str(trees) + str(sea) + str(mountains) + str(lowSubdivs)

    '''Create the terrain'''
    if (lowSubdivs == True):
        createTerrain(3, random.randint(0,8), random.randint(0,8), random.randint(0,8), random.randint(0,8), 1)
    else:
        createTerrain(random.randint(3,4), random.randint(0,8), random.randint(0,8), random.randint(0,8), random.randint(0,8), random.randint(0,2))
    
    '''set variables'''
    cmds.select('terrain')
    noFaces = cmds.polyEvaluate(f=True)
    noVerts = cmds.polyEvaluate(v=True)
    
    '''find lowest point to know where to put sea'''
    lowestYValue = 10
    greatestYValue = -15
    for vtx in range(0, noVerts-1):
        vtxY = cmds.pointPosition('terrain.vtx['+str(vtx)+']')[1]
        if(vtxY < lowestYValue):
            lowestYValue = vtxY
        elif(vtxY > greatestYValue):
            greatestYValue = vtxY   

    '''Smooth :)'''
    if (lowSubdivs == False):
        smoothTerrain()
     
    cmds.select('terrain')
    noFaces = cmds.polyEvaluate(f=True)
    noVerts = cmds.polyEvaluate(v=True)
    
    '''Create some mountains'''
    if (mountains == True):
        def randMountain(rchance,rnum1,rnum2,rnum3,rnum4):
            if random.uniform(0,1) > rchance:
                randomMountainFace = random.randint(0, noFaces-1)
                cmds.select('terrain.f['+str(randomMountainFace)+']')
                createMountain(random.uniform(rnum1,rnum2),random.uniform(rnum3,rnum4))

        randMountain(0.3,1,6,0.5,5)
        randMountain(0.5,2,7,0.5,3)
        randMountain(0.5,2,7,0.5,3)
        randMountain(0.5,2,7,0.5,3)
    
    '''add some heightOffset to the surface'''
    cmds.select('terrain')
    noVerts = cmds.polyEvaluate(v=True)
    if(noVerts < 2000):
        bumpTerrain(random.uniform(0.05,0.25))
    elif(noVerts < 4000):
        bumpTerrain(random.uniform(0.05,0.1))
    elif(noVerts < 5000):
        bumpTerrain(random.uniform(0.02,0.05))
     
    '''Generates sea level (1 in 2 chance)'''          
    if (checkboxesUsed == True and sea==True and random.uniform(0,1)) or (checkboxesUsed == False and random.uniform(0,1)):
        print 'creating sea'
        #createWaterCube(random.uniform(lowestYValue+1.0,lowestYValue+1.5)+1)
        createWaterCube(random.uniform(float(lowestYValue)+2.5,float(greatestYValue)-1.0))
        waterExists=True   

    '''Generates some lakes/rivers'''
    if random.uniform(0,1) > 0.3 and waterExists==True:
        cmds.select('terrain.f['+ str(random.randint(0,noFaces-1)) + ']')
        '''for i in range(random.randint(5,15)):
            cmds.select(cmds.pickWalk(), add=True)
        createTrenches(random.uniform(), random.uniform)'''
        createTrenches(random.uniform(1,5), random.uniform(0,2))
    

    '''Generate trees (3 in 5 chance of spawning)'''
    if trees == True:
        if noVerts < 1000:
            generateTrees(random.uniform(5,11), 5.5, 50, 80, 0.3)
        elif noVerts > 10000:
            generateTrees(random.uniform(1,4), 5.5, 15, 25, 0.3)
        elif noVerts > 3000:
            generateTrees(random.uniform(2,5), 5.5, 15, 30, 0.3)
        else:
            generateTrees(random.uniform(2,7), 5.5, 30, 40, 0.3)

    '''Turn into a cube'''
    if cube == True:
        createWalls() #d

    '''Generate Caves'''
    if caves == True:
        for i in range(0,random.randint(1,4)):
            if lowSubdivs == True:
                createCaves(3.5, 2.5, 20)
                return()
            createCaves() #use noverts to determine how big to make the caves

def repeatedButtons():
    ''' ui elements repeated on each tab '''
    cmds.separator(h=15)
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1,166), (2,166), (3,166)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.button(label = "undo", command=lambda *args: undoFunc())
    cmds.button(label = "redo", command=lambda *args: redoFunc())
    cmds.button(label = "close window", command=lambda *args: cancelProc()) 
    cmds.setParent( '..' )
    cmds.setParent( '..' )

def sep(h):
    ''' Shortens the cmds.separator call
    
    h: integer value of the separators height flag
    '''
    cmds.separator(h=h, st='none')#d
        
def createUI():
    ''' Generates the whole user interface '''
    global filePath
    windowID = 'Landscaper'
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    cmds.window(windowID, widthHeight=(500, 400), resizeToFitChildren=True)
    form = cmds.formLayout()
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
    
    ''' Guide Tab '''
    child5 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.frameLayout(borderVisible=False, lv=False)
    cmds.image(image=filePath+"banner2 ssresize.PNG",width=500,height=100)
    cmds.setParent("..")
    sep(10)
    cmds.text('Use the automation tab to automatically generate a terrain, then customise it further in the editor')
            
    cmds.separator(h=40)
    cmds.text('    Ideas to make a better terrain', bgc=(0.5,0.7,0.9))
    sep(5)
    cmds.text('    The best way to create a terrain is by using the terrain editor tabs in order. \n    Start off with low subvidisions, then smooth later to reduce lag', al='left')
    sep(5)
    cmds.text('    1. Create a few of different mountains a few faces apart instead of just one', al='left')
    cmds.text('    2. When flattening faces, flatten a cluster of adjacent faces \n    3. If you flatten faces on the side of a hill, a cliff can be produced \n', al='left')
    cmds.separator(h=40)
    cmds.text('    If you need to reset the objects, click the button below to delete them', bgc=(0.9,0.5,0.5))
    sep(5)       
    cmds.text("    (When an .obj file isn't located, it will be replaced with a sphere or cube. Click this button to reset them, then change the path)", al='left')
    sep(5) 
    cmds.button(label='Delete OBJS', c=lambda *args: deleteObjects(delOBJList))
    newFilePath=''
    cmds.separator(h=45)
    cmds.text('    If you need to reset the asset folder path', bgc=(0.5,0.9,0.5))
    sep(5)
    cmds.text('    Hold shift and right click the asset folder, then copy the path and paste it here \n    Use this format: "C:/Users/jamal/OneDrive - Bournemouth University/Semester 2/Python Project/" \n    When the UI images load in, you have set the file path correctly', al='left')
    sep(5)
    cmds.textField("newFilePath", pht='Enter the file path', tx='"C:\Users\jamal\OneDrive - Bournemouth University\Year 1\Semester 2\Python Project\Final Submission\"')
    sep(5)
    cmds.button(label='Change file path', c=lambda *args: changeFilePath())
    repeatedButtons()

    ''' Automation Tab '''
    child6 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.text('Click the button directly below to generate a completely random terrain')
    sep(5)
    cmds.button(label = "Generate Completely Random Terrain", command=lambda *args: createRandomTerrain(False))
    cmds.separator(h=30)
    cmds.text('Check the boxes of the things you want in your terrain, then click the bottom button')
    sep(5)
    randomTerrainCBG = cmds.checkBoxGrp('randomTerrainCBG', numberOfCheckBoxes=3, label='', labelArray3=['Trees', 'Sea', 'Mountains'] )
    randomTerrainCBG2 = cmds.checkBoxGrp('randomTerrainCBG2', numberOfCheckBoxes=3, label='', labelArray3=['Low n.o subdivs','Cube Terrain', 'Caves'] )
    sep(10) #probs could do 4 boxes per row
    cmds.button(label = "Generate Terrain", command=lambda *args: createRandomTerrain(True))
    cmds.separator(h=20)
    cmds.text('After generating the terrain, you can proceed to edit the terrain or generate structures using the other tabs')
    sep(5)
    repeatedButtons()
    
    ''' Editor form '''
    child7=cmds.columnLayout(adjustableColumn=True)    
    form1 = cmds.formLayout()
    tabs1 = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    cmds.formLayout( form1, edit=True, attachForm=((tabs1, 'top', 0), (tabs1, 'left', 0), (tabs1, 'bottom', 0), (tabs1, 'right', 0)) )
 
    ''' Base Terrain Tab '''
    child1 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.frameLayout(borderVisible=False, lv=False)
    cmds.image(image=filePath+"banner ssresize.PNG",width=500,height=100)
    cmds.setParent("..")
    sep(5)
    cmds.text('Play around with the first set of sliders, then click generate terrain to get a base terrain that you would like.')
    sep(5)
    nControl = cmds.intSliderGrp(label='heightOffset', min=0, max=5, value=3, step=0.5, sbm=1, field=True)
    smoothControl = cmds.intSliderGrp(label='Smoothness (subdivs)', min=0, max=5, value=1, step=1, sbm=1, field=True)
    sep(10)

    c1HeightControl = cmds.intSliderGrp(label='Corner 1 Height', min=-5, max=10, value=0, step=1, sbm=1, field=True)
    c2HeightControl = cmds.intSliderGrp(label='Corner 2 Height', min=-5, max=10, value=0, step=1, sbm=1, field=True)
    c3HeightControl = cmds.intSliderGrp(label='Corner 3 Height', min=-5, max=10, value=0, step=1, sbm=1, field=True)
    c4HeightControl = cmds.intSliderGrp(label='Corner 4 Height', min=-5, max=10, value=0, step=1, sbm=1, field=True)
    sep(10)
    
    cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1,250), (2,250)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.button(label = "Generate Terrain", command=lambda *args: createTerrain(cmds.intSliderGrp(nControl, q=True, v=True), cmds.intSliderGrp(c1HeightControl, q=True, v=True), cmds.intSliderGrp(c2HeightControl, q=True, v=True), cmds.intSliderGrp(c3HeightControl, q=True, v=True), cmds.intSliderGrp(c4HeightControl, q=True, v=True), cmds.intSliderGrp(smoothControl, q=True, v=True)))
    cmds.button(label = "Delete Terrain (deletes all generated objects)", command=lambda *args: deleteObjects(delTerrainList))
    cmds.setParent( '..' )
    cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1,166), (2,166), (3,166)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.button(label = "Slightly Flatten Plane", command=lambda *args: bumpTerrain(0))
    cmds.button(label = "Flatten Selected Faces", command=lambda *args: flattenFaces())
    cmds.button(label = "Smooth (subdivide) Plane Once", command=lambda *args: smoothTerrain())
    cmds.setParent( '..' )
    repeatedButtons()

    ''' Terraforming Tab '''
    child2 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.text('Add heightOffset to the terrain')
    sep(5)
    bumpControl = cmds.floatSliderGrp(label='heightOffset Height', min=0.01, max=0.5, value=0.2, step=0.01, sbm=1, field=True)
    sep(5)
    cmds.button(label = "Bump Plane", command=lambda *args: bumpTerrain(cmds.floatSliderGrp(bumpControl, q=True, v=True)))
    sep(20)
    cmds.text('Select a face, then create a mountain there')
    sep(10)
    mountainHeightControl = cmds.floatSliderGrp(label='Mountain height', min=0.1, max=20, value=6, step=0.1, sbm=1, field=True) 
    mountainRadiusControl = cmds.floatSliderGrp(label='Mountain radius', min=0.1, max=7, value=3, step=0.1, sbm=1, field=True)
    sep(10)
    cmds.button(label = "Create mountain on face", command=lambda *args: createMountain(cmds.floatSliderGrp(mountainRadiusControl, q=True, v=True), cmds.floatSliderGrp(mountainHeightControl, q=True, v=True)))
    sep(20)
    cmds.text('Select one of more faces to create a trench (select a line to make a river, or just make a valley)')
    sep(10)
    trenchDepthControl = cmds.floatSliderGrp(label='Trench depth', min=0, max=5, value=1, step=0.01, sbm=1, field=True)
    trenchRadiusControl = cmds.floatSliderGrp(label='Trench walls width', min=0, max=5, value=3, step=0.01, sbm=1, field=True)
    sep(10)
    cmds.button(label = "Create trench on face(s)", command=lambda *args: createTrenches(cmds.floatSliderGrp(trenchRadiusControl, q=True, v=True), cmds.floatSliderGrp(trenchDepthControl, q=True, v=True)))
    sep(10)
    cmds.text('Make sure to have finalised your terrain before adding trees or buildings')
    sep(5)
    cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1,166), (2,166), (3,166)], adjustableColumn=2)
    cmds.button(label = "Slightly Flatten Plane", command=lambda *args: bumpTerrain(0))
    cmds.button(label = "Flatten Selected Faces", command=lambda *args: flattenFaces())
    cmds.button(label = "Smooth (subdivide) Plane Once", command=lambda *args: smoothTerrain())
    cmds.setParent( '..' )
    repeatedButtons()

    child9 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.text('Generate water at a given depth')
    sep(10)
    waterDepthControl = cmds.floatSliderGrp(label='Sea level', min=globalBottomOfCube, max=10, value=1, step=0.01, sbm=1, field=True)
    sep(10)
    cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1,250), (2,250)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.button(label = "Create water", command=lambda *args: createWaterCube(cmds.floatSliderGrp(waterDepthControl, q=True, v=True)))
    cmds.button(label = "Delete water", command=lambda *args: deleteObjects('water'))
    cmds.setParent("..") 
    repeatedButtons()

    ''' Cave Tab '''
    child10 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    sphereRadiusMinControl = cmds.floatSliderGrp(label='Sphere Radius Min', min=1, max=10, value=1, step=0.01, sbm=1, field=True)
    sphereRadiusMaxControl = cmds.floatSliderGrp(label='Sphere Radius Min', min=0, max=9, value=1, step=0.01, sbm=1, field=True)
    noSpheresControl = cmds.intSliderGrp(label='Number of Sphere', min=5, max=20, value=1, step=1, sbm=1, field=True)
    cmds.button(label = "Generate Cave", command=lambda *args: createCaves(cmds.floatSliderGrp(sphereRadiusMaxControl, q=True, v=True), cmds.floatSliderGrp(sphereRadiusMinControl, q=True, v=True), cmds.intSliderGrp(noSpheresControl, q=True, v=True))) #sphereRadiusMax, sphereRadiusMin, noSpheres)
    repeatedButtons()

    ''' Tree Tab '''
    child3 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.frameLayout(borderVisible=False, lv=False)
    cmds.image(image=filePath+"bannertree ssresize.PNG",width=500,height=100)
    cmds.setParent("..")
    sep(5)
    cmds.text('     Adjust the sliders then click generate trees', al='left')
    cmds.text('     Above the tree species threshold height, tall trees will spawn, otherwise smaller trees will spawn', al='left')
    cmds.text('     The maximum angle goes from 0.01 spawning trees on only flat surfaces to 0.99 with trees anywhere', al='left')
    cmds.text('     Each vertice of the plane has a % chance of generating a tree, use a low spawn rate for a high vertex number', al='left')
    cmds.separator(h=20)
    noTreesControl = cmds.intSliderGrp(label='Spawn rate per vert', min=1, max=100, value=20, step=1, sbm=1, field=True)
    treeSteepnessControl = cmds.floatSliderGrp(label='Max angle trees grow on', min=0.01, max=0.99, value=0.3, step=0.01, sbm=1, field=True)
    differentTreeHeightControl = cmds.floatSliderGrp(label='Tree species threshold', min=0, max=10, value=4, step=0.01, sbm=1, field=True)
    sep(5)
    minTreeSizeControl = cmds.floatSliderGrp(label='Minimum Tree Size %', min=0.01, max=100, value=60, step=0.01, sbm=1, field=True)
    maxTreeSizeControl = cmds.floatSliderGrp(label='Maximum Tree Size %', min=0.01, max=100, value=80, step=0.01, sbm=1, field=True)
    #cmds.rowLayout(numberOfColumns=2)
    sep(10)
    cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1,250), (2,250)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.button(label = "Generate Trees", command=lambda *args: generateTrees(cmds.intSliderGrp(noTreesControl, q=True, v=True), cmds.floatSliderGrp(differentTreeHeightControl, q=True, v=True), cmds.floatSliderGrp(minTreeSizeControl, q=True, v=True), cmds.floatSliderGrp(maxTreeSizeControl, q=True, v=True), cmds.floatSliderGrp(treeSteepnessControl, q=True, v=True)))
    cmds.button(label = "Delete Trees", command=lambda *args: deleteObjects(delTreeList))
    cmds.setParent( '..' )
    repeatedButtons()
    
    ''' Building Tab '''
    child4 = cmds.columnLayout(adjustableColumn=True)
    sep(5)
    cmds.text('Select a face that you want to generate a building/buildings on')
    sep(5)
    #slider for 1-4 : select n.o. buildings per face
    noBuildingsControl = cmds.intSliderGrp(label='Buildings per face', min=1, max=4, value=1, step=1, sbm=1, field=True)
    cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1,20), (2,150), (3, 150), (4,150)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.separator(st='none')
    #radiobuttons asking for city buildings or houses
    cmds.text('Building Type:', al='left')
    cmds.radioCollection()
    status=0
    rb1=cmds.radioButton( label='Skyscraper', onc=lambda *args: initialiseRadioButtons(1), sl=True)
    rb2=cmds.radioButton( label='House', onc=lambda *args: initialiseRadioButtons(2))
    cmds.setParent( '..' )
    #slider for max & min building size
    minBuildingSizeControl = cmds.floatSliderGrp(label='Minimum Building Size %', min=30, max=100, value=45, step=0.01, sbm=1, field=True)
    maxBuildingSizeControl = cmds.floatSliderGrp(label='Maximum Building Size %', min=30, max=100, value=90, step=0.01, sbm=1, field=True)
    buildingRotationControl = cmds.floatSliderGrp(label='Building Rotation (deg)', min=0, max=360, value=0, step=0.01, sbm=1, field=True)
    #no max min
    sep(10)
    cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1,166), (2,166), (3,166)], adjustableColumn=2, columnAttach=[(1, 'both', 0), (2, 'both', 0) ])
    cmds.button(label = "Create a building", command=lambda *args: createBuildings(cmds.intSliderGrp(noBuildingsControl, q=True, v=True), cmds.floatSliderGrp(maxBuildingSizeControl, q=True, v=True), cmds.floatSliderGrp(minBuildingSizeControl, q=True, v=True), cmds.floatSliderGrp(buildingRotationControl, q=True, v=True)))
    cmds.button(label = "Delete all buildings", command=lambda *args: deleteObjects('Buildings')) 
    cmds.button(label = "Flatten Selected Faces", command=lambda *args: flattenFaces())
    cmds.setParent( '..' )
    sep(5)   
    repeatedButtons()
    
    ''' Finalise Tab '''
    child8 = cmds.columnLayout(adjustableColumn=True)   
    sep(5)
    cmds.button(label = "Turn terrain into a cube", command=lambda *args: createWalls())
    sep(5)
    cmds.text('Only turn the terrain into a cube when you are done otherwise errors may occur')
    cmds.separator(h=20)       
    cmds.button(label="Click here to delete the reference obj files to clear the outliner and viewport", c=lambda *args: deleteObjects(delOBJList))
    repeatedButtons()

    cmds.tabLayout( tabs1, edit=True, tabLabel=((child1, 'Base Terrain'), (child2, 'Terraforming'), (child10, 'Caves'),(child3, 'Trees'), (child4, 'Buildings'), (child8, 'Finalise'), (child9, 'Water')))
    cmds.setParent( '..' )
    
    cmds.tabLayout( tabs, edit=True, tabLabel=((child6, 'Automation'), (child7, 'Editor'), (child5, 'Guide')))
    cmds.showWindow()

if __name__=="__main__":
    createUI()
    
    
   #caves can only exist if sea doesnt and vice versa
