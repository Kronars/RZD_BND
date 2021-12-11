"""
Модуль, который загружает и обрабатывает данные файлов excel.

Input:
    На вход подается путь до директории с входными файлами.
Output:
    На выходе будут pandas.DataFrame-ы для каждого табличного файла
"""
import os
import re
import pandas as pd


def filter_UKSPS(df: pd.DataFrame) -> pd.DataFrame:
    condition = df['Основной/дополнительный'] == 'о'
    df = df[condition].dropna(subset=['Ординаты УКСПС нечетных'])
    return df


def filter_bridges(df: pd.DataFrame, route_number: int = 1) -> pd.DataFrame:
    df['Наименование сооружения'] = df['Наименование сооружения'].apply(
        str.strip)
    condition = (df['Наименование сооружения'] == 'Железобетонный мост') &\
                (df['Путь'] == route_number)
    df = df[condition]
    return df


def get_files_paths(dirname: str, file_extensions: tuple) -> dict:
    """
    Получение путей до всех файлов с данными
    в директории dirname и с расширениями file_extensions

    Args:
        dirname (str): путь до директории
        file_extensions (tuple): кортеж файловых расширений

    Returns:
        dict: словарь: ключ - название таблицы, значение -  с путями до файлов с данными
    """
    files_paths = {}
    for file in os.listdir(dirname):
        if file.endswith(file_extensions):
            table_name = os.path.splitext(file)[0]
            table_name = re.sub(r'[\d\\.]', '', table_name).strip()
            files_paths[table_name] = (os.path.join(dirname, file))
    return files_paths


def divide_ordinate(df, ordinate_col: str = 'Ордината', table_name: str = None):
    df['Киллометр'] = df[ordinate_col].apply(lambda x: int(x.split('+')[0]))
    df['Метр'] = df[ordinate_col].apply(lambda x: int(x.split('+')[1]))
    df[table_name] = df.apply(lambda row: row.to_dict(), axis=1)
    return df


def calculate_percent(df, table_name):
    result_dict = {}
    data = df[table_name]
    percent = round(int(data['Метр']) / 10)
    result_dict['Процент'] = percent
    if table_name == 'Светофоры':
        result_dict['Цвет'] = 'красный' if str(
            data['Номер']).isalpha() else 'голубой'
        result_dict['Метр'] = str(data['Метр'] // 100) + '+' + str(data['Метр'] % 100)
    df[table_name] = result_dict
    return df


def get_dataframes(dirname: str):
    dataframes = {}
    for table_name, path in get_files_paths(dirname, ("xls", "xlsx")).items():
        dataframes[table_name] = pd.read_excel(path)

    # Фильтрация данных для определенных таблиц
    dataframes['Устройства контроля схода подвижного состава (УКСПС)'] = filter_UKSPS(
        dataframes['Устройства контроля схода подвижного состава (УКСПС)'])
    dataframes['Мосты'] = filter_bridges(dataframes['Мосты'])

    for table_name in dataframes.keys():
        dataframes[table_name] = divide_ordinate(
            dataframes[table_name], table_name=table_name)

    striped_tables = ('Оси станций', 'Светофоры', 'Граничные стрелки станций')
    for striped_table in striped_tables:
        dataframes[striped_table] = dataframes[striped_table].apply(
            calculate_percent, axis=1, table_name=striped_table)

    start = dataframes['Профиль']['Ордината начало (км)'].min()
    end = dataframes['Профиль']['Ордината начало (км)'].max()

    result_df = pd.DataFrame(data={'Киллометр': range(start, end+1)})
    for merge_table_name in dataframes.keys():
        result_df = result_df.merge(dataframes[merge_table_name][[
                                    'Киллометр', merge_table_name]], left_on='Киллометр', right_on='Киллометр', how='left')

    for table_name in dataframes.keys():
        # if table_name not in striped_tables:
        result_df[table_name] = result_df[table_name].fillna(False)

    result_df.drop_duplicates(['Киллометр'], inplace=True)

    return result_df, start, end
