from fastapi import HTTPException, Header

# Secures an endpoint by verifying a simulated HMAC-SHA256 token exists
def verify_token(authorization: str = Header(default=None)):
    if not authorization or authorization != "Bearer instructor-super-secret-token":
        raise HTTPException(status_code=401, detail="Invalid Authentication token")
    return True