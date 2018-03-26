import matplotlib.pyplot as plt
import numpy as np
import gtc
from matplotlib import collections  as mc
from matplotlib import animation
import random

def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

class Vertex:
	""" 2-D Vertex with coordinates and an Edge """
	
	def __init__(self,coords,edge=None):
		self.coords = coords
		self.edge = edge
	
	def getEdges(self):
		e0 = self.edge
		edges = [e0]
		e = e0.prev.twin
		while e != e0:
			edges.append(e)
			e = e.prev.twin
		return edges
	
	def getNeighbours(self):
		edges = self.getEdges()
		return [edge.next.origin for edge in edges]
	
	def getFaces(self):
		edges = self.getEdges()
		return [edge.face for edge in edges]
	
	def getForceVector(self):
		vectors = [[vertex.coords[0]-self.coords[0],vertex.coords[1]-self.coords[1]] for vertex in self.getNeighbours()]
		vector = [sum(v[0] for v in vectors),sum(v[1] for v in vectors)]
		return vector
	
	def addForceVector(self,face0, coef=0.01):
		if face0 not in self.getFaces():
			vector = self.getForceVector()
			self.coords[0] = self.coords[0]+vector[0]*coef
			self.coords[1] = self.coords[1]+vector[1]*coef
	
class Edge:
	""" 2-D Edge with an Origin Vertex, twin edge, previous edge and next edge """
	
	def __init__(self,origin,twin=None,prev=None,
			  next_=None,face=None):
		self.origin = origin
		self.twin = twin
		self.prev = prev
		self.next = next_
		self.face = face
	
	def flip(self):
		
		twin = self.twin
		origin = self.origin
		face = self.face
		prev = self.prev
		next_ = self.next
		
		origin_twin = twin.origin
		face_twin = twin.face
		prev_twin = twin.prev
		next_twin = twin.next
		
		self.origin = prev.origin
		self.prev = next_
		self.next = prev_twin
		
		twin.origin = prev_twin.origin
		twin.prev = next_twin
		twin.next = prev
		
		next_.prev = prev_twin
		next_.next = self
		
		prev.prev = twin
		prev.next = next_twin
		prev.face = face_twin
		
		next_twin.prev = prev
		next_twin.next = twin
		
		prev_twin.prev = self
		prev_twin.next = next_
		prev_twin.face = face
		
		face.edge = self
		face_twin.edge = twin
		origin_twin.edge = next_
		origin.edge = next_twin
		return
	
	def isLegal(self,face0):
		if self.face == face0 or self.twin.face == face0:
			return True
		A = self.origin.coords
		B = self.twin.prev.origin.coords
		C = self.next.origin.coords
		D = self.next.next.origin.coords
		if -1 in [gtc.orientation(A,B,C),gtc.orientation(A,C,D),gtc.orientation(B,C,D),gtc.orientation(B,D,A)]:
			return True
		return gtc.inCircle(A,C,D,B)==-1
	
	def isFlippable(self,face0):
		if self.face == face0 or self.twin.face == face0:
			return False
		A = self.origin.coords
		B = self.twin.prev.origin.coords
		C = self.next.origin.coords
		D = self.next.next.origin.coords
		return -1 not in [gtc.orientation(A,B,C),gtc.orientation(A,C,D),gtc.orientation(B,C,D),gtc.orientation(B,D,A)]
	
class Face:
	
	def __init__(self,edge):
		self.edge = edge
	
	def getEdges(self):
		edge = self.edge
		edges= [edge]
		edge = edge.next
		while edge != edges[0]:
			edges.append(edge)
			edge = edge.next
		return edges
	
	def getVertices(self):
		edges = self.getEdges()
		return [edge.origin for edge in edges]
		
