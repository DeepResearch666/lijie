    payload = {
        'url': url['url']
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
