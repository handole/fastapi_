import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

from app.utils.audit_log import BauditLogger

audit_log = BauditLogger()


class BauditLogMiddleware(BaseHTTPMiddleware, UserInfoBackend):
    async def dispatch(self, request, call_next):
        routes = request.app.router.routes
        query_params = []
        for route in routes:
            match, scope = route.matchs(request)
            if match == Match.FULL:
                for name, value in scope["path_params"].items():
                    query_params.append({name: value})

        response = await call_next(request)

        # consuming FastAPI response and grabbing body here
        resp_body = [section async for section in response.__dict__["body_iterator"]]
        # Repairing FastAPI response
        response.__setattr__("body_iterator", aiwrapper(resp_body))

        # Formatting response body for logging
        try:
            resp_body = json.loads(resp_body[0].decode())
        except Exception:
            resp_body = str(resp_body)

        headers = dict(request.headers)

        # Check user bellow here
        user_info = await self.get_user_info(
            auth_header=headers.get("authorization", None)
        )

        http_status_description = HTTP_STATUS_DESCRIPTION.get(
            resp_body.status_code, "Unknown"
        )

        audit_log.set_http_request(
            method=request.method,
            url=request.url.path,
            user_agent=headers.get("user-agent"),
        ).set_http_response(
            status_code=response.status_code,
            reason=http_status_description,
            headers=dict(response.headers),
        ).set_user(
            authenticated=user_info.get("authenticated"),
            provider=user_info.get("provider"),
            email=user_info.get("email"),
            roles=user_info.get("roles"),
            ip=request.client.host,
            realm=user_info.get("realm"),
        ).set_filter(
            object_name=request.url.path, kwargs={"params": query_params}
        ).set_results(
            results=resp_body
        ).info(
            f"{request.method} {request.url.path} "
            f"{response.status_code} {http_status_description}"
        ).send_log()

        return response
