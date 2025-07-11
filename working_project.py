import csv, sys, itertools, argparse, re
from tabulate import tabulate

# Создаю класс с помощью которого изменю вывод ошибок при вводе названий параметров скрипта
class ParserMyClass(argparse.ArgumentParser):
    def error(self, message):
        if "argument --file:" in message: sys.stderr.write("Параметр --file написан с ошибкой.\n")
        elif "argument --where:" in message: sys.stderr.write("Параметр --where написан с ошибкой.\n")
        elif "argument --aggregate:" in message: sys.stderr.write("Параметр --aggregate написан с ошибкой.\n")
        else: pass
        sys.exit(2)

# Функция которая парсит аргументы командной строки и
# возвращает объект с данными, соответствующими переданным аргументам.
def parser_function(args_for_test=None):
    parser = ParserMyClass()
    parser.add_argument('--file', type=str, help='Введите путь до файла CSV')
    parser.add_argument('--where', type=str, help='Введите параметр --where, например "brand=apple"')
    parser.add_argument('--aggregate', type=str, help='Введите параметр --aggregate, например "brand=min"')
    return parser.parse_args(args_for_test)

# Функция, которая читает и дробит аргументы параметров --where и --aggregate на отдельные значения
def filter_str_parameter(where_str):
    search_sign = re.findall(r"(==|!=|<=|>=|<|>|=)", where_str)
    if not search_sign:
        print("\nНи один знак сравнения не найден.")
        sys.exit(1)
    if len(search_sign) > 1:
        print("\nЗнак сравнения может быть в строке только один.")
        sys.exit(1)
    if len(search_sign[0]) > 1:
        print("\nЗнак сравнения может состоять только из одного элемента.")
        sys.exit(1)
    sign = search_sign[0]
    column, value = where_str.split(f'{sign}')
    if sign == '=': sign = '=='
    return column.strip(), value, sign.strip()

# Функция, которая обрабатывает вводные данные, дробя на отдельные необходимые элементы (переменные)
def output_parameters(reader_file_csv, argparse_parameter):
    f_column, f_value, f_sign = filter_str_parameter(argparse_parameter)
    first_str_reader_csv = next(reader_file_csv, None)
    if not f_column in first_str_reader_csv:
        print(f"\nВведённое название столбца {f_column} \n"
              f"не соответствует ни одному из столбцов в таблице.")
        sys.exit(1)
    index_ = first_str_reader_csv.index(f_column)
    return [f_column, f_value, f_sign, index_, first_str_reader_csv]
# Функция, которая выводит данные для создания таблицы.
# Исключает те строки в столбцах которых отсутствует значение аргумента параметра --where
def filter_where(reader_file_csv, args):
    reader_file_csv = iter(reader_file_csv)
    list_parameters = output_parameters(reader_file_csv, args.where)
    f_column, f_value, f_sign, index_column, first_str_reader_file_csv = list_parameters
    iter_reader_file_csv_v2, iter_reader_file_csv = itertools.tee(reader_file_csv)
    number_hits = 0
    for test_2_str in iter_reader_file_csv_v2:
        number_hits += 1 if f_value == test_2_str[index_column] else 0
        continue
    if number_hits == 0:
        print(f"\nУкажите значение в аргументе параметра --where,\n"
              f"соответствующее одному из слов в столбце {f_column}.")
        sys.exit(1)
    if not (f_value.replace(".", "").isdigit()) and f_sign != "==":
        print("\nЕсли значение в аргументе параметра --where не является\n"
              "цифрой знак сравнения должен быть только '='.")
        sys.exit(1)
    rows_table = [first_str_reader_file_csv]
    for line in iter_reader_file_csv:
        if eval(f"'{line[index_column]}' {f_sign} '{f_value}'"):
            rows_table.append(line)
        else: continue
    return rows_table

# Функция, которая проводит агрегацию табличных данных объявленного столбца
def filter_aggregate(reader_file_csv, args):
    reader_file_csv = iter(reader_file_csv)
    list_parameters = output_parameters(reader_file_csv, args.aggregate)
    f_column, f_value, f_sign, index_column, first_str_reader_csv = list_parameters
    iter_reader_file_csv_v2, iter_reader_file_csv = itertools.tee(reader_file_csv)
    str_iter_reader_file_csv_v2 = next(iter(iter_reader_file_csv_v2), None)
    if not (str_iter_reader_file_csv_v2[index_column].replace(".", "").isdigit()):
        print("\nУкажите название столбца в котором присутствуют только цифры или числа,\n"
              "в том числе могут быть значения с плавающей точкой.")
        sys.exit(1)
    if f_sign != "==":
        print("\nЗнак сравнения должен быть только '='.")
        sys.exit(1)
    value_aggregate = ['min', 'max', 'avg']
    if not f_value in value_aggregate:
        print(f"\nЗначение должно быть одно из этих вариантов: {', '.join(value_aggregate)}.")
        sys.exit(1)
    result = []
    for line in iter_reader_file_csv:
        if re.search(r'\d+\.\d+', line[index_column]):
            result.append(float(line[index_column]))
        else: result.append(int(line[index_column]))
    reader_csv_lambda = lambda column, result_value: [[column], [result_value]]
    if f_value == "avg":
        avg = round((sum(result) / len(result)), 2)
        return reader_csv_lambda("avg", avg)
    elif f_value == "min":
        min_ = min(result)
        return reader_csv_lambda("min", min_)
    else:
        max_ = max(result)
        return reader_csv_lambda("max", max_)

# Функция запуска скрипта
def whole_program(parser_str_file_csv=parser_function()):
    args = parser_str_file_csv
    if args.file is None:
        print('\n-------------------------------------------------------------------------------------\n'
              '\n                         Инструкция запуска скрипта:\n'
              '\n Скрипт использует такие параметры:\n'
              '\n --file      =     Здесь необходимо ввести путь до файла CSV.\n'
              '\n --where     =     Введите параметр фильтра, например: "brand=samsung";\n'
              '                   Название параметра должно соответствовать названию\n'
              '                   одного из столбцов таблицы, где производится фильтрация;\n'
              '                   Знак сравнения только "=";\n'
              '                   Значение параметра может быть любым в пределах выбранного столбца.\n'
              '\n --aggregate =     Введите параметр агрегации, например: "price=min";\n'
              '                   Название параметра должно соответствовать названию\n'
              '                   столбца, где присутствуют исключительно числа или цифры,\n'
              '                   в том числе могут быть значения с плавающей точкой;\n'
              '                   Знак сравнения только "=";\n'
              '                   Значение параметра один из этих вариантов:\n'
              '\n                   min = Минимальное значение в столбце;\n'
              '                   max = Максимальное значение в столбце;\n'
              '                   avg = Среднее значение в столбце.\n'
              '\n-------------------------------------------------------------------------------------\n')
        sys.exit(1)
    try:
        with (open(args.file, "r") as file_test_csv):
            reader_csv = csv.reader(file_test_csv)
            if args.where is not None:
                reader_csv = filter_where(reader_csv, args)
            if args.aggregate is not None:
                reader_csv = filter_aggregate(reader_csv, args)
            # Схема таблицы для дальнейшего отображения
            return tabulate(list(reader_csv), tablefmt='grid')
    except FileNotFoundError:
        print("\nВы вели не верный аргумент - путь к файлу CSV.")
        sys.exit(1)
print(whole_program())
