

from django.http import JsonResponse


def user_not_logged_in_response() -> JsonResponse:
    return JsonResponse(
        {"message": "로그인이 필요합니다."},
        status=401,
        json_dumps_params={'ensure_ascii': False}
    )
