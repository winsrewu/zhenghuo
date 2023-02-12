import requests
import json

'''token 获取方式:
https://login.live.com/oauth20_authorize.srf
?client_id=00000000402b5328
&response_type=code
&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL
&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf
'''
authorizationCode = "???"

authUrl = "https://login.live.com/oauth20_token.srf"
xblUrl = "https://user.auth.xboxlive.com/user/authenticate"
xstsUrl = "https://xsts.auth.xboxlive.com/xsts/authorize"
mcUrl = "https://api.minecraftservices.com/authentication/login_with_xbox"
mcdetailUrl = "https://api.minecraftservices.com/minecraft/profile"


'''microroft oauth验证'''
def oauth():
	authData = {
		"client_id": "00000000402b5328",
		"code": authorizationCode,
		"grant_type": "authorization_code",
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "scope": "service::user.auth.xboxlive.com::MBI_SSL"
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	authRes = requests.post(authUrl, data = authData, headers = headers)
	print(authRes)
	print(authRes.text)

	accessToken = "null"

	authJson = json.loads(authRes.text)
	if 'access_token' in authJson:
		accessToken = authJson['access_token']
	else:
		print('bruh!!!!!')

	print('\naccess_token: ' + accessToken)
	print(" -*- \n\n")

	xbl(accessToken)


'''xbox live验证'''
def xbl(accessToken):
	xblData = {
		"Properties": {
			"AuthMethod": "RPS",
			"SiteName": "user.auth.xboxlive.com",
			"RpsTicket": accessToken
		},
		"RelyingParty": "http://auth.xboxlive.com",
		"TokenType": "JWT"
	}
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json"
	}

	xblData = json.dumps(xblData)
	xblData = xblData.replace("'", '"')

	xblRes = requests.post(xblUrl, data = xblData, headers = headers)

	print(xblRes)
	print(xblRes.text)

	token = "null"
	uhs = "null"

	xblJson = json.loads(xblRes.text)
	if 'Token' in xblJson and 'DisplayClaims' in xblJson:
		token = xblJson['Token']
		uhs = xblJson['DisplayClaims']['xui'][0]['uhs']
	else:
		print('bruh!!!!!')

	print('\ntoken: ' + token)
	print('\nuhs: ' + uhs)
	print(" -*- \n\n")

	xsts(token, uhs)


'''xsts验证'''
def xsts(token, uhs):
	xstsData =  {
		"Properties": {
			"SandboxId": "RETAIL",
			"UserTokens": {
				"xbl_token": token
			}
		},
		"RelyingParty": "rp://api.minecraftservices.com/",
		"TokenType": "JWT"
	}
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json"
	}

	xstsData = json.dumps(xstsData)
	xstsData = xstsData.replace("'", '"')
	xstsData = xstsData.replace('{"xbl_token": ', '[')
	xstsData = xstsData.replace('"}},', '"]},')

	xstsRes = requests.post(xstsUrl, data = xstsData, headers = headers)

	print(xstsRes)
	print(xstsRes.text)

	xblToken = "null"

	xstsJson = json.loads(xstsRes.text)
	if 'Token' in xstsJson:
		xstsToken = xstsJson['Token']
	else:
		print('bruh!!!!!')

	print('\ntoken: ' + xstsToken)
	print(" -*- \n\n")

	mc(xstsToken, uhs)


'''MinecraftToken'''
def mc(token, uhs):
	identityToken = "XBL3.0 x=" + uhs + ";" + token

	mcData =  {
		"identityToken": identityToken
	}

	mcData = json.dumps(mcData)
	mcData = mcData.replace("'", '"')

	mcRes = requests.post(mcUrl, data = mcData)

	print(mcRes)
	print(mcRes.text)
	mcToken = "null"

	mcJson = json.loads(mcRes.text)
	if 'access_token' in mcJson:
		mcToken = mcJson['access_token']
	else:
		print('bruh!!!!!')

	print('\ntoken: ' + mcToken)
	print(" -*- \n\n")

	mcdetail(mcToken)

'''get uuid and name'''
def mcdetail(token):
	Authorization = "Bearer " + token
	headers = {
		'Authorization': Authorization
	}

	mcdetailRes = requests.get(mcdetailUrl, headers = headers)

	print(mcdetailRes)
	print(mcdetailRes.text)

'''use refresh token to get microsoft token again'''
def msrf(refresh_token):
	authData = {
		"client_id": "00000000402b5328",
		"refresh_token": refresh_token,
		"grant_type": "refresh_token",
		"scope": "service::user.auth.xboxlive.com::MBI_SSL"
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	authRes = requests.post(authUrl, data = authData, headers = headers)
	print(authRes)
	print(authRes.text)

	accessToken = "null"

	authJson = json.loads(authRes.text)
	if 'access_token' in authJson:
		accessToken = authJson['access_token']
	else:
		print('bruh!!!!!')

	print('\naccess_token: ' + accessToken)
	print(" -*- \n\n")


'''Main'''
if False:
	oauth()
else:
	msrf("???")