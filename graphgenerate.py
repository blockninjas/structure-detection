import numpy
import graphfeature

def adjFun(x, y):
  ret = numpy.empty((x.shape[0], y.shape[1]))
  threshold = 0
  for xIndex in range(0, x.shape[0]):
    threshold = 0.3 + numpy.random.poisson()
    for yIndex in range(0, y.shape[1]):
      val = numpy.random.normal()
      if numpy.absolute(val) >= threshold:
        ret[xIndex][yIndex] = 1
      else:
        ret[xIndex][yIndex] = 0
  return ret

def generateRandomGraph(x, y):
  adjMat_dir = numpy.fromfunction(adjFun, (x, y))
  for index in range(0, len(adjMat_dir)):
    adjMat_dir[index][index] = 0
  adjMat_undir = graphfeature.getUndirectedAdj(adjMat_dir)
  (D_in, D_out, D) = graphfeature.degrees(adjMat_dir, adjMat_undir)
  return adjMat_dir, D_in, D_out, D, adjMat_undir

