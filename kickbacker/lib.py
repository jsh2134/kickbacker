
def strip_url_args(url):
	if url.find('?') != -1:
		url = url[:url.find('?')]
	return url


