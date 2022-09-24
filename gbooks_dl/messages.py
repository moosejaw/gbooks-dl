from gbooks_dl.logging import log_out, log_err


def write_max_page(pg):
    if not hasattr(pg, '__str__'):
        return
    log_out(f"Found max page: {str(pg)}\n")


def write_current_page(pg):
    if not hasattr(pg, '__str__'):
        return
    log_out(f"Querying source for page {str(pg)}\n")


def write_max_dl_pages(pg):
    log_out(f"Got {pg} pages to download\n")


def write_current_dl_page(pg, _max):
    log_out(f"Downloading page {pg}/{_max}\n")
