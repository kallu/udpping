import os
import json
import socket 
import binascii
import datetime

def status(statusMsg):

	statusMsg['timestamp'] = datetime.datetime.utcnow().isoformat()
	return {
		'statusCode': statusMsg['statusCode'],
		'body': json.dumps(statusMsg),
		'headers': {'Content-Type': 'application/json'}
	}

def handler(event, context):

	# All 5 URL parameters must be provided

	# AUTH  = SHARED SECRET
	# HOST  = "my.fqdn.com" 
	# PORT  = 12345
	# SEND  = "deadbeef"
	# REPLY = "cafebabe"

	statusMsg = {
		'statusCode': 200,
		'targetHost': '',
		'targetPort': '',
		'sendData': '',
		'replyData': '',
		'expectData': '',
		'status': 'OK',
		'timestamp': ''
	}

	try:
		targetHost = str(event['queryStringParameters']['HOST'])
		targetPort = int(event['queryStringParameters']['PORT'])
		sendData = str(event['queryStringParameters']['SEND'])
		expectData = str(event['queryStringParameters']['REPLY'])
		secret = str(event['queryStringParameters']['AUTH'])

	except Exception:
		statusMsg['statusCode'] = 400
		statusMsg['status'] = 'Missing parameters'
		return status(statusMsg)

	if secret != os.environ.get('SECRET1') and secret != os.environ.get('SECRET2'):
		statusMsg['statusCode'] = 401
		statusMsg['status'] = 'Unauthorized'
		return status(statusMsg)

	statusMsg['targetHost'] = targetHost
	statusMsg['targetPort'] = targetPort
	statusMsg['sendData'] = sendData
	statusMsg['expectData'] = expectData

	# Create a UDP datagram socket with address family of IPv4 (INET) 
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Send message to server
	try:
		sock.sendto(binascii.unhexlify(sendData.upper()), (targetHost, targetPort))
	except Exception:
		statusMsg['statusCode'] = 404
		statusMsg['status'] = 'Can not connect'
		return status(statusMsg)

	# Wait 1s for reply from server (max 1024 bytes)
	sock.settimeout(1.0)
	try:
		replyData, addr = sock.recvfrom(1024)
	except Exception:
		statusMsg['statusCode'] = 408
		statusMsg['status'] = 'Timeout'
		return status(statusMsg)

	statusMsg['replyData'] = binascii.hexlify(replyData).upper()

	if binascii.hexlify(replyData).upper() != expectData.upper():
		statusMsg['statusCode'] = 404
		statusMsg['status'] = 'Reply does not match with expected data'
		return status(statusMsg)

	return status(statusMsg)
