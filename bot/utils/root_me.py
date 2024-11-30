

from urllib.parse import urlparse


def scribe_root_me(root_me_link: str):
    """
    Extracts the nickname from a given URL.
    
    Example:
        Input: https://www.root-me.org/Banzai-443597?lang=ru
        Output: Banzai-443597
    """
    # Parse the URL
    parsed_url = urlparse(root_me_link)
    
    # Extract the path and split it
    path_parts = parsed_url.path.strip("/").split("/")
    
    # The nickname is typically the last part of the path
    if path_parts:
        return path_parts[-1]
    else:
        raise ValueError("No valid nickname found in the URL.")