import json
import re
import logging

#from AM.utilities import constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_response(status_code, msg, data: dict, headers=None, klass=None, default=None):
    """

    :param status_code:
    :param msg:
    :param data:
    :param headers:
    :param klass:
    :param default:
    :return:
    """
    if not isinstance(msg, str):
        msg = json.dumps(msg)

    data["message"] = msg

    permissions_policy = (
        "interest-cohort=(), "  # Disable Google FLoC
        "accelerometer=(), "  # Disable accelerometer access
        "camera=(), "  # Disable camera access
        "geolocation=(), "  # Disable geolocation
        "microphone=(), "  # Disable microphone access
        "payment=(), "  # Disable payment API
        "usb=(), "  # Disable USB access
        "vr=(), "  # Disable VR features
        "gyroscope=(), "  # Disable gyroscope
        "magnetometer=(), "  # Disable magnetometer
        "midi=(), "  # Disable MIDI access
        "encrypted-media=(), "  # Disable encrypted media
        "picture-in-picture=(), "  # Disable picture-in-picture
        "sync-xhr=self, "  # Restrict synchronous XMLHttpRequest
        "autoplay=(), "  # Disable autoplay
        "fullscreen=(self), "  # Restrict fullscreen to same origin
        "web-share=(self)"  # Restrict web share API
    )

    _headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Origin, Content-Type, Authorization",
        "Access-Control-Allow-Methods": "POST, PUT, GET, OPTIONS, DELETE",

        # Security headers
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "X-Content-Type-Options": "nosniff",

        # Transport Security
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",

        # Content Security Policy
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'"
            "cookie-policy 'strict'; "
            "frame-ancestors 'none'; "
        ),

        # Added Permission-Policy
        "Permissions-Policy": permissions_policy,

        # Referrer-Policy Configuration
        "Referrer-Policy": "strict-origin-when-cross-origin",

        # SameSite Cookie Configuration
        "Set-Cookie": "CookieName=value; Secure; HttpOnly; SameSite=Strict"

    }

    if headers and isinstance(headers, dict):
        _headers.update(headers)

    if default:
        body = json.dumps(data, default=default)
    elif klass:
        body = json.dumps(data, cls=klass)
    else:
        body = json.dumps(data)

    return {
        "statusCode": status_code,
        "headers": _headers,
        "body": body,
    }

