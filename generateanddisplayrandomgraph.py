import numpy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import motifs
import graphgenerate
import graphdisplay
import graphfeature
import graphkstest
from scipy.spatial import distance
from scipy import stats
import matplotlib.cm as cm
import warnings
import sys
warnings.simplefilter("ignore")
nodeCount = 8

def sqrUndir(v1, v2):
  error = 0
  if len(v1) != len(v2):
    raise Exception("Length not equal")
  for index in range(0, len(v1)):
    error = error + numpy.power(numpy.absolute(v1[index] - v2[index]), graphfeature.maxDepth - index + 1)
  return error # / float(len(v1))

def sqrDir(v1, v2, v3, v4):
  errorIn = 0
  errorOut = 0
  if len(v1) != len(v2) or len(v3) != len(v4):
    raise Exception("Length not equal")
  for index in range(0, len(v1)):
    errorIn = errorIn + numpy.power(numpy.absolute(v1[index] - v2[index]), graphfeature.maxDepth - index + 1)
  for index in range(0, len(v3)):
    errorOut = errorOut + numpy.power(numpy.absolute(v3[index] - v4[index]), graphfeature.maxDepth - index + 1)
  return errorIn + errorOut # / float(len(v1))

def ppArray(a, depth=0):
  for ele in a:
    if isinstance(ele, list):
      if isinstance(ele[0], list):
        print(' ' * (depth * 3), "[")
        ppArray(ele, depth + 1)
        print(' ' * (depth * 3), "]")
      else:
        print(' ' * (depth * 3), str(ele))
    else:
      print(' ' * (depth * 3), str(ele) + ",")

def compareUndirPart(node1Features, node2Features):
  indexesUsed = []
  bestIndexes = []
  for index1 in range(0, len(node1Features)):
    dists = []
    for index2 in range(0, len(node2Features)):
      #print node1Features[index1]
      #print node2Features[index2]
      v1 = numpy.log(node1Features[index1])
      v2 = numpy.log(node2Features[index2])
      cleanInfValues(v1)
      cleanInfValues(v2)
      test = sqrUndir(v1, v2)
      dist = test
      dists.append(dist)
    maxIndex = -1
    for index in range(0, len(dists)):
      if maxIndex == -1 and index not in indexesUsed:
        maxIndex = index
      elif dists[maxIndex] > dists[index] and index not in indexesUsed:
        maxIndex = index
    if maxIndex != -1:
      indexesUsed.append(maxIndex)
      bestIndexes.append((index1, maxIndex, dists[maxIndex]))
  return bestIndexes

def compareDirPart(node1InFeatures, node2InFeatures, node1OutFeatures, node2OutFeatures):
  indexesUsed = []
  bestIndexes = []
  #print "data:", len(node1InFeatures), len(node2InFeatures), len(node1OutFeatures), len(node2OutFeatures)
  #print node1InFeatures
  #print node2InFeatures
  #print node1OutFeatures
  #print node2OutFeatures
  maxLen = len(node1InFeatures)
  if maxLen > len(node2InFeatures):
    maxLen = len(node2InFeatures)
  if maxLen > len(node1OutFeatures):
    maxLen = len(node1OutFeatures)
  if maxLen > len(node2OutFeatures):
    maxLen = len(node2OutFeatures)
  #print maxLen

  for index1 in range(0, maxLen):
    dists = []
    for index2 in range(0, maxLen):
      #print node1Features[index1]
      #print node2Features[index2]
      v1 = numpy.log(node1InFeatures[index1])
      v2 = numpy.log(node2InFeatures[index2])
      v3 = numpy.log(node1OutFeatures[index1])
      v4 = numpy.log(node2OutFeatures[index2])
      cleanInfValues(v1)
      cleanInfValues(v2)
      cleanInfValues(v3)
      cleanInfValues(v4)
      test1 = sqrUndir(v1, v2)
      test2 = sqrUndir(v3, v4)
      dist = test1 + test2
      dists.append(dist)
    maxIndex = -1
    for index in range(0, len(dists)):
      if maxIndex == -1 and index not in indexesUsed:
        maxIndex = index
      elif dists[maxIndex] > dists[index] and index not in indexesUsed:
        maxIndex = index
    if maxIndex != -1:
      indexesUsed.append(maxIndex)
      bestIndexes.append((index1, maxIndex, dists[maxIndex]))
  return bestIndexes