class Dcel:
	
	def __init__(self,orderedPoints):
		n = len(orderedPoints)
		self.vertices = [Vertex(orderedPoints[i]) for i in range(n)]
		self.edges = [Edge(self.vertices[i]) for i in range(n)]
		self.edges += [Edge(self.vertices[(i+1)%n]) for i in range(n)]
		
		for i in range(n):
			edge = self.edges[i]
			self.vertices[i].edge = edge
			edge.twin = self.edges[n+i]
			edge.prev = self.edges[(i-1)%n]
			edge.next = self.edges[(i+1)%n]
			
			edge = self.edges[n+i]
			edge.twin = self.edges[i]
			edge.prev = self.edges[n+(i+1)%n]
			edge.next = self.edges[n+(i-1)%n]
			""" END  Vertices """
		
		self.faces = [Face(self.edges[n]),Face(self.edges[0])]
		""" END  Faces """
		
		for i in range(n):
			self.edges[i].face = self.faces[1]
			self.edges[n+i].face = self.faces[0]
		""" END edges """
	
	@classmethod
	def deloneFromPoints(cls,points):
		P = gtc.angularSort(points,min(points))
		D = cls(P)
		D.triangulateInterior()
		D.triangulateExterior()
		D.legalize()
		return D
	
	@classmethod
	def triangulatePolygonWithPoints(cls,points,polygon):
		D = Dcel.deloneFromPoints(points)
		D.enforceEdges(polygon)
		D.polygon = polygon
		return D
	
	def plotPolygon(self):
		if self.polygon:
			points, simplices = D.getInteriorTriangles(self.polygon)
			plt.triplot(points[:,0], points[:,1], simplices)
			plt.plot(points[:,0], points[:,1], 'bo')
			plt.show()
	
	def plot(self):
		lines =  [[edge.origin.coords, edge.twin.origin.coords] for edge in self.edges]
		for i in lines:
			plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'bo-')
		plt.show()
	
	def plotWithEdges(self, edges):
		lines =  [[edge.origin.coords, edge.twin.origin.coords] for edge in self.edges]
		lc = mc.LineCollection(lines, linewidths=2)
		fig, ax = plt.subplots()
		ax.add_collection(lc)
		x = [i[0][0] for i in lines]
		y = [i[0][1] for i in lines]
		lc = mc.LineCollection(edges, linewidths=2,color='k')
		ax.add_collection(lc)
		plt.plot(x,y,'ro')
		plt.show()
	
	def plotWithVertexNumber(self):
		lines =  [[edge.origin.coords, edge.twin.origin.coords] for edge in self.edges]
		lc = mc.LineCollection(lines, linewidths=2)
		fig, ax = plt.subplots()
		ax.add_collection(lc)
		x = []
		y = []
		for i,vertex in enumerate(self.vertices):
			x.append(vertex.coords[0])
			y.append(vertex.coords[1])
			plt.text(x[-1],y[-1]+0.02,i)
		plt.plot(x,y,'ro')
		plt.show()
	def splitFace(self,e1,e2):
		if e1.face != e2.face or e2.origin == e1.twin.origin or e1.origin == e2.twin.origin:
			return "no diagonal"
		
		newEdge = Edge(e1.origin, None, e1.prev, e2, e1.face)
		twinNewEdge = Edge(e2.origin, None, e2.prev, e1, None)
		
		newEdge.twin = twinNewEdge
		twinNewEdge.twin = newEdge
		
		newFace = Face(twinNewEdge)
		twinNewEdge.face = newFace
		
		k = e1.face
		
		self.edges.append(newEdge)
		self.edges.append(twinNewEdge)
		
		e1.prev.next = newEdge
		e1.prev = twinNewEdge
		e2.prev.next = twinNewEdge
		e2.prev = newEdge
		
		i = e1
		while i != twinNewEdge:
			i.face = newFace
			i = i.next
	
		k.edge = newEdge
	
		self.faces.append(newFace)
	
	def triangulateInterior(self):
		"""Triangula la cara interna del DCEL D"""
		ini = self.faces[1].edge
		mostLeftEdge = ini
		iterator = ini
		while True:
			if iterator.origin.coords[0] < mostLeftEdge.origin.coords[0]:
				mostLeftEdge = iterator
			iterator = iterator.next
			if iterator == ini:
				break
		iterator = mostLeftEdge
		while True:
			if iterator.face == self.faces[0]:
				break
			if gtc.orientation(iterator.origin.coords,iterator.next.origin.coords,iterator.next.next.origin.coords) == 1:
				self.splitFace(iterator,iterator.next.next)
				iterator = iterator.prev.twin
			else:
				iterator = iterator.next
	
	def triangulateExterior(self):
		ini = self.faces[0].edge
		mostLeftEdge = ini
		iterator = ini
		while True:
			if iterator.origin.coords[0] < mostLeftEdge.origin.coords[0]:
				mostLeftEdge = iterator
			iterator = iterator.next
			if iterator == ini:
				break
		iterator = mostLeftEdge
		while True:
			if gtc.orientation(iterator.origin.coords,iterator.next.origin.coords,iterator.next.next.origin.coords) == 1:
				self.splitFace(iterator,iterator.next.next)
				iterator = iterator.prev.twin.prev
				continue
			else:
				iterator = iterator.next
			if iterator.next.origin == mostLeftEdge.origin:
				break
			
	def legalize(self):
		flipped = True
		lastChanged = []
		while flipped:
			changed = []
			flipped = False
			for edge in self.edges:
				if not edge.isLegal(self.faces[0]):
					changed.append(edge)
					edge.flip()
					flipped = True
			if changed in lastChanged:
				return
			else:
				lastChanged.append(changed)
		return
	
	def containsEdge(self,searched_edge):
		for edge in self.edges:
			if edge.origin.coords in searched_edge and edge.next.origin.coords in searched_edge:
				return True
		else:
			return False
	
	def enforceEdges(self,edges):
		for (Vi,Vj) in edges:
			if self.containsEdge([Vi,Vj]):
				continue
			newEdges = []
			crossingEdges = []
			for edge in self.edges:
				if edge.twin in crossingEdges:
					continue
				if gtc.segmentCrossing([Vi,Vj],[edge.origin.coords,edge.next.origin.coords]):
					crossingEdges.append(edge)
			while len(crossingEdges) > 0:
				e = crossingEdges.pop()
				if not e.isFlippable(self.faces[0]):
					crossingEdges.insert(0,e)
				else:
					e.flip()
					if gtc.segmentCrossing([Vi,Vj],[e.origin.coords,e.next.origin.coords]):
						crossingEdges.insert(0,e)
					else:
						newEdges.append(e)
			swap = True
			while swap:
				swap = False
				for e in newEdges:
					if e.origin.coords in [Vi,Vj] and e.next.origin.coords in [Vi,Vj]:
						continue
					if not e.isLegal:
						e.flip()
						swap = True
	
	def animateForces(self):
		fig = plt.figure()
		ax = plt.axes(xlim=(0, 1), ylim=(0, 1))
		
		lines = [plt.plot([], [],'bo-')[0] for _ in range(len(self.edges))]
		def init():
			for line in lines:
				line.set_data([], [])
			return lines
		def animate(i):
			for vertex in self.vertices:
				vertex.addForceVector(self.faces[0])
			edges =  [[edge.origin.coords, edge.twin.origin.coords] for edge in self.edges]
			for i,edge in enumerate(edges):
				lines[i].set_data([edge[0][0],edge[1][0]],[edge[0][1],edge[1][1]])
			return lines
		ani = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=100, interval=10, blit=True)
		plt.show()
		ani.save('particle_box.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
	
	def getInteriorTriangles(self, polygon):
		""" Returns [points, interiorSimplices] """
		poly = [i[0] for i in polygon]
		triangles = [face.getVertices() for face in self.faces if face != self.faces[0]]
		exterior = []
		for i,(a,b,c) in enumerate(triangles):
			 x = (a.coords[0]+b.coords[0]+c.coords[0])/3
			 y = (a.coords[1]+b.coords[1]+c.coords[1])/3
			 if not gtc.pointInPolygon([x,y],poly):
				 exterior.append(i)
		triangles = [t for i,t in enumerate(triangles) if i not in exterior]
		return [np.array([vertex.coords for vertex in self.vertices]),
		  [[self.vertices.index(a),self.vertices.index(b),self.vertices.index(c)] for (a,b,c) in triangles]]

""" DELONE NORMAL """
points = [list(np.random.uniform(0,1,2)) for i in range(20)]
D = Dcel.deloneFromPoints(points)
#D.plot()
D.animateForces()

""" Polygon """
#polyP = gtc.randomPolyPoints(20,5)
#gtc.plotPolyPoints(polyP)
#D = Dcel.triangulatePolygonWithPoints(polyP[1],polyP[0])
#D.plotPolygon()