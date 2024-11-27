from core.extraction.sitemapExtractor import (SiteMapExtractor,
                                              ExtractorOptions)
from core.extraction.sitemap import SiteMap


def request_sitemap(options: ExtractorOptions) -> SiteMap:
    """
    Загружает sitemap c url указанного в options
    :param options: Настройки для SiteMapExtractor
    :return: Карта сайта
    """
    map_extractor = SiteMapExtractor(options)
    sitemap: SiteMap = map_extractor.extract_site_map()
    return sitemap

def request_sitemap_and_export(options: ExtractorOptions, file_name: str) -> SiteMap:
    """
    Загружает sitemap c url указанного в options и сохраняет ее в json файл
    :param options: Настройки для SiteMapExtractor
    :param file_name: Имя файла для экспорта
    :return: Карта сайта
    """
    map_extractor = SiteMapExtractor(options)
    sitemap: SiteMap = map_extractor.extract_site_map()
    map_extractor.export_results(sitemap, file_name)
    return sitemap

def import_sitemap_from_json_file(options: ExtractorOptions, file_name: str) -> SiteMap:
    """
    Импортирует sitemap из указанного файла
    :param options: Настройки для SiteMapExtractor
    :param file_name: Имя файла для импорта
    :return: Карта сайта
    """
    map_extractor = SiteMapExtractor(options)
    sitemap: SiteMap = map_extractor.load_site_map_from_json(file_name)
    return sitemap
