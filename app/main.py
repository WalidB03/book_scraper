from playwright.sync_api import sync_playwright
import logging as log

log.basicConfig(level=log.DEBUG, format="[%(asctime)s - %(levelname)s]\t%(message)s")

error_log = log.getLogger("error")
error_handler = log.FileHandler("logs/error.log", mode="w")
error_log.addHandler(error_handler)

network_log = log.getLogger("network")
network_handler = log.FileHandler("logs/network.log", mode="w")
network_log.addHandler(network_handler)

with sync_playwright() as p:
    browser = p.firefox.launch()
    context = browser.new_context()
    page = context.new_page()
    page.on("request", lambda req: network_log.info(f"[REQ] {req.method} {req.url}"))
    page.on("response", lambda res: network_log.info(f"[RES] {res.status} {res.url}"))

    try:
        step = "main"
        network_log.info(f"<{step}>")
        page.goto("https://books.toscrape.com/")
        log.debug(f"</{step}>")

        step = "travel"
        network_log.info(f"<{step}>")
        page.get_by_role("link", name="Travel", exact=True).click()
        log.debug(f"</{step}>")

        books_loc = page.locator("ol.row li")
        books_count = books_loc.count()
        log.debug(f"books count: {books_count}")

        info_table = None
        def get_info_table_data(text, table = info_table):
            data_tr = info_table.locator("tr").filter(has_text=text)
            data = data_tr.locator("td").inner_text()
            return data

        books_info = []

        for n in range(books_count):
            step = f"book{(n + 1):>02}"
            network_log.info(f"<{step}>")
            books_loc.nth(n).locator("h3 a").click()
            log.debug(f"</{step}>")

            title = page.locator(".product_main h1").inner_text()
            log.debug(f"\ttitle: {title}")

            stars_class = page.locator(".product_main p.star-rating").get_attribute("class")
            stars = stars_class.split()[1]
            log.debug(f"\tstars: {stars}")

            info_table = page.locator(".table-striped")

            upc = get_info_table_data("UPC")
            log.debug(f"\tupc: {upc}")

            price_excl_tax = get_info_table_data("Price (excl. tax)")
            log.debug(f"\tprice_excl_tax: {price_excl_tax}")

            price_incl_tax = get_info_table_data("Price (incl. tax)")
            log.debug(f"\tprice_incl_tax: {price_incl_tax}")

            availability = get_info_table_data("Availability")
            log.debug(f"\tavailability: {availability}")

            num_reviews = get_info_table_data("Number of reviews")
            log.debug(f"\tnum_reviews: {num_reviews}")

            books_info.append({
                "upc"           : upc,
                "title"         : title,
                "availability"  : availability,
                "price_excl_tax": price_excl_tax,
                "price_incl_tax": price_incl_tax,
                "stars"         : stars,
                "num_review"    : num_reviews
            })

            step = "travel"
            network_log.info(f"<{step}>")
            page.go_back()
            log.debug(f"</{step}>")

        print(books_info)

    except Exception as e:
        error_log.exception(step)
        page.screenshot(path=f"logs/[ERROR]-{step}.png", full_page=True)

