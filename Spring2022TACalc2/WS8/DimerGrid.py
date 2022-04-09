#
# Dimer model on grid
# Bryan Clair, June 2012
#
import random
import sys

class DimerGrid:
    def __init__(self,sizex, sizey):
        """Planar square grid of sizex X sizey vertices.
        Grid entries are coded as:
        * a pair (dx,dy) giving the direction of the dimer at that vertex
        * False, indicating that vertex is not part of the graph
        * True, indicating there is no dimer at that vertex"""
        self._sizex = sizex
        self._sizey = sizey
        self._contents = []
        for y in range(sizey):
            self._contents.append([True]*sizex)

    def clear(self):
        """Remove all dimers from the graph"""
        for x in range(self._sizex):
            for y in range(self._sizey):
                if self[x,y]:
                    self[x,y] = True

    def fillhorizontal(self):
        """Fill with all horizontal dimers, if possible.
        Raise a ValueError if it fails, leaving the graph a mess."""
        try:
            for y in range(self._sizey):
                x = 0
                while x < self._sizex:
                    if self[x,y]:
                        if not self[x+1,y]:
                            raise ValueError()
                        # OK to put something here
                        self[x,y] = (1,0)
                        x += 1
                        self[x,y] = (-1,0)
                    x += 1
        except (IndexError, ValueError):
            raise ValueError('Graph not tileable by horizontal dimers')

    def fillvertical(self):
        """Fill with all vertical dimers, if possible.
        Raise a ValueError if it fails, leaving the graph a mess."""
        try:
            for x in range(self._sizex):
                y = 0
                while y < self._sizey:
                    if self[x,y]:
                        if not self[x,y+1]:
                            raise ValueError()
                        # OK to put something here
                        self[x,y] = (0,1)
                        y += 1
                        self[x,y] = (0,-1)
                    y += 1
        except (IndexError, ValueError):
            raise ValueError('Graph not tileable by vertical dimers')

    def augment(self,path):
        """Call with an augmenting path, and form the symmetric difference
        of self with path. An augmenting path begins and ends at open (True)
        vertices, and alternates dimer/no-dimer edges for its length."""
        assert self[path[0]]==True and self[path[-1]]==True, 'Path not augmenting.'
        spot = 0
        while spot < len(path):
            v1 = path[spot]
            v2 = path[spot+1]
            self[path[spot]] = (v2[0]-v1[0],v2[1]-v1[1])
            self[path[spot+1]] = (v1[0]-v2[0],v1[1]-v2[1])
            spot += 2
            
    def findAugmentingPath(self):
        # build tag structure
        # free (unpaired) white vertices tagged with True
        # as breadth first search runs, vertices will be tagged with the
        # coordinates of their parent vertex
        tags = []
        for x in range(self._sizex):
            tags.append([None]*self._sizey)

        whitelist = []
        for x in range(self._sizex):
            for y in range(self._sizey):
                if (x+y) % 2 == 0:
                    if self[x,y] == True:
                        whitelist.append((x,y))
        
        # breadth first search, whitelist is the list of white
        # vertices to be dealt with
        while whitelist:
            w = whitelist.pop(0)
            # loop over neighbors of w
            for dir in [(1,0),(-1,0),(0,1),(0,-1)]:
                # b is the neighbor
                b = (w[0]+dir[0],w[1]+dir[1])
                # Check if b is actually part of the graph
                try:
                    bval = self[b[0],b[1]]
                except IndexError:
                    continue
                if bval == False:
                    continue
                # Ok, b is part of the graph, now see if it's been tagged
                if tags[b[0]][b[1]]:
                    continue
                # Found a virgin black vertex, tag it with w
                tags[b[0]][b[1]] = w
                
                # If b is a free vertex, we've got an augmenting path!
                if bval == True:
                    path = [b]
                    while tags[b[0]][b[1]]:
                        b = tags[b[0]][b[1]]
                        path.append(b)
                    return path

                # Find the matching vertex of b, tag it, add it to whitelist
                match = (b[0]+bval[0],b[1]+bval[1])
                tags[match[0]][match[1]] = b
                whitelist.append(match)

        # Failed to find an augmenting path
        return False

    def fill(self):
        """Fill with dimers, if possible.  Uses the simpler bipartite version
        of Edmond's algorithm.  Always results a maximum matching, but gives no indication
        of whether it succeeded in a perfect matching."""
        path = self.findAugmentingPath()
        while path:
            self.augment(path)
            path = self.findAugmentingPath()

    def size(self):
        """Returns a pair (sizex, sizey)"""
        return (self._sizex,self._sizey)

    def __getitem__(self,spot):
        (x,y) = spot
        return self._contents[y][x]

    def __setitem__(self,spot,val):
        (x,y) = spot
        self._contents[y][x] = val

    dimerascii = { (1,0):'-', (-1,0):'-',
                   (0,1):'|', (0,-1):'|',
                   True:'?', False:' '}
    dimerunicode = { (1,0):u"\u257A", (-1,0):u"\u2578",
                     (0,1):u"\u257B", (0,-1):u"\u2579",
                     True:'?', False:' '}

    def __str__(self):
        """Convert to string, . for empty site, * for occupied."""
        out = ''
        for y in range(self._sizey):
            for x in range(self._sizex):
                out += DimerGrid.dimerascii[self[x,y]]
            out += '\n'
        return out[:-1]

    def display(self):
        """Display using unicode box drawing art"""
        for y in range(self._sizey):
            for x in range(self._sizex):
                sys.stdout.write(DimerGrid.dimerunicode[self[x,y]])
            sys.stdout.write('\n')

    def tilecounts(self):
        """Returns a four entry list of tile counts:
        [horizontal even, horizontal odd, vertical even, vertical odd]"""
        count = [0,0,0,0]
        for x in range(self._sizex):
            for y in range(self._sizey):
                if self[x,y] == (1,0):
                    count[(x+y) % 2] += 1
                elif self[x,y] == (0,1):
                    count[(x+y)%2+2] += 1
        return count

    def rotate(self,x,y):
        """Rotate the dimer pair with upper left corner (x,y).
        Returns (x,y) if sucessful, False if impossible."""
        try:
            if self[x,y] == (1,0):
                # Horizontal across top
                if self[x,y+1] == (1,0):
                    # OK to rotate
                    self[x+1,y+1] = (0,-1)
                    self[x+1,y] = (0,1)
                    self[x,y+1] = (0,-1)
                    self[x,y] = (0,1)
                    return (x,y)
            elif self[x,y] == (0,1):
                # Vertical on left side
                if self[x+1,y] == (0,1):
                    # OK to rotate
                    self[x+1,y+1] = (-1,0)
                    self[x+1,y] = (-1,0)
                    self[x,y] = (1,0)
                    self[x,y+1] = (1,0)
                    return (x,y)
        except IndexError:
            pass
        return False

    def onestep(self):
        """Perform a random rotation.
        Returns (x,y) if sucessful, False if no rotation occurred."""     
        x = random.randint(0,self._sizex-2)
        y = random.randint(0,self._sizey-2)
        return self.rotate(x,y)

    def takesteps(self,steps):
        """Perform steps rotations"""
        for i in range(steps):
            self.onestep()

