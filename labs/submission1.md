# Triage Report — OWASP Juice Shop

## Scope & Asset
- Asset: OWASP Juice Shop (local lab instance)
- Image: bkimminich/juice-shop:v19.0.0
- Release link/date: https://github.com/juice-shop/juice-shop/releases/tag/v19.0.0 — September 4, 2025
- Image digest (optional): sha256:2765a26de7647609099a338d5b7f61085d95903c8703bb70f03fcc4b12f0818d

## Environment
- Host OS: Ubuntu 24.04
- Docker: 29.1.3

## Deployment Details
- Run command used: `docker run -d --name juice-shop -p 127.0.0.1:3000:3000 bkimminich/juice-shop:v19.0.0`
- Access URL: http://127.0.0.1:3000
- Network exposure: 127.0.0.1 only [X] Yes  [ ] No

## Health Check
- Page load: ![Juice Shop Homepage](./screenshots/juice-shop-homepage.png)
- API check:

    Original endpoint from lab instructions `curl -s http://127.0.0.1:3000/rest/products | head` gives:
    ```html
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Error: Unexpected path: /rest/products</title>
        <style>* {
    margin: 0;
    padding: 0;
    outline: 0;
    }
    ```

    Working endpoint found during testing `curl -s "http://127.0.0.1:3000/rest/products/search?q=" | head` gives:
    ```json
    {"status":"success","data":[{"id":1,"name":"Apple Juice (1000ml)","description":"The all-time classic.","price":1.99,"deluxePrice":0.99,"image":"apple_juice.jpg","createdAt":"2026-02-09 06:52:26.771 +00:00","updatedAt":"2026-02-09 06:52:26.771 +00:00","deletedAt":null},
    ```

## Surface Snapshot (Triage)
- Login/Registration visible: [X] Yes  [ ] No — notes: Account button visible in top-right navigation bar, if you click on it then Login button appears
- Product listing/search present: [X] Yes  [ ] No — notes: Main page displays product cards with images, prices, and search bar at top
- Admin or account area discoverable: [X] Yes  [ ] No — notes: Account menu accessible after login at the same place where was Login button
- Client-side errors in console: [X] Yes  [ ] No — notes: Single warning about deprecated feature used in `content.js:213`: "Unload event listeners are deprecated and will be removed."
- Security headers (quick look — optional):
    ```http
    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    X-Content-Type-Options: nosniff
    X-Frame-Options: SAMEORIGIN
    Feature-Policy: payment 'self'
    X-Recruiting: /#/jobs
    Accept-Ranges: bytes
    Cache-Control: public, max-age=0
    Last-Modified: Mon, 09 Feb 2026 06:52:27 GMT
    ETag: W/"124fa-19c412c49d5"
    Content-Type: text/html; charset=UTF-8
    Content-Length: 75002
    Vary: Accept-Encoding
    Date: Mon, 09 Feb 2026 07:50:11 GMT
    Connection: keep-alive
    Keep-Alive: timeout=5
    ```

    Quick analysis:
    - `X-Content-Type-Options` and `X-Frame-Options` present (MIME-type sniffing and basic clickjacking protection)
    - Missing `Content-Security-Policy (CSP)`
    - Missing `Strict-Transport-Security (HSTS)`
    - Overly premissive CORS

## Risks Observed (Top 3)
1) **Missing Content-Security-Policy (CSP) header**: Absence of CSP allows unrestricted script execution, making the application highly vulnerable to Cross-Site Scripting (XSS) attacks and malicious code injection
2) **Overly permissive CORS policy (Access-Control-Allow-Origin: \*)** — Allows any external website to make API requests to the application, enabling potential data theft and unauthorized API access from malicious sites
3) **Missing HTTP Strict-Transport-Security (HSTS) header** — Without HSTS, users are vulnerable to man-in-the-middle attacks and SSL stripping, allowing attackers to downgrade connections to insecure HTTP
