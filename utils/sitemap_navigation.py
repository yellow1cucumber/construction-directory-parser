from core.extraction.sitemap import SiteMap


def find_page_by_id(site_map: SiteMap, suffix_number: int):
    """
    Ищет статью или категорию в SiteMap, URL которой заканчивается на заданное число.

    :param site_map: Объект SiteMap для поиска.
    :param suffix_number: Число, на которое должен оканчиваться URL.
    :return: Найденная статья или категория, либо None, если ничего не найдено.
    """
    suffix_str = str(suffix_number)

    def search(categories):
        for category in categories:
            # Проверяем URL категории
            if category.url.endswith(suffix_str):
                return category

            # Проверяем статьи в категории
            for article in category.articles:
                if article.url.endswith(suffix_str):
                    return article

            # Рекурсивно ищем в подкатегориях
            result = search(category.subcategories)
            if result:
                return result
        return None

    return search(site_map.categories)