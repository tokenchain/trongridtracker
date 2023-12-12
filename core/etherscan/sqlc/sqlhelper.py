import os.path
import sqlite3
import json
import re
import sys
import time

from SQLiteAsJSON.SQLiteAsJSON import db_logger

from core import DATAPATH_BASE
from core.common.utils import folder_paths, FolderBase

from SQLiteAsJSON import ManageDB

import ast


class LargeTransactionDb(FolderBase):
    def __init__(self, project_name: str):
        self.by_project_name(project_name)
        self.data_schema = "data/sql/project_planner.json"
        self._project = project_name
        path_db = os.path.join(self.cachefolder, 'cache.db')
        self.sb = ManageDB(path_db, self.data_schema)
        self.sb.create_table()

    def init(self):
        self.data_schema = "data/sql/project_planner.json"
        path_db = os.path.join(self.cachefolder, 'cache.db')
        self.sb = ManageDB(path_db, self.data_schema)
        self.sb.create_table()

    def response_from_etherscan(self, params: dict):
        self.sb.insert_data(
            "transactions",
            params=params
        )


def obj_to_tuple(obj) -> dict:
    """ Parse JSON object and format it for insert_data method

    Parameters:
        obj (dict): The JSON object that should be formatted

    Returns:
        dict: JSON object with keys and values formatted for insert_data method """

    keys = ''
    values = ''
    for key, value in obj.items():
        keys = f'{keys},{key}' if keys != '' else key
        values = f'{values}, :{key}' if values != '' else f':{key}'

    return {"keys": keys, "values": values}


def obj_to_string(update_config) -> str:
    update_string = ''
    index = 0
    for key, value in update_config.items():
        update_string = update_string + f"{key}='{value}'," if index < len(
            update_config) - 1 else update_string + f"{key}='{value}'"
        index = index + 1

    return update_string


class BlockChainCase(ManageDB):
    """
    modified blockchain db controller

    """

    def found_table(self, tableName: str) -> bool:
        sqlStatement = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'"
        cursor = self.conn.cursor()
        cursor.execute(sqlStatement)
        db_result = cursor.fetchone()
        if db_result is None:
            return False
        else:
            return True

    def has_has(self, table_name: str, hash: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT rowid FROM {table_name} WHERE txid = ?", (hash,))
        db_result = cursor.fetchone()
        cursor.close()
        if db_result is None:
            return False
        else:
            return True

    def update_data_hash(self, table_name: str, hash: str, params: dict) -> bool:

        if self.has_has("transaction_cache", hash) is False:
            return False

        if hash[0:2] == "0x":
            try:

                columns = obj_to_string(params)

                # update query
                self.conn.execute(f"UPDATE {table_name} set {columns} where txid='{hash}'")

            except Exception as E:
                db_logger.error('Data Update Error : ', E)
                return False

            self.conn.commit()
            return True
        else:

            return False

    def insert_chain_hash(self, table_name: str, hash: str, params: dict) -> bool:

        # Create UUID
        params["txid"] = hash
        params["timestamp"] = round(time.time() * 1000)  # Current unix time in milliseconds
        columns = obj_to_tuple(params)
        # insert query
        try:
            query = (
                f'INSERT INTO {table_name} ({columns["keys"]}) VALUES ({columns["values"]})'
            )
            self.conn.execute(query, params)
            self.conn.commit()


        except (
                sqlite3.OperationalError,
                Exception
        ) as e:
            db_logger.error('Data Insert Error : ', e)
            return False

        return True

    def get_raw_json(self, table_name: str, hash: str) -> dict:
        cursor = self.conn.cursor()
        data = ''
        tx_id = ''
        try:
            cursor.execute(f'SELECT txid, file FROM {table_name} WHERE txid = ?', (hash,))
            (tx_id, data) = cursor.fetchone()

        except Exception as E:
            db_logger.error('Data Insert Error : ', E)
        # print('-------------')
        # print(isinstance(data, dict))
        # print(isinstance(data, str))
        # print(data)
        # _da = json.loads(data)
        #
        # print(isinstance(_da, dict))
        # exit(0)

        _da = json.loads(data)

        return _da


class LargeCacheTransferToDb(FolderBase):
    def __init__(self, project_name: str):
        self.by_project_name(project_name)
        self.data_schema = "data/sql/project_planner.json"
        self._project = project_name
        path_db = os.path.join(DATAPATH_BASE, self.cachefolder, 'cache.db')
        self.sb = BlockChainCase(
            db_name=path_db,
            db_config_file_path=self.data_schema,
            same_thread=False
        )
        self.cache_db_path = path_db

    def isDbExist(self) -> bool:
        if os.path.isfile(self.cache_db_path) is False:
            return False
        return self.sb.found_table("transaction_cache")

    def newTable(self):
        self.sb.create_table()
        print("---------- reinstall db is now on")

    def find_in_cache(self, hash: str) -> bool:
        return self.sb.has_has("transaction_cache", hash)

    def get_in_hash(self, hash: str) -> dict:
        return self.sb.get_raw_json("transaction_cache", hash)

    def process(self, hash: str, blob: str) -> bool:
        if self.sb.has_has("transaction_cache", hash) is True:
            return False

        return self.sb.insert_chain_hash("transaction_cache", hash, {
            "file": blob,
        })

    def processUpdate(self, hash: str, blob: str) -> bool:
        if self.sb.has_has("transaction_cache", hash) is False:
            return False

        return self.sb.update_data_hash("transaction_cache", hash, {
            "file": blob,
        })
