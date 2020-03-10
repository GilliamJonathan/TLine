import math
import random



class Node:
    #   a representation of Nodes
    #   holds some additonal usefull info
    def __init__(self,pot,res,interface,strip):
        self.pot = float(pot)
        self.res = float(res)
        self.interface = bool(interface)
        self.strip = bool(strip)

    def getPot(self):
        return self.pot
    def getRes(self):
        return self.res
    def setInterface(self,B):
        self.interface = B
    def isInterface(self):
        return self.interface
    def isStrip(self):
        return self.strip
    def nodePrint(self):
        return "p: " + str.format('{0:1.4f}', self.pot) + ", r: " + str.format('{0:1.4f}', self.res)
        #return "p: " + str(self.pot) + ", r: " + str(self.res)
        #return "p: " + str(self.pot) + ", r: " + str(self.res) + ", i: " + str(int(self.interface)) \
        #       + ", s: " + str(int(self.strip))

class customReturn:
    #custom return function returns a matrix and additonal value

    def __init__(self, mat, additional1, additional2):
        self.mat = mat
        self.additional1 = additional1
        self.additional2 = additional2
    def getMat(self):
        return self.mat
    def getAdditional1(self):
        return self.additional1
    def getAdditional2(self):
        return self.additional2

def initNodeMatrix (wd,bd,aw,na,nb):
    #   makes the initial matrix, how nice

    #   assume a = 1 and derive the rest of the values
    a = 1
    w = float(a / aw)
    d = float(w / wd)
    b = float(d * bd)

    #just checking
    print("a: " + str(a) + " w: " + str(w) + " d: " + str(d) + " b: " + str(b))
    #derive h and k values, usefull to check if a node is on the strip or not
    k = float(a/(na-1))
    h = float(b/(nb-1))

    #   calc where strip is relative to top left as well as calc how long the strip is in terms of nodes
    #
    ind = float(b - d)
    interfaceY = math.floor(ind/h) + 1
    print("interface y: " + str(interfaceY))
    stripThreshX = math.floor(w/k) + 1
    print("strip x: " + str(stripThreshX))
    #   generate matrix skeleton
    nodes = [[Node(0, 0, False, False) for j in range(na)] for i in range(nb)]


    #   apply values to special cases, strip and
    for x in range(0, na):
        if x < stripThreshX:
            nodes[interfaceY][x] = Node(1, 0, True, True)
        else:
            nodes[interfaceY][x] = Node(0, 0, True, False)


    shell = customReturn([],stripThreshX,interfaceY)
    ret = customReturn(nodes, float(h/k),shell)


    return ret


def calcNode(mat, row, col, alpha, relaxation, Er):
    #   Calculates a new node from the old node
    #   handles both potential and residual

    #   if the node is the strip then just pass over it
    if mat[row][col].isStrip():
        return mat[row][col]

    top = mat[row - 1][col]
    bottom = mat[row + 1][col]
    right = mat[row][col + 1]
    left = Node(0, 0, False, False)
    if col == 0:
        left = right

    else:
        left = mat[row][col - 1]

    if mat[row][col].isInterface():
        E = Er
    else:
        E = 1

    A = 1 / (2 * (1 + (alpha*alpha) ))
    B = left.getPot() + right.getPot()
    C = (2*alpha*alpha)/(1+E)
    D = top.getPot() + E*bottom.getPot()

    #My way but not SOR way
    newPot = A * (B + C*D)
    #if (row == 3 and col == 0):
    #    print(str(A))
    #    print(str(B))
    #    print(str(C))
    #    print(str(D))
    #    print(str(newPot))
    oldPot = mat[row][col].getPot()
    Res = (newPot - oldPot) / relaxation

    #implement sor algo
    #Res = A * (B + C*D) - mat[row][col].getPot()
    #newPot = mat[row][col].getPot() + relaxation*Res

    ret = Node(newPot, Res, mat[row][col].isInterface(), mat[row][col].isStrip())
    return ret

def reRoll(mat,na,nb,resMax, alpha , relaxation, Er):
    #   snake iteration starting from bottom left ignoring top, bottom and right sides
    #   as these sides will always be zero
    check = (nb) % 2
    for row in range(nb - 2, 0, -1):
        if row % 2 == check:
            for col in range(0, na-1):
                mat[row][col] = calcNode(mat, row, col, alpha, relaxation, Er)
                if mat[row][col].getRes() > resMax:
                    resMax = mat[row][col].getRes()
                #print(str(row) + " " + str(col))
        else:
            for col in range(na - 2, -1, -1):
                mat[row][col] = calcNode(mat, row, col, alpha, relaxation, Er)
                if mat[row][col].getRes() > resMax:
                    resMax = mat[row][col].getRes()
                #print(str(row) + " " + str(col))

    ret = customReturn(mat,resMax,0)
    return ret

def contourCalc(mat,stripthreshX,interfaceY,na,nb,alpha,Er):
    sumtopbot = 0;
    sumRT = 0
    sumRB = 0
    offsetTop = 1
    offsetBot = 1
    offsetRight = 1
    #if interfaceY - 2 <= 0:
    #    offsetTop = 1
    #if interfaceY + 2 >= nb:
    #    offsetBot = 1
    #if stripthreshX + 2 >= na:
    #    offsetRight = 1

    topoffset = interfaceY - offsetTop
    botoffset = interfaceY + offsetBot
    rightoffset = stripthreshX + offsetRight
    #print(str(topoffset))
    #print(str(botoffset))
    #print(str(rightoffset))

    #sum bottom and top leg
    for col in range(0, rightoffset):
        print("nb-1 : " + str(mat[botoffset+1][col].getPot()) + " nb+1: " + str(mat[botoffset-1][col].getPot()))
        tempbot = Er*(mat[botoffset+1][col].getPot() -
                      mat[botoffset-1][col].getPot())
        print("na+1 : " + str(mat[topoffset-1][col].getPot()) + " na-1: " + str(mat[topoffset+1][col].getPot()))
        temptop = (mat[topoffset-1][col].getPot() -
                   mat[topoffset+1][col].getPot())

        if (col == 0 or col == rightoffset-1):
            sumtopbot = sumtopbot + (1/4)*(temptop + tempbot)
        else:
            sumtopbot = sumtopbot + (1/2)*(temptop + tempbot)

    #print("sumtopbot: "+ str(Er) + ": " + str(sumtopbot))


    for row in range(topoffset,interfaceY+1):

        print("mr+1 : " + str(mat[row][rightoffset].getPot()) + " mr-1: " + str(mat[row][rightoffset-2].getPot()))
        tempRT =(mat[row][rightoffset].getPot() -
                      mat[row][rightoffset-2].getPot())
        if (row == topoffset or row == interfaceY):
            sumRT = sumRT + (1/4)*tempRT
        else:
            sumRT = sumRT + (1/2)*tempRT
    #print("sumRT:" +str(Er) + ": " + str(sumRT))

    #print()
    for row in range(interfaceY,botoffset+1):
        print("mr+1 : " + str(mat[row][rightoffset].getPot()) + " mr-1: " + str(mat[row][rightoffset - 2].getPot()))
        tempRB =Er*(mat[row][rightoffset].getPot() -
                      mat[row][rightoffset-2].getPot())
        if (row == interfaceY or row == botoffset-1):
            sumRB = sumRB + (1/4)*tempRB
        else:
            sumRB = sumRB + (1/2)*tempRB
    #print("sumRB:" + str(Er) + ": " + str(sumRB))

    negCEo = alpha*sumtopbot + (1/alpha)*(sumRT+sumRB)

    return negCEo




























