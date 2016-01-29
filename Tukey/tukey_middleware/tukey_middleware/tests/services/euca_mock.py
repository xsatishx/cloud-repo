#  Copyright 2013 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

''' Runs as a fake euca cc for testing purposes '''

from flask import Flask, request

app = Flask(__name__)

@app.route("/services/Eucalyptus", methods=["GET","POST"])
#@app.route("/services/Eucalyptus/", methods=["GET","POST"])
def euca_get():

    action = request.args.get('Action')
    if action is None:
        action = request.form['Action']

    if action == "DescribeInstances":
        return '<DescribeInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2010-08-31/"><requestId>7e8f5e41-37f8-4cd2-8788-0b8000872b9a</requestId><reservationSet><item><reservationId>r-4CF809C2</reservationId><ownerId>mgreenway</ownerId><groupSet><item><groupId>default</groupId></item></groupSet><instancesSet><item><instanceId>i-4917082C</instanceId><imageId>emi-938D136D</imageId><instanceState><code>16</code><name>running</name></instanceState><privateDnsName>10.103.112.67</privateDnsName><dnsName>10.103.112.67</dnsName><reason>NORMAL:  -- [UPDATE]</reason><keyName/><amiLaunchIndex>0</amiLaunchIndex><productCodes/><instanceType>m1.small</instanceType><launchTime>2013-06-24T22:48:22.468Z</launchTime><placement><availabilityZone>kg12</availabilityZone></placement><kernelId>eki-E7641078</kernelId><ramdiskId>eri-1BF61154</ramdiskId><monitoring><state>false</state></monitoring></item></instancesSet></item></reservationSet></DescribeInstancesResponse>'

    elif action == "DescribeAddresses":
        return '<DescribeAddressesResponse xmlns="http://ec2.amazonaws.com/doc/2010-08-31/"><requestId>1ef7ff29-eda7-4df1-a399-13491fbc2dc4</requestId><addressesSet/></DescribeAddressesResponse>'

    elif action == "DescribeImages":
        return '<DescribeImagesResponse xmlns="http://ec2.amazonaws.com/doc/2010-08-31/"><requestId>7bb219d5-646b-491f-a445-d506fc420ac9</requestId><imagesSet><item><imageId>emi-938D136D</imageId><imageLocation>admin/prototypical-2011-08-04-t2.img.manifest.xml</imageLocation><imageState>available</imageState><imageOwnerId>admin</imageOwnerId><isPublic>true</isPublic><productCodes/><architecture>x86_64</architecture><imageType>machine</imageType></item></imagesSet></DescribeImagesResponse>'

    elif action == "DescribeKeyPairs":
        return '<DescribeKeyPairsResponse xmlns="http://ec2.amazonaws.com/doc/2010-08-31/"><requestId>e6113078-bf43-4427-b073-0268a6f20243</requestId><keySet><item><keyName>testadler</keyName><keyFingerprint>87:f9:0c:ff:e9:ea:c8:05:7f:d7:7c:c5:7e:78:6f:2a:aa:80:9a:e3</keyFingerprint></item></keySet></DescribeKeyPairsResponse>'
    elif action == "TerminateInstances":
        return '<TerminateInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2010-08-31/"><requestId>4da18f07-d8b4-4546-af40-cfc88ef62ab8</requestId><instancesSet><item><instanceId>i-4917082C</instanceId><shutdownState><code>32</code><name>shutting-down</name></shutdownState><previousState><code>16</code><name>running</name></previousState></item></instancesSet></TerminateInstancesResponse>'
    elif action == "RunInstances":
        return '<RunInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2010-08-31/"><requestId>e70dd984-04ce-4d86-bb13-2ef3f6b2df7f</requestId><reservationId>r-437D084C</reservationId><ownerId>mgreenway</ownerId><groupSet><item><groupId>mgreenway-default</groupId></item></groupSet><instancesSet><item><instanceId>i-4917082C</instanceId><imageId>emi-938D136D</imageId><instanceState><code>0</code><name>pending</name></instanceState><privateDnsName>0.0.0.0</privateDnsName><dnsName>0.0.0.0</dnsName><reason>NORMAL:  -- []</reason><keyName>osdc_keypair</keyName><amiLaunchIndex>0</amiLaunchIndex><productCodes/><instanceType>m1.small</instanceType><launchTime>2013-07-28T22:00:52.108Z</launchTime><placement><availabilityZone>kg12</availabilityZone></placement><kernelId>eki-E7641078</kernelId><ramdiskId>eri-1BF61154</ramdiskId><monitoring><state>false</state></monitoring></item></instancesSet></RunInstancesResponse>'
    else:
        return ''

if __name__ == "__main__":
    app.run(host='127.3', debug=True, port=8773)

