#两个爬虫代理池，spyder2暂时没有额度，目前使用spyder1
def spyder1(url):
#url格式  url  = "https://scholar.google.com/scholar?start={startnum}&hl=en&as_sdt=0,5&q={query.replace(' ', '+')}&btnG="
    payload = {
        'url': url
    }

    # Get response.
    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=('google_OoUoK', 'jynni8qixson+bikbIc'),
        json=payload,
    )
    status_code = response.status_code
    reason = response.reason
    html_content = response.json().get('results', [{}])[0].get('content', 'No HTML content found.')
    return status_code, reason, html_content
def spyder2(url):
 #url格式 url = {
        #     "url": f"https://scholar.google.com/scholar?start={startnum}&hl=en&as_sdt=0,5&q={query.replace(' ', '+')}&btnG=",
        #     "type": "html",
        #     "country": "us",
        #     "js_render": "False",
        #     "block_resources": "image, font, media"
        # }
    conn = http.client.HTTPSConnection("unlocker-api.lunaproxy.com", timeout=15)
    payload_json = json.dumps(url)
    headers = {
        'Authorization': "Bearer gm963avxp3iepk03o1wc68bl13sms65j6sjg43wajxy8xfafe84125k6sqr84y19",
        'content-type': "application/json",
    }

    conn.request("POST", "/request", body=payload_json.encode('utf-8'), headers=headers)
    res = conn.getresponse()
    html_content = res.read().decode("utf-8")
    print(html_content)
    status_code = res.status
    reason = res.reason
    conn.close()
    return status_code, reason, html_content
