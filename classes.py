from utils import interpolate

class RequestBuilder:
    def __init__(self, api_template, test_data):
        self.api = api_template
        self.data = test_data
    
    def build_url(self):
        base_url = self.api["base_url"]
        endpoint = interpolate(self.api["endpoint"], self.data)
        return base_url + endpoint

    def build_headers(self, auth_config):
        return 1
    
    def build_param_dict(self, target, payload=None):
        params = self.api.get(target, None)
        if not params: return params
        if not payload: payload = dict()

        for key, placeholder in params.items():
            if isinstance(placeholder, dict):
                payload.update({key : {}})
                for nested_item in placeholder:
                    try:                        
                        payload[key].update({nested_item : self.data[nested_item]})                       
                    except KeyError:
                        payload[key].update({nested_item : self.build_param_dict(nested_item, payload)})
            try:
                payload.update({key : self.data[key]})
            except KeyError:
                continue
        return payload

    def get_internet_token(self):
        return 1

    def get_intranet_token(self):
        return 1

    def get_trasaction_token(self):
        return 1