def cleanInfValues(v):
  for index in range(0, len(v)):
    if v[index] == numpy.NINF:
      v[index] = 0
"""
def compareDirPart(node1InFeatures, node2InFeatures, node1OutFeatures, node2OutFeatures):
  '''
  indexesUsed = []
  bestIndexes = []
  for index1 in range(0, len(node1InFeatures)):
    for index2 in range(0, len(node2InFeatures)):
      for index3 in range(0, len(node1OutFeatures)):
        dists = []
        for index4 in range(0, len(node2OutFeatures)):
          #print node1Features[index1]
          #print node2Features[index2]
          v1 = numpy.log(node1InFeatures[index1])
          v2 = numpy.log(node2InFeatures[index2])
          v3 = numpy.log(node1OutFeatures[index3])
          v4 = numpy.log(node2OutFeatures[index4])
          cleanInfValues(v1)
          cleanInfValues(v2)
          cleanInfValues(v3)
          cleanInfValues(v4)
          test = sqrDir(v1, v2, v3, v4)
          dist = test
          dists.append((index1, index2, index3, index4, dist))
        maxIndex = -1
        for index in range(0, len(dists)):
          if maxIndex == -1 and index not in indexesUsed:
            maxIndex = index
          elif dists[maxIndex] > dists[index] and index not in indexesUsed:
            maxIndex = index
        if maxIndex != -1:
          indexesUsed.append(maxIndex)
          bestIndexes.append((index1, maxIndex, dists[maxIndex]))
  '''
  indexesIn = compareUndirPart(node1InFeatures, node2InFeatures)
  indexesOut = compareUndirPart(node1OutFeatures, node2OutFeatures)
  return (indexesIn, indexesOut)
"""
def compareUndir(node1Features, node2Features):
  if node1Features[0][0] == 0 and node2Features[0][0] == 0:
    return ([(0, 0)], 0.0)
  elif node1Features[0][0] == 0 or node2Features[0][0] == 0:
    return ([(0, 0)], numpy.inf)
  length = len(node1Features[0]) if len(node1Features[0]) < len(node2Features[0]) else len(node2Features[0])
  node1FeaturesLocal = cutMatrixElementsToLength(node1Features, length)
  node2FeaturesLocal = cutMatrixElementsToLength(node2Features, length)

  indexes1 = compareUndirPart(node1FeaturesLocal, node2FeaturesLocal)
  indexes2 = compareUndirPart(node2FeaturesLocal, node1FeaturesLocal)
  diff1 = diff(indexes1)
  diff2 = diff(indexes2)
  return (indexes1, diff1) if diff1 < diff2 else (indexes2, diff2)

def cutMatrixElementsToLength(nodeFeatures, length):
  ret = []
  for index in range(0, len(nodeFeatures)):
    ret.append(nodeFeatures[index][0:length])
  return ret

