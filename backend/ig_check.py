# python, backend/ig_check.py
import requests
import json
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def check_password(username: str, password: str) -> tuple[bool, str]:
    print(f"\n[IG] >>> START CHECK FOR: {username}")
    try:
        s = requests.Session()
        s.headers.update({
            "User-Agent": UA,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "X-Instagram-AJAX": "1",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/login/",
        })
        
        # 1. Получаем csrf
        try:
            r1 = s.get("https://www.instagram.com/accounts/login/", timeout=10)
            csrf = s.cookies.get("csrftoken")
            if not csrf:
                match = re.search(r'"csrf_token":"(.*?)"', r1.text)
                if match:
                    csrf = match.group(1)
            
            if csrf:
                s.headers["X-CSRFToken"] = csrf
            else:
                print("[IG] !!! No CSRF token found")
                return False, "no_csrf"
        except Exception as e:
            print(f"[IG] !!! Connection error: {e}")
            return False, "connection_error"

        # 2. Отправляем логин
        try:
            r2 = s.post(
                "https://www.instagram.com/api/v1/web/accounts/login/ajax/",
                data={
                    "username": username,
                    "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:0:{password}",
                    "queryParams": "{}",
                    "optIntoOneTap": "false",
                    "stopDeletionNonce": "",
                    "trustedDeviceRecords": "{}"
                },
                timeout=15
            )
            
            print(f"[IG] >>> STATUS: {r2.status_code}")
            try:
                j = r2.json()
                print(f"[IG] >>> JSON: {json.dumps(j, indent=2, ensure_ascii=False)[:500]}")
            except Exception:
                print(f"[IG] >>> RAW TEXT: {r2.text[:200]}")
                return False, "bad_json"
                
        except Exception as e:
            print(f"[IG] !!! Request error: {e}")
            return False, "request_failed"

        # 3. Анализ
        if j.get("authenticated") is True:
            print("[IG] >>> RESULT: SUCCESS")
            return True, "ok"
            
        if j.get("checkpoint_required") or j.get("message") == "challenge_required":
            print("[IG] >>> RESULT: CHECKPOINT (password correct)")
            return True, "checkpoint"
            
        if j.get("error_type") == "FakeIncorrectPassword" or j.get("user") is False:
            print("[IG] >>> RESULT: WRONG PASSWORD")
            return False, "wrong_password"
            
        print(f"[IG] >>> RESULT: UNKNOWN")
        return False, "unknown"

    except Exception as e:
        print(f"[IG] !!! CRITICAL ERROR: {e}")
        return False, "critical_error"