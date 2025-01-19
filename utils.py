from urllib.parse import urlparse, urlunparse

class Utils:
    def normalize_url(url: str) -> str|None:
        if url is None:
            return None
        
        parsed_url = urlparse(url)
        
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc.rstrip('/')
        path = parsed_url.path.rstrip('/')
        
        normalized_url = scheme + "://" + netloc + path
        
        return normalized_url

    def normalize_domain(url) -> str|None:
        if url is None:
            return None
        
        parsed_url = urlparse(url)
        
        netloc = parsed_url.netloc
        
        domain_parts = netloc.split('.')
        if len(domain_parts) > 2:
            normalized_domain = '.'.join(domain_parts[-2:])
        else:
            normalized_domain = netloc
        
        return normalized_domain