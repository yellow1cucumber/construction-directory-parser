from core.extraction.article import Article
from core.extraction.category import Category
from core.extraction.sitemap import SiteMap


def find_page_by_id(site_map: SiteMap, suffix_number: int) -> Article | Category | None:
    """
    Searches for an article or category in the SiteMap whose URL ends with the specified number.

    :param site_map: The SiteMap object to search.
    :param suffix_number: The number the URL should end with.
    :return: The found article or category, or None if not found.
    """
    if not hasattr(site_map, 'categories'):
        raise ValueError("SiteMap object does not have 'categories' attribute.")

    suffix_str = str(suffix_number)

    def search(categories):
        for category in categories:
            # Check category URL
            if category.url.endswith(suffix_str):
                return category

            # Check articles in the category
            for article in category.articles:
                if article.url.endswith(suffix_str):
                    return article

            # Recursively search subcategories
            result = search(category.subcategories)
            if result:
                return result
        return None

    return search(site_map.categories)
