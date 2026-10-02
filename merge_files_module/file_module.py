from pathlib import Path
from datetime import datetime

from loguru import logger
from openpyxl import Workbook, load_workbook


# ============================================================
# НАСТРОЙКИ
# ============================================================


DATE_FILE = "2026-10-02"  # дата, которая устанавливается только в файлах
DATE_OBJ_F = datetime.strptime(DATE_FILE, "%Y-%m-%d")
DATE_FILE = DATE_OBJ_F.strftime("%Y-%m-%d")

DATE = "2026-10-02"  # дата, которая прописывается в столбцах и создает папку
DATE_DATETIME = datetime.strptime(DATE, "%Y-%m-%d") # для экселя в столбце Дата
DATE_OBJ = datetime.strptime(DATE, "%Y-%m-%d")
DATE_FILE_AVITO = DATE_OBJ.strftime("%Y-%m-%d")
DATE_EXCEL = DATE_OBJ.strftime("%d.%m.%Y")
RESULT_DATE = DATE_OBJ.strftime("%d.%m.%Y")


# ============================================================
# ПУТИ
# ============================================================

BASE_DIR = Path(r"C:\Users\Projects\my_projects\parser_3000")

RESULT_DIR = Path.cwd() / "result_files" / RESULT_DATE


# ============================================================
# ФАЙЛЫ ДЛЯ ОБЪЕДИНЕНИЯ
# ============================================================

MERGE_FILES = {
    # --------------------- ДКП ---------------------
    "ДКП RESULT": [
        BASE_DIR
        / "p3000"
        / "parsers"
        / "Avito_parser"
        / "all_exel"
        / f"exel_{DATE_FILE_AVITO}"
        / f"{DATE_FILE}_Ivanovo.xlsx",

        BASE_DIR
        / "p3000"
        / "parsers"
        / "Avito_parser"
        / "all_exel"
        / f"exel_{DATE_FILE_AVITO}"
        / f"{DATE_FILE}_Kovrov.xlsx",

        BASE_DIR
        / "p3000"
        / "parsers"
        / "Avito_parser"
        / "all_exel"
        / f"exel_{DATE_FILE_AVITO}"
        / f"{DATE_FILE}_Vladimir.xlsx",
    ],

    # ------------------ ОМЦ Владимир ------------------
    # "ОМЦ Владимир": [
    #     BASE_DIR
    #     / "p3000"
    #     / "parsers"
    #     / "Vladimir_parsers"
    #     / "all_exel"
    #     / f"{DATE_FILE}_vt.xlsx",
    #
    #     BASE_DIR
    #     / "p3000"
    #     / "parsers"
    #     / "Vladimir_parsers"
    #     / "all_exel"
    #     / f"vt.xlsx",
    #
    #     BASE_DIR
    #     / "all_exel"
    #     / f"{DATE_FILE}_Vladimir.xlsx",
    # ],

    # ------------------ ОМЦ Иваново ------------------
    # "ОМЦ Иваново": [
    #     BASE_DIR
    #     / "all_exel"
    #     / f"{DATE_FILE}_Ivanovo.xlsx",
    #
    #     BASE_DIR
    #     / "merge_files_module"
    #     / "нити_макет.xlsx",
    # ],
}


# ============================================================
# КЛАСС
# ============================================================