def compareDir(node1InFeatures, node2InFeatures, node1OutFeatures, node2OutFeatures):
  if node1InFeatures[0][0] == 0 and node1OutFeatures[0][0] == 0 and node2InFeatures[0][0] == 0 and node2OutFeatures[0][0] == 0:
    return ([(0, 0)], 0.0)
  elif (
        ((node1InFeatures[0][0] == 0 and node2InFeatures[0][0] != 0) or (node1InFeatures[0][0] != 0 and node2InFeatures[0][0] == 0)) or 
        ((node1OutFeatures[0][0] == 0 and node2OutFeatures[0][0] != 0) or (node1OutFeatures[0][0] != 0 and node2OutFeatures[0][0] == 0))
       ):
    return ([(0, 0)], numpy.inf)
  lengthIn = len(node1InFeatures[0]) if len(node1InFeatures[0]) < len(node2InFeatures[0]) else len(node2InFeatures[0])
  lengthOut = len(node1OutFeatures[0]) if len(node1OutFeatures[0]) < len(node2OutFeatures[0]) else len(node2OutFeatures[0])
  node1InFeaturesLocal = cutMatrixElementsToLength(node1InFeatures, lengthIn)
  node2InFeaturesLocal = cutMatrixElementsToLength(node2InFeatures, lengthIn)
  node1OutFeaturesLocal = cutMatrixElementsToLength(node1OutFeatures, lengthOut)
  node2OutFeaturesLocal = cutMatrixElementsToLength(node2OutFeatures, lengthOut)

  indexes1 = compareDirPart(node1InFeaturesLocal, node2InFeaturesLocal, node1OutFeaturesLocal, node2OutFeaturesLocal)
  indexes2 = compareDirPart(node2InFeaturesLocal, node1InFeaturesLocal, node2OutFeaturesLocal, node1OutFeaturesLocal)
  diff1 = diff(indexes1)
  diff2 = diff(indexes2)
  #print "diff1In", diff1In
  #print "diff1Out", diff1Out
  #print "diff2In", diff2In
  #print "diff2Out", diff2Out
  #print("returning", (indexes1, diff1) if diff1 < diff2 else (indexes2, diff2))
  return (indexes1, diff1) if diff1 < diff2 else (indexes2, diff2)

def diff(v):
  diffVal = 0
  for data in v:
    diffVal = diffVal + numpy.power(data[2], 2)
  diffVal = diffVal / len(v)
  return diffVal

def euclideanDist(v1, v2):
  return distance.euclidean(v1, v2)

def printPairs(pairs):
  for pair in pairs:
    if pair[0] != pair[1]:
      print(pair[0], "vs.", pair[1], "=", pair[2])

def printPairsIndexed(pairs, indexToElement):
  for pair in pairs:
    if pair[0] != pair[1]:
      print(indexToElement[pair[0]], "(", pair[0], ")", "vs.", indexToElement[pair[1]], "(", pair[1], ")", "=", pair[2])

def cleanFeatureMatrix(featureMatrix):
  finishedMatrix = []
  for featureIndex in range(0, len(featureMatrix)):
    finishedMatrix.append([])
    matrix = []
    graphfeature.processMatrix(featureMatrix[featureIndex], [], matrix)
    length = 0
    for vec in matrix:
      if len(vec) > length:
        length = len(vec)

    for vec in matrix:
      if len(vec) == length:
        finishedMatrix[len(finishedMatrix) - 1].append(vec)
      elif len(vec) == 1:
        if vec[0] == 0:
          finishedMatrix[len(finishedMatrix) - 1].append([0])
  return finishedMatrix

def calcDiffsUndir(adjMat, DegMat):
  featureMatrix = graphfeature.generateFeatureMatrix(adjMat, DegMat)
  finishedMatrix = cleanFeatureMatrix(featureMatrix)
  normalizedMatrix = generateNormalizedMatrix(finishedMatrix)

  pairs = []
  keyPairs = {}
  for index1 in range(0, len(normalizedMatrix)):
    for index2 in range(index1 + 1, len(normalizedMatrix)):
      cVal = compareUndir(normalizedMatrix[index1], normalizedMatrix[index2])
      #print(cVal)
      pairs.append((index1, index2, cVal[1]))
      keyPairs[(index1, index2)] = cVal[1]

  pairs.sort(key=lambda x: x[2], reverse=False)
  return pairs, keyPairs

def generateNormalizedMatrix(finishedMatrix):
  normalizedMatrix = []
  for matrix in finishedMatrix:
    normalizedMatrix.append([])
    for vector in matrix:
      normalizedMatrix[len(normalizedMatrix) - 1].append(vector)
  return normalizedMatrix

