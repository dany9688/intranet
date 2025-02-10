from django.utils.deprecation import MiddlewareMixin

class ForceSessionDomainMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if 'sessionid' in response.cookies:
            response.cookies['sessionid']['domain'] = "192.168.0.251"
        return response