class AztecDiamond(DimerGrid):
    def __init__(self,size):
        """An AztecDiamond graph with 2*size rows"""
        if size < 2:
            raise ValueError('Size must be 2 or more')
        DimerGrid.__init__(self,2*size,2*size)
        for x in range(2*size):
            for y in range(2*size):
                if abs(x-size+.5)+abs(y-size+.5) > size:
                    self[x,y] = False

class ListGrid(DimerGrid):
    """Produce a custom shaped grid from a description of its geometry"""
    def __init__(self,description):
        """Description is a list of rows.  Each row is a list of tuples,
        of the form (count, value), which will fill the next count vertices
        of that row with the given value.
        value can be True for an empty but usable vertex, False for an
        unusable vertex, or a pair (dx,dy) to initialize with half a dimer.
        """
        height = len(description)
        width = 0
        for (count,val) in description[0]:
            width += count
        DimerGrid.__init__(self,width,height)

        for y in range(height):
            x = 0
            for (count,val) in description[y]:
                for i in range(count):
                    self[x,y] = val
                    x += 1
            if x != width:
                raise ValueError('Row ' + str(y) + ' wrong width.')

class StringGrid(DimerGrid):
    """Produce a custom shaped grid from an ASCII art image."""
    def __init__(self,description,empty=' '):
        """Description is an ASCII art string, using spaces (by default)
        for empty spots and any other character for spots to be tiled."""
        rows = description.split('\n')
        height = len(rows)
        width = max([len(r) for r in rows])
        DimerGrid.__init__(self,width,height)

        for y in range(height):
            for x in range(width):
                try:
                    self[x,y] = (rows[y][x] != empty)
                except IndexError:
                    self[x,y] = False

