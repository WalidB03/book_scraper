from playwright.sync_api import sync_playwright
import logging

format = "[%(asctime)s - %(name)s - %(levelname)s]\t%(message)s"
logging.basicConfig(level=logging.DEBUG, format=format)
def set_logger(name, level, format, prop=False, file=None, file_mode="a"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = prop
    if file:
        handler = logging.FileHandler(file, mode=file_mode)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
    return logger

debug_log = set_logger("debug_log", logging.DEBUG, format=format)
network_log = set_logger("network_log", logging.DEBUG, format=format, prop=True, file="logs/network.log", file_mode="w")
error_log = set_logger("error_log", logging.ERROR, format=format, prop=True, file="logs/error.log", file_mode="w")

with sync_playwright() as p:
    browser = p.firefox.launch()
    context = browser.new_context()
    page = context.new_page()
    page.on("request", lambda req: network_log.info(f"REQ: {req.method} {req.url}"))
    page.on("response", lambda res: network_log.info(f"RES: {res.status} {res.url}"))

    try:
        step = "landing_page"
        network_log.debug(f"At: {step}")
        page.goto("https://books.toscrape.com/")
        debug_log.debug(f"On: {step}")

        step = "travel_link"
        network_log.debug(f"At: {step}")
        page.get_by_role("link", name="Travel", exact=True).click()
        debug_log.debug(f"On: {step}")

        books_loc = page.locator("ol.row li")
        books_count = books_loc.count()
        debug_log.debug(f"books count: {books_count}")

        info_table = None
        def get_info_table_data(text, table = info_table):
            data_tr = info_table.locator("tr").filter(has_text=text)
            data = data_tr.locator("td").inner_text()
            return data

        books_info = []

        for n in range(books_count):
            step = f"book{(n + 1):>02}"
            network_log.debug(f"At: {step}")
            books_loc.nth(n).locator("h3 a").click()
            debug_log.debug(f"On: {step}")

            title = page.locator(".product_main h1").inner_text()
            debug_log.debug(f"\ttitle: {title}")

            stars_class = page.locator(".product_main p.star-rating").get_attribute("class")
            stars = stars_class.split()[1]
            debug_log.debug(f"\tstars: {stars}")

            info_table = page.locator(".table-striped")

            upc = get_info_table_data("UPC")
            debug_log.debug(f"\tupc: {upc}")

            price_excl_tax = get_info_table_data("Price (excl. tax)")
            debug_log.debug(f"\tprice_excl_tax: {price_excl_tax}")

            price_incl_tax = get_info_table_data("Price (incl. tax)")
            debug_log.debug(f"\tprice_incl_tax: {price_incl_tax}")

            availability = get_info_table_data("Availability")
            debug_log.debug(f"\tavailability: {availability}")

            num_reviews = get_info_table_data("Number of reviews")
            debug_log.debug(f"\tnum_reviews: {num_reviews}")

            books_info.append({
                "upc"           : upc,
                "title"         : title,
                "availability"  : availability,
                "price_excl_tax": price_excl_tax,
                "price_incl_tax": price_incl_tax,
                "stars"         : stars,
                "num_review"    : num_reviews
            })

            step = "travel_link"
            network_log.debug(f"At: {step}")
            page.go_back()
            debug_log.debug(f"On: {step}")

        print(books_info)

    except Exception as e:
        error_log.exception(step)
        page.screenshot(path=f"logs/[ERROR]-{step}.png", full_page=True)