class FileModule:

    def _get_result_folder(self) -> Path:
        RESULT_DIR.mkdir(parents=True, exist_ok=True)

        logger.info(f"Папка результатов: {RESULT_DIR}")

        return RESULT_DIR

    def _remove_pagination_column(self, ws) -> bool:
        """
        Проверяет первый столбец на наличие пагинации.

        Поддерживает пагинацию:
            0, 1, 2, 3, ...
        или:
            1, 2, 3, 4, ...

        Также проверяет известные названия столбца.
        """

        if ws.max_column < 1 or ws.max_row < 2:
            return False

        # --------------------------------------------
        # Проверка заголовка
        # --------------------------------------------

        header = ws.cell(
            row=1,
            column=1,
        ).value

        pagination_headers = {
            "№",
            "номер",
            "номер.",
            "пагинация",
            "pagination",
            "page",
            "страница",
            "",
        }

        if header is None:
            normalized_header = ""
        elif isinstance(header, str):
            normalized_header = header.strip().lower()
        else:
            normalized_header = str(header).strip().lower()

        if normalized_header in pagination_headers:
            ws.delete_cols(1)

            logger.info(
                "Удалён первый столбец: "
                f"обнаружена пагинация (заголовок: {header!r})"
            )

            return True

        # --------------------------------------------
        # Проверка последовательности чисел
        # --------------------------------------------

        values = []

        max_check_row = min(
            ws.max_row,
            20,
        )

        for row in range(2, max_check_row + 1):

            value = ws.cell(
                row=row,
                column=1,
            ).value

            if value is not None:
                values.append(value)

        # Нужно минимум 10 значений
        if len(values) < 10:
            return False

        try:
            numbers = [
                int(value)
                for value in values
            ]

        except (ValueError, TypeError):
            return False

        # --------------------------------------------
        # Пагинация может начинаться с 0 или с 1
        # --------------------------------------------

        starts_from_zero = numbers == list(
            range(0, len(numbers))
        )

        starts_from_one = numbers == list(
            range(1, len(numbers) + 1)
        )

        if starts_from_zero or starts_from_one:
            ws.delete_cols(1)

            logger.info(
                "Удалён первый столбец: "
                f"обнаружена пагинация "
                f"(начало: {numbers[0]})"
            )

            return True

        return False

    def add_first_column(self):
        result_folder = self._get_result_folder()

        for result_name, files in MERGE_FILES.items():

            # RESULT-файл уже был создан после объединения.
            file_path = result_folder / f"{result_name}.xlsx"

            logger.info(f"Начата обработка файла '{file_path}'")

            try:
                wb = load_workbook(file_path)
                ws = wb.active

                logger.debug("Вставка первого столбца")

                ws.insert_cols(1)

                ws["A1"] = "Дата"

                for row in range(2, ws.max_row + 1):
                    cell = ws.cell(
                        row=row,
                        column=1,
                        value=DATE_DATETIME,
                    )
                    cell.number_format = "DD.MM.YYYY"

                wb.save(file_path)

                logger.success(
                    f"Файл '{file_path.name}' успешно обработан"
                )

            except Exception:
                logger.exception(
                    f"Ошибка при обработке файла '{file_path}'"
                )
                raise

    def merge_excel_files(self):
        logger.info(
            f"Найдено групп для объединения: {len(MERGE_FILES)}"
        )

        result_folder = self._get_result_folder()

        try:
            for result_name, files in MERGE_FILES.items():

                logger.info(
                    f"Начато объединение группы '{result_name}' "
                    f"({len(files)} файлов)"
                )

                new_wb = Workbook()
                new_ws = new_wb.active

                first_file = True
                current_row = 1

                for file_path in files:

                    logger.info(f"Чтение файла: {file_path}")

                    wb = load_workbook(file_path)
                    ws = wb.active

                    pagination_removed = (
                        self._remove_pagination_column(
                            ws
                        )
                    )

                    start_row = 1 if first_file else 2

                    copied_rows = 0

                    for row in ws.iter_rows(
                        min_row=start_row,
                        max_row=ws.max_row,
                        values_only=True,
                    ):
                        for col, value in enumerate(row, start=1):
                            new_ws.cell(
                                row=current_row,
                                column=col,
                                value=value,
                            )

                        current_row += 1
                        copied_rows += 1

                    logger.debug(
                        f"Из '{file_path.name}' "
                        f"скопировано строк: {copied_rows}"
                    )

                    first_file = False

                save_path = result_folder / f"{result_name}.xlsx"

                new_wb.save(save_path)

                logger.success(
                    f"Группа '{result_name}' успешно объединена "
                    f"в '{save_path.name}'"
                )

        except Exception:
            logger.exception("Ошибка при объединении Excel файлов")
            raise


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":

    logger.add(
        "logs/file_module.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        level="DEBUG",
    )

    fm = FileModule()

    # Объединяем файлы
    fm.merge_excel_files()

    # Добавляем дату в первый столбец
    fm.add_first_column()