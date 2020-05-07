import os
import boto3
import cfnresponse
import xml.etree.ElementTree as ET


def lambda_handler(event, context):

    ec2 = boto3.client('ec2')
    
    response = ec2.describe_vpn_connections()
    
    responseData = {}
    InsideList = []
    
    # First find the correct vpn tunnel and then
    # Walk the XML to find the private IP addresses for both tunnels
    for vpn in response['VpnConnections']:
        if vpn['VpnConnectionId']==os.environ['VpnId']:
            xmlstring = vpn['CustomerGatewayConfiguration']
            root = ET.fromstring(xmlstring)
            for tunnel in root.findall('ipsec_tunnel/customer_gateway/tunnel_inside_address'):
                InsideList.append(tunnel.find('ip_address').text)
    
    responseData['CgwInsideIpAddress1'] = InsideList[0]
    responseData['CgwInsideIpAddress2'] = InsideList[1]
    
    # take the last octect of the ip address and subtract it by 1 to get the VGW inside IP address
    responseData['TgwInsideIpAddress1'] = InsideList[0][:-1]+str(int(InsideList[0][-1])-1)
    responseData['TgwInsideIpAddress2'] = InsideList[1][:-1]+str(int(InsideList[1][-1])-1)
    
    responseData['OutsideIpAddress1'] = response['VpnConnections'][0]['VgwTelemetry'][0]['OutsideIpAddress']
    responseData['OutsideIpAddress2'] = response['VpnConnections'][0]['VgwTelemetry'][1]['OutsideIpAddress']
    
    print(responseData)

    # return a dict to cloudformation
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)