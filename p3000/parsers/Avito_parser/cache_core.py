import diskcache
from loguru import logger

#cache_name [  Ivanovo ;  Vladimir;  Kovrov;  ]

#https://www.avito.ru/vladimir/kvartiry/prodam/novostroyka/na-stadii-sdachi-ASgBAgECAkSSA8YQ5geOUgFFuMENFHsiZnJvbSI6bnVsbCwidG8iOjF9?f=ASgBAgECBESSA8YQ5geOUpC~DZKuNdKEEsyKiwMBRbjBDRR7ImZyb20iOm51bGwsInRvIjoxfQ
#https://www.avito.ru/vladimir/kvartiry/prodam/novostroyka/na-stadii-sdachi-ASgBAgECAkSSA8YQ5geOUgFFuMENFHsiZnJvbSI6bnVsbCwidG8iOjF9?f=ASgBAgECBESSA8YQ5geOUpC~DZKuNdKEEsyKiwMBRbjBDRR7ImZyb20iOm51bGwsInRvIjoxfQ&localPriority=0&p=2


class CacheCore:

    def __init__(self, cache_name: str):
        self.cache_name = cache_name
        self.cache = diskcache.Cache(f'avito__{cache_name}')

    # 1. Добавление уникальных данных
    def add(self, key: str, value: dict | list) -> bool:
        if key in self.cache:
            logger.warning(
                f'CacheCore (add); KEY already exists ({self.cache_name}) -> {key}'
            )
            return False

        self.cache[key] = value
        logger.success(
            f'ADD DATA ({self.cache_name}) -> {key}'
        )
        return True

    # 2. Проверка существования ключа
    def exists(self, key: str) -> bool:
        if key not in self.cache:
            logger.info(f'CacheCore (exists); Unique KEY ({self.cache_name}) -> {key}')
            return True
        logger.warning(f'CacheCore (exists); KEY already exists ({self.cache_name}) -> {key}')
        return False

    # 3. Получить все значения без ключей
    def get_all_values(self, flag_with_pars_urls: bool = False) -> list:
        result = []
        for k in self.cache:
            if k == 'pars_cards_urls': continue

            result.append(self.cache[k])

        return result

    # 4. Изменить значение по ключу
    def update(self, key: str, value: dict | list) -> bool:
        if key not in self.cache and key != 'pars_cards_urls':
            logger.warning(
                f'CacheCore (update); KEY not found ({self.cache_name}) -> {key}'
            )
            return False

        self.cache[key] = value
        logger.success(
            f'CacheCore (update); UPDATED ({self.cache_name}) -> {key}'
        )
        return True

    # 5. Удалить данные по ключу
    def delete(self, key: str) -> bool:
        if key not in self.cache:
            logger.warning(
                f'CacheCore (delete); KEY not found ({self.cache_name}) -> {key}'
            )
            return False

        del self.cache[key]
        logger.success(
            f'CacheCore (delete); DELETED ({self.cache_name}) -> {key}'
        )
        return True

    # дополнительный полезный метод
    def get(self, key: str = 'pars_cards_urls'):
        if key not in self.cache and key == 'pars_cards_urls':
            return []
        return self.cache.get(key)

    # длина кеша
    def size(self) -> int:
        return len(self.cache) - 1 if 'pars_cards_urls' in self.cache else len(self.cache)



if __name__ == '__main__':
    from pprint import pprint
    per = CacheCore('Kovrov')
    pprint(per.get())
    print(per.size())