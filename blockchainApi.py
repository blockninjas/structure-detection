from blockchain import blockexplorer
import math
import time
import generateanddisplayrandomgraph
import graphgenerate
import numpy

"""
blockHash = "00000000000001e4277b696b03ed1e085037bcfec8e2a1b7454f9cfd2d936e41"
block = blockexplorer.get_block(blockHash)
print "building data"
for tx in block.transactions:
  for input in tx.inputs:
    if hasattr(input, "address"):
      address = input.address
      if address not in addresses:
        addresses.append({ "address": address, "in": [], "out": [], "txs": []})
  for output in tx.outputs:
    address = output.address
    if address not in addresses:
      addresses.append({ "address": address, "in": [], "out": [], "txs": []})
"""

def addAddress(address):
  global addresses
  addresses[address] = { "in": [], "out": [], "txs": [], "address": address, "inAddresses": [], "outAddresses": [] }

def getAddressData(address):
  global addresses
  for addressData in addresses:
    if addressData["address"] == address:
      return addressData

def txInTxList(tx, txs):
  global addresses
  for txLocal in txs:
    if txLocal.hash == tx.hash:
      return True
  return False

def getAllIncomeAddressesFromAddress(address):
  return importDataAndGetAddressesFromIndex(address, "inAddresses")

def getAllOutgoingAddressesFromAddress(address):
  return importDataAndGetAddressesFromIndex(address, "outAddresses")

def importDataAndGetAddressesFromIndex(address, key):
  global addresses
  global sleepTime
  inAddresses = []
  outAddresses = []
  addressObject = None
  print "query for data", key
  if address not in addresses:
    addAddress(address)
    addressObject = addresses[address]
    addressData = blockexplorer.get_address(address)
    addressObject["txs"] = addressObject["txs"] + addressData.transactions
    for noTx in range(1, int(math.ceil(float(addressData.n_tx) / 50.0))):
      print "getting more data", key
      time.sleep(sleepTime)
      addressData = blockexplorer.get_address(address, offset = noTx * 50)
      addressObject["txs"] = addressObject["txs"] + addressData.transactions
      print noTx * 50, "/", addressData.n_tx
      #if noTx > 1:
      #  break
    print "processing queried data", len(addressObject["txs"])
    for tx in addressObject["txs"]:
      print "tx", tx.hash
      for input in tx.inputs:
        if hasattr(input, "address"):
          if addressObject["address"] == input.address:
            if not txInTxList(tx, addressObject["out"]):
              addressObject["out"] = addressObject["out"] + [tx]
          #if input.address not in inAddresses:
          inAddresses.append(input.address)
      for output in tx.outputs:
        if addressObject["address"] == output.address:
          if txInTxList(tx, addressObject["in"]):
            addressObject["in"] = addressObject["in"] + [tx]
        #if output.address not in outAddresses:
        outAddresses.append(output.address)
    addressObject["inAddresses"] = numpy.array(numpy.unique(inAddresses))
    addressObject["outAddresses"] = numpy.array(numpy.unique(outAddresses))
    addresses[address] = addressObject
  print "return data", key
  return addresses[address][key].tolist()

def processAddress(address, level):
  global processedAddresses
  global addressToIndex, indexToAddress
  global adjMat_dir, adjMat_undir
  global D, D_in, D_out
  global edges
  incomingAddresses = []
  outgoingAddresses = []
  if address not in processedAddresses:
    incomingAddresses = getAllIncomeAddressesFromAddress(address)
    outgoingAddresses = getAllOutgoingAddressesFromAddress(address)

    newIndex = len(adjMat_dir) # also possible: len(adjMat_undir)
    addressToIndex[address] = newIndex
    indexToAddress[newIndex] = address
    adjMat_dir.append([])
    adjMat_undir.append([])
    D.append([])
    D_in.append([])
    D_out.append([])
    edges[address] = {}
    edges[address]["in"] = incomingAddresses
    edges[address]["out"] = outgoingAddresses
    processedAddresses.append(address)

    if level < 2:
      for incomingAddress in incomingAddresses:
        processAddress(incomingAddress, level + 1)
      for outgoingAddress in outgoingAddresses:
        processAddress(outgoingAddress, level + 1)

def setAdjMat(fromAdr, toAdr, val, adjMat):
  global addressToIndex
  global indexToAddress
  if fromAdr in addressToIndex and toAdr in addressToIndex:
    adjMat[addressToIndex[fromAdr]][addressToIndex[toAdr]] = val

def getAdjMat(fromAdr, toAdr, adjMat):
  global addressToIndex
  global indexToAddress
  if fromAdr in addressToIndex and toAdr in addressToIndex:
    return adjMat[addressToIndex[fromAdr]][addressToIndex[toAdr]]

addresses = {}
sleepTime = 0.9

addresses = {}
processedAddresses = []
addressToIndex = {}
indexToAddress = {}
edges = {}

adjMat_dir = []
adjMat_undir = []
D = []
D_in = []
D_out = []

processAddress("1BTCDiceLs79syendE1DM1XCaHcKkzBNnP", 1)
processAddress("1JDeVnSeRUm7G5okbnmFnRwvfsWDmG2oSe", 1)
processAddress("16LQodsvHtydHPrsFqBw63c8z6R2F8Nayt", 1)
processAddress("1BTCDicen28RVKQeMCPKyEcEWFVE9MpJ1i", 1)

print "process all addresses"
for address in addressToIndex:
  adjMat_dir[addressToIndex[address]] = [0] * len(adjMat_dir)
  adjMat_undir[addressToIndex[address]] = [0] * len(adjMat_undir)
  D[addressToIndex[address]] = [0] * len(D)
  D_out[addressToIndex[address]] = [0] * len(D_out)
  D_in[addressToIndex[address]] = [0] * len(D_in)

print "process all edges"
for address in edges:
  incomingAddresses = getAllIncomeAddressesFromAddress(address)
  outgoingAddresses = getAllOutgoingAddressesFromAddress(address)

  print "building D_in"
  for inAddress in edges[address]["in"]:
    setAdjMat(inAddress, address, 1, adjMat_dir)
  D_in[addressToIndex[address]][addressToIndex[address]] = len(edges[address]["in"])

  print "building D_out"
  for outAddress in edges[address]["out"]:
    setAdjMat(address, outAddress, 1, adjMat_dir)
  D_out[addressToIndex[address]][addressToIndex[address]] = len(edges[address]["out"])

  print "building D"
  connectedAddresses = list(set(incomingAddresses + outgoingAddresses))
  for connectedAddress in connectedAddresses:
    setAdjMat(address, connectedAddress, 1, adjMat_undir)
    setAdjMat(connectedAddress, address, 1, adjMat_undir)
  D[addressToIndex[address]][addressToIndex[address]] = len(connectedAddresses)

print "addressToIndex", addressToIndex
print "indexToAddress", indexToAddress
print "adjMat_dir", adjMat_dir
print "adjMat_undir", adjMat_undir
print "D", D
print "D_in", D_in
print "D_out", D_out

#adjMat_dir, D_in, D_out, D, adjMat_undir = graphgenerate.generateRandomGraph(nodeCount, nodeCount)
adjMat_dir = numpy.array(adjMat_dir)
adjMat_undir = numpy.array(adjMat_undir)
D = numpy.array(D)
D_in = numpy.array(D_in)
D_out = numpy.array(D_out)

#directed graph
pairs2, keyPairs2 = generateanddisplayrandomgraph.calcDiffsDir(adjMat_dir, D_in, D_out)
print "Directed Graph Differences between nodes"
generateanddisplayrandomgraph.printPairsIndexed(pairs2, indexToAddress)
