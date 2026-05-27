from django.http import HttpResponse, HttpResponseServerError
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase, HttpResponseRedirectBase
from django.shortcuts import redirect
from django.views.generic import View


class CoreSystemBaseView(View):
    page_title = None
    page_name = ""

    def get(self, request, *args, **kwargs):
        return HttpResponse("", status=405)

    def post(self, request, *args, **kwargs):
        return HttpResponse("", status=405)

    def put(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass

    @staticmethod
    def get_extra_context(*args, **kwargs):
        return {}

    def get_base_context(self) -> dict:
        return {
            "headInfo": {
                "title": self.page_title,
                "currentPage": self.page_name,
            }
        }

    def get_context(self, **kwargs):
        return {
            **self.get_base_context(),
            **self.get_extra_context(),
            **kwargs,
            "context": kwargs,
        }

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        method = getattr(self, str(request.method).lower())

        response = method(request, *args, **kwargs)
        if isinstance(response, str):
            return redirect(response)  # redirect to an url
        elif isinstance(response, HttpResponseBase) or isinstance(
            response, HttpResponseRedirectBase
        ):
            return response
        else:
            return HttpResponseServerError(
                "Unknown response, please contact the administrator."
            )
