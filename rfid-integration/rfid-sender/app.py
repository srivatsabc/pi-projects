import logging
import msal
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'myHttpTrigger')))
import app_config
import requests
import json
import oled

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        logging.info("req_body " + str(req_body))
        oid = req_body.get('objectId')
        logging.info("oid " + oid)
        customertype = req_body.get('customertype')
        token = _build_msal_app().acquire_token_for_client(
            scopes=app_config.SCOPE)
        
        logging.info("Sign up")
        data = json.dumps(_build_message(customertype))
        logging.info("msg " + str(data))
        graph_data = requests.patch(
            app_config.WRITE_ENDPOINT + oid,
            data=data,
            headers={'Authorization': 'Bearer ' + token['access_token'], 'Content-Type': 'application/json'},
        )
        logging.info("graph_data " + str(graph_data))
        if str(graph_data) == app_config.RESPONSE:
            return func.HttpResponse(
                json.dumps(_build_response(json.loads(data)[app_config.ROLE_TAG])),
                mimetype='application/json',
                status_code=201
            )
        else:
            return func.HttpResponse(
                "Unable to update role",
                mimetype='application/json',
                status_code=200
            )

def _build_message(type):
    role = type + app_config.ROLE
    message = {
        app_config.ROLE_TAG: role,
    }
    return message

def _build_response(role):
    message = {
        "extension_role": role,
    }
    return message

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)
