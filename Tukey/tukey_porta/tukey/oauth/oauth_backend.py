import requests,unicodedata,base64, json
from django.conf import settings
NORMAL_FORM = 'NFKD'

class OauthBackend:
    '''Google oauth2.0 backend'''
    #endpoints for varies google oauth services
    urls={}
    def __init__(self):
        self.urls=self.getUrls()
    
    def getUrls(self):
        r=requests.get(settings.OAUTH['discovery_document'])
        return r.json()      
    

    def getToken(self,code):
        '''
        Get access token and id token from google
        
        @param string code      temporary authorization code get from google
        @return string email    user identifier that's used in keystone backend
        '''
        data={'code':code,\
              'client_id':settings.OAUTH['parameters']['client_id'],
              'client_secret':settings.OAUTH['client_secret'],
              'redirect_uri':settings.OAUTH['parameters']['redirect_uri'],
              'grant_type':'authorization_code'}
        r=requests.post(self.urls['token_endpoint'],data=data)
        return r.json()
    
    def decode(self,token):
        '''
        Decode Id token and extract user email, validity of the token is not 
        checked since SSL communication between tukey and google is trusted
        
        @param unicode token    a JWT that contains identity information about the user that is digitally signed by Google
        @return string email    user identifier that's used in keystone backend
        '''
        [header,payload,signature]=token.split(".")
        payload=unicodedata.normalize(NORMAL_FORM,payload).encode('ascii','ignore')
        payload+='='*(4-(len(payload)%4))
        decoded_payload = base64.urlsafe_b64decode(payload)
        return json.loads(decoded_payload)['email']
