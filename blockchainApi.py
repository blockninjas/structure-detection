from blockchain import blockexplorer
import math
import time

blockHeight = 200111
blockHash = "00000000000001e4277b696b03ed1e085037bcfec8e2a1b7454f9cfd2d936e41"
addresses = {}
startAddress = "1BTCDiceLs79syendE1DM1XCaHcKkzBNnP"

print "get blk chain data"
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

addresses = {}
addresses["1BTCDiceLs79syendE1DM1XCaHcKkzBNnP"] = { "in": [], "out": [], "txs": [] }
addresses["1JDeVnSeRUm7G5okbnmFnRwvfsWDmG2oSe"] = { "in": [], "out": [], "txs": [] }
addresses["16LQodsvHtydHPrsFqBw63c8z6R2F8Nayt"] = { "in": [], "out": [], "txs": [] }
addresses["1BTCDicen28RVKQeMCPKyEcEWFVE9MpJ1i"] = { "in": [], "out": [], "txs": [] }

print "post processing data"
for address in addresses.values():
  addressObject = addresses[address]
  addressData = blockexplorer.get_address(address["address"])
  addressObject["txs"] = addressObject["txs"] + addressData.transactions
  for noTx in range(1, int(math.ceil(float(addressData.n_tx) / 50.0))):
    print "getting more data"
    time.sleep(0.01)
    addressData = blockexplorer.get_address(address["address"], offset = noTx * 50)
    addressObject["txs"] = addressObject["txs"] + addressData.transactions

  for tx in addressObject["txs"]:
    for input in tx.inputs:
      if hasattr(input, "address"):
        if addressObject["address"] == input.address:
          if tx not in addressObject["out"]:
            addressObject["out"] = addressObject["out"] + [tx]
        if input.address not in addresses:
          addresses[input.address] = { "in": [], "out": [], "txs": [] }
    for output in tx.outputs:
      if addressObject["address"] == output.address:
        if tx not in addressObject["in"]:
          addressObject["in"] = addressObject["in"] + [tx]
      if output.address not in addresses:
        addresses[output.address] = { "in": [], "out": [], "txs": [] }

  addresses[address] = addressObject
  print "processing", index, "of", len(addresses)

print addresses

def getAddressData(address):
  global addresses
  for addressData in addresses:
    if addressData["address"] == address:
      return addressData

def getAllIncomeAddressesFromAddress(address):
  global addresses
  addresses = []
  addressData = getAddressData(address)
  for tx in addressData["in"]:
    for input in tx.inputs:
      if hasattr(input, "address"):
        if input.address not in addresses:
          addresses = addresses + [input.address]
  return addresses

def getAllOutgoingAddressesFromAddress(address):
  global addresses
  addresses = []
  addressData = getAddressData(address)
  for tx in addressData["out"]:
    for output in tx.outputs:
      if output.address not in addresses:
        addresses = addresses + [output.address]
  return addresses

def processAddress(address, level):
  global processedAddresses
  global addressToIndex, indexToAddress
  global adjMat_dir, adjMat_undir
  global D, D_in, D_out
  incomingAddresses = []
  outgoingAddresses = []
  if address not in processedAddresses:
    incomingAddresses = getAllIncomeAddressesFromAddress(address)
    outgoingAddresses = getAllOutgoingAddressesFromAddress(address)

    newIndex = len(adjMat_dir) # also possible: len(adjMat_undir)
    addressToIndex[newIndex] = address
    indexToAddress[address] = newIndex
    adjMat_dir.append([])
    adjMat_undir.append([])
    D.append([])
    D_in.append([])
    D_out.append([])
    edges[address]["in"] = incomingAddresses
    edges[address]["out"] = outgoingAddresses
    processedAddresses.append(address)

    if level < 2:
      for incomingAddress in incomingAddresses:
        processAddress(incomingAddress, level + 1)
      for outgoingAddress in outgoingAddresses:
        processAddress(outgoingAddress, level + 1)

processedAddresses = []
addressToIndex = {}
indexToAddress = {}
edges = {}

adjMat_dir = []
adjMat_undir = []
D = []
D_in = []
D_out = []

processAddress(startAddress, 1)
print addressToIndex
print indexToAddress
print adjMat_dir
print adjMat_undir
print D
print D_in
print D_out
quit()

def setAdjMat(fromAdr, toAdr, val, adjMat):
  global addressToIndex
  global indexToAddress
  adjMat[addressToIndex[fromAdr]][addressToIndex[toAdr]] = val

def getAdjMat(fromAdr, toAdr, adjMat):
  global addressToIndex
  global indexToAddress
  return adjMat[addressToIndex[fromAdr]][addressToIndex[toAdr]]

for address in addressToIndex:
  adjMat_dir[addressToIndex[address]] = [0] * len(adjMat_dir)
  adjMat_undir[addressToIndex[address]] = [0] * len(adjMat_undir)
  D[addressToIndex[address]] = [0] * len(D)
  D_out[addressToIndex[address]] = [0] * len(D_out)
  D_in[addressToIndex[address]] = [0] * len(D_in)

for address in edges:
  for inAddress in edges[address]["in"]:
    setAdjMat(inAddress, address, 1, adjMat_dir)
  D_in[addressToIndex[address]][addressToIndex[address]] = len(edges[address]["in"])

  for outAddress in edges[address]["out"]:
    setAdjMat(address, outAddress, 1, adjMat_dir)
  D_out[addressToIndex[address]][addressToIndex[address]] = len(edges[address]["out"])

  connectedAddresses = list(set(incomingAddresses + outgoingAddresses))
  for connectedAddress in connectedAddresses:
    setAdjMat(address, connectedAddress, 1, adjMat_undir)
    setAdjMat(connectedAddress, address, 1, adjMat_undir)
  D[addressToIndex[address]][addressToIndex[address]] = len(connectedAddresses)