def calcDiffsDir(adjMat, d_in, d_out):
  featureMatrixIn = graphfeature.generateFeatureMatrix(adjMat, d_in)
  featureMatrixOut = graphfeature.generateFeatureMatrix(adjMat, d_out)
  finishedMatrixIn = cleanFeatureMatrix(featureMatrixIn)
  finishedMatrixOut = cleanFeatureMatrix(featureMatrixOut)
  normalizedMatrixIn = generateNormalizedMatrix(finishedMatrixIn)
  normalizedMatrixOut = generateNormalizedMatrix(finishedMatrixOut)

  pairs = []
  keyPairs = {}
  for index1 in range(0, len(normalizedMatrixIn)):
    for index2 in range(index1 + 1, len(normalizedMatrixIn)):
      cVal = compareDir(normalizedMatrixIn[index1], normalizedMatrixIn[index2], normalizedMatrixOut[index1], normalizedMatrixOut[index2])
      #print("got", cVal)
      pairs.append((index1, index2, cVal[1]))
      keyPairs[(index1, index2)] = cVal[1]

  pairs.sort(key=lambda x: x[2], reverse=False)
  return pairs, keyPairs


if __name__ == "__main__":
  adjMat_dir, D_in, D_out, D, adjMat_undir = graphgenerate.generateRandomGraph(nodeCount, nodeCount)
#  adjMat_undir = numpy.array([
#   [0, 1, 0, 1, 1, 0],
#   [1, 0, 1, 0, 0, 1],
#   [0, 1, 0, 1, 0, 0],
#   [1, 0, 1, 0, 0, 1],
#   [1, 0, 0, 0, 0, 0],
#   [0, 1, 0, 1, 0, 0]])
#  D = numpy.array([
#   [3, 0, 0, 0, 0, 0],
#   [0, 3, 0, 0, 0, 0],
#   [0, 0, 2, 0, 0, 0],
#   [0, 0, 0, 3, 0, 0],
#   [0, 0, 0, 0, 1, 0],
#   [0, 0, 0, 0, 0, 2]])

#  adjMat_undir = numpy.array([
#    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]])
#  D = numpy.array([
#    [12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]])

#  D = numpy.array([
#    [0, 0, 0, 0],
#    [0, 0, 0, 0],
#    [0, 0, 0, 0],
#    [0, 0, 0, 0]])
#  adjMat_undir = numpy.array([
#    [0, 0, 0, 0],
#    [0, 0, 0, 0],
#    [0, 0, 0, 0],
#    [0, 0, 0, 0]])
  plt.subplot(221)
  graphdisplay.renderDiGraphFromAdj(adjMat_dir)
  plt.subplot(222)
  graphdisplay.renderUndirGraphFromAdj(adjMat_undir)
  #undirected graph
  pairs1, keyPairs1 = calcDiffsUndir(adjMat_undir, D)
  print("Undirected Graph Differences between nodes")
  printPairs(pairs1)

  #directed graph
  pairs2, keyPairs2 = calcDiffsDir(adjMat_dir, D_in, D_out)
  print("Directed Graph Differences between nodes")
  printPairs(pairs2)
  #for ele2 in pairs2:
  #  cVal1 = ele2[2]
  #  cVal2 = keyPairs3[(ele2[0], ele2[1])]
  #  if cVal1 != numpy.Inf and cVal2 != numpy.Inf:
  #    pairs4.append((ele2[0], ele2[1], cVal1, cVal2))
  #print "Directed Graph Differences between nodes"
  #for index1 in range(0, len(pairs4)):
  #  for index2 in range(0, len(pairs4)):
  #    x1 = pairs4[index1][2]
  #    y1 = pairs4[index1][3]
  #    x2 = pairs4[index2][2]
  #    y2 = pairs4[index2][3]
  #    print pairs4[index1][euclideanDist([x1, y1], [x2, y2])
  plt.show()