class ParallelogramGrid(ListGrid):
    """A grid that is more or less paralleogram shaped"""
    def __init__(self,width,height):
        """A paralleogram-like shape with height rows, each with width
           vertices.  First and last row are doubled to allow some covers.
           *****
           *****
            *****
             *****
              *****
              *****
        """
        data = [ [ (width,True), (height,False) ] ]
        for y in range(height+1):
            data.append([ (y,False), (width,True), (height-y,False) ])
        data.append( [ (height,False), (width, True) ] )
        ListGrid.__init__(self,data)

if __name__ == '__main__':
    g = DimerGrid(8,8)
    print 'Empty 8x8 grid:'
    g.display()

    print 'Horizontal:'
    g.fillhorizontal()
    g.display()
    print '[horizontal even, horizontal odd, vertical even, vertical odd] = ',g.tilecounts()
    print 'Vertical:'
    g.fillvertical()
    g.display()
    print '[horizontal even, horizontal odd, vertical even, vertical odd] = ',g.tilecounts()

    print 'Rotations down the diagonal'
    g.rotate(0,0)
    g.rotate(2,2)
    g.rotate(4,4)
    g.rotate(6,6)
    g.display()
    print '[horizontal even, horizontal odd, vertical even, vertical odd] = ',g.tilecounts()

    print 'ASCII display'
    print g

    raw_input('Custom shape using ListGrid')
    g = ListGrid([ [ (10,True) ],
                   [ (10,True) ],
                   [ (2,True), (2, False), (2,True), (2,False), (2,True) ],
                   [ (2,True), (2, False), (2,True), (2,False), (2,True) ],
                   [ (10,True) ],
                   [ (2,True), (4,False), (4,True) ],
                   [ (10,True) ],
                   [ (10,True) ],
                   [ (2,True), (2, False), (2,True), (2,False), (2,True) ],
                   [ (2,True), (2, False), (2,True), (2,False), (2,True) ] ])
    g.display()
    try:
        g.fillvertical()
        print 'SOMETHING IS WRONG: Vertical fill should have failed.'
        g.display()
    except ValueError:
        print 'Vertical filling fails.'
    print 'Filled horizontally'
    g.fillhorizontal()
    g.display()
    print 'Randomized'
    g.takesteps(10000)
    g.display()

    raw_input('Edmonds fill algorithm')
    g = StringGrid(' ***\n****\n***\n**')
    g.fill()
    g.display()

    raw_input('Custom shape using StringGrid:')
    mask = '****  \n****  \n  ****\n******\n **** \n **\n **'
    print mask
    g = StringGrid(mask)
    g.fillhorizontal()
    g.takesteps(10000)
    g.display()

    raw_input('Other shapes')
    p = ParallelogramGrid(12,50)
    p.fillhorizontal()
    p.display()

    raw_input('Many rotations')
    g = DimerGrid(40,40)
    g.fillhorizontal()
    for i in range(10000+1):
        g.onestep()
        if i % 1000 == 0:
            print i
            g.display()

    raw_input('Aztec Diamonds')
    ad = AztecDiamond(4)
    ad.display()
    ad.fillhorizontal()
    ad.display()

    raw_input('Many rotations')
    ad = AztecDiamond(20)
    ad.fillhorizontal()
    for i in range(1000000+1):
        ad.onestep()
        if i % 100000 == 0:
            print i
            ad.display()
    