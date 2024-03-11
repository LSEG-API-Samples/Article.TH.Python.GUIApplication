#=============================================================================
#   This source code is provided under the Apache 2.0 license
#   and is provided AS IS with no warranty or guarantee of fit for purpose.
#   Copyright (C) 2024 LSEG. All rights reserved.
#=============================================================================

import requests, json

# ----------------------------
# TH class implements the REST API calls for getting VBD data from Tick History
# User has to successfully login and receive an OAuth token as the first step
class TH():
# ----------------------------
	def __init__(self, controller):
		self.BASE_URL = 'https://selectapi.datascope.refinitiv.com/RestApi/v1'
		self.hdrs = {
			"Prefer": "respond-async",
			"Content-Type": "application/json",
		}
		self.controller = controller



	# Tickhistory REST-GET function
	def _getJsonAsync(self, uri):
		dResp = requests.get(uri, headers=self.hdrs)
		# is it a 202 (in progress)
		while dResp.status_code == 202:
			self.controller.setMsg("waiting for response...")
			# check if the response completed yet
			nURL = dResp.headers['Location']
			dResp = requests.get(nURL, headers=self.hdrs)

		if (dResp.status_code == 200):
			return dResp.json(), ''
		else:
			return None, dResp.json()



	def login(self, username, password):
		pData = {
			"Credentials": {
				"Username": username,
				"Password": password
			}
		}
		dResp = requests.post(f'{self.BASE_URL}/Authentication/RequestToken', data=json.dumps(pData), headers=self.hdrs)

		if (dResp.status_code == 200):
			aToken = dResp.json()['value']
			# keep a copy of the oAuth token for other calls
			self.hdrs["Authorization"] = "Token " + aToken
			return aToken, ''
		else:
			return None, dResp.json()['error']['message']



	def getAllPackages(self):
		uPackages, msg = self._getJsonAsync(f'{self.BASE_URL}/StandardExtractions/UserPackages')
		return uPackages, msg



	def getSchedules(self, packageID):
		delivery, msg = self._getJsonAsync(f'{self.BASE_URL}/StandardExtractions/UserPackageDeliveryGetUserPackageDeliveriesByPackageId(PackageId=\'{packageID}\')')

		# Use Server-Paging to loop through the delivery schedule results and get more previous days
		# while '@odata.nextlink' in delivery:
		# 	self.controller.setMsg("Getting next page...")
		# 	delivery, msg = self._getJsonAsync(delivery['@odata.nextlink'])
		# 	# append the values array in this json message to the root json message

		return delivery, msg



	def downloadFile(self, view, deliveryID, fileName, fileSize, downloadFromAWS=True):
		uri = f'{self.BASE_URL}/StandardExtractions/UserPackageDeliveries(\'{deliveryID}\')/$value'

		downloadHdrs = dict(self.hdrs)
		if downloadFromAWS:
			downloadHdrs['X-Direct-Download'] = 'true'

		dResp = requests.get(uri, headers=downloadHdrs, stream=True)
		# do not auto decompress the data
		dResp.raw.decode_content = False

		chunkSize = 1024*1024
		cStep = chunkSize * 100 / fileSize
		if cStep > 100:
			cStep = 100

		with open(fileName, 'wb') as f:
			step = 1
			for chunk in dResp.iter_content(chunk_size=chunkSize):
				if chunk:
					f.write(chunk)
					progr = int(cStep * step)
					if progr > 100:
						progr = 100

					view.setProgress(progr)
					self.controller.update_idletasks()
					step += 1

		f.close
		self.controller.setMsg(f'File "{fileName}" downloaded')